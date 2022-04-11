..
 Copyright 2021 Graviti. Licensed under MIT License.
 
##################
 Squash and Merge
##################

TensorBay supports squashing and merging between different branches asynchronously.

Firstly, a dataset client instance with commits on different branches is needed.
See more details in :ref:`features/version_control/draft_and_commit:Draft and Commit`.

.. figure:: /images/squash_and_merge.png
   :scale: 40 %
   :align: center

   The graphical gas log about the squash and merge operation below.

.. literalinclude:: ../../../../docs/code/squash_and_merge.py
      :language: python
      :start-after: """Authorize a Dataset Client Instance"""
      :end-before: """"""

*******************
 SquashAndMergeJob
*******************

TensorBay SDK allows create, get, list or delete :class:`~tensorbay.client.job.SquashAndMergeJob` via :class:`~tensorbay.client.version.SquashAndMerge`.

Create 
======

In the case of creating a SquashAndMergeJob, the ``target_branch_name`` could be given in advance: 

.. literalinclude:: ../../../../docs/code/squash_and_merge.py
      :language: python
      :start-after: """Create Job"""
      :end-before: """"""

Or ``checkout`` to the target_branch first. In this case, the current branch is ``main``, so we can create job directly.

.. literalinclude:: ../../../../docs/code/squash_and_merge.py
      :language: python
      :start-after: """Checkout First"""
      :end-before: """"""

.. note::
    There are three strategies for handling the branch conflict:

    #. "abort": abort the opetation;

    #. "override": the squashed branch will override the target branch;

    #. "skip": keep the origin branch.

Get, list or delete
===================

The latest SquashAndMergeJob can be obtained by :func:`~tensorbay.client.version.SquashAndMerge.get_job` or :func:`~tensorbay.client.version.SquashAndMerge.list_jobs`.
The finished SquashAndMergeJob can be deleted by :func:`~tensorbay.client.version.JobMixin.delete_job`.

.. literalinclude:: ../../../../docs/code/squash_and_merge.py
      :language: python
      :start-after: """Get, List and Delete"""
      :end-before: """"""

Get information
===============

Available SquashAndMergeJob information includes ``title``, ``description``, ``job_id``, ``arguments``, ``created_at``, ``started_at``, ``finished_at``,
``status``, ``error_message`` and ``result``.

.. literalinclude:: ../../../../docs/code/squash_and_merge.py
      :language: python
      :start-after: """Get Job Info"""
      :end-before: """"""

.. note::
    If the SquashAndMergeJob is successfully completed, the result will be a :class:`~tensorbay.client.struct.Draft`.

Update
======

The latest information of a SquashAndMergeJob can be obtained after :func:`~tensorbay.client.job.Job.update`. Note that if the ``until_complete`` is
set to ``True``, the SquashAndMergeJob will be blocked until it is completed.

.. literalinclude:: ../../../../docs/code/squash_and_merge.py
      :language: python
      :start-after: """Update Job"""
      :end-before: """"""

Abort or retry
==============

SquashAndMergeJob also supports :func:`~tensorbay.client.job.Job.abort` and :func:`~tensorbay.client.job.SquashAndMergeJob.retry`:

.. literalinclude:: ../../../../docs/code/squash_and_merge.py
      :language: python
      :start-after: """Abort and Retry Job"""
      :end-before: """"""
