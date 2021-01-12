import discord
import typing

if typing.TYPE_CHECKING:
    from client import NoteblockClient


class Command:

    def __init__(self, client: 'NoteblockClient'):
        self.client = client

    def get_base_command(self):
        pass

    def get_alias(self):
        pass

    def get_help(self):
        pass

    async def execute(self, message: discord.Message, args: typing.List[str]):
        pass

    # Called after execute
    async def on_message(self, message: discord.Message):
        pass