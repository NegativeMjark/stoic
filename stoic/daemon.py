# #!/usr/bin/python
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

import fcntl
import os
import sys
import resource
import logging
import socket
import errno
import contextlib


@contextlib.contextmanager
def lockfile(path):
    path = os.path.abspath(path)
    fd = os.open(path, os.O_CREAT | os.O_RDWR)
    try:
        fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
        os.write(fd, "%5d" % os.getpid())
        yield
    finally:
        os.remove(path)
        os.close(fd)


class DaemonError(Exception):
    pass


class Daemon(object):
    """ Daemon object
    Object constructor expects two arguments:
    - app: contains the application name used for logging
    - socket_file: path to control socket.
    - keep_fds: optional list of fds which should not be closed.
    """
    def __init__(self, name, socket_file, keep_fds=None, logger=None,
                 startup_lock_file=None):
        self.name = name
        self.socket_file = os.path.abspath(socket_file)
        self.keep_fds = keep_fds or []
        if logger is None:
            logger = logging.getLogger(name)
        self.logger = logger
        if startup_lock_file is None:
           startup_lock_file = socket_file + ".lock"
        self.startup_lock_file = os.path.abspath(startup_lock_file)

    def check_if_already_running(self):
        with contextlib.closing(socket.socket(socket.AF_UNIX)) as client:
            try:
                client.connect(self.socket_file)
                self.logger.error(
                    "Daemon is already running at socket %r", self.socket_file
                )
                raise DaemonError("Daemon is already running")
            except socket.error as error:
                if error.errno == errno.ECONNREFUSED:
                    return
                else:
                    raise

    def setup(self):
        pass

    def teardown(self):
        pass

    def listen(self, server_socket):
        while True:
            (connection, addr) = server_socket.accept()
            try:
                data = connection.recv(1)
                if data == "\x00":
                    self.shutdown_connection = connection
                    break
            except:
                pass
            connection.close()

    def stop(self):
        with contextlib.closing(socket.socket(socket.AF_UNIX)) as client:
            try:
                client.connect(self.socket_file)
            except socket.error as error:
                if error.errno == errno.ENOENT:
                    raise DaemonError("Daemon isn't running")
                else:
                    raise
            client.send("\x00")
            client.recv(1)

    def start(self):
        """ start method
        Main daemonization process.
        """

        with contextlib.closing(socket.socket(socket.AF_UNIX)) as server:
            with lockfile(self.startup_lock_file):
                try:
                    server.bind(self.socket_file)
                except socket.error as error:
                    if error.errno == errno.EADDRINUSE:
                        self.check_if_already_running()
                        os.remove(self.socket_file)
                        server.bind(self.socket_file)
                    else:
                        raise
                server.listen(1)

            # Fork, creating a new process for the child.
            if os.fork():
                return

            # Move child process into a different session
            os.setsid()

            # Fork again so that we aren't the group leader.
            if os.fork():
                sys.exit(0)

            # Add socket to self.keep_fds.
            self.keep_fds.append(server.fileno())

            # Close all file descriptors, except the ones in self.keep_fds.
            devnull = "/dev/null"
            if hasattr(os, "devnull"):
                # Python has set os.devnull on this system, use it instead as
                # it might be different than /dev/null.
                devnull = os.devnull

            for fd in range(3, resource.getrlimit(resource.RLIMIT_NOFILE)[0]):
                if fd not in self.keep_fds:
                    try:
                        os.close(fd)
                    except OSError:
                        pass

            devnull_fd = os.open(devnull, os.O_RDWR)
            os.dup2(devnull_fd, 0)
            os.dup2(devnull_fd, 1)
            os.dup2(devnull_fd, 2)

            # Set umask to default to safe file permissions when running as a
            # root daemon. 027 is an octal number which we are typing as 0o27
            # for Python3 compatibility.
            os.umask(0o27)

            # Change to a known directory. If this isn't done, starting a
            # daemon in a subdirectory that needs to be deleted results in
            # "directory busy" errors.
            os.chdir("/")

            self.logger.warn("Starting daemon.")

            self.setup()
            self.listen(server)
            self.teardown()
            server.close()
            os.remove(self.socket_file)
            sys.exit(0)
