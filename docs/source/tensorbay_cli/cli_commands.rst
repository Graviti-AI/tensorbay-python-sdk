##############
 CLI Commands
##############

The following table lists the currently supported CLI commands.(:numref:`Table. %s <cli_commands_table>`).

.. _cli_commands_table:

.. table:: CLI Commands
   :align: center
   :widths: auto

   =======================================================  ===========================================================
   Commands                                                 Description
   =======================================================  ===========================================================
   :ref:`tensorbay_cli/cli_commands:gas auth`               authentication operations.
   :ref:`tensorbay_cli/cli_commands:gas config`             config operations
   :ref:`tensorbay_cli/cli_commands:gas dataset`            dataset operations.
   :ref:`tensorbay_cli/cli_commands:gas ls`                 list operations.
   :ref:`tensorbay_cli/cli_commands:gas cp`                 copy operations.
   :ref:`tensorbay_cli/cli_commands:gas rm`                 remove operations.
   :ref:`tensorbay_cli/cli_commands:gas draft`              draft operations.
   :ref:`tensorbay_cli/cli_commands:gas commit`             commit operations.
   :ref:`tensorbay_cli/cli_commands:gas tag`                tag operations.
   :ref:`tensorbay_cli/cli_commands:gas log`                log operations.
   :ref:`tensorbay_cli/cli_commands:gas branch`             branch operations
   =======================================================  ===========================================================

**********
 gas auth
**********

Work with authentication operations.

Authenticate the accesskey of the TensorBay account.
If the accesskey is not provided, interactive authentication will be launched.

.. code:: html

   $ gas auth [ACCESSKEY]

Get the authentication information.

.. code:: html

   $ gas auth --get [--all]

Unset the authentication information.

.. code:: html

   $ gas auth --unset [--all]


*************
 gas config
*************

Work with configuration operations.

``gas config`` supports modifying the configurations about network request and editor.

Add a single configuration, see the available keys and corresponding values about network request at
:ref:`request_configuration<advanced_features/request_configuration:Request Configuration>`.

.. code:: html

   $ gas config [key] [value]

For example:

.. code:: html

   $ gas config editor vim
   $ gas config max_retries 5

Show all the configurations.

.. code:: html

   $ gas config

Show a single configuration.

.. code:: html

   $ gas config [key]

For example:

.. code:: html

   $ gas config editor

Unset a single configuration.

.. code:: html

   $ gas config --unset <key>

For example:

.. code:: html

   $ gas config --unset editor


*************
 gas dataset
*************

Work with dataset operations.

Create a dataset.

.. code:: html

   $ gas dataset tb:<dataset_name>

List all datasets.

.. code:: html

   $ gas dataset

Delete a dataset.

.. code:: html

   $ gas dataset -d tb:<dataset_name>


*********
 gas ls
*********

Work with list operations.

List the segments of a dataset.(default branch)

.. code:: html

    $ gas ls tb:<dataset_name>

List the segments of a specific dataset :ref:`revision<reference/glossary:revision>`.

.. code:: html

    $ gas ls tb:<dataset_name>@<revision>

List the segments of a specific dataset draft.

See :ref:`tensorbay_cli/cli_commands:gas draft` for more information.

.. code:: html

    $ gas ls tb:<dataset_name>#<draft_number>

List all files of a segment.

.. code:: html

    $ gas ls tb:<dataset_name>:<segment_name>
    $ gas ls tb:<dataset_name>@<revision>:<segment_name>
    $ gas ls tb:<dataset_name>#<draft_number>:<segment_name>

Get a certain file.

.. code:: html

    $ gas ls tb:<dataset_name>:<segment_name>://<remote_path>
    $ gas ls tb:<dataset_name>@<revision>:<segment_name>://<remote_path>
    $ gas ls tb:<dataset_name>#<draft_number>:<segment_name>://<remote_path>


********
 gas cp
********


Work with copy operations.

Upload a file to a segment. The ``local_path`` refers to a file.

The target dataset must be in draft status,
see :ref:`tensorbay_cli/cli_commands:gas draft` for more information.

.. code:: html

    $ gas cp <local_path> tb:<dataset_name>#<draft_number>:<segment_name>

Upload files to a segment. The ``local_path`` refers to a directory.

.. code:: html

    $ gas cp -r <local_path> tb:<dataset_name>#<draft_number>:<segment_name>

Upload a file to a segment with a given ``remote_path``, which is the target path on TensorBay.
The ``local_path`` can refer to only one file.

.. code:: html

    $ gas cp <local_path> tb:<dataset_name>#<draft_number>:<segment_name>://<remote_path>


********
 gas rm
********

Work with remove operations.

Remove a segment.

The target dataset must be in draft status,
see :ref:`tensorbay_cli/cli_commands:gas draft` for more information.

.. code:: html

    $ gas rm -r tb:<dataset_name>#<draft_number>:<segment_name>

Remove a file.

.. code:: html

    $ gas rm tb:<dataset_name>#<draft_number>:<segment_name>://<remote_path>


***********
 gas draft
***********

Work with :ref:`reference/glossary:draft` operations.

Create a draft with a title.

.. code:: html

   $ gas draft tb:<dataset_name> [-m <title>]

List the drafts of a dataset.

.. code:: html

   $ gas draft -l tb:<dataset_name>

Edit the draft of a dataset.

.. code:: html

   $ gas draft -e tb:<dataset_name>#<draft_number> [-m <title>]

Close the draft of a dataset.

.. code:: html

   $ gas draft -c tb:<dataset_name>#<draft_number>


***********
 gas commit
***********

Work with commit operations.

Commit a :ref:`reference/glossary:draft` with a title.

.. code:: html

   $ gas commit tb:<dataset_name>#<draft_number> [-m <title>]


***********
 gas tag
***********

Work with :ref:`reference/glossary:tag` operations.

Create a tag on the current commit or a specific :ref:`revision<reference/glossary:revision>`.

.. code:: html

   $ gas tag tb:<dataset_name> <tag_name>
   $ gas tag tb:<dataset_name>@<revision> <tag_name>

List all tags.

.. code:: html

   $ gas tag tb:<dataset_name>

Delete a tag.

.. code:: html

   $ gas tag -d tb:<dataset_name>@<tag_name>


*********
 gas log
*********

Work with log operations.

Show the commit logs.

.. code:: html

   $ gas log tb:<dataset_name>

Show commit logs from a certain :ref:`reference/glossary:revision`.

.. code:: html

   $ gas log tb:<dataset_name>@<revision>

Limit the number of commit logs to show.

.. code:: html

   $ gas log -n <number> tb:<dataset_name>
   $ gas log --max-count <number> tb:<dataset_name>

Show commit logs in oneline format.

.. code:: html

   $ gas log --oneline tb:<dataset_name>

Show commit logs of all revisions.

.. code:: html

   $ gas log --all tb:<dataset_name>

Show graphical commit logs.

.. code:: html

   $ gas log --graph tb:<dataset_name>


*************
 gas branch
*************

Work with :ref:`reference/glossary:branch` operations.

Create a new branch from the default branch.

.. code:: html

   $ gas branch tb:<dataset_name> <branch_name>

Create a new branch from a certain :ref:`reference/glossary:revision`.

.. code:: html

   $ gas branch tb:<dataset_name>@<revision> <branch_name>

Show all branches.

.. code:: html

   $ gas branch tb:<dataset_name>

Delete a branch.

.. code:: html

   $ gas branch --delete tb:<dataset_name>@<branch_name>
