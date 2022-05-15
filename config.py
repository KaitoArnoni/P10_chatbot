import os

#from dotenv import load_dotenv

class DefaultConfig:
     """Configuration for the bot."""

    #load_dotenv()
    PORT = 3978
    APP_ID = "a477203b-cbe8-42cb-818b-4f770713d3d6"
    APP_PASSWORD = "2nl8Q~k.StUr6UBOFbHBnCfBAtr9ETt3UPoXoa3f"



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
    APPINSIGHTS_INSTRUMENTATION_KEY = "cc047ac6-f7bb-4a55-b1f0-84097220789c"
