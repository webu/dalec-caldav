#!/usr/bin/env python
import os
import sys
from multiprocessing import Process

import django
from django.conf import settings
from django.test.utils import get_runner
from radicale.__main__ import run as run_radicale

if __name__ == "__main__":
    os.environ["RADICALE_CONFIG"] = "./.radicale/config"
    os.environ["DJANGO_SETTINGS_MODULE"] = "tests.settings"
    radicale_server = Process(target=run_radicale)
    django.setup()
    TestRunner = get_runner(settings)
    test_runner = TestRunner(failfast=True)
    radicale_server.start()
    try:
        failures = test_runner.run_tests(["tests"])
    finally:
        radicale_server.terminate()
    sys.exit(bool(failures))
