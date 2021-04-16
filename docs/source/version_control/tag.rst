#####
 Tag
#####

TensorBay SDK has the ability to tag specific commits in a dataset's history as being important.
Typically, people use this functionality to mark release points (v1.0, v2.0 and so on).
In this section, you'll learn how to list existing tags, how to create and delete tags.

Before operating tags, a dataset client instance with commit is needed.

.. literalinclude:: ../../../examples/tag.py
      :language: python
      :start-after: """Authorize a Dataset Client Instance"""
      :end-before: """"""

************
 Create Tag
************

TensorBay SDK supports two approaches of creating the tag.

One is creating the tag straightforwardly, which is based on the current commit.

.. literalinclude:: ../../../examples/tag.py
      :language: python
      :start-after: """Create Tag"""
      :end-before: """"""


The other is creating the tag when committing.

.. literalinclude:: ../../../examples/tag.py
      :language: python
      :start-after: """Create Tag When Committing"""
      :end-before: """"""

*********
 Get Tag
*********

TensorBay SDK supports getting the :class:`~tensorbay.client.struct.Tag` with the tag name.

.. literalinclude:: ../../../examples/tag.py
      :language: python
      :start-after: """Get Tag"""
      :end-before: """"""

***********
 list Tags
***********

Listing the existing :class:`~tensorbay.client.struct.Tag` in TensorBay SDK is simple.

.. literalinclude:: ../../../examples/tag.py
      :language: python
      :start-after: """List Tags"""
      :end-before: """"""

************
 Delete Tag
************

TensorBay SDK supports deleting the tag with the tag name.

.. literalinclude:: ../../../examples/tag.py
      :language: python
      :start-after: """Delete Tag"""
      :end-before: """"""