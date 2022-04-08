..
 Copyright 2021 Graviti. Licensed under MIT License.

#############
Search Result
#############

***************************
 Search Result from Dataset
***************************

TensorBay SDK allows create :class:`~tensorbay.client.search.SearchResult` via :class:`~tensorbay.client.job.BasicSearchJob`.

.. literalinclude:: ../../../../docs/code/search_result.py
      :language: python
      :start-after: """Obtain a SearchResult Instance"""
      :end-before: """"""

Get Label Statistics
====================

The label statistics of the search result can be obtained by :func:`~tensorbay.client.search.SearchResult.get_label_statistics`

.. literalinclude:: ../../../../docs/code/search_result.py
      :language: python
      :start-after: """Get Label Statistics"""
      :end-before: """"""

List Segment Names
==================

All segment names can be obtained by :func:`~tensorbay.client.search.SearchResult.list_segment_names`

.. literalinclude:: ../../../../docs/code/search_result.py
      :language: python
      :start-after: """List Segment names"""
      :end-before: """"""

List Data
=========

Required data of the specific segment can be obtained by :func:`~tensorbay.client.search.SearchResult.list_data`

.. literalinclude:: ../../../../docs/code/search_result.py
      :language: python
      :start-after: """List Data"""
      :end-before: """"""


*********************************
Search Result from Fusion Dataset
*********************************

TensorBay SDK allows create :class:`~tensorbay.client.search.FusionSearchResult` via :class:`~tensorbay.client.job.BasicSearchJob`.

.. literalinclude:: ../../../../docs/code/search_result.py
      :language: python
      :start-after: """Obtain a FusionSearchResult Instance"""
      :end-before: """"""

FusionSearchResult can also get label statistics and list segment names in the same way as searchResult.

.. literalinclude:: ../../../../docs/code/search_result.py
      :language: python
      :start-after: """The same function as SearchResult"""
      :end-before: """"""


List Frames
===========

Required frames of the specific segment can be obtained by :func:`~tensorbay.client.search.FusionSearchResult.list_frames`

.. literalinclude:: ../../../../docs/code/search_result.py
      :language: python
      :start-after: """List Frames"""
      :end-before: """"""

Get Sensors
===========

The sensors of the specific segment can be obtained by :func:`~tensorbay.client.search.FusionSearchResult.get_sensors`

.. literalinclude:: ../../../../docs/code/search_result.py
      :language: python
      :start-after: """Get Sensors"""
      :end-before: """"""
