.. credrails-reconciler documentation master file, created by
   sphinx-quickstart on Thu Feb 15 21:09:29 2024.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

.. image:: images/reconciler-logo.svg
   :align: center
   :alt: reconciler logo
   :scale: 60%

Credrails Reconciler
====================

credrails-reconciler is a tool that reads in two datasets, reconciles their
records, and produce a report detailing the differences between the two.


Installation
------------

We recommend using the latest version of Python. Python 3.12 and newer is
supported. We also recommend using a `virtual environment`_ in order
to isolate your project dependencies from other projects and the system.

Install the latest credrails-reconciler version using pip:

.. code-block:: bash

    pip install credrails-reconciler


API Reference
-------------

.. autosummary::
   :template: module.rst
   :toctree: api
   :caption: API
   :recursive:

     credrails.reconciler


.. _virtual environment: https://packaging.python.org/tutorials/installing-packages/#creating-virtual-environments
