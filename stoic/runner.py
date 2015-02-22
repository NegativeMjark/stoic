# Copyright 2015 Mark Haines
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import subprocess
import logging
import threading
import time

class Runner(object):

    def __init__(self, name, arguments, executable=None):
        self.name = name
        self.executable = executable
        self.arguments = arguments
        self.shutting_down = False
        self.time_last_restarted = None
        self.default_backoff_seconds = 1
        self.current_backoff_seconds = self.default_backoff_seconds
        self.process_logger = logging.getLogger(name + "-process")
        self.stdout_logger = logging.getLogger(name + "-stdout")
        self.stderr_logger = logging.getLogger(name + "-stderr")
        self.process_condition = threading.Condition()

    @staticmethod
    def log_from_pipe(pipe, logger, level):
        try:
            line = pipe.readline()
            while line:
                logger.log(level, line.rstrip('\n').replace("%","%%"))
                line = pipe.readline()
        except:
            pass

    def run_once(self):
        with self.process_condition:
            process = subprocess.Popen(
                self.arguments,
                executable=self.executable,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                stdin=None,
            )
            self.process = process
        stdout_thread = threading.Thread(
            target=self.log_from_pipe,
            args=(process.stdout, self.stdout_logger, logging.INFO),
        )
        stderr_thread = threading.Thread(
            target=self.log_from_pipe,
            args=(process.stderr, self.stderr_logger, logging.ERROR),
        )
        stdout_thread.start()
        stderr_thread.start()
        result = process.wait()
        stdout_thread.join()
        stderr_thread.join()
        self.process = None
        return result

    def start(self):
        self.process_thread = threading.Thread(
            name=self.name + "-process",
            target=self.run,
        )
        self.process_thread.start()
        return self.process_thread

    def restart(self):
        with self.process_condition:
            if self.process:
                self.process.terminate()
                self.process_condition.notify()

    def shutdown(self):
        self.shutting_down = True
        with self.process_condition:
            if self.process:
                self.process.terminate()
            self.process_condition.notify()
        self.process_thread.join()

    def restart_delay(self):
        time_now = time.time()
        if self.time_last_restarted is None:
            delay = None
        else:
            time_since_restart = self.time_last_restarted - time_now
            current_backoff = self.current_backoff_seconds
            if current_backoff <= time_since_restart:
                self.current_backoff_seconds = max(
                    self.default_backoff_seconds,
                    2 * current_backoff - time_since_restart / 2
                )
                delay = None
            else:
                delay = current_backoff - time_since_restart
                self.current_backoff_seconds *= 2

        self.time_last_restarted = time_now
        return delay

    def run(self):
        while True:
            with self.process_condition:
                if self.shutting_down:
                    self.process_logger.info("Shutting down, not restarting")
                    break
                elif self.time_last_restarted is not None:
                    self.process_logger.info("Restarting process")
                else:
                    self.process_logger.info("Starting process")

            code = self.run_once()

            with self.process_condition:
                if self.shutting_down:
                    self.process_logger.info(
                        "Process shutdown with return code %d", code
                    )
                    break

                delay = self.restart_delay()

                if delay is None:
                    self.process_logger.warn(
                        "Process ended with return code %d."
                        " Restarting immediately.", code
                    )
                else:
                    self.process_logger.warn(
                        "Process ended with return code %d."
                        " Restarting in %d seconds", code, delay
                    )
                    self.process_condition.wait(delay)
