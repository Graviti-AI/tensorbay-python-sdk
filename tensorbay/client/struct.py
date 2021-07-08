#!/usr/bin/env python3
#
# Copyright 2021 Graviti. Licensed under MIT License.
#

"""User, Commit, Tag, Branch and Draft classes.

:class:`User` defines the basic concept of a user with an action.

:class:`Commit` defines the structure of a commit.

:class:`Tag` defines the structure of a commit tag.

:class:`Branch` defines the structure of a branch.

:class:`Draft` defines the structure of a draft.

"""

from functools import partial
from typing import Any, Dict, Optional, Tuple, Type, TypeVar

from ..utility import AttrsMixin, NameMixin, ReprMixin, attr, camel, common_loads

ROOT_COMMIT_ID = "00000000000000000000000000000000"


class TeamInfo(NameMixin):
    """This class defines the basic concept of a TensorBay team.

    Arguments:
        name: The name of the team.
        email: The email of the team.
        description: The description of the team.

    """

    _T = TypeVar("_T", bound="TeamInfo")

    _repr_attrs = ("email",)

    email: Optional[str] = attr(default=None)

    def __init__(self, name: str, *, email: Optional[str] = None, description: str = "") -> None:
        super().__init__(name, description)
        self.email = email

    @classmethod
    def loads(cls: Type[_T], contents: Dict[str, Any]) -> _T:
        """Loads a :class:`TeamInfo` instance from the given contents.

        Arguments:
            contents: A dict containing all the information of the commit::

                    {
                        "name": <str>
                        "email": <str>
                        "description": <str>
                    }

        Returns:
            A :class:`TeamInfo` instance containing all the information in the given contents.

        """
        return common_loads(cls, contents)

    def dumps(self) -> Dict[str, Any]:
        """Dumps all the information into a dict.

        Returns:
            A dict containing all the information of the team::

                {
                        "name": <str>
                        "email": <str>
                        "description": <str>
                }

        """
        return self._dumps()


class UserInfo(NameMixin):
    """This class defines the basic concept of a TensorBay user.

    Arguments:
        name: The nickname of the user.
        email: The email of the user.
        mobile: The mobile of the user.
        description: The description of the user.
        team: The team of the user.

    """

    _T = TypeVar("_T", bound="UserInfo")

    _repr_attrs = ("email", "mobile", "team")

    _name: str = attr(key="nickname")
    email: Optional[str] = attr(default=None)
    mobile: Optional[str] = attr(default=None)
    team: Optional[TeamInfo] = attr(default=None)

    def __init__(
        self,
        name: str,
        *,
        email: Optional[str] = None,
        mobile: Optional[str] = None,
        description: str = "",
        team: Optional[TeamInfo] = None,
    ) -> None:
        super().__init__(name, description=description)
        self.email = email
        self.mobile = mobile
        self.team = team

    @classmethod
    def loads(cls: Type[_T], contents: Dict[str, Any]) -> _T:
        """Loads a :class:`UserInfo` instance from the given contents.

        Arguments:
            contents: A dict containing all the information of the commit::

                    {
                        "name": <str>
                        "email": <str>
                        "mobile": <str>
                        "description": <str>
                        "team": {  <dict>
                            "name": <str>
                            "email": <str>
                            "description": <str>
                        }
                    }

        Returns:
            A :class:`UserInfo` instance containing all the information in the given contents.

        """
        return common_loads(cls, contents)

    def dumps(self) -> Dict[str, Any]:
        """Dumps all the information into a dict.

        Returns:
            A dict containing all the information of the user::

                {
                        "name": <str>
                        "email": <str>
                        "mobile": <str>
                        "description": <str>
                        "team": {  <dict>
                            "name": <str>
                            "email": <str>
                            "description": <str>
                        }
                }

        """
        return self._dumps()


