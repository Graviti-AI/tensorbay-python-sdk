#!/usr/bin/env python3
#
# Copyright 2021 Graviti. Licensed under MIT License.
#

"""TensorBay dataset version control related classes."""

from typing import TYPE_CHECKING, Any, Dict, Generator, Optional, Union

from tensorbay.client.lazy import PagingList
from tensorbay.client.status import Status
from tensorbay.client.struct import Branch, Commit, Draft, Tag
from tensorbay.exception import ResourceNotExistError, StatusError

if TYPE_CHECKING:
    from tensorbay.client.gas import GAS


class VersionControlClient:
    """TensorBay dataset version control client.

    Arguments:
        dataset_id: Dataset ID.
        gas: The initial client to interact between local and TensorBay.
        status: The version control status of the dataset.

    """

    def __init__(self, dataset_id: str, gas: "GAS", *, status: Status) -> None:
        self._dataset_id = dataset_id
        self._client = gas._client  # pylint: disable=protected-access
        self._status = status

    def _get_basehead(
        self, base: Optional[Union[str, int]] = None, head: Optional[Union[str, int]] = None
    ) -> str:
        if head:
            head = f"draft-{head}" if isinstance(head, int) else f"commit-{head}"
        else:
            if self._status.is_draft:
                head = f"draft-{self.status.draft_number}"
            else:
                head = f"commit-{self.status.commit_id}"

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

    @property
    def dataset_id(self) -> str:
        """Return the TensorBay dataset ID.

        Returns:
            The TensorBay dataset ID.

        """
        return self._dataset_id

    @property
    def status(self) -> Status:
        """Return the status of the dataset client.

        Returns:
            The status of the dataset client.

        """
        return self._status

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
            branch_name = self.status.branch_name
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
            draft_number = self.status.draft_number

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
        if number == self.status.draft_number:
            raise StatusError("Closing the current draft is not allowed")

        self._close_draft(number)

    def squash_and_merge(
        self,
        title: str,
        description: str = "",
        *,
        source_branch_name: str,
        target_branch_name: Optional[str] = None,
        strategy: Optional[str] = "abort",
    ) -> int:
        """Squash and merge.

        Squash commits in source branch, then merge into target branch by creating a new draft.
        If the target branch name is not given, the draft will be based on the branch name stored
        in the dataset client. And during merging, the conflicts between branches can be resolved
        in three different strategies: "abort", "override" and "skip".

        Arguments:
            title: The draft title.
            description: The draft description.
            source_branch_name: The name of the branch to be squashed.
            target_branch_name: The target branch name of the merge operation.
            strategy: The strategy of handling the branch conflict. There are three options:

                1. "abort": abort the opetation;
                2. "override": the squashed branch will override the target branch;
                3. "skip": keep the origin branch.

        Raises:
            StatusError: When squashing and merging without basing on a branch.

        Returns:
            The draft number of the new draft.

        """
        if not target_branch_name:
            target_branch_name = self.status.branch_name
            if not target_branch_name:
                raise StatusError(
                    message="Squash and merge without basing on a branch is not allowed"
                )
            self._status.check_authority_for_commit()

        post_data: Dict[str, Any] = {
            "title": title,
            "sourceBranchName": source_branch_name,
            "targetBranchName": target_branch_name,
            "strategy": strategy,
        }

        if description:
            post_data["description"] = description

        response = self._client.open_api_do(
            "POST", "squashAndMerge", self._dataset_id, json=post_data
        )
        draft_number: int = response.json()["draftNumber"]

        self._status.checkout(draft_number=draft_number)
        self._status.branch_name = target_branch_name
        return draft_number

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
            if self.status.is_draft:
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
        if name == self.status.branch_name:
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
