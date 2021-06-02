########
 Branch
########

TensorBay supports diverging from the main line of development and continue
to do work without messing with that main line. Like Git, the way Tensorbay branches is incredibly lightweight,
making branching operations nearly instantaneous, and switching back and forth between branches generally just as fast.
Tensorbay encourages workflows that branch often, even multiple times in a day.

Before operating branches, a dataset client instance with existing commit is needed.

.. literalinclude:: ../../../docs/code/branch.py
      :language: python
      :start-after: """Authorize a Dataset Client Instance"""
      :end-before: """"""

***************
 Create Branch
***************

Create Branch on the Current Commit
===================================

TensorBay SDK supports creating the branch straightforwardly, which is based on the current commit.

.. literalinclude:: ../../../docs/code/branch.py
      :language: python
      :start-after: """Create Branch"""
      :end-before: """"""

Then the dataset client will storage the branch name. "main" is the default branch, it will be created when init the
dataset

.. literalinclude:: ../../../docs/code/branch.py
      :language: python
      :start-after: """Branch Name Will Be Stored"""
      :end-before: """"""

Create Branch on a Revision
============================

Also, creating a branch based on a revision is allowed.

.. literalinclude:: ../../../docs/code/branch.py
      :language: python
      :start-after: """Create Branch Based On a Revision"""
      :end-before: """"""

The dataset client will checkout to the branch. The stored commit id is from the commit which the branch points to.

.. literalinclude:: ../../../docs/code/branch.py
      :language: python
      :start-after: """Branch Name Will Be Stored(Revision)"""
      :end-before: """"""

Specially, creating a branch based on a former commit is permitted.

.. literalinclude:: ../../../docs/code/branch.py
      :language: python
      :start-after: """Create Branch Based On a Former Commit"""
      :end-before: """"""

Similarly, the dataset client will checkout to the branch.

.. literalinclude:: ../../../docs/code/branch.py
      :language: python
      :start-after: """Branch Name Will Be Stored(Former Commit)"""
      :end-before: """"""

Then, through creating and committing the draft
based on the branch, diverging from the current line of development can be realized.

.. literalinclude:: ../../../docs/code/branch.py
      :language: python
      :start-after: """Create and Commit Draft"""
      :end-before: """"""

***************
 List Branches
***************

.. literalinclude:: ../../../docs/code/branch.py
      :language: python
      :start-after: """List Branches"""
      :end-before: """"""

************
 Get Branch
************

.. literalinclude:: ../../../docs/code/branch.py
      :language: python
      :start-after: """Get a Branch"""
      :end-before: """"""

***************
 Delete Branch
***************

.. literalinclude:: ../../../docs/code/branch.py
      :language: python
      :start-after: """Delete a Branch"""
      :end-before: """"""
