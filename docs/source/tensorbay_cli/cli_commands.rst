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

.. code:: console

   gas auth [ACCESSKEY]

Get the authentication information.

.. code:: console

   gas auth --get [--all]

Unset the authentication information.

.. code:: console

   gas auth --unset [--all]


*************
 gas config
*************

Work with configuration operations.

Add a single configuration.

.. code:: console

   gas config [key] [value]

For example:

.. code:: console

   gas config editor vim

Show all the configurations.

.. code:: console

   gas config

Show a single configuration.

.. code:: console

   gas config [key]

For example:

.. code:: console

   gas config editor

Unset a single configuration.

.. code:: console

   gas config --unset [key]

For example:

.. code:: console

   gas config --unset editor


*************
 gas dataset
*************

Work with dataset operations.

Create a dataset.

.. code:: console

   gas dataset tb:[dataset_name]

List all datasets.

.. code:: console

   gas dataset

Delete a dataset.

.. code:: console

   gas dataset -d tb:[dataset_name]


*********
 gas ls
*********

Work with list operations.

List the segments of a dataset.(default branch)

.. code:: console

    gas ls tb:[dataset_name]

List the segments of a specific dataset :ref:`revision<reference/glossary:revision>`.

.. code:: console

   gas ls tb:[dataset_name]@[revision]

List the segments of a specific dataset draft.

See :ref:`tensorbay_cli/cli_commands:gas draft` for more information.

.. code:: console

    gas ls tb:[dataset_name]#[draft_number]

List all files of a segment.

.. code:: console

    gas ls tb:[dataset_name]:[segment_name]
    gas ls tb:[dataset_name]@[revision]:[segment_name]
    gas ls tb:[dataset_name]#[draft_number]:[segment_name

Get a certain file.

.. code:: console

    gas ls tb:[dataset_name]:[segment_name]://[remote_path]
    gas ls tb:[dataset_name]@[revision]:[segment_name]://[remote_path]
    gas ls tb:[dataset_name]#[draft_number]:[segment_name]://[remote_path]


********
 gas cp
********


Work with copy operations.

Upload a file to a segment. The ``local_path`` refers to a file.

The target dataset must be in draft status,
see :ref:`tensorbay_cli/cli_commands:gas draft` for more information.

.. code:: console

    gas cp [local_path] tb:[dataset_name]#[draft_number]:[segment_name]

Upload files to a segment. The ``local_path`` refers to a directory.

.. code:: console

    gas cp -r [local_path] tb:[dataset_name]#[draft_number]:[segment_name]

Upload a file to a segment with a given ``remote_path``. The ``local_path`` can only refer to a file.

.. code:: console

    gas cp [local_path] tb:[dataset_name]#[draft_number]:[segment_name]://[remote_path]


********
 gas rm
********

Work with remove operations.

Remove a segment.

The target dataset must be in draft status,
see :ref:`tensorbay_cli/cli_commands:gas draft` for more information.

.. code:: console

    gas rm -r tb:[dataset_name]#[draft_number]:[segment_name]

Remove a file.

.. code:: console

    gas rm tb:[dataset_name]@[revision]:[segment_name]://[remote_path]

***********
 gas draft
***********

Work with :ref:`reference/glossary:draft` operations.

Create a draft with a title.

.. code:: console

   gas draft tb:[dataset_name] -t [title]

List the drafts of a dataset.

.. code:: console

   gas draft -l tb:[dataset_name]


***********
 gas commit
***********

Work with commit operations.

Commit a :ref:`reference/glossary:draft` with a message.

.. code:: console

   gas commit tb:[dataset_name]#[draft_number] -m [message]


***********
 gas tag
***********

Work with :ref:`reference/glossary:tag` operations.

Create a tag on the current commit or a specific :ref:`revision<reference/glossary:revision>`.

.. code:: console

   gas tag tb:[dataset_name] [tag_name]
   gas tag tb:[dataset_name]@[revision] [tag_name]

List all tags.

.. code:: console

   gas tag tb:[dataset_name]

Delete a tag.

.. code:: console

   gas tag -d tb:[dataset_name]@[tag_name]


*********
 gas log
*********

Work with log operations.

Show the commit logs.

.. code:: console

   gas log tb:[dataset_name]

Show commit logs from a certain :ref:`reference/glossary:revision`.

.. code:: console

   gas log tb:[dataset_name]@[revision]

Limit the number of commit logs to show.

.. code:: console

   gas log -n <number> tb:[dataset_name]
   gas log --max-count <number> tb:[dataset_name]

Show commit logs in oneline format.

.. code:: console

   gas log --oneline tb:[dataset_name]

Show a text-based graphical representaion of commit history

.. code:: console

   gas log --graph tb:[dataset_name]


*************
 gas branch
*************

Work with :ref:`reference/glossary:branch` operations.

Create a new branch from the default branch.

.. code:: console

   gas branch tb:[dataset_name] [branch_name]

Create a new branch from a certain :ref:`reference/glossary:revision`.

.. code:: console

   gas branch tb:[dataset_name]@[revision] [branch_name]

Show all branches.

.. code:: console

   gas branch tb:[dataset_name]

Delete a branch.

.. code:: console

   gas branch --delete tb:[dataset_name]@[branch_name]