class User(AttrsMixin, ReprMixin):
    """This class defines the basic concept of a user with an action.

    Arguments:
        name: The name of the user.
        date: The date of the user action.

    """

    _T = TypeVar("_T", bound="User")

    _repr_attrs = ("date",)

    name: str = attr()
    date: int = attr()

    def __init__(self, name: str, date: int) -> None:
        self.name = name
        self.date = date

    def _repr_head(self) -> str:
        return f'{self.__class__.__name__}("{self.name}")'

    @classmethod
    def loads(cls: Type[_T], contents: Dict[str, Any]) -> _T:
        """Loads a :class:`User` instance from the given contents.

        Arguments:
            contents: A dict containing all the information of the commit::

                    {
                        "name": <str>
                        "date": <int>
                    }

        Returns:
            A :class:`User` instance containing all the information in the given contents.

        """
        return common_loads(cls, contents)

    def dumps(self) -> Dict[str, Any]:
        """Dumps all the user information into a dict.

        Returns:
            A dict containing all the information of the user::

                {
                    "name": <str>
                    "date": <int>
                }

        """
        return self._dumps()


class Commit(AttrsMixin, ReprMixin):
    """This class defines the structure of a commit.

    Arguments:
        commit_id: The commit id.
        parent_commit_id: The parent commit id.
        title: The commit title.
        description: The commit description.
        committer: The commit user.

    """

    _T = TypeVar("_T", bound="Commit")

    _repr_attrs: Tuple[str, ...] = ("parent_commit_id", "title", "committer")
    _repr_maxlevel = 2

    commit_id: str = attr(key=camel)
    parent_commit_id: Optional[str] = attr(key=camel)
    title: str = attr()
    description: str = attr(default="")
    committer: User = attr()

    def __init__(  # pylint: disable=too-many-arguments
        self,
        commit_id: str,
        parent_commit_id: Optional[str],
        title: str,
        description: str,
        committer: User,
    ) -> None:
        self.commit_id = commit_id
        self.parent_commit_id = parent_commit_id
        self.title = title
        self.description = description
        self.committer = committer

    def _repr_head(self) -> str:
        return f'{self.__class__.__name__}("{self.commit_id}")'

    @classmethod
    def loads(cls: Type[_T], contents: Dict[str, Any]) -> _T:
        """Loads a :class:`Commit` instance for the given contents.

        Arguments:
            contents: A dict containing all the information of the commit::

                    {
                        "commitId": <str>
                        "parentCommitId": <str> or None
                        "title": <str>
                        "description": <str>
                        "committer": {
                            "name": <str>
                            "date": <int>
                        }
                    }

        Returns:
            A :class:`Commit` instance containing all the information in the given contents.

        """
        return common_loads(cls, contents)

    def dumps(self) -> Dict[str, Any]:
        """Dumps all the commit information into a dict.

        Returns:
            A dict containing all the information of the commit::

                {
                    "commitId": <str>
                    "parentCommitId": <str> or None
                    "title": <str>
                    "description": <str>
                    "committer": {
                        "name": <str>
                        "date": <int>
                    }
                }

        """
        return self._dumps()


class _NamedCommit(Commit):
    """This class defines the structure of a named commit.

    :class:`_NamedCommit` is the base class of :class:`Tag` and :class:`Branch`.

    Arguments:
        name: The name of the named commit.
        commit_id: The commit id.
        parent_commit_id: The parent commit id.
        title: The commit title.
        description: The commit description.
        committer: The commit user.

    """

    _T = TypeVar("_T", bound="_NamedCommit")

    _repr_attrs = ("commit_id",) + Commit._repr_attrs

    name: str = attr()

    def __init__(  # pylint: disable=too-many-arguments
        self,
        name: str,
        commit_id: str,
        parent_commit_id: Optional[str],
        title: str,
        description: str,
        committer: User,
    ) -> None:
        super().__init__(commit_id, parent_commit_id, title, description, committer)
        self.name = name

    def _repr_head(self) -> str:
        return f'{self.__class__.__name__}("{self.name}")'

    @classmethod
    def loads(cls: Type[_T], contents: Dict[str, Any]) -> _T:
        """Loads a :class:`_NamedCommit` instance for the given contents.

        Arguments:
            contents: A dict containing all the information of the named commit::

                    {
                        "name": <str>
                        "commitId": <str>
                        "parentCommitId": <str> or None
                        "title": <str>
                        "description": <str>
                        "committer": {
                            "name": <str>
                            "date": <int>
                        }
                    }

        Returns:
            A :class:`_NamedCommit` instance containing all the information in the given contents.

        """
        return common_loads(cls, contents)

    def dumps(self) -> Dict[str, Any]:
        """Dumps all the named commit information into a dict.

        Returns:
            A dict containing all the information of the named commit::

                {
                    "name": <str>
                    "commitId": <str>
                    "parentCommitId": <str> or None
                    "title": <str>
                    "description": <str>
                    "committer": {
                        "name": <str>
                        "date": <int>
                    }
                }

        """
        return self._dumps()


