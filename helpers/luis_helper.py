# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
from enum import Enum
from typing import Dict
from botbuilder.ai.luis import LuisRecognizer
from botbuilder.core import IntentScore, TopIntent, TurnContext
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
from datatypes_date_time import Timex

from booking_details import BookingDetails



class Intent(Enum):
    BOOK_FLIGHT = "book_flight"
    NONE_INTENT = "None"

def top_intent(intents: Dict[Intent, dict]) -> TopIntent:
    max_intent = Intent.NONE_INTENT
    max_value = 0.0

    for intent, value in intents:
        intent_score = IntentScore(value)
        if intent_score.score > max_value:
            max_intent, max_value = intent, intent_score.score

    return TopIntent(max_intent, max_value)


class LuisHelper:
    @staticmethod
    async def execute_luis_query(
        luis_recognizer: LuisRecognizer, turn_context: TurnContext
    ) -> (Intent, object):
        """
        Returns an object with preformatted LUIS results for the bot's dialogs to consume.
        """
        result = None
        intent = None

        try:
            recognizer_result = await luis_recognizer.recognize(turn_context)

            intent = (
                sorted(
                    recognizer_result.intents,
                    key=recognizer_result.intents.get,
                    reverse=True,
                )[:1][0]
                if recognizer_result.intents
                else None
            )

            if intent == Intent.BOOK_FLIGHT.value:
                #print('intent detected')
                result = BookingDetails()

                # We need to get the result from the LUIS JSON which at every level returns an array.
                # Extract the departure city
                from_city = recognizer_result.entities.get("from_city")
                #print(from_city)
                if from_city:
                    result.from_city = from_city[0]
                    
                # Extract the arrival city
                to_city = recognizer_result.entities.get("to_city")
                #print(to_city)
                if to_city:
                    result.to_city = to_city[0]

                # Extract the budget
                budget = recognizer_result.entities.get("budget")
                #print(budget)
                if budget:
                    result.budget = budget[0]  

                # Extract from_dt
                
                from_dt = recognizer_result.entities.get("from_dt")
                #print(from_dt)
                if from_dt:
                    from_dt = LuisHelper.transform_data(from_dt[0])
                    result.from_dt = from_dt 

                # Extract to_dt
                to_dt = recognizer_result.entities.get("to_dt")
                #print(to_dt)
                if to_dt:
                    to_dt = LuisHelper.transform_data(to_dt[0])
                    result.to_dt = to_dt 
                    

        except Exception as exception:
            print(exception)

        print ("return")
        return intent, result

    @staticmethod
    def transform_data (date_time):
        try:
            format = '%d / %m / %Y'
            datetime_str = datetime.strptime(date_time, format) 
            change_format = datetime_str.strftime('%Y-%m-%d')
            return change_format
        except:
            try:
                format = '%d - %m - %Y'
                datetime_str = datetime.strptime(date_time, format) 
                change_format = datetime_str.strftime('%Y-%m-%d')
                return change_format
            except:
                return None



            
