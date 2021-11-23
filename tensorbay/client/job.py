#!/usr/bin/env python3
#
# Copyright 2021 Graviti. Licensed under MIT License.
#

"""Basic structures of asynchronous jobs."""

from typing import Any, Dict, Optional


class Job:  # pylint: disable=too-many-instance-attributes
    """This class defines :class:`Job`.

    Arguments:
        title: Title of the Job.
        job_id: ID of the Job.
        job_type: Type of the Job.
        creator: The creator of the Job.
        arguments: Arguments of the Job.
        created_at: The time when the Job is created.
        started_at: The time when the Job is started.
        max_retries: The maximum retry times of the Job.
        finished_at: The time when the Job is finished.
        description: The description of the Job.

    """

    def __init__(  # pylint: disable=too-many-arguments
        self,
        title: str,
        job_id: str,
        job_type: str,
        creator: str,
        arguments: Dict[str, Any],
        created_at: str,
        started_at: str,
        max_retries: int,
        finished_at: Optional[str] = None,
        description: Optional[str] = "",
    ) -> None:
        self.title = title
        self.job_id = job_id
        self.job_type = job_type
        self.creator = creator
        self.arguments = arguments
        self.created_at = created_at
        self.started_at = started_at
        self.max_retries = max_retries
        self.finished_at = finished_at
        self.description = description

    def get_status(self) -> Dict[str, Any]:
        """Get the status of the Job.

        Return:
            The status dict of the Job::

                {
                    "status": <str>,
                    "code": <str>,
                    "errorMessage": <str>
                }


        """

    def get_log(self) -> str:
        """Get the log of the Job.

        Return:
            The log of the Job.

        """


class SquashAndMergeJob(Job):
    """This class defines :class:`SquashAndMergeJob`."""

    def get_result(self) -> Dict[str, int]:
        """Get the result of the SquashAndMergeJob.

        Return:
            The result dict of the SquashAndMergeJob::

                {
                    "draftNumber": <int>,
                }



        """
