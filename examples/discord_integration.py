import asyncio

import discord  # pip install discord.py
from discord.ext import commands

import steam


class DiscordBot(commands.Bot):
    def __init__(self):
        super().__init__(
            command_prefix="!",
            intents=discord.Intents.default(),
            description="A simple bot that can get steam user info",
        )
        self.client = steam.Client()  # attach a steam.Client instance to the bot

    async def on_ready(self) -> None:
        await self.client.wait_until_ready()
        print("Ready")

    async def start(self, token: str, username: str, password: str) -> None:
        await asyncio.gather(
            super().start(token),
            self.client.login(username, password),
        )  # start the client and bot concurrently

    async def close(self) -> None:
        await self.client.close()  # make sure to close the client when we close the discord bot
        await super().close()


class UserNotFound(commands.BadArgument):
    """For when a matching user cannot be found"""

    def __init__(self, argument: str):
        self.argument = argument
        super().__init__(f"User {argument!r} not found.")


class UserConverter(commands.Converter[steam.User]):
    """Simple user converter"""

    async def convert(self, ctx: commands.Context[DiscordBot], argument: str) -> steam.User:
        try:
            user = await ctx.bot.client.fetch_user(argument)
        except steam.InvalidID:
            id64 = await steam.utils.id64_from_url(argument)
            if id64 is None:
                raise UserNotFound(argument)
            user = await ctx.bot.client.fetch_user(id64)
        if user is None:
            raise UserNotFound(argument)
        return user


bot = DiscordBot()


@bot.command()
async def user(ctx: commands.Context[DiscordBot], user: steam.User = commands.param(converter=UserConverter)):
    """Show some basic info on a steam user"""
    profile = await user.profile()
    embed = discord.Embed(description=user.name)
    embed.set_thumbnail(url=user.avatar.url)
    embed.add_field(name="64 bit ID:", value=str(user.id64))
    embed.add_field(name="Currently playing:", value=f"{user.app or 'Nothing'}")
    embed.add_field(name="Friends:", value=len(await user.friends()))
    embed.add_field(name="Apps:", value=len(await user.apps()))
    embed.set_footer(text="Account created on")  # set timestamp goes after this
    await ctx.send(f"Info on {user.name}", embed=embed)


@user.error
async def on_user_command_error(ctx: commands.Context[DiscordBot], error: commands.CommandError):
    if isinstance(error, UserNotFound):
        return await ctx.send(str(error))
    raise error


async def main():
    async with bot:
        await bot.start("discord_token", "username", "password")


asyncio.run(main())
