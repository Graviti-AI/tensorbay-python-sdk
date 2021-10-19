######
 Diff
######

TensorBay supports showing changes between commits or drafts.

Before operating the :ref:`reference/glossary:diff`, a dataset client instance with commits is needed.
See more details in :ref:`features/version_control/draft_and_commit:Draft and Commit`

**********
 Get Diff
**********

TensorBay SDK allows getting the dataset :ref:`reference/glossary:diff`
through :ref:`reference/glossary:basehead`. Currently, only obtaining the :ref:`reference/glossary:diff`
between the head and its parent commit is supported; that is, the head is the given version(commit or draft) while the
base is parent commit of the head.

.. literalinclude:: ../../../../docs/code/diff.py
      :language: python
      :start-after: """Get Diff"""
      :end-before: """"""

The type of the head indicates the version status: ``string`` for commit, ``int`` for draft.


Get Diff on Revision
====================

For example, the following diff records the difference between the commit whose id is ``"3bc35d806e0347d08fc23564b82737dc"``
and its parent commit.

.. literalinclude:: ../../../../docs/code/diff.py
      :language: python
      :start-after: """Get Diff on Commit"""
      :end-before: """"""

Get Diff on Draft Number
========================

For example, the following diff records the difference between the draft whose draft number is ``1``
and its parent commit.

.. literalinclude:: ../../../../docs/code/diff.py
      :language: python
      :start-after: """Get Diff on Draft"""
      :end-before: """"""

Diff Object
===========

The structure of the returning :class:`~tensorbay.client.diff.DatasetDiff` looks like::

   dataset_diff
   ├── segment_diff
   │   ├── action
   │   │   └── <str>
   │   ├── data_diff
   │   │   ├── file_diff
   │   │   │   └── action
   │   │   │       └── <str>
   │   │   └── label_diff
   │   │       └── action
   │   │           └── <str>
   │   └── ...
   ├── segment_diff
   │   ├── action
   │   │   └── <str>
   │   ├── data_diff
   │   │   ├── file_diff
   │   │   │   └── action
   │   │   │       └── <str>
   │   │   └── label_diff
   │   │       └── action
   │   │           └── <str>
   │   └── ...
   └── ...

The :class:`~tensorbay.client.diff.DatasetDiff` is a list which is composed of :class:`~tensorbay.client.diff.SegmentDiff`
recording the changes of the segment. The :class:`~tensorbay.client.diff.SegmentDiff` is a lazy-load sequence
which is composed of :class:`~tensorbay.client.diff.DataDiff` recording the changes of data.

The attribute "action" represents the status difference of the relative resource. It is an enum which includes:

- unmodify
- add
- delete
- modify
