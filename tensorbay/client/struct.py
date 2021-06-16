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

from typing import Any, Dict, Optional, Tuple, Type, TypeVar

from ..utility import AttrsMixin, ReprMixin, attr, camel, common_loads


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

    _repr_attrs: Tuple[str, ...] = ("parent_commit_id", "title", "description", "committer")
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


class Draft(AttrsMixin, ReprMixin):
    """This class defines the basic structure of a draft.

    Arguments:
        number: The number of the draft.
        title: The title of the draft.
        branch_name: The branch name.

    """

    _T = TypeVar("_T", bound="Draft")

    _repr_attrs = ("title",)

    number: int = attr()
    title: str = attr()
    branch_name: str = attr(key=camel)

    def __init__(self, number: int, title: str, branch_name: str) -> None:
        self.number = number
        self.title = title
        self.branch_name = branch_name

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
                }

        """
        return self._dumps()
