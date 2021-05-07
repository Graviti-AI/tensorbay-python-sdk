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
        Raised when the response from TensorBay has error. And different subclass exceptions will be raised according to different error code.

    AccessDeniedError
        :class:`~tensorbay.exception.AccessDeniedError` defines the exception for access denied response error in the client module.
        Raised when the current account has no permission to access the resource.

    InvalidParamsError
        :class:`~tensorbay.exception.InvalidParamsError` defines the exception for invalid parameters response error in the client module.
        Raised when the parameters of the request are invalid.

    NameConflictError
        :class:`~tensorbay.exception.NameConflictError` defines the exception for name conflict response error in the client module.
        Raised when the name of the resource to be created already exists on Tensorbay.

    RequestParamsMissingError
        :class:`~tensorbay.exception.RequestParamsMissingError` defines the exception for request parameters missing response error in the client module.
        Raised when necessary parameters of the request are missing.

    ResourceNotExistError
        :class:`~tensorbay.exception.ResourceNotExistError` defines the exception for resource not existing response error in the client module.
        Raised when the request resource does not exist on Tensorbay.

    ResponseSystemError
        :class:`~tensorbay.exception.ResponseSystemError` defines the exception for system response error in the client module.
        Raised when system error was responded.

    UnauthorizedError
        :class:`~tensorbay.exception.UnauthorizedError` defines the exception for unauthorized response error in the client module.
        Raised when the :ref:`reference/glossary:accesskey` is incorrect.

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
             +-- AccessDeniedError
             +-- InvalidParamsError
             +-- NameConflictError
             +-- RequestParamsMissingError
             +-- ResourceNotExistError
             +-- ResponseSystemError
             +-- UnauthorizedError
     +-- TBRNError
     +-- TensorBayOpenDatasetError
         +-- NoFileError
         +-- FileStructureError

