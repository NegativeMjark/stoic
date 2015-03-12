Stoic
=====

A more reliable way to run programs.

Features
--------

* Stoic restarts your process when it dies.
* Stoic doesn't tightloop if your process immediately dies again.
* Stoic captures stdout and stderr from your process and logs them with
  timestamps.
* Stoic can run in the background as a daemon.
* A new stoic program will wait for the old process to finish and release any
  sockets before starting.
* Notifies by email [4]_, IRC [5]_ or HTTP [6]_ when the process restarts.


Usage
-----

.. code:: sh

    # Run a command
    stoic -- myprogram myarguments

    # Run a process in the background.
    stoic --start --log-file=stoic.log --socket=stoic.socket -- myprogram

    # Replace a running background process
    stoic --replace --log-file=stoic.log --socket=stoic.socket -- myprogram

    # Stops a running background process and waits for it to finish
    stoic --stop --socket=stoic.socket


Installation
------------

.. code:: sh

    pip install stoic

----

.. [4] Email notifications not implemented yet.
.. [5] IRC notifications not implemented yet.
.. [6] HTTP notifications not implemented yet.
