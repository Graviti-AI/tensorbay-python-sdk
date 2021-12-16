#!/usr/bin/env python3
#
# Copyright 2021 Graviti. Licensed under MIT License.
#

from textwrap import indent

from tensorbay.cli.auth import INDENT
from tensorbay.cli.cli import auth
from tensorbay.cli.tests.conftest import assert_cli_fail, assert_cli_success


def test_auth(mocker, invoke, context, mock_get_users):

    url = context.url
    access_key = context.access_key
    profile_name = context.profile_name
    new_access_key = "Accesskey-11111111111111111111111111111111"
    wrong_access_key = access_key + "1"

    get_users, user_info = mock_get_users(mocker, False)
    stderr = f"ERROR: {access_key} is not a valid AccessKey\n"
    result = invoke(auth, [access_key])
    assert_cli_fail(result, stderr)

    result = invoke(auth, ["--status"])
    assert_cli_fail(result, stderr)
    get_users.assert_called_with("GET", "users")

    mock_get_users(mocker, True)

    urls_hint = (
        " > https://gas.graviti.com/tensorbay/developer (Global site)\n"
        " > https://gas.graviti.cn/tensorbay/developer (Chinese site)\n\n"
    )
    url_hint = f" > {url}tensorbay/developer\n\n"
    success_hint = (
        f'Successfully set authentication info of "{user_info["nickname"]}"'
        f' in "{user_info["team"]["name"]}" team'
        f' into profile "{profile_name}"\n'
    )
    output = (
        "Please visit and login to the TensorBay website to generate your AccessKey\n"
        "Note: TensorBay has multi-regional websites, "
        "please visit the corresponding website based on your location for better experience\n\n"
        "{}"
        f"Paste your AccessKey here: {new_access_key}\n"
    )
    result = invoke(auth, [], new_access_key)
    assert_cli_success(result, output.format(urls_hint) + success_hint)

    result = invoke(auth, [url], new_access_key)
    assert_cli_success(result, output.format(url_hint) + success_hint)

    result = invoke(auth, ["https://gas.graviti.cn/", new_access_key])
    assert_cli_success(result, success_hint)

    formatted_value = indent(context.config_parser["profiles"][profile_name], INDENT)
    result = invoke(auth, ["--get"])
    assert_cli_success(result, f"{profile_name} = {formatted_value}\n\n")

    profiles = context.config_parser["profiles"]
    output = "".join([f"{key} = {indent(value, INDENT)}\n\n" for key, value in profiles.items()])
    result = invoke(auth, ["--get", "--all"])
    assert_cli_success(result, output)

    output = (
        f"{profile_name}\n"
        f"{INDENT}USER: {user_info['nickname']}\n"
        f"{INDENT}TEAM: {user_info['team']['name']}\n"
        f"{INDENT}{new_access_key}\n"
        f"{INDENT}{url}\n\n"
    )
    result = invoke(auth, ["--status"])
    assert_cli_success(result, output)

    output_rows = []
    for profile, access_key, url in context.generate_profiles():
        output_rows.append(
            f"{profile}\n"
            f"{INDENT}USER: {user_info['nickname']}\n"
            f"{INDENT}TEAM: {user_info['team']['name']}\n"
            f"{INDENT}{access_key}\n"
        )
        if url:
            output_rows.append(f"{INDENT}{url}\n\n")
    result = invoke(auth, ["--status", "--all"])
    assert_cli_success(result, "".join(output_rows))

    invoke(auth, ["--unset"])
    result = invoke(auth, ["--get"])
    stderr = f'ERROR: Profile "{profile_name}" does not exist.\n'
    assert_cli_fail(result, stderr)

    result = invoke(auth, ["--unset", "--all"])
    assert_cli_success(result, "Successfully unset all auth info\n")

    result = invoke(auth, ["--unset"])
    assert_cli_fail(result, stderr)

    result = invoke(auth, ["--get", "--all"])
    assert_cli_success(result, "")

    stderr = 'ERROR: Use "--all" option with "--get", "--unset" or "--status" option\n'
    result = invoke(auth, ["--all"])
    assert_cli_fail(result, stderr)

    result = invoke(auth, ["--get", "--status", "--all"])
    assert_cli_fail(result, 'ERROR: Use at most one of "--get", "--unset" and "--status"\n')

    result = invoke(auth, [access_key, "--get"])
    assert_cli_fail(result, "ERROR: Option requires 0 arguments\n")

    result = invoke(auth, [access_key, url])
    stderr = 'ERROR: Please use "gas auth [url] [accessKey]" to specify the url and accessKey\n'
    assert_cli_fail(result, stderr)

    result = invoke(auth, [access_key, access_key])
    assert_cli_fail(result, f'ERROR: Redundant argument "{access_key}"\n')

    result = invoke(auth, [url, wrong_access_key])
    assert_cli_fail(result, "ERROR: Wrong accesskey format\n")

    result = invoke(auth, [wrong_access_key])
    assert_cli_fail(result, f'ERROR: Invalid argument "{wrong_access_key}"\n')
