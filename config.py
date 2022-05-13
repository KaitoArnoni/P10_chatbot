#!/usr/bin/env python
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
"""Configuration for the bot."""

import os

from dotenv import load_dotenv

class DefaultConfig:
    """Configuration for the bot."""
    load_dotenv()
    PORT = 3978
    APP_ID = os.getenv("APP_PASSWORD")
    APP_PASSWORD = os.getenv("APP_PASSWORD")
    LUIS_APP_ID = os.getenv("LUIS_APP_ID" 
    LUIS_API_KEY = os.getenv("LUIS_API_KEY")    
    LUIS_API_HOST_NAME = os.getenv("LUIS_API_HOST_NAME")
    APPINSIGHTS_INSTRUMENTATION_KEY = os.getenv("APPINSIGHTS_INSTRUMENTION_KEY")
