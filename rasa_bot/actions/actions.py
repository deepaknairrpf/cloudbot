# This files contains your custom actions which can be used to run
# custom Python code.
#
# See this guide on how to implement these action:
# https://rasa.com/docs/rasa/custom-actions


# This is a simple example for a custom action which utters "Hello World!"
from datetime import datetime, timedelta
from typing import Any, Text, Dict, List

from mongoengine import connect
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import AllSlotsReset, SlotSet

from constants import MONGO_DB, MONGO_USERNAME, MONGO_HOST
from models import SpanLatency, FAILURE, SERVER_KIND, CpuLoad, MemLoad
from rasa_bot.actions.utils import extract_int_from_string
from rasa_bot.actions.constants import DEFAULT_LATENCY_THRESHOLD

# Mongo Queries to be used by the chat bot
connect(db=MONGO_DB, username=MONGO_USERNAME, host=MONGO_HOST)


class ActionSlowService(Action):

    def name(self) -> Text:
        return "action_slow_service"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        latency_threshold = tracker.get_slot("threshold")
        latency_threshold = extract_int_from_string(latency_threshold)
        if not latency_threshold:
            latency_threshold = DEFAULT_LATENCY_THRESHOLD


        x = latency_threshold
        slow_services = SpanLatency.objects.aggregate([
            {"$match": {'span_kind': 'SERVER', 'response_status': 'SUCCESS'}},
            {"$group": {"_id": "$span_name", "average_latency": {"$avg": "$duration"}}},
            {"$match": {'average_latency': {'$gt': x * 1000}}},  # Milliseconds to Zipkin's microsecond conversion
        ])

        if slow_services:
            response = f'Services having an average latency greater than {x} milliseconds.\n'

            for result in slow_services:
                service = result['_id']
                average_latency = result['average_latency']
                average_latency = average_latency / 1000
                response += f'{service} has an avg latency of {average_latency} milliseconds\n'
        else:
            response = f'No services have average latency greater than {x} milliseconds'

        dispatcher.utter_message(text=response)

        return [AllSlotsReset(), SlotSet('threshold', str(latency_threshold))]


def convert_to_trace_links(trace_ids):
    zipkin_url = 'http://localhost:9411/zipkin/traces/'
    hyperlinks = []
    for i, trace_id in enumerate(trace_ids):
        trace_name = f'trace-{i}'
        trace_link = zipkin_url + str(trace_id)
        hyperlink = f'{trace_name} - {trace_link}'
        hyperlinks.append(hyperlink)
    return hyperlinks


class ActionFailingService(Action):

    def name(self) -> Text:
        return "action_failing_service"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        # Services that are failing.
        failing_services_qs = SpanLatency.objects(response_status=FAILURE, span_kind=SERVER_KIND).distinct('span_name')
        failing_services = [service_name for service_name in failing_services_qs]
        print(f'Failing services are {", ".join(failing_services)}')

        # Show top three traces of failing services
        top_three_failing_traces_qry = [
            {"$match": {'span_kind': 'SERVER', 'response_status': 'FAILURE'}},
            {'$sort': {"duration": -1}},
            {"$group": {"_id": "$span_name", "trace_ids": {"$push": {"trace_id": "$trace_id"}}}},
            {"$project": {"trace_ids": {"$slice": ["$trace_ids", 3]}}}
        ]
        top_three_failing_traces = SpanLatency.objects.aggregate(top_three_failing_traces_qry)
        results_response = ''
        for result in top_three_failing_traces:
            service = result['_id']
            trace_ids = result['trace_ids']
            trace_ids = [item['trace_id'] for item in trace_ids]
            trace_links = convert_to_trace_links(trace_ids)
            results_response += f'Service name : {service} \n'
            trace_links = ','.join(trace_links)
            results_response += f'{len(trace_ids)} failed traces : {trace_links}'

        response = 'Here are the services that failed.\n'
        response += results_response
        dispatcher.utter_message(text=response)
        return [AllSlotsReset()]


class ActionDegradingService(Action):

    def name(self) -> Text:
        return "action_degrading_service"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        # Services which are degrading in performance
        distinct_services = SpanLatency.objects(span_kind=SERVER_KIND).distinct('span_name')
        if distinct_services:
            for service in distinct_services:
                most_recent_span = SpanLatency.objects(span_name=service, span_kind=SERVER_KIND).order_by(
                    '-start_timestamp').first()
                most_recent_span_id = most_recent_span.id
                most_recent_span_duration = most_recent_span.duration
                avg_latency = SpanLatency.objects(span_name=service, span_id__ne=most_recent_span_id,
                                                  span_kind=SERVER_KIND).average('duration')

                if most_recent_span_duration > avg_latency:

                    response = f'''{service} is degrading in performance.\nDuration of latest request took {most_recent_span_duration} microseconds as opposed to an average latency of {avg_latency} microseconds\n'''
        else:
            response = 'No services are degrading in performance.'

        dispatcher.utter_message(text=response)

        return [AllSlotsReset()]


class ActionAskMaintainer(Action):

    def name(self) -> Text:
        return "action_ask_maintainer"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        service_name = tracker.get_slot("service_name")

        latest_service_span = SpanLatency.objects(span_name=service_name, span_kind=SERVER_KIND).order_by(
            '-start_timestamp').first()
        developer_details = latest_service_span.developer_details
        response = f'Developer details for the service : {service_name}.\n'
        for k, v in developer_details.items():
            k = k.title()
            response += f'{k}: {v}\n'
        dispatcher.utter_message(text=response)

        return [AllSlotsReset()]


class ActionAskMoreInfo(Action):

    def name(self) -> Text:
        return "action_ask_moreinfo"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        service_name = tracker.get_slot("service_name")

        response = f"asking more info about service : {service_name}"
        dispatcher.utter_message(text=response)
        return [AllSlotsReset()]


class ActionServiceLoad(Action):

    def name(self) -> Text:
        return "action_service_load"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        service_name = tracker.get_slot("service_name")
        current_time = datetime.now()
        previous_hour = current_time - timedelta(hours=1)
        previous_hour_ts = previous_hour.timestamp()

        avg_cpu_load = CpuLoad.objects(service_name=service_name).average('cpu_load')
        hourly_avg_cpu_load = CpuLoad.objects(service_name=service_name, timestamp__gte=previous_hour_ts).average(
            'cpu_load')

        response = f'Avg CPU load for service - {service_name} is {round(avg_cpu_load, 2)}% and the hourly average is {round(hourly_avg_cpu_load, 2)}% \n'

        avg_mem_usage = MemLoad.objects(service_name=service_name).average('mem_load_bytes')
        hourly_avg_mem_usage = MemLoad.objects(service_name=service_name, timestamp__gte=previous_hour_ts).average(
            'mem_load_bytes')

        response += f'Avg memory consumption for service - {service_name} is {int(avg_mem_usage)} bytes and the hourly average is {int(hourly_avg_mem_usage)} bytes'
        dispatcher.utter_message(text=response)
        return [AllSlotsReset()]
