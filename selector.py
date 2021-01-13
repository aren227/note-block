import typing

import discord

if typing.TYPE_CHECKING:
    from client import NoteblockClient


class Selector:

    def __init__(self, client: 'NoteblockClient'):
        self.client = client

        self.guilds: typing.Dict[discord.Guild, typing.Dict[discord.Member, Choices]] = {}

    async def query_to_member(self, guild: discord.Guild,
                              member: discord.Member,
                              str_list: typing.List[str],
                              data_list: typing.List[object],
                              callback: typing.Callable[[object, discord.Member, discord.TextChannel], typing.Awaitable[None]],
                              channel: discord.TextChannel,
                              hint: str):
        if len(str_list) == 0:
            raise ValueError("str_list is empty.")

        if len(str_list) != len(data_list):
            raise ValueError("Length of data_list must be equal to length of str_list")

        # No need to query
        if len(str_list) == 1:
            await callback(data_list[0], member, channel)

        if guild not in self.guilds:
            self.guilds[guild] = {}

        msg = ""
        for i in range(len(str_list)):
            msg += "**{}*. {}\n".format(i + 1, str_list[i])
        msg += hint

        query_message = await channel.send(msg)

        self.guilds[guild][member] = Choices(data_list, callback, query_message)

    async def on_message(self, message: discord.Message):
        if len(message.content) > 2 or not message.content.isdigit():
            return

        if message.guild not in self.guilds or message.author not in self.guilds[message.guild]:
            return

        choices = self.guilds[message.guild][message.author]

        index = int(message.content)
        if index < 1 or choices.length() < index:
            return

        await choices.callback(choices.data_list[index - 1], message.author, message.channel)

        self.guilds[message.guild].pop(message.author, None)

        await choices.query_message.delete()
        await message.delete()


class Choices:

    def __init__(self, data_list: typing.List, callback: typing.Callable[[object, discord.Member, discord.TextChannel], typing.Awaitable[None]],
                 query_message: discord.Message):
        self.data_list = data_list
        self.callback = callback
        self.query_message = query_message

    def length(self):
        return len(self.data_list)
