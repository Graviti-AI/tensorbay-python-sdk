#!/usr/bin/env python3
#
# Copyright 2021 Graviti. Licensed under MIT License.
#
# pylint: disable=import-outside-toplevel

"""Subclass declaration and definition of click class."""

from types import MethodType
from typing import Any, Optional, Sequence, Tuple, Union

import click


class CustomCommand(click.Command):
    """Wrapper class of ``click.Command`` for CLI commands with custom help.

    Arguments:
        kwargs: The keyword arguments pass to ``click.Command``.

    """

    def __init__(self, **kwargs: Any) -> None:
        self.synopsis = kwargs.pop("synopsis", ())
        super().__init__(**kwargs)

    def format_help(self, ctx: click.Context, formatter: click.HelpFormatter) -> None:
        """Writes the custom help into the formatter if it exists.

        Override the original ``click.Command.format_help`` method by
        adding :meth:`CustomCommand.format_synopsis` to form custom help message.

        Arguments:
            ctx: The context of the command.
            formatter: The help formatter of the command.

        """
        formatter.width = 100
        self.format_usage(ctx, formatter)
        self.format_help_text(ctx, formatter)
        self.format_synopsis(formatter)  # Add synopsis in command help.
        self.format_options(ctx, formatter)
        self.format_epilog(ctx, formatter)

    def format_synopsis(self, formatter: click.HelpFormatter) -> None:
        """Wirte the synopsis to the formatter if exist.

        Arguments:
            formatter: The help formatter of the command.

        """
        if not self.synopsis:
            return

        with formatter.section("Synopsis"):
            for example in self.synopsis:
                formatter.write_text(example)


class DeprecatedCommand(CustomCommand):
    """Customized ``click.Command`` wrapper class for deprecated CLI commands.

    Arguments:
        args: The positional arguments pass to ``click.Command``.
        since: The version the function is deprecated.
        removed_in: The version the function will be removed in.
        substitute: The substitute command.
        kwargs: The keyword arguments pass to ``click.Command``.
    """

    def __init__(
        self,
        *args: Any,
        since: str,
        removed_in: Optional[str] = None,
        substitute: Optional[str] = None,
        **kwargs: Any,
    ):
        super().__init__(*args, **kwargs)

        messages = [
            f'DeprecationWarning: The command "{self.name}" is deprecated since version {since}.'
        ]
        if removed_in:
            messages.append(f'It will be removed in version "{removed_in}".')
        if substitute:
            messages.append(f'Use "{substitute}" instead.')

        self.deprecated_message = " ".join(messages)

    def invoke(self, ctx: click.Context) -> Any:
        """This invokes the command to print the deprecated message.

        Arguments:
            ctx: The click Context.

        Returns:
            The invoke result of ``click.Command``.

        """
        click.secho(self.deprecated_message, fg="red", err=True)
        return super().invoke(ctx)


class DeprecatedOption(click.Option):
    """Customize deprecated option."""

    def __init__(
        self,
        *args: Any,
        deprecated: Union[str, Tuple[str, ...]],
        since: str,
        removed_in: Optional[str] = None,
        preferred: Optional[Union[str, Tuple[str, ...]]] = None,
        **kwargs: Any,
    ) -> None:
        if isinstance(deprecated, str):
            self.deprecated: Tuple[str, ...] = (deprecated,)
        else:
            self.deprecated = deprecated
        self.since = since
        self.removed_in = removed_in
        self.preferred = preferred
        super().__init__(*args, **kwargs)

    def join_options(self, options: Sequence[str]) -> Tuple[str, bool]:
        """Join the options that are not deprecated.

        Copied from ``click.formatting.join_options``
        and add some code to exclude the deprecated opts in help message.

        Arguments:
            options: The options.

        Returns:
            The joined option string and whether there is slash prefix in options.

        """
        prefix_opt = []
        any_prefix_is_slash = False

        for opt in options:
            if opt in self.deprecated:  # Exclude the deprecated opts in help message.
                continue

            prefix = click.parser.split_opt(opt)[0]

            if prefix == "/":
                any_prefix_is_slash = True

            prefix_opt.append((len(prefix), opt))

        prefix_opt.sort(key=lambda x: x[0])
        return ", ".join(x[1] for x in prefix_opt), any_prefix_is_slash

    def get_help_record(  # type: ignore[override]
        self, ctx: click.Context
    ) -> Optional[Tuple[str, str]]:
        """Get help record.

        Arguments:
            ctx: The context of the option.

        Returns:
            The option help message.

        """
        if self.hidden:
            return None

        _, help_message = super().get_help_record(ctx)
        any_prefix_is_slash = False

        def _write_opts(opts: Sequence[str]) -> str:
            nonlocal any_prefix_is_slash

            # Use `self.join_options` instead of `click.formatting.join_options`
            # to exclude the deprecated opts in help message.
            opt_message, any_slashes = self.join_options(opts)

            if any_slashes:
                any_prefix_is_slash = True

            if not self.is_flag and not self.count:
                opt_message += f" {self.make_metavar()}"

            return opt_message

        opt_messages = [_write_opts(self.opts)]

        if self.secondary_opts:
            opt_messages.append(_write_opts(self.secondary_opts))

        return ("; " if any_prefix_is_slash else " / ").join(opt_messages), help_message


class DeprecatedOptionsCommand(CustomCommand):
    """Customize command with deprecated options."""

    def make_parser(self, ctx: click.Context) -> click.OptionParser:
        """Hook 'make_parser' and check whether the name used to invoke the option is preferred.

        Arguments:
            ctx: The context of the command.

        Returns:
            The option parser.

        """
        parser = super().make_parser(ctx)

        options = set(parser._short_opt.values()) | set(  # pylint: disable=protected-access
            parser._long_opt.values()  # pylint: disable=protected-access
        )

        for option in options:
            if not isinstance(option.obj, DeprecatedOption):
                continue

            def _process(
                self: click.parser.Option,
                value: Any,
                state: click.parser.ParsingState,
            ) -> None:
                option_obj = self.obj

                # reach up the stack and get 'opt'
                import inspect

                frame = inspect.currentframe()
                if frame and frame.f_back:
                    opt = frame.f_back.f_locals.get("opt")
                else:
                    opt = None

                if opt in option_obj.deprecated:
                    messages = [
                        "DeprecationWarning: "
                        f'The option "{opt}" is deprecated since version {option_obj.since}.'
                    ]
                    if option_obj.removed_in:
                        messages.append(f"It will be removed in version {option_obj.removed_in}.")
                    if option_obj.preferred:
                        messages.append(f'Please use "{option_obj.preferred}" instead.')
                    click.secho(" ".join(messages), fg="yellow")
                return click.parser.Option.process(self, value, state)

            option.process = MethodType(_process, option)  # type: ignore[assignment]
        return parser
