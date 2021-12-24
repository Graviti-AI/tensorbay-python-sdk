#!/usr/bin/env python3
#
# Copyright 2021 Graviti. Licensed under MIT License.
#

"""Related methods of the TensorBay version control."""

from typing import Any, Callable, Dict, Generator, Optional, Union

from tensorbay.client.job import SquashAndMergeJob
from tensorbay.client.lazy import PagingList
from tensorbay.client.requests import Client
from tensorbay.client.status import Status
from tensorbay.client.struct import Branch, Commit, Draft, Tag
from tensorbay.exception import ResourceNotExistError, StatusError


class VersionControlMixin:  # pylint: disable=too-many-public-methods
    """A mixin class supporting version control methods."""

    _dataset_id: str
    _client: Client
    _status: Status

    def _get_basehead(
        self, base: Optional[Union[str, int]] = None, head: Optional[Union[str, int]] = None
    ) -> str:
        if head:
            head = f"draft-{head}" if isinstance(head, int) else f"commit-{head}"
        else:
            if self._status.is_draft:
                head = f"draft-{self._status.draft_number}"
            else:
                head = f"commit-{self._status.commit_id}"

        if base:
            base = f"draft-{base}" if isinstance(base, int) else f"commit-{base}"
            basehead = f"{base}...{head}"
        else:
            basehead = head

        return basehead

    def _commit(self, title: str, description: str, tag: Optional[str] = None) -> str:
        post_data: Dict[str, Any] = {"title": title}
        post_data.update(self._status.get_status_info())

        if description:
            post_data["description"] = description

        if tag:
            post_data["tag"] = tag

        response = self._client.open_api_do("POST", "commits", self._dataset_id, json=post_data)
        return response.json()["commitId"]  # type: ignore[no-any-return]

    def _generate_drafts(
        self, status: Optional[str], branch_name: Optional[str], offset: int = 0, limit: int = 128
    ) -> Generator[Draft, None, int]:
        params = {"offset": offset, "limit": limit, "status": status, "branchName": branch_name}
        response = self._client.open_api_do("GET", "drafts", self._dataset_id, params=params).json()

        for item in response["drafts"]:
            yield Draft.loads(item)

        return response["totalCount"]  # type: ignore[no-any-return]

    def _close_draft(self, number: int) -> None:
        patch_data = {"status": "CLOSED"}
        self._client.open_api_do("PATCH", f"drafts/{number}", self._dataset_id, json=patch_data)

    def _generate_commits(
        self, revision: str, offset: int = 0, limit: int = 128
    ) -> Generator[Commit, None, int]:
        params: Dict[str, Any] = {"offset": offset, "limit": limit, "commit": revision}

        response = self._client.open_api_do(
            "GET", "commits", self._dataset_id, params=params
        ).json()

        for item in response["commits"]:
            yield Commit.loads(item)

        return response["totalCount"]  # type: ignore[no-any-return]

    def _generate_branches(
        self, name: Optional[str] = None, offset: int = 0, limit: int = 128
    ) -> Generator[Branch, None, int]:
        params: Dict[str, Any] = {"offset": offset, "limit": limit}
        if name:
            params["name"] = name

        response = self._client.open_api_do(
            "GET", "branches", self._dataset_id, params=params
        ).json()

        for item in response["branches"]:
            yield Branch.loads(item)

        return response["totalCount"]  # type: ignore[no-any-return]

    def _generate_tags(
        self, name: Optional[str] = None, offset: int = 0, limit: int = 128
    ) -> Generator[Tag, None, int]:
        params: Dict[str, Any] = {"offset": offset, "limit": limit}
        if name:
            params["name"] = name

        response = self._client.open_api_do("GET", "tags", self._dataset_id, params=params).json()

        for item in response["tags"]:
            yield Tag.loads(item)

        return response["totalCount"]  # type: ignore[no-any-return]

    def _delete_branch(self, name: str) -> None:
        """Delete a branch without checking current branch.

        Arguments:
            name: The name of the branch to be deleted.

        """
        delete_data: Dict[str, Any] = {"name": name}

        self._client.open_api_do("DELETE", "branches", self._dataset_id, json=delete_data)

    def checkout(self, revision: Optional[str] = None, draft_number: Optional[int] = None) -> None:
        """Checkout to commit or draft.

        Arguments:
            revision: The information to locate the specific commit, which can be the commit id,
                the branch, or the tag.
            draft_number: The draft number.

        Raises:
            TypeError: When both commit and draft number are provided or neither.

        """
        if revision is None and draft_number is None:
            raise TypeError("Neither revision nor draft number is given, please give one")
        if revision is not None and draft_number is not None:
            raise TypeError("Both revision and draft number are given, please only give one")

        if revision:
            try:
                branch = self.get_branch(revision)
                self._status.checkout(commit_id=branch.commit_id)
                self._status.branch_name = branch.name
            except ResourceNotExistError:
                self._status.checkout(commit_id=self.get_commit(revision).commit_id)
                self._status.branch_name = None

        if draft_number:
            draft = self.get_draft(draft_number)
            self._status.checkout(draft_number=draft.number)
            self._status.branch_name = draft.branch_name

    def commit(self, title: str, description: str = "", *, tag: Optional[str] = None) -> None:
        """Commit the draft.

        Commit the draft based on the draft number stored in the dataset client.
        Then the dataset client will change the status to "commit"
        and store the branch name and commit id.

        Arguments:
            title: The commit title.
            description: The commit description.
            tag: A tag for current commit.

        """
        self._status.check_authority_for_draft()
        self._status.checkout(commit_id=self._commit(title, description, tag))

    def create_draft(
        self, title: str, description: str = "", branch_name: Optional[str] = None
    ) -> int:
        """Create a draft.

        Create a draft with the branch name. If the branch name is not given,
        create a draft based on the branch name stored in the dataset client.
        Then the dataset client will change the status to "draft"
        and store the branch name and draft number.

        Arguments:
            title: The draft title.
            description: The draft description.
            branch_name: The branch name.

        Returns:
            The draft number of the created draft.

        Raises:
            StatusError: When creating the draft without basing on a branch.

        """
        if not branch_name:
            branch_name = self._status.branch_name
            if not branch_name:
                raise StatusError(
                    message="Creating the draft without basing on a branch is not allowed"
                )
            self._status.check_authority_for_commit()

        post_data: Dict[str, Any] = {"branchName": branch_name, "title": title}

        if description:
            post_data["description"] = description

        response = self._client.open_api_do("POST", "drafts", self._dataset_id, json=post_data)
        draft_number: int = response.json()["draftNumber"]

        self._status.checkout(draft_number=draft_number)
        self._status.branch_name = branch_name
        return draft_number

    def get_draft(self, draft_number: Optional[int] = None) -> Draft:
        """Get the certain draft with the given draft number.

        Get the certain draft with the given draft number. If the draft number is not given,
        get the draft based on the draft number stored in the dataset client.

        Arguments:
            draft_number: The required draft number.
                If is not given, get the current draft.

        Returns:
            The :class:`.Draft` instance with the given number.

        Raises:
            TypeError: When the given draft number is illegal.
            ResourceNotExistError: When the required draft does not exist.

        """
        if draft_number is None:
            self._status.check_authority_for_draft()
            draft_number = self._status.draft_number

        if not draft_number:
            raise TypeError("The given draft number is illegal")

        for draft in self.list_drafts():
            if draft_number == draft.number:
                return draft

        raise ResourceNotExistError(resource="draft", identification=draft_number)

    def list_drafts(
        self, status: Optional[str] = "OPEN", branch_name: Optional[str] = None
    ) -> PagingList[Draft]:
        """List all the drafts.

        Arguments:
            status: The draft status which includes "OPEN", "CLOSED", "COMMITTED", "ALL" and None.
                    where None means listing open drafts.
            branch_name: The branch name.

        Returns:
            The PagingList of :class:`drafts<.Draft>`.

        """
        return PagingList(
            lambda offset, limit: self._generate_drafts(status, branch_name, offset, limit),
            128,
        )

    def update_draft(
        self,
        draft_number: Optional[int] = None,
        *,
        title: Optional[str] = None,
        description: Optional[str] = None,
    ) -> None:
        """Update the draft.

        Arguments:
            draft_number: The updated draft number.
                If is not given, update the current draft.
            title: The title of the draft.
            description: The description of the draft.

        """
        if draft_number is None:
            self._status.check_authority_for_draft()
            draft_number = self._status.draft_number

        patch_data: Dict[str, Any] = {}
        if title is not None:
            patch_data["title"] = title

        if description is not None:
            patch_data["description"] = description

        self._client.open_api_do(
            "PATCH", f"drafts/{draft_number}", self._dataset_id, json=patch_data
        )

    def close_draft(self, number: int) -> None:
        """Close the draft.

        Arguments:
            number: The draft number.

        Raises:
            StatusError: When closing the current draft.

        """
        if number == self._status.draft_number:
            raise StatusError("Closing the current draft is not allowed")

        self._close_draft(number)

    def get_commit(self, revision: Optional[str] = None) -> Commit:
        """Get the certain commit with the given revision.

        Get the certain commit with the given revision. If the revision is not given,
        get the commit based on the commit id stored in the dataset client.

        Arguments:
            revision: The information to locate the specific commit, which can be the commit id,
                the branch name, or the tag name.
                If is not given, get the current commit.

        Returns:
            The :class:`.Commit` instance with the given revision.

        Raises:
            TypeError: When the given revision is illegal.
            ResourceNotExistError: When the required commit does not exist.

        """
        if revision is None:
            self._status.check_authority_for_commit()
            revision = self._status.commit_id

        if not revision:
            raise TypeError("The given revision is illegal")

        try:
            commit = next(self._generate_commits(revision))
        except StopIteration as error:
            raise ResourceNotExistError(resource="commit", identification=revision) from error

        return commit

    def list_commits(self, revision: Optional[str] = None) -> PagingList[Commit]:
        """List the commits.

        Arguments:
            revision: The information to locate the specific commit, which can be the commit id,
                the branch name, or the tag name.
                If is given, list the commits before the given commit.
                If is not given, list the commits before the current commit.

        Raises:
            TypeError: When the given revision is illegal.

        Returns:
            The PagingList of :class:`commits<.Commit>`.

        """
        if revision is None:
            if self._status.is_draft:
                revision = self._status.branch_name
            else:
                revision = self._status.commit_id

        if not revision:
            raise TypeError("The given revision is illegal")

        return PagingList(
            lambda offset, limit: self._generate_commits(
                revision, offset, limit  # type: ignore[arg-type]
            ),
            128,
        )

    def create_branch(self, name: str, revision: Optional[str] = None) -> None:
        """Create a branch.

        Create a branch based on a commit with the given revision. If the revision is not given,
        create a branch based on the commit id stored in the dataset client.
        Then the dataset client will change the status to "commit"
        and store the branch name and the commit id.

        Arguments:
            name: The branch name.
            revision: The information to locate the specific commit, which can be the commit id,
                the branch name, or the tag name.
                If the revision is not given, create the branch based on the current commit.

        """
        if not revision:
            self._status.check_authority_for_commit()
        else:
            self.checkout(revision=revision)
        revision = self._status.commit_id

        post_data: Dict[str, Any] = {"name": name, "commit": revision}
        self._client.open_api_do("POST", "branches", self._dataset_id, json=post_data)

        self._status.branch_name = name

    def get_branch(self, name: str) -> Branch:
        """Get the branch with the given name.

        Arguments:
            name: The required branch name.

        Returns:
            The :class:`.Branch` instance with the given name.

        Raises:
            TypeError: When the given branch is illegal.
            ResourceNotExistError: When the required branch does not exist.

        """
        if not name:
            raise TypeError("The given branch name is illegal")

        try:
            branch = next(self._generate_branches(name))
        except StopIteration as error:
            raise ResourceNotExistError(resource="branch", identification=name) from error

        return branch

    def list_branches(self) -> PagingList[Branch]:
        """List the information of branches.

        Returns:
            The PagingList of :class:`branches<.Branch>`.

        """
        return PagingList(lambda offset, limit: self._generate_branches(None, offset, limit), 128)

    def delete_branch(self, name: str) -> None:
        """Delete a branch.

        Delete the branch with the given branch name. Note that deleting the branch with the name
        which is stored in the current dataset client is not allowed.

        Arguments:
            name: The name of the branch to be deleted.

        Raises:
            StatusError: When deleting the current branch.

        """
        if name == self._status.branch_name:
            raise StatusError("Deleting the current branch is not allowed")

        self._delete_branch(name)

    def create_tag(self, name: str, revision: Optional[str] = None) -> None:
        """Create a tag for a commit.

        Create a tag for a commit with the given revision. If the revision is not given,
        create a tag based on the commit id stored in the dataset client.

        Arguments:
            name: The tag name to be created for the specific commit.
            revision: The information to locate the specific commit, which can be the commit id,
                the branch name, or the tag name.
                If the revision is not given, create the tag for the current commit.

        """
        if not revision:
            self._status.check_authority_for_commit()
            revision = self._status.commit_id

        post_data: Dict[str, Any] = {"commit": revision, "name": name}

        self._client.open_api_do("POST", "tags", self._dataset_id, json=post_data)

    def get_tag(self, name: str) -> Tag:
        """Get the certain tag with the given name.

        Arguments:
            name: The required tag name.

        Returns:
            The :class:`.Tag` instance with the given name.

        Raises:
            TypeError: When the given tag is illegal.
            ResourceNotExistError: When the required tag does not exist.

        """
        if not name:
            raise TypeError("The given tag name is illegal")

        try:
            tag = next(self._generate_tags(name))
        except StopIteration as error:
            raise ResourceNotExistError(resource="tag", identification=name) from error

        return tag

    def list_tags(self) -> PagingList[Tag]:
        """List the information of tags.

        Returns:
            The PagingList of :class:`tags<.Tag>`.

        """
        return PagingList(lambda offset, limit: self._generate_tags(None, offset, limit), 128)

    def delete_tag(self, name: str) -> None:
        """Delete a tag.

        Arguments:
            name: The tag name to be deleted for the specific commit.

        """
        delete_data: Dict[str, Any] = {"name": name}

        self._client.open_api_do("DELETE", "tags", self._dataset_id, json=delete_data)


