# Copyright 2015: Mirantis Inc.
# All Rights Reserved.
#    Licensed under the Apache License, Version 2.0 (the "License");
#    you may not use this file except in compliance with the License.
#    You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS,
#    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#    See the License for the specific language governing permissions and
#    limitations under the License.

import asyncio
import logging

LOG = logging.getLogger(__name__)

class PeriodicTask(object):
    def __init__(self, interval, method):
        self.active = False
        self._interval = interval
        self.method = method
        self._loop = asyncio.get_event_loop()

    def _run(self):
        self.run()
        self._handler = self._loop.call_later(self._interval, self._run)

    def run(self):
        self.method()

    def start(self):
        self._handler = self._loop.call_later(self._interval, self._run)

    def stop(self):
        self._handler.cancel()
