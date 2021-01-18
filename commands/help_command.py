import discord
import typing

from commands.command import Command

if typing.TYPE_CHECKING:
    from client import NoteblockClient


class HelpCommand(Command):

    def __init__(self, client: 'NoteblockClient'):
        super().__init__(client)

    def get_base_command(self) -> str:
        return "help"

    def get_alias(self):
        return "h"

    def get_help(self) -> str:
        return ";**h**elp : 도움말을 출력합니다."

    async def execute(self, message: discord.Message, args: typing.List[str]):
        msg = "지원되는 명령어 목록:"
        for command in self.client.get_commands():
            msg += "\n" + command.get_help().strip()
        await message.channel.send(msg)

        return True
