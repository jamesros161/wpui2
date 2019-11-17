#!/usr/bin/python3.7
"""Main application module"""
# -*- coding: utf-8 -*-
# import os
import sys
# import tempfile

from datetime import datetime

from application import App
from settings import Settings
import logger

# Set python io encoding to utf-8
PYTHONIOENCODING = "utf-8"

# Catch all uncaugh exceptions and log exception

def main():
    """Initializes App instance and Starts main loop"""
    settings = Settings()
    log = logger.Log(settings)

    sys.excepthook = log.handle_exception
    log.debug("\n****\nApplication Started at %s \n\n****\n",
            datetime.strftime(datetime.now(), "%Y-%m-%d %H:%M:%S.%f"))
    app = App(log, settings)
    app.loop.run()

if __name__ == '__main__':
    main()
