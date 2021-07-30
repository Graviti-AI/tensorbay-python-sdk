##################
 Shell Completion
##################

CLI provides tab completion support for Bash (version not lower than 4.4), Zsh, and Fish. It is possible to add support
for other shells too.

Shell completion suggests command names and option names. Options are only listed if at least a dash has been entered.

Here is an example of completion:

.. code:: console

    $ gas <TAB><TAB>
    auth     -- Authenticate the accessKey of gas.
    branch   -- List, create or delete branches.
    commit   -- Commit drafts.
    config   -- Configure the options when using gas CLI.
    cp       -- Copy local data to a remote path.
    dataset  -- List, create or delete datasets.
    draft    -- List or create drafts.
    log      -- Show commit logs.
    ls       -- List data under the path.
    rm       -- Remove the remote data.
    tag      -- List, create or delete tags.
    $ gas auth -<TAB><TAB>
    --get    -g  -- Get the accesskey of the profile
    --unset  -u  -- Unset the accesskey of the profile
    --all    -a  -- All the auth info
    --help       -- Show this message and exit.

.. note::
    The result may differ with different versions of click or shell.

Activation
**********

Completion is only available if ``tensorbay`` is installed and invoked through ``gas``, not through the ``python``
command.

In order for completion to be used, the user needs to register a special function with their shell. The script is
different for every shell. The built-in shells are ``bash``, ``zsh``, and ``fish``. The following instructions will lead
user to configure the completion:

Before configuring completion, the user needs to check the version of ``click``:

.. code:: console

    $ pip show click

Activation for Click 7.x
------------------------

For Bash:
    Add this to ``~/.bashrc``:

    .. code:: console

        eval "$(_GAS_COMPLETE=source_bash gas)"

For Zsh:
    Add this to ``~/.zshrc``:

    .. code:: console

        eval "$(_GAS_COMPLETE=source_zsh gas)"

For Fish:
    Add this to ``~/.config/fish/completions/gas.fish``:

    .. code:: console

        eval (env _GAS_COMPLETE=source_fish gas)

Activation for Click 8.x
------------------------

For Bash:
    Add this to ``~/.bashrc``:

    .. code:: console

        eval "$(_GAS_COMPLETE=bash_source gas)"

For Zsh:
    Add this to ``~/.zshrc``:

    .. code:: console

        eval "$(_GAS_COMPLETE=zsh_source gas)"

For Fish:
    Add this to ``~/.config/fish/completions/gas.fish``:

    .. code:: console

        eval (env _GAS_COMPLETE=fish_source gas)

Activation Script
*****************

Using ``eval`` means that the command is invoked and evaluated every time a shell is started, which can delay shell
responsiveness. Using activation script is faster than using ``eval``: write the generated script to a file, then
source that.

Activation Script for Click 7.x
-------------------------------

For Bash:
    Save the script somewhere.

    .. code:: console

        _GAS_COMPLETE=source_bash gas > ~/.gas-complete.bash

    Source the file in ``~/.bashrc``.

    .. code:: console

        . ~/.gas-complete.bash

For Zsh:
    Save the script somewhere.

    .. code:: console

        _GAS_COMPLETE=source_zsh gas > ~/.gas-complete.zsh

    Source the file in ``~/.zshrc``.

    .. code:: console

        . ~/.gas-complete.zsh

For Fish:
    Add the file to the completions directory:

    .. code:: console

        _GAS_COMPLETE=source_fish gas > ~/.config/fish/completions/gas-complete.fish

Activation Script for Click 8.x
-------------------------------

For Bash:
    Save the script somewhere.

    .. code:: console

        _GAS_COMPLETE=bash_source gas > ~/.gas-complete.bash

    Source the file in ``~/.bashrc``.

    .. code:: console

        . ~/.gas-complete.bash

For Zsh:
    Save the script somewhere.

    .. code:: console

        _GAS_COMPLETE=zsh_source gas > ~/.gas-complete.zsh

    Source the file in ``~/.zshrc``.

    .. code:: console

        . ~/.gas-complete.zsh

For Fish:
    Save the script to ``~/.config/fish/completions/gas.fish``:

    .. code:: console

        _GAS_COMPLETE=fish_source gas > ~/.config/fish/completions/gas.fish

.. note::

    After modifying the shell config, the user needs to start a new shell or source the modified files in order for the
    changes to be loaded.
