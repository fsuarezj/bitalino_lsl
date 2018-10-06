Introduction
============

A python module called `bitalino-lsl` to stream BITalino data though the
Lab Streaming Layer (LSL). This module gets data from the
BITalino_ device through the
`bitalino python api`_ and uses the `Lab Stream Layer`_ to stream the data.

The module should work with python versions >= 2.7 although it has only been
tested for:

* Python 2.7.15

* Python 3.6.5

Getting started
---------------

You can install the module with pip:

.. code-block:: bash

  $ pip install bitalino_lsl

This examples streams BITalino data through the LSL and reads it from the
stream for 5 seconds:

.. literalinclude:: example.py
  :language: python
  
.. _BITalino: http://www.bitalino.com
.. _bitalino python api: https://github.com/BITalinoWorld/revolution-python-api
.. _Lab Stream Layer: https://github.com/sccn/labstreaminglayer
