##################
 Draft And Commit
##################

The version control is based on the :ref:`version_control/draft_and_commit:draft` and
:ref:`version_control/draft_and_commit:commit`.

In TensorBay SDK, the :class:`~tensorbay.client.gas.GAS` is responsible for operating the datasets, while
the :class:`~tensorbay.client.dataset.DatasetClient` is for operating content of one dataset
in the draft or commit. Thus, the dataset client supports the function of version control.

In this section, you’ll learn the relationship between the draft and commit.

*******
Commit
*******

Similar with Git, a commit is a version of a dataset,
which contains the changes compared with the former commit.
You can view a certain commit of a dataset based on the given commit ID.

A commit is readable, but is not writable.
Thus, only read operations such as getting catalog, files and labels are allowed.
To make changes to a dataset, please create a draft first.
See :ref:`version_control/draft_and_commit:draft` for details.

On the other hand,
"commit" also represents the action to save the changes inside a :ref:`version_control/draft_and_commit:draft`
into a commit.

******
Draft
******

Unlike Git, a draft is a new concept which represents a workspace in which changing the dataset is allowed.

A draft is created based on a :ref:`version_control/draft_and_commit:commit`,
and the changes inside it will be made into a commit.

There are scenarios when modifications of a dataset are required,
such as correcting errors, enlarging dataset, adding more types of labels, etc.
Under these circumstances, you can create a draft, edit the dataset and commit the draft.

***********
Before Use
***********

In the next part, you'll learn the basic operations towards draft and commit.

First, a dataset client object is needed.

.. literalinclude:: ../../../examples/draft_and_commit.py
      :language: python
      :start-after: """Authorize a Dataset Client Object"""
      :end-before: """"""

*************
Create Draft
*************

TensorBay SDK supports creating the draft straightforwardly, which is based on the current commit.

.. literalinclude:: ../../../examples/draft_and_commit.py
      :language: python
      :start-after: """Create Draft"""
      :end-before: """"""

Then the dataset client will change the status to "draft" and store the draft number.
The draft number will be auto-increasing every time you create a draft.
The draft number can be found through listing drafts.

.. literalinclude:: ../../../examples/draft_and_commit.py
      :language: python
      :start-after: """Draft Number Will Be Stored"""
      :end-before: """"""

************
List Drafts
************

Listing the existing :class:`~tensorbay.client.struct.Draft` in TensorBay SDK is simple.

.. literalinclude:: ../../../examples/draft_and_commit.py
      :language: python
      :start-after: """List Drafts"""
      :end-before: """"""

**********
Get Draft
**********

TensorBay SDK supports getting the :class:`~tensorbay.client.struct.Draft` with the draft number.

.. literalinclude:: ../../../examples/draft_and_commit.py
      :language: python
      :start-after: """Get Draft"""
      :end-before: """"""

*************
Commit Draft
*************

TensorBay SDK supports committing the draft, after that the draft will be closed.

.. literalinclude:: ../../../examples/draft_and_commit.py
      :language: python
      :start-after: """Commit Draft"""
      :end-before: """"""

Then the dataset client will change the status to "commit" and store the commit ID.

.. literalinclude:: ../../../examples/draft_and_commit.py
      :language: python
      :start-after: """Commit ID Will Be Stored"""
      :end-before: """"""

***********
Get Commit
***********

TensorBay SDK supports getting the :class:`~tensorbay.client.struct.Commit` with the commit ID.

.. literalinclude:: ../../../examples/draft_and_commit.py
      :language: python
      :start-after: """Get Commit"""
      :end-before: """"""

*************
List Commits
*************

Listing the existing :class:`~tensorbay.client.struct.Commit` in TensorBay SDK is simple.

.. literalinclude:: ../../../examples/draft_and_commit.py
      :language: python
      :start-after: """List Commits"""
      :end-before: """"""

*********
Checkout
*********

The dataset client can checkout to other draft with draft number or to commit with commit id.

.. literalinclude:: ../../../examples/draft_and_commit.py
      :language: python
      :start-after: """Checkout"""
      :end-before: """"""
