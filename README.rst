Stoic
=====

A more reliable way to run programs.

Features
--------

* Restarts your process when it dies.
* Doesn't tightloop if your process immediately dies again.
* Captures stdout and stderr from your process and logs them with
  timestamps[1]_.
* Can be run in the background as a daemon[2]_.
* Gracefully move between different stoic processses, waiting for the previous
  process to stop and release any ports before starting the next[3]_.
* Notifies by email[4]_, IRC[5]_ or HTTP[6]_ when the process restarts.

.. [1] Timestamps in log files not implemented yet.
.. [2] Daemonising not implemented yet.
.. [3] Graceful restarts not implemented yet.
.. [4] Email notifications not implemented yet.
.. [5] IRC notifications not implemented yet.
.. [6] HTTP notifications not implemented yet.

Usage
-----

.. code:: sh

    # Run a command
    stoic -- myprogram myarguments

    # Run a process in the background.
    stoic --daemon --log-file=stoic.log --socket=stoic.control -- myprogram

    # Replace a running process
    stoic --replace --log-file=stoic.log --socket=stoic.control -- myprogram

Installation
------------

.. code:: sh

    pip install stoic
