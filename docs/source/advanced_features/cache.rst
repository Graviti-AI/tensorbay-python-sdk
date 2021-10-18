#######
 Cache
#######

This topic describes how to use cache while opening remote data on Tensorbay.

While using online data, sometimes it may be neccessary to use the entire dataset multiple times,
such as training model.

This would cause redundant requests and responses between the local computer and TensorBay,
and cost extra time.

Therefore, TensorBaySDK provides caching to speed up data access and reduce repeated requests.

********************
 Get Remote Dataset
********************

To use the cache, first get the remote dataset on TensorBay.

.. literalinclude:: ../../../docs/code/cache.py
   :language: python
   :start-after: """Get Remote Dataset"""
   :end-before: """"""

**************
 Enable Cache
**************

Then use :meth:`~tensorbay.dataset.dataset.DatasetBase.enable_cache()` to start using cache for this dataset.
The cache path is set in the temporary directory by default, which differs according to the system.

.. literalinclude:: ../../../docs/code/cache.py
   :language: python
   :start-after: """Enable Cache"""
   :end-before: """"""

It's also feasible to pass a custom cache path to the function as below.

.. literalinclude:: ../../../docs/code/cache.py
   :language: python
   :start-after: """Setting Cache Path"""
   :end-before: """"""

.. note::
   Please make sure there is enough free storage space to cache the dataset.

Use :attr:`~tensorbay.dataset.dataset.DatasetBase.cache_enabled` to check whether the cache is in use.

.. literalinclude:: ../../../docs/code/cache.py
   :language: python
   :start-after: """Cache Enabled"""
   :end-before: """"""

.. note::
   Cache is not available for datasets in draft status.
   The ``dataset.cache_enabled`` will remain ``False`` for datasets in draft status,
   even if the cache has already been set by ``dataset.enable_cache()``.

**********
 Use Data
**********

After enabling the cache, use the data as desired.
Note that the cache works when the :meth:`data.open()<tensorbay.utility.file.RemoteFileMixin.open()>` method is called,
and only data and mask labels will be cached.

.. literalinclude:: ../../../docs/code/cache.py
   :language: python
   :start-after: """Open Remote Data"""
   :end-before: """"""

*******************
 Delete Cache Data
*******************

After use, according to the cache path, the cache data can be deleted as needed.

Note that if the default cache path is used,
the cache will be removed automatically when the computer restarts.
