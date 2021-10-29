############
 Exceptions
############

TensorBay SDK defines a series of custom exceptions.

*********************
 Exception Hierarchy
*********************

The class hierarchy for TensorBay custom exceptions is::

 +-- TensorBayException
     +-- ClientError
         +-- StatusError
         +-- DatasetTypeError
         +-- FrameError
         +-- ResponseError
             +-- AccessDeniedError
             +-- ForbiddenError
             +-- InvalidParamsError
             +-- NameConflictError
             +-- RequestParamsMissingError
             +-- ResourceNotExistError
             +-- InternalServerError
             +-- UnauthorizedError
     +-- TBRNError
     +-- OpenDatasetError
         +-- NoFileError
         +-- FileStructureError




***********************
 Exception Definitions
***********************

The definitions for TensorBay custom exceptions are:

.. glossary::

    AccessDeniedError
        :class:`~tensorbay.exception.AccessDeniedError` defines the exception for access denied response error in the client module.
        Raised when the current account has no permission to access the resource.

    ClientError
        :class:`~tensorbay.exception.ClientError` is the base class for custom exceptions in the client module.

    DatasetTypeError
        :class:`~tensorbay.exception.DatasetTypeError` defines the exception for incorrect type of the requested dataset in the client module.
        Raised when the type of the required dataset is inconsistent with the input "is_fusion" parameter while getting dataset from TensorBay.

    FileStructureError
        :class:`~tensorbay.exception.FileStructureError` defines the exception for incorrect file structure in the opendataset directory.

    ForbiddenError
        :class:`~tensorbay.exception.ForbiddenError` defines the exception for illegal operations Tensorbay forbids.
        Raised when the current operation is forbidden by Tensorbay.

    FrameError
        :class:`~tensorbay.exception.FrameError` defines the exception for incorrect frame id in the client module.
        Raised when the frame id and timestamp of a frame conflicts or missing.

    InternalServerError
        :class:`~tensorbay.exception.InternalServerError` defines the exception for internal server error in the client module.
        Raised when internal server error was responded.

    InvalidParamsError
        :class:`~tensorbay.exception.InvalidParamsError` defines the exception for invalid parameters response error in the client module.
        Raised when the parameters of the request are invalid.

    NameConflictError
        :class:`~tensorbay.exception.NameConflictError` defines the exception for name conflict response error in the client module.
        Raised when the name of the resource to be created already exists on Tensorbay.

    NoFileError
        :class:`~tensorbay.exception.NoFileError` defines the exception for no matching file found in the opendataset directory.

    OpenDatasetError
        :class:`~tensorbay.exception.OpenDatasetError` is the base class for custom exceptions in the opendataset module.

    RequestParamsMissingError
        :class:`~tensorbay.exception.RequestParamsMissingError` defines the exception for request parameters missing response error in the client module.
        Raised when necessary parameters of the request are missing.

    ResourceNotExistError
        :class:`~tensorbay.exception.ResourceNotExistError` defines the exception for resource not existing response error in the client module.
        Raised when the request resource does not exist on Tensorbay.

    ResponseError
        :class:`~tensorbay.exception.ResponseError` defines the exception for post response error in the client module.
        Raised when the response from TensorBay has error. And different subclass exceptions will be raised according to different error code.

    StatusError
        :class:`~tensorbay.exception.StatusError` defines the exception for illegal status in the client module.
        Raised when the status is draft or commit, while the required status is commit or draft.

    TBRNError
        :class:`~tensorbay.exception.TBRNError` defines the exception for invalid TBRN. Raised when the TBRN format is incorrect.

    TensorBayException
        :class:`~tensorbay.exception.TensorBayException` is the base class for TensorBay SDK custom exceptions.

    UnauthorizedError
        :class:`~tensorbay.exception.UnauthorizedError` defines the exception for unauthorized response error in the client module.
        Raised when the :ref:`reference/glossary:accesskey` is incorrect.