############
 Exceptions
############

TensorBay SDK defines a series of custom exceptions.

*****************
 Base Exceptions
*****************

The following exceptions are used as the base classes for other concrete exceptions.

TensorBayException
^^^^^^^^^^^^^^^^^^

:class:`~tensorbay.exception.TensorBayException` is the base class for TensorBay SDK custom exceptions.

ClientError
^^^^^^^^^^^

:class:`~tensorbay.exception.ClientError` is the base class for custom exceptions in client module.

OpenDatasetError
^^^^^^^^^^^^^^^^

:class:`~tensorbay.exception.OpenDatasetError` is the base class for custom exceptions in opendataset module.

*********************
 Concrete Exceptions
*********************

CommitStatusError
^^^^^^^^^^^^^^^^^

:class:`~tensorbay.exception.CommitStatusError` defines the exception for illegal commit status. Raised when the status is draft or commit, while the required status is commit or draft.

DatasetTypeError
^^^^^^^^^^^^^^^^

:class:`~tensorbay.exception.DatasetTypeError` defines the exception for incorrect type of the requested dataset. Raised when the type of the required dataset is inconsistent with the input "is_fusion" parameter while getting dataset from TensorBay.

FrameError
^^^^^^^^^^

:class:`~tensorbay.exception.FrameError` defines the exception for incorrect frame id. Raised when the frame id and timestamp of a frame conflicts or missing.

ResponseError
^^^^^^^^^^^^^

:class:`~tensorbay.exception.ResponseError` defines the exception for post response error. Raised when the response from TensorBay has error.

TBRNError
^^^^^^^^^

:class:`~tensorbay.exception.TBRNError` defines the exception for invalid TBRN. Raised when the TBRN format is incorrect.

NoFileError
^^^^^^^^^^^

:class:`~tensorbay.exception.NoFileError` defines the exception for no matching file found in the opendataset directory.

FileStructureError
^^^^^^^^^^^^^^^^^^

:class:`~tensorbay.exception.FileStructureError` defines the exception for incorrect file structure in the opendataset directory.

*********************
 Exception hierarchy
*********************

The class hierarchy for TensorBay custom exceptions is::

 +-- TensorBayException
     +-- ClientError
         +-- CommitStatusError
         +-- DatasetTypeError
         +-- FrameError
         +-- ResponseError
     +-- TBRNError
     +-- OpenDatasetError
         +-- NoFileError
         +-- FileStructureError

