# This files contains your custom actions which can be used to run
# custom Python code.
#
# See this guide on how to implement these action:
# https://rasa.com/docs/rasa/custom-actions


# This is a simple example for a custom action which utters "Hello World!"

from typing import Any, Text, Dict, List

from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher

from mongoengine import connect
from mongoengine.errors import NotUniqueError, ValidationError

from constants import MONGO_DB, MONGO_USERNAME, MONGO_HOST

import time

class ActionFindFailingServices(Action):

    def name(self) -> Text:
        return "action_service_latency"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        # Connect To DB
        connect(db=MONGO_DB, username=MONGO_USERNAME, host=MONGO_HOST)       
        # Create Query
        failedServices = SpanLatency.objects(response_status="failure").order_by('-start_timestamp')
        # Return Response
        responses = [], traces = {}
        for data in failedServices:
          responses.append([data.span_name])
          traces[data.span_name] = '...url/' + data.trace_id 

        list(dict.fromkeys(responses))
        response = 'Hey .....' # Build Apt Response
        dispatcher.utter_message(text=response)

        return []

class ActionServiceLatency(Action):

    def name(self) -> Text:
        return "action_service_latency"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        # Connect To DB
        connect(db=MONGO_DB, username=MONGO_USERNAME, host=MONGO_HOST)       
        # Create Query
        slowServices = SpanLatency.objects(span_kind="SERVER", duration__gte=220).order_by('-duration')
        # Return Response
        responses = []
        for data in slowServices:
          responses.append(data.span_name)
        list(dict.fromkeys(responses))

        response = 'Hey .....' # Build Apt Response
        dispatcher.utter_message(text=response)

        return []

class ActionsDegradingServices(Action):

    def name(self) -> Text:
        return "action_service_latency"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        # Connect To DB
        connect(db=MONGO_DB, username=MONGO_USERNAME, host=MONGO_HOST)       
        
        # Create Query
        currentTimestamp = round(time.time())
        previousHourTimestamp = currentTimestamp - 3600*1000000
        previousDayTimestamp = currentTimestamp - 3600*24*1000000
        seviceOneRecent = SpanLatency.objects(start_timestamp__gte=previousHourTimestamp, span_name="service1").average('duration')
        seviceOnePrevious = SpanLatency.objects(start_timestamp__lt=previousHourTimestamp, start_timestamp__gte=, span_name="service1").average('duration')
        didServiceOneDegrade = seviceOneRecent < seviceOnePrevious ? true : false 
        seviceTwoRecent = SpanLatency.objects(start_timestamp__gte=previousHourTimestamp, span_name="service2").average('duration')
        seviceTwoPrevious = SpanLatency.objects(start_timestamp__lt=previousHourTimestamp, start_timestamp__gte=, span_name="service2").average('duration')
        didServiceTwoDegrade = seviceTwoRecent < seviceTwoPrevious ? true : false 
        seviceThreeRecent = SpanLatency.objects(start_timestamp__gte=previousHourTimestamp, span_name="service3").average('duration')
        seviceThreePrevious = SpanLatency.objects(start_timestamp__lt=previousHourTimestamp, start_timestamp__gte=, span_name="service3").average('duration')
        didServiceThreeDegrade = seviceThreeRecent < seviceThreePrevious ? true : false 
        
        # Return Response
        response = 'Hey .....' # Build Apt Response
        dispatcher.utter_message(text=response)

        return []

class ActionServiceLoad(Action):

    def name(self) -> Text:
        return "action_service_load"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        # Connect To DB
        connect(db=MONGO_DB, username=MONGO_USERNAME, host=MONGO_HOST)       
        # Create Query
        service = tracket.get_slot('slow_service_name')
        cpuLoad = CpuLoad.objects(service_name=service).cpu_load
        memLoad = MemLoad.objects(service_name=service).mem_load_bytes

        response = 'Hey .....' # Build Apt Response
        dispatcher.utter_message(text=response)

        return []

class ActionFindMaintainer(Action):

    def name(self) -> Text:
        return "action_service_load"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
  
        service = tracket.get_slot('slow_service_name')
        maintainers = {
         'service1' : {
            'email' : '',
            'phone' : ''
            'manager_email' : ''
          }
        }        
        maintainer = maintainers[service]
        response = 'Hey .....' # Build Apt Response
        dispatcher.utter_message(text=response)

        return []

class ActionServiceInfo(Action):

    def name(self) -> Text:
        return "action_service_load"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        # Connect To DB
        connect(db=MONGO_DB, username=MONGO_USERNAME, host=MONGO_HOST)       
        # Create Query
        service = tracket.get_slot('slow_service_name')

        response = 'Hey .....' # Build Apt Response
        dispatcher.utter_message(text=response)

        return []
