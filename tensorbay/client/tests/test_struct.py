#!/usr/bin/env python3
#
# Copyright 2021 Graviti. Licensed under MIT License.
#


from ..struct import Commit, Draft, User, _NamedCommit

_DATE = 1617183289
_USER_NAME = "user_name@graviti.cn"
_USER_DATA = {"name": _USER_NAME, "date": _DATE}

_COMMIT_ID = "b8946338-76dc-4d8b-be4c-0171ed4aad79"
_PARENT_COMMIT_ID = "a8946e39-75fc-4d8b-be4c-0171ed4aad79"
_TITLE = "commit title"
_DESCRIPTION = "commit description"
_COMMIT_DATA = {
    "commitId": _COMMIT_ID,
    "parentCommitId": _PARENT_COMMIT_ID,
    "title": _TITLE,
    "description": _DESCRIPTION,
    "committer": _USER_DATA,
}

_COMMIT_NAME = "commit name"
_NAMED_COMMIT_DATA = {"name": _COMMIT_NAME}
_NAMED_COMMIT_DATA.update(_COMMIT_DATA)

_DRAFT_NUMBER = 1
_DRAFT_TITLE = "draft title"
_DRAFT_BRANCH_NAME = "main"
_DRAFT_DATA = {"number": _DRAFT_NUMBER, "title": _DRAFT_TITLE, "branchName": _DRAFT_BRANCH_NAME}


class TestUser:
    def test_init(self):
        user = User(_USER_NAME, _DATE)
        assert user.name == _USER_NAME
        assert user.date == _DATE

    def test_loads(self):
        user = User.loads(_USER_DATA)
        assert user.name == _USER_DATA["name"]
        assert user.date == _USER_DATA["date"]

    def test_dumps(self):
        user = User(_USER_NAME, _DATE)
        assert user.dumps() == _USER_DATA


class TestCommit:
    def test_init(self):
        user = User.loads(_USER_DATA)
        commit = Commit(_COMMIT_ID, _PARENT_COMMIT_ID, _TITLE, _DESCRIPTION, user)
        assert commit.commit_id == _COMMIT_ID
        assert commit.title == _TITLE
        assert commit.description == _DESCRIPTION
        assert commit.committer == user
        assert commit.parent_commit_id == _PARENT_COMMIT_ID

    def test_loads(self):
        commit = Commit.loads(_COMMIT_DATA)
        assert commit.commit_id == _COMMIT_DATA["commitId"]
        assert commit.title == _COMMIT_DATA["title"]
        assert commit.description == _COMMIT_DATA["description"]
        assert commit.committer == User.loads(_COMMIT_DATA["committer"])
        assert commit.parent_commit_id == _COMMIT_DATA["parentCommitId"]

    def test_dumps(self):
        user = User.loads(_USER_DATA)
        commit = Commit(_COMMIT_ID, _PARENT_COMMIT_ID, _TITLE, _DESCRIPTION, user)
        assert commit.dumps() == _COMMIT_DATA


class Test_NamedCommit:
    def test_init(self):
        user = User.loads(_USER_DATA)
        named_commit = _NamedCommit(
            _COMMIT_NAME, _COMMIT_ID, _PARENT_COMMIT_ID, _TITLE, _DESCRIPTION, user
        )
        assert named_commit.name == _COMMIT_NAME
        assert named_commit.commit_id == _COMMIT_ID
        assert named_commit.title == _TITLE
        assert named_commit.description == _DESCRIPTION
        assert named_commit.committer == user
        assert named_commit.parent_commit_id == _PARENT_COMMIT_ID

    def test_loads(self):
        named_commit = _NamedCommit.loads(_NAMED_COMMIT_DATA)
        assert named_commit.name == _NAMED_COMMIT_DATA["name"]
        assert named_commit.commit_id == _NAMED_COMMIT_DATA["commitId"]
        assert named_commit.title == _NAMED_COMMIT_DATA["title"]
        assert named_commit.description == _NAMED_COMMIT_DATA["description"]
        assert named_commit.committer == User.loads(_NAMED_COMMIT_DATA["committer"])
        assert named_commit.parent_commit_id == _NAMED_COMMIT_DATA["parentCommitId"]

    def test_dumps(self):
        user = User.loads(_USER_DATA)
        named_commit = _NamedCommit(
            _COMMIT_NAME, _COMMIT_ID, _PARENT_COMMIT_ID, _TITLE, _DESCRIPTION, user
        )
        assert named_commit.dumps() == _NAMED_COMMIT_DATA


class TestDraft:
    def test_init(self):
        draft = Draft(_DRAFT_NUMBER, _DRAFT_TITLE, _DRAFT_BRANCH_NAME)
        assert draft.number == _DRAFT_NUMBER
        assert draft.title == _DRAFT_TITLE

    def test_loads(self):
        draft = Draft.loads(_DRAFT_DATA)
        assert draft.number == _DRAFT_DATA["number"]
        assert draft.title == _DRAFT_DATA["title"]
        assert draft.branch_name == _DRAFT_DATA["branchName"]

    def test_dumps(self):
        draft = Draft(_DRAFT_NUMBER, _DRAFT_TITLE, _DRAFT_BRANCH_NAME)
        assert draft.dumps() == _DRAFT_DATA
