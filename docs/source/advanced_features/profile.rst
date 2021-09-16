###########
 Profilers
###########

This topic describes how to use :class:`~tensorbay.client.profile.Profile`
to record speed statistics.

Usage
=====

You can save the statistical record to a txt, csv or json file.

.. literalinclude:: ../../../docs/code/profile.py
      :language: python
      :start-after: """Usage of Profile"""
      :end-before: """"""

Set ``multiprocess=True`` to record the multiprocessing program.

.. literalinclude:: ../../../docs/code/profile.py
      :language: python
      :start-after: """Usage of Multiprocess"""
      :end-before: """"""


The above action would save a summary.txt file and the result is as follows::

    |Path                    |totalTime (s) |callNumber  |avgTime (s) |totalResponseLength  |totalFileSize (B)|
    |[GET] data06/labels     |11.239        |25          |0.450       |453482               |0                |
    |[GET] data06/data/urls  |16.739        |25          |0.670       |794545               |0                |
    |[POST] oss-cn-shanghai  |0.567         |10          |0.057       |0                    |8058707          |

.. note::
   The `profile` will only record statistics of the interface that interacts with Tensorbay.
