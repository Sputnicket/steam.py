# -*- coding: utf-8 -*-

"""
The MIT License (MIT)

Copyright (c) 2020 James

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

from typing import TYPE_CHECKING, Protocol

from ... import utils
from ...game import Game
from .errors import BadArgument

if TYPE_CHECKING:
    from steam.ext import commands

    from ...channel import BaseChannel
    from ...clan import Clan
    from ...group import Group
    from ...user import User
    from .context import Context

__all__ = (
    "Converter",
    "UserConverter",
    "ChannelConverter",
    "ClanConverter",
    "GroupConverter",
    "GameConverter",
    "Default",
    "DefaultAuthor",
    "DefaultChannel",
    "DefaultClan",
    "DefaultGroup",
    "DefaultGame",
)


class Converter(Protocol):
    """A custom class from which converters can be derived.
    They should be type-hinted to a command's argument.

    Some custom types from this library can be type-hinted
    just using their normal type (see below).

    Examples
    --------

    Builtin: ::

        @bot.command()
        async def command(ctx, user: steam.User):
            # this will end up making the user variable a `User` object.

        # invoked as
        # !command 76561198248053954
        # or !command "Gobot1234"

    A custom converter: ::

        class ImageConverter:
            async def convert(self, ctx: 'commands.Context', argument: str):
                async with aiohttp.ClientSession as session:
                    async with session.get(argument) as r:
                        image_bytes = await r.read()
                try:
                    return steam.Image(image_bytes)
                except (TypeError, ValueError) as exc:  # failed to convert to an image
                    raise commands.BadArgument from exc

        # then later

        @bot.command()
        async def set_avatar(ctx, avatar: ImageConverter):
            await bot.edit(avatar=avatar)
        await ctx.send('👌')

        # invoked as
        # !set_avatar "my image url"
    """

    async def convert(self, ctx: "commands.Context", argument: str):
        raise NotImplementedError("Derived classes must implement this")


class UserConverter(Converter):
    """The converter that is used when the
    type-hint passed is :class:`~steam.User`.

    Lookup is in the order of:
        - Steam ID
        - Name
    """

    async def convert(self, ctx: "commands.Context", argument: str) -> "User":
        user = ctx.bot.get_user(argument) or await ctx.bot.fetch_user(argument)
        if user is None:
            user = utils.get(ctx.bot.users, name=argument)
        if user is None:
            raise BadArgument(f'Failed to convert "{argument}" to a Steam user')
        return user


class ChannelConverter(Converter):
    """The converter that is used when the
    type-hint passed is :class:`~steam.Channel`.

    Lookup is in the order of:
        - ID
        - Name
    """

    async def convert(self, ctx: "commands.Context", argument: str) -> "BaseChannel":
        channel = None
        if argument.isdigit():
            groups = ctx.bot._connection._combined.values()
            for group in groups:
                channels = [c for c in group.channels if c.id == int(argument)]
                if channels:
                    return channels[0]
        else:
            if ctx.clan:
                channel = utils.get(ctx.clan.channels, name=argument)
            elif ctx.group:
                channel = utils.get(ctx.group.channels, name=argument)
        if channel is None:
            raise BadArgument(f'Failed to convert "{argument}" to a channel')
        return channel


class ClanConverter(Converter):
    """The converter that is used when the
    type-hint passed is :class:`~steam.Clan`.

    Lookup is in the order of:
        - Steam ID
        - Name
    """

    async def convert(self, ctx: "commands.Context", argument: str) -> "Clan":
        clan = ctx.bot.get_clan(argument)
        if clan is None:
            clan = utils.get(ctx.bot.clans, name=argument)
        if clan is None:
            raise BadArgument(f'Failed to convert "{argument}" to a Steam clan')
        return clan


class GroupConverter(Converter):
    """The converter that is used when the
    type-hint passed is :class:`~steam.Group`.

    Lookup is in the order of:
        - ID
        - Name
    """

    async def convert(self, ctx: "commands.Context", argument: str) -> "Group":
        if argument.isdigit():
            group = ctx.bot.get_group(int(argument))
        else:
            group = utils.get(ctx.bot.clans, name=argument)
        if group is None:
            raise BadArgument(f'Failed to convert "{argument}" to a Steam group')
        return group


class GameConverter(Converter):
    """The converter that is used when the
    type-hint passed is :class:`~steam.Game`.

    If the param is a digit it is assumed
    that the argument is the game's app id else
    it is assumed it is the game's title.
    """

    async def convert(self, ctx: "commands.Context", argument: str):
        return Game(app_id=int(argument)) if argument.isdigit() else Game(title=argument)


class Default(Protocol):
    """A custom way to specify a default values for commands.

    Examples
    --------
    Builtin: ::

        @bot.command()
        async def info(ctx, user: steam.User = DefaultAuthor):
            # if no user is passed it will be ctx.author

    A custom default: ::

        class CurrentCommand(commands.Default):
            async def default(self, ctx: 'commands.Context'):
                return ctx.command  # return the current command

        # then later

        @bot.command()
        async def source(ctx, command=CurrentCommand):
            # command would now be source

        # this could also be mixed in with a converter to convert a string to a command.
    """

    async def default(self, ctx: "commands.Context"):
        raise NotImplementedError("Derived classes need to implement this")


class DefaultAuthor(Default):
    """Returns the :attr:`.Context.author`"""

    async def default(self, ctx: "commands.Context"):
        return ctx.author


class DefaultChannel(Default):
    """Returns the :attr:`.Context.channel`"""

    async def default(self, ctx: "commands.Context"):
        return ctx.channel


class DefaultGroup(Default):
    """Returns the :attr:`.Context.group`"""

    async def default(self, ctx: "commands.Context"):
        return ctx.group


class DefaultClan(Default):
    """Returns the :attr:`.Context.clan`"""

    async def default(self, ctx: "commands.Context"):
        return ctx.clan


class DefaultGame(Default):
    """Returns the author's :attr:`~steam.User.game`"""

    async def default(self, ctx: "commands.Context"):
        return ctx.author.game
