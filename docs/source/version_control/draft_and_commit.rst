##################
 Draft and Commit
##################

The version control is based on the :ref:`reference/glossary:draft` and
:ref:`reference/glossary:commit`.

Similar with Git, a :ref:`reference/glossary:commit` is a version of a dataset,
which contains the changes compared with the former commit.

Unlike Git, a :ref:`reference/glossary:draft` is a new concept which represents a workspace in which changing the dataset is allowed.

In TensorBay SDK, the dataset client supplies the function of version control.

**************
Authorization
**************

.. literalinclude:: ../../../docs/code/draft_and_commit.py
      :language: python
      :start-after: """Authorize a Dataset Client Instance"""
      :end-before: """"""

*************
Create Draft
*************

TensorBay SDK supports creating the draft straightforwardly, which is based on the current commit.

.. literalinclude:: ../../../docs/code/draft_and_commit.py
      :language: python
      :start-after: """Create Draft"""
      :end-before: """"""

Then the dataset client will change the status to "draft" and store the draft number.
The draft number will be auto-increasing every time a draft is created.

.. literalinclude:: ../../../docs/code/draft_and_commit.py
      :language: python
      :start-after: """Draft Number Will Be Stored"""
      :end-before: """"""

************
List Drafts
************

The draft number can be found through listing drafts.

.. literalinclude:: ../../../docs/code/draft_and_commit.py
      :language: python
      :start-after: """List Drafts"""
      :end-before: """"""

**********
Get Draft
**********

.. literalinclude:: ../../../docs/code/draft_and_commit.py
      :language: python
      :start-after: """Get Draft"""
      :end-before: """"""

*************
Commit Draft
*************

After the commit, the draft will be closed.

.. literalinclude:: ../../../docs/code/draft_and_commit.py
      :language: python
      :start-after: """Commit Draft"""
      :end-before: """"""

***********
Get Commit
***********

.. literalinclude:: ../../../docs/code/draft_and_commit.py
      :language: python
      :start-after: """Get Commit"""
      :end-before: """"""

*************
List Commits
*************

.. literalinclude:: ../../../docs/code/draft_and_commit.py
      :language: python
      :start-after: """List Commits"""
      :end-before: """"""

*********
Checkout
*********

.. literalinclude:: ../../../docs/code/draft_and_commit.py
      :language: python
      :start-after: """Checkout"""
      :end-before: """"""