class JobMixin:
    """A mixin class supporting asynchronous jobs."""

    _dataset_id: str
    _client: Client
    _status: Status

    def _create_job(
        self,
        title: str,
        job_type: str,
        arguments: Dict[str, Any],
        description: str = "",
    ) -> Dict[str, Any]:
        """Create a :class:`Job`.

        Arguments:
            title: The Job title.
            job_type: The type of Job.
            arguments: The arguments dict of the specific job.
            description: The Job description.

        Returns:
            The info of the job.

        """
        post_data: Dict[str, Any] = {"title": title, "jobType": job_type, "arguments": arguments}
        if description:
            post_data["description"] = description

        response: Dict[str, Any] = self._client.open_api_do(
            "POST", "jobs", self._dataset_id, json=post_data
        ).json()

        response.update(
            title=title,
            arguments=arguments,
            status="QUEUING",
            description=description,
        )
        return response

    def _get_job(self, job_id: str) -> Dict[str, Any]:
        """Get a :class:`Job`.

        Arguments:
            job_id: The Job id.

        Returns:
            The info of Job.

        """
        return self._client.open_api_do(  # type: ignore[no-any-return]
            "GET", f"jobs/{job_id}", self._dataset_id
        ).json()

    def _list_jobs(
        self,
        job_type: str,
        status: Optional[str] = None,
        offset: int = 0,
        limit: int = 128,
    ) -> Dict[str, Any]:
        """Get a dict containing the information of :class:`Job` list.

        Arguments:
            job_type: Type of the Job.
            status: The Job status which includes "QUEUING", "PROCESSING", "SUCCESS", "FAILED",
                    "ABORTED" and None. None means all kinds of status.
            offset: The offset of the page.
            limit: The limit of the page.

        Returns:
            A dict containing the information of Job list.

        """
        params = {"jobType": job_type, "status": status, "offset": offset, "limit": limit}

        response = self._client.open_api_do("GET", "jobs", self._dataset_id, params=params)
        return response.json()  # type: ignore[no-any-return]

    def delete_job(self, job_id: str) -> None:
        """Delete a :class:`Job`.

        Arguments:
            job_id: The Job id.

        """
        self._client.open_api_do("DELETE", f"jobs/{job_id}", self._dataset_id)


