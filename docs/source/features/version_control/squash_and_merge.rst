##################
 Squash and Merge
##################

TensorBay supports squashing and merging between different branches.

Before :func:`~tensorbay.client.version.VersionControlMixin.squash_and_merge`, a dataset client instance with commits on different branches is needed.
See more details in :doc:`/features/version_control/draft_and_commit`.

.. figure:: /images/squash_and_merge.png
   :scale: 40 %
   :align: center

   The graphical gas log about the squash and merge operation below.

.. literalinclude:: ../../../../docs/code/squash_and_merge.py
      :language: python
      :start-after: """Authorize a Dataset Client Instance"""
      :end-before: """"""

TensorBay SDK allows :func:`~tensorbay.client.version.VersionControlMixin.squash_and_merge` by giving the ``target_branch_name``:

.. literalinclude:: ../../../../docs/code/squash_and_merge.py
      :language: python
      :start-after: """Squash and Merge"""
      :end-before: """"""

Or ``checkout`` to the target_branch first. In this case, the current branch is ``main``, so we can do squash_and_merge operation directly.

.. literalinclude:: ../../../../docs/code/squash_and_merge.py
      :language: python
      :start-after: """Checkout First"""
      :end-before: """"""

.. note::
    There are three strategies for handling the branch conflict:

    #. "abort": abort the opetation;

    #. "override": the squashed branch will override the target branch;

    #. "skip": keep the origin branch.
