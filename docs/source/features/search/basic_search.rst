..
 Copyright 2021 Graviti. Licensed under MIT License.

##############
 Basic Search
##############

TensorBay supports basic search based on different commits.

.. literalinclude:: ../../../../docs/code/basic_search.py
      :language: python
      :start-after: """Authorize a Dataset Client Instance"""
      :end-before: """"""

****************
 BasicSearchJob
****************

TensorBay SDK allows create, get or list :class:`~tensorbay.client.job.BasicSearchJob` via :class:`~tensorbay.client.version.BasicSearch`.

Create
======

A BasicSearchJob can be created by :func:`~tensorbay.client.version.BasicSearch.create_job`

.. literalinclude:: ../../../../docs/code/basic_search.py
      :language: python
      :start-after: """Create Job"""
      :end-before: """"""

.. note::
    ``conjunction``: The logical conjunction between search filters, which includes "AND" and "OR".

.. note::
    ``unit``:The unit of basic search. There are two options:
        * "FILE": Get the data that meets search filters;
        * "FRAME": If at least one data in a frame meets search filters, all data in the frame will be get. This option only works on fusion dataset.

.. note::
    ``filters``: The list of basic search criteria whose format is (key, operator, value, label_type).
        * key: The keyword of filters, which could be "segment", "size", "withLabel", "frame", "sensor", "category", "attribute" or "dataRemotePath".
        * operator: The operational relationship between the key and value. The supported operators are "like", "in", "=", ">", "<", ">=" and "<=".
        * value: The value of filters.
        * label_type：It only needs to be used if the key is "category" or "attribute", indicating the label type to which the category or attribute belongs.

        There are also some restrictions on operators and values:

        .. list-table::
           :widths: auto
           :header-rows: 1

           * - key
             - permitted operator
             - type of value
           * - "segment"
             - "in"
             - list
           * - "size"
             - "=", ">", "<", ">=", "<="
             - int
           * - "withLabel"
             - "="
             - boolean
           * - "frame"
             - "like", "="
             - string
           * - "sensor"
             - "in"
             - list
           * - "category"
             - "in"
             - list
           * - "attribute"
             - "in"
             - dict
           * - "dataRemotePath"
             - "like", "="
             - string

Get or List
===========

The latest BasicSearchJob can be obtained by :func:`~tensorbay.client.version.BasicSearch.get_job` or :func:`~tensorbay.client.version.BasicSearch.list_jobs`.

.. literalinclude:: ../../../../docs/code/basic_search.py
      :language: python
      :start-after: """Get and List"""
      :end-before: """"""

Get Information
===============

Available BasicSearchJob information includes ``title``, ``description``, ``job_id``, ``arguments``, ``created_at``, ``started_at``, ``finished_at``,
``status``, ``error_message`` and ``result``.

.. literalinclude:: ../../../../docs/code/basic_search.py
      :language: python
      :start-after: """Get Job Info"""
      :end-before: """"""

.. note::
    If the BasicSearchJob is successfully completed, the result will be :class:`~tensorbay.client.search.SearchResult` or :class:`~tensorbay.client.search.FusionSearchResult`.
    See more details in :doc:`/features/search/search_result`.

.. important::
    Only the latest five search results for one dataset can be used.

Update
======

The latest information of a BasicSearchJob can be obtained after :func:`~tensorbay.client.job.Job.update`. Note that if the ``until_complete`` is
set to ``True``, the BasicSearchJob will be blocked until it is completed.

.. literalinclude:: ../../../../docs/code/basic_search.py
      :language: python
      :start-after: """Update Job"""
      :end-before: """"""

Abort or Retry
==============

BasicSearchJob also supports :func:`~tensorbay.client.job.Job.abort` and :func:`~tensorbay.client.job.Job.retry`:

.. literalinclude:: ../../../../docs/code/basic_search.py
      :language: python
      :start-after: """Abort and Retry Job"""
      :end-before: """"""
