#!/usr/bin/env python3
#
# Copyright 2021 Graviti. Licensed under MIT License.
#


from ..struct import Commit, User

_DATE = 1617183289
_USER_NAME = "user_name@graviti.cn"
_USER_DATA = {"name": _USER_NAME, "date": _DATE}

_COMMIT_ID = "b8946338-76dc-4d8b-be4c-0171ed4aad79"
_PARENT_COMMIT_ID = "a8946e39-75fc-4d8b-be4c-0171ed4aad79"
_MESSAGE = "commit message"
_COMMIT_DATA = {
    "commitId": _COMMIT_ID,
    "parentCommitId": _PARENT_COMMIT_ID,
    "message": _MESSAGE,
    "committer": _USER_DATA,
}


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
        commit = Commit(_COMMIT_ID, _PARENT_COMMIT_ID, _MESSAGE, user)
        assert commit.commit_id == _COMMIT_ID
        assert commit.message == _MESSAGE
        assert commit.committer == user
        assert commit.parent_commit_id == _PARENT_COMMIT_ID

    def test_loads(self):
        commit = Commit.loads(_COMMIT_DATA)
        assert commit.commit_id == _COMMIT_DATA["commitId"]
        assert commit.message == _COMMIT_DATA["message"]
        assert commit.committer == User.loads(_COMMIT_DATA["committer"])
        assert commit.parent_commit_id == _COMMIT_DATA["parentCommitId"]

    def test_dumps(self):
        user = User.loads(_USER_DATA)
        commit = Commit(_COMMIT_ID, _PARENT_COMMIT_ID, _MESSAGE, user)
        assert commit.dumps() == _COMMIT_DATA
