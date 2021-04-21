############
 Exceptions
############

TensorBay SDK defines a series of custom exceptions.

.. glossary::

    TensorBayException
        :class:`~tensorbay.exception.TensorBayException` is the base class for TensorBay SDK custom exceptions.

    TBRNError
        :class:`~tensorbay.exception.TBRNError` defines the exception for invalid TBRN. Raised when the TBRN format is incorrect.

    TensorBayClientError
        :class:`~tensorbay.exception.TensorBayClientError` is the base class for custom exceptions in the client module.

    CommitStatusError
        :class:`~tensorbay.exception.CommitStatusError` defines the exception for illegal commit status in the client module.
        Raised when the status is draft or commit, while the required status is commit or draft.

    DatasetTypeError
        :class:`~tensorbay.exception.DatasetTypeError` defines the exception for incorrect type of the requested dataset in the client module.
        Raised when the type of the required dataset is inconsistent with the input "is_fusion" parameter while getting dataset from TensorBay.

    FrameError
        :class:`~tensorbay.exception.FrameError` defines the exception for incorrect frame id in the client module.
        Raised when the frame id and timestamp of a frame conflicts or missing.

    ResponseError
        :class:`~tensorbay.exception.ResponseError` defines the exception for post response error in the client module.
        Raised when the response from TensorBay has error.

    TensorBayOpenDatasetError
        :class:`~tensorbay.exception.TensorBayOpenDatasetError` is the base class for custom exceptions in the opendataset module.

    NoFileError
        :class:`~tensorbay.exception.NoFileError` defines the exception for no matching file found in the opendataset directory.

    FileStructureError
        :class:`~tensorbay.exception.FileStructureError` defines the exception for incorrect file structure in the opendataset directory.

*********************
 Exception hierarchy
*********************

The class hierarchy for TensorBay custom exceptions is::

 +-- TensorBayException
     +-- TensorBayClientError
         +-- CommitStatusError
         +-- DatasetTypeError
         +-- FrameError
         +-- ResponseError
     +-- TBRNError
     +-- TensorBayOpenDatasetError
         +-- NoFileError
         +-- FileStructureError

