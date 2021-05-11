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

If the endpoint of the cloud server is the same as the TensorBay storage, set `is_internal` to `True`
to use the internal endpoint for obtaining a faster network speed.

.. literalinclude:: ../../../docs/code/use_internal_endpoint.py
   :language: python
   :start-after: """Usage of Upload Dataset By Internal Endpoint"""
   :end-before: """"""