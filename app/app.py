#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
This will run the service in a looping standby.
"""

import os
import time
from k_util.logger import Logger
from logic.service import Service

__author__ = "Jakrin Juangbhanich"
__email__ = "juangbhanich.k@gmail.com"

K_SERVICE_INTERVAL = "SERVICE_INTERVAL"


if __name__ == "__main__":

    Logger.header("Running Style Transfer App")
    service = Service()

    service_interval = int(os.environ[K_SERVICE_INTERVAL]) if K_SERVICE_INTERVAL in os.environ else 60
    Logger.field("Service Interval", service_interval)

    while True:
        message, receipt_handle = service.check_for_message()
        if message is None:
            # Sleep for the service interval.
            time.sleep(service_interval)
            continue

        # Process the message.
        service.process_message(message, receipt_handle)