class SquashAndMerge(JobMixin):
    """This class defines :class:`SquashAndMerge`.

    Arguments:
        client: The :class:`~tensorbay.client.requests.Client`.
        dataset_id: Dataset ID.
        status: The version control status of the dataset.
        draft_getter: The function to get draft by draft_number.

    """

    _JOB_TYPE = "squashAndMerge"

    def __init__(
        self,
        client: Client,
        dataset_id: str,
        status: Status,
        draft_getter: Callable[[int], Draft],
    ) -> None:
        self._client = client
        self._dataset_id = dataset_id
        self._status = status
        self._draft_getter = draft_getter

    def _generate_jobs(
        self,
        status: Optional[str] = None,
        offset: int = 0,
        limit: int = 128,
    ) -> Generator[SquashAndMergeJob, None, int]:
        response = self._list_jobs(self._JOB_TYPE, status, offset, limit)
        for item in response["jobs"]:
            yield SquashAndMergeJob.from_response_body(
                item,
                dataset_id=self._dataset_id,
                client=self._client,
                job_updater=self._get_job,
                draft_getter=self._draft_getter,
            )

        return response["totalCount"]  # type: ignore[no-any-return]

    def create_job(
        self,
        title: str = "",
        description: str = "",
        *,
        draft_title: str,
        source_branch_name: str,
        target_branch_name: Optional[str] = None,
        draft_description: str = "",
        strategy: Optional[str] = "abort",
    ) -> SquashAndMergeJob:
        """Create a :class:`SquashAndMergeJob`.

        Squash commits in source branch, then merge into target branch by creating a new draft.
        If the target branch name is not given, the draft will be based on the branch name stored
        in the dataset client. And during merging, the conflicts between branches can be resolved
        in three different strategies: "abort", "override" and "skip".

        Arguments:
            title: The SquashAndMergeJob title.
            description: The SquashAndMergeJob description.
            draft_title: The draft title.
            source_branch_name: The name of the branch to be squashed.
            target_branch_name: The target branch name of the merge operation.
            draft_description: The draft description.
            strategy: The strategy of handling the branch conflict. There are three options:

                1. "abort": abort the opetation;
                2. "override": the squashed branch will override the target branch;
                3. "skip": keep the origin branch.

        Raises:
            StatusError: When squashing and merging without basing on a branch.

        Returns:
            The SquashAndMergeJob.

        """
        if not target_branch_name:
            target_branch_name = self._status.branch_name
            if not target_branch_name:
                raise StatusError(
                    message="Squash and merge without basing on a branch is not allowed"
                )
            self._status.check_authority_for_commit()

        if not title:
            title = f"{source_branch_name}->{target_branch_name}({strategy})"

        arguments = {
            "title": draft_title,
            "sourceBranchName": source_branch_name,
            "targetBranchName": target_branch_name,
            "strategy": strategy,
        }
        if draft_description:
            arguments["description"] = draft_description

        job_info = self._create_job(title, self._JOB_TYPE, arguments, description)
        return SquashAndMergeJob.from_response_body(
            job_info,
            dataset_id=self._dataset_id,
            client=self._client,
            job_updater=self._get_job,
            draft_getter=self._draft_getter,
        )

    def get_job(self, job_id: str) -> SquashAndMergeJob:
        """Get a :class:`SquashAndMergeJob`.

        Arguments:
            job_id: The SquashAndMergeJob id.

        Returns:
            The SquashAndMergeJob.

        """
        job_info = self._get_job(job_id)
        return SquashAndMergeJob.from_response_body(
            job_info,
            dataset_id=self._dataset_id,
            client=self._client,
            job_updater=self._get_job,
            draft_getter=self._draft_getter,
        )

    def list_jobs(self, status: Optional[str] = None) -> PagingList[SquashAndMergeJob]:
        """List the SquashAndMergeJob.

        Arguments:
            status: The SquashAndMergeJob status which includes "QUEUING", "PROCESSING", "SUCCESS",
                    "FAIL", "ABORT" and None. None means all kinds of status.

        Returns:
            The PagingList of SquashAndMergeJob.

        """
        return PagingList(
            lambda offset, limit: self._generate_jobs(status, offset, limit),
            128,
        )
