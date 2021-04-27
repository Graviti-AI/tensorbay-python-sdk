#######################
 Request Configuration
#######################

This topic introduces the currently supported :class:`~tensorbay.client.requests.Config`
options(:numref:`Table. %s <request_config_table>`) for customizing request.
Note that the default settings can satisfy most use cases.

.. _request_config_table:

.. table:: Requests Configuration Tables
   :align: center
   :widths: auto

   ===================== =================================================================
   Variables             Description                                              
   ===================== =================================================================
   max_retries           | The number of maximum retry times of the request.
                         | If the request method is one of the allowed_retry_methods
                         | and the response status is one of the allowed_retry_status,
                         | then the request can auto-retry `max_retries` times.
                         | Scenario: Enlarge it when under poor network quality.
                         | Default: 3 times.
   allowed_retry_methods | The allowed methods for retrying request.
                         | Default: ["HEAD", "OPTIONS", "POST", "PUT"]
   allowed_retry_status  | The allowed status for retrying request.
                         | Default: [429, 500, 502, 503, 504]
   timeout               | The number of seconds before the request times out.
                         | Scenario: Enlarge it when under poor network quality.
                         | Default: 30 seconds.
   is_internal           | Whether the request is from internal or not. 
                         | Scenario: Set it to True for quicker network speed when datasets
                         | and cloud servers are in the same region.
                         | See :ref:`advanced features/use_internal_endpoint` for details.
                         | Default: False
   ===================== =================================================================

Usage
=====

Use upload `LISATrafficLight`_ dataset as an exmaple:

.. _LISATrafficLight: https://gas.graviti.cn/dataset/hello-dataset/LISATrafficLight

.. literalinclude:: ../../../examples/request_configuration.py
   :language: python
   :start-after: """Example of request config"""
   :end-before: """"""