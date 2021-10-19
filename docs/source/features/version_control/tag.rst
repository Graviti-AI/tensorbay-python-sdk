#####
 Tag
#####

TensorBay supports tagging specific commits in a dataset's history as being important.
Typically, people use this functionality to mark release revisions (v1.0, v2.0 and so on).

Before operating tags, a dataset client instance with existing commit is needed.

.. literalinclude:: ../../../../docs/code/tag.py
      :language: python
      :start-after: """Authorize a Dataset Client Instance"""
      :end-before: """"""

************
 Create Tag
************

TensorBay SDK supports three approaches of creating the tag.

First is to create the tag when committing.

.. literalinclude:: ../../../../docs/code/tag.py
      :language: python
      :start-after: """Create Tag When Committing"""
      :end-before: """"""

Second is to create the tag straightforwardly, which is based on the current commit.

.. literalinclude:: ../../../../docs/code/tag.py
      :language: python
      :start-after: """Create Tag Straightforwardly"""
      :end-before: """"""

Third is to create tag on an existing commit.

.. literalinclude:: ../../../../docs/code/tag.py
      :language: python
      :start-after: """Create Tag on an Existing Commit"""
      :end-before: """"""

*********
 Get Tag
*********

.. literalinclude:: ../../../../docs/code/tag.py
      :language: python
      :start-after: """Get Tag"""
      :end-before: """"""

***********
 List Tags
***********

.. literalinclude:: ../../../../docs/code/tag.py
      :language: python
      :start-after: """List Tags"""
      :end-before: """"""

************
 Delete Tag
************

.. literalinclude:: ../../../../docs/code/tag.py
      :language: python
      :start-after: """Delete Tag"""
      :end-before: """"""
