#!/usr/bin/env python3
#
# Copyright 2021 Graviti. Licensed under MIT License.
#

"""Basic structures of asynchronous jobs."""

from typing import Any, Dict, Optional, Tuple, Type, TypeVar

from tensorbay.client.struct import Draft
from tensorbay.utility import AttrsMixin, ReprMixin, ReprType, attr, camel, common_loads


class Job(AttrsMixin, ReprMixin):  # pylint: disable=too-many-instance-attributes
    """This class defines :class:`Job`.

    Arguments:
        title: Title of the Job.
        job_id: ID of the Job.
        arguments: Arguments of the Job.
        created_at: The time when the Job is created.
        started_at: The time when the Job is started.
        finished_at: The time when the Job is finished.
        status: The status of the Job.
        error_message: The error message of the Job.
        result: The result of the Job.
        description: The description of the Job.

    """

    _T = TypeVar("_T", bound="Job")

    _repr_type = ReprType.INSTANCE
    _repr_maxlevel = 2

    _repr_attrs: Tuple[str, ...] = (
        "title",
        "arguments",
        "created_at",
        "started_at",
        "finished_at",
        "status",
        "error_message",
    )

    title: str = attr()
    job_id: str = attr(key=camel)
    arguments: Dict[str, Any] = attr()
    created_at: int = attr(key=camel)
    started_at: Optional[int] = attr(key=camel)
    finished_at: Optional[int] = attr(key=camel)
    status: str = attr()
    error_message: str = attr(key=camel)
    _result: Optional[Dict[str, Any]] = attr(key="result")
    description: Optional[str] = attr(default="")

    def __init__(  # pylint: disable=too-many-arguments
        self,
        title: str,
        job_id: str,
        arguments: Dict[str, Any],
        created_at: int,
        started_at: Optional[int],
        finished_at: Optional[int],
        status: str,
        error_message: str,
        result: Optional[Dict[str, Any]],
        description: Optional[str] = "",
    ) -> None:
        self.title = title
        self.job_id = job_id
        self.arguments = arguments
        self.created_at = created_at
        self.started_at = started_at
        self.finished_at = finished_at
        self.status = status
        self.error_message = error_message
        self._result = result
        self.description = description

    def _repr_head(self) -> str:
        return f'{self.__class__.__name__}("{self.job_id}")'

    @classmethod
    def loads(cls: Type[_T], contents: Dict[str, Any]) -> _T:
        """Loads a :class:`Job` instance for the given contents.

        Arguments:
            contents: A dict containing the information of the Job::

                {
                    "title": <str>
                    "jobId": <str>
                    "arguments": <object>
                    "createdAt": <int>
                    "startedAt": <int>
                    "finishedAt": <int>
                    "status": <str>
                    "errorMessage": <str>
                    "result": <object>
                    "description": <str>
                }

        Returns:
            A :class:`Job` instance containing all the information in the given contents.

        """
        return common_loads(cls, contents)

    def update(self, until_complete: bool = False) -> None:
        """Update attrs of the Job instance.

        Arguments:
            until_complete: Whether to update job information until it is complete.

        """

    def abort(self) -> None:
        """Abort a :class:`Job`."""

    def retry(self) -> None:
        """Retry a :class:`Job`."""


class SquashAndMergeJob(Job):
    """This class defines :class:`SquashAndMergeJob`."""

    @property
    def result(self) -> Optional[Draft]:
        """Get the result of the SquashAndMergeJob.

        Return:
            The draft obtained from SquashAndMergeJob.

        """
