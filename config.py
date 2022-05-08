#!/usr/bin/env python
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
"""Configuration for the bot."""

import os

#from dotenv import load_dotenv


class DefaultConfig:
    """Configuration for the bot."""

    PORT = 3978
    APP_ID = "de2c8460-1479-4dd0-bebd-d97f47702983"
    APP_PASSWORD = os.environ.get("MicrosoftAppPassword", "")



    #PORT = 62077
    #APP_ID = "a90f7de4-f3d6-4fe0-ad0e-bdde96ff8974"
    #self.CHATBOT_BOT_ID = os.environ.get("CHATBOT_BOT_ID", "")
        
    #APP_PASSWORD = ""
    #self.CHATBOT_BOT_PASSWORD = os.environ.get("CHATBOT_BOT_PASSWORD", "")

    LUIS_APP_ID = "4151fd40-18a7-4701-8d67-bf7ec96a511a"
    #self.LUIS_APP_ID = os.environ.get("LUIS_APP_ID", "")
        
    LUIS_API_KEY = 'ff3063c9b2d0417c8e0e4ccc92b73dff'
    #self.LUIS_PRED_KEY = os.environ.get("LUIS_PRED_KEY", "")        


    LUIS_API_HOST_NAME = 'https://p10luis.cognitiveservices.azure.com/'
    #self.LUIS_PRED_ENDPOINT = os.environ.get("LUIS_PRED_ENDPOINT", "")
          
    #self.APPINSIGHTS_INSTRUMENTATIONKEY = os.environ.get("APPINSIGHTS_INSTRUMENTATIONKEY", "")
    APPINSIGHTS_INSTRUMENTATION_KEY = "9b6d58f6-50f3-4024-a6eb-5c2958c029af"
