# This files contains your custom actions which can be used to run
# custom Python code.
#
# See this guide on how to implement these action:
# https://rasa.com/docs/rasa/custom-actions


# This is a simple example for a custom action which utters "Hello World!"

from typing import Any, Text, Dict, List

from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import AllSlotsReset
from rasa_bot.actions.utils import extract_int_from_string
from rasa_bot.actions.constants import DEFAULT_LATENCY_THRESHOLD


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

        response = f"Query to find services slower than {latency_threshold} milli seconds"

        dispatcher.utter_message(text=response)

        return [AllSlotsReset()]


class ActionFailingService(Action):

    def name(self) -> Text:
        return "action_failing_service"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        dispatcher.utter_message(text="Message from action_failing_service")

        return [AllSlotsReset()]


class ActionDegradingService(Action):

    def name(self) -> Text:
        return "action_degrading_service"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        dispatcher.utter_message(text="Message from action_degrading_service")

        return [AllSlotsReset()]


class ActionAskMaintainer(Action):

    def name(self) -> Text:
        return "action_ask_maintainer"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        service_name = tracker.get_slot("service_name")

        response = f"asking Maintainer for service : {service_name}"
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
        response = f"load on service : {service_name} is ..."
        dispatcher.utter_message(text=response)
        return [AllSlotsReset()]