class Tag(_NamedCommit):
    """This class defines the structure of the tag of a commit.

    Arguments:
        name: The name of the tag.
        commit_id: The commit id.
        parent_commit_id: The parent commit id.
        title: The commit title.
        description: The commit description.
        committer: The commit user.

    """


_ERROR_MESSAGE = "The '{attr_name}' is not available due to this branch has no commit history."
_attr = partial(attr, is_dynamic=True, error_message=_ERROR_MESSAGE)


class Branch(_NamedCommit):
    """This class defines the structure of a branch.

    Arguments:
        name: The name of the branch.
        commit_id: The commit id.
        parent_commit_id: The parent commit id.
        title: The commit title.
        description: The commit description.
        committer: The commit user.

    """

    parent_commit_id: Optional[str] = _attr(key=camel)
    title: str = _attr()
    description: str = _attr()
    committer: User = _attr()

    def _loads(self, contents: Dict[str, Any]) -> None:
        self.name = contents["name"]
        self.commit_id = contents["commitId"]

        if self.commit_id == ROOT_COMMIT_ID:
            return

        self.parent_commit_id = contents["parentCommitId"]
        self.title = contents["title"]
        self.description = contents["description"]
        self.committer = User.loads(contents["committer"])


class Draft(AttrsMixin, ReprMixin):
    """This class defines the basic structure of a draft.

    Arguments:
        number: The number of the draft.
        title: The title of the draft.
        branch_name: The branch name.
        status: The status of the draft.
        description: The draft description.

    """

    _T = TypeVar("_T", bound="Draft")

    _repr_attrs = ("title", "status", "branch_name")

    number: int = attr()
    title: str = attr()
    branch_name: str = attr(key=camel)
    status: str = attr()
    description: str = attr(default="")

    def __init__(  # pylint: disable=too-many-arguments
        self, number: int, title: str, branch_name: str, status: str, description: str = ""
    ) -> None:
        self.number = number
        self.title = title
        self.branch_name = branch_name
        self.status = status
        self.description = description

    def _repr_head(self) -> str:
        return f"{self.__class__.__name__}({self.number})"

    @classmethod
    def loads(cls: Type[_T], contents: Dict[str, Any]) -> _T:
        """Loads a :class:`Draft` instance from the given contents.

        Arguments:
            contents: A dict containing all the information of the draft::

                    {
                        "number": <int>
                        "title": <str>
                        "branchName": <str>
                        "status": "OPEN", "CLOSED" or "COMMITTED"
                        "description": <str>
                    }

        Returns:
            A :class:`Draft` instance containing all the information in the given contents.

        """
        return common_loads(cls, contents)

    def dumps(self) -> Dict[str, Any]:
        """Dumps all the information of the draft into a dict.

        Returns:
            A dict containing all the information of the draft::

                {
                    "number": <int>
                    "title": <str>
                    "branchName": <str>
                    "status": "OPEN", "CLOSED" or "COMMITTED"
                    "description": <str>
                }

        """
        return self._dumps()
