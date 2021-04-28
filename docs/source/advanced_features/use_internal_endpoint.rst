#######################
 Use Internal Endpoint
#######################

This topic describes how to use the internal endpoint when using TensorBay.

Region and Endpoint
===================

For a cloud storage service platform, a region is a collection of its resources in a geographic
area. Each region is isolated and independent of the other regions.
Endpoints are the domain names that other services can use to access the cloud platform.
Thus, there are mappings between regions and endpoints.
Take OSS as an example, the endpoint for region **China (Hangzhou)** is
*oss-cn-hangzhou.aliyuncs.com*.

Actually, the endpoint mentioned above is the public endpoint.
There is another kind of endpoint called the internal endpoint.
The internal endpoint can be used by other cloud services in the
**same region** to access cloud storage services. For example, the internal endpoint for region
**China (Hangzhou)** is *oss-cn-hangzhou-internal.aliyuncs.com*.

Much quicker internet speed is the most important benefit of using an internal endpoint.
Currently, TensorBay supports using the internal endpoint of OSS for operations such as uploading
and reading datasets.

Usage
=====

For users with unstable network, we recommend the following solution:

   #. Make sure that a cloud server in a specific region is available.
   #. Create and upload datasets to TensorBay storage space which is in the same region as your cloud server.
   #. Read the datasets from your cloud server using the internal endpoint. 

Use upload `LISATrafficLight`_ dataset as an exmaple, set `is_internal` to `True` when using
internal endpoint:

.. _LISATrafficLight: https://gas.graviti.cn/dataset/hello-dataset/LISATrafficLight

.. literalinclude:: ../../../examples/use_internal_endpoint.py
   :language: python
   :start-after: """Usage of Upload Dataset By Internal Endpoint"""
   :end-before: """"""