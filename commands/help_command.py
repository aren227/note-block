import discord
import typing

from commands.command import Command

if typing.TYPE_CHECKING:
    from client import NoteblockClient


class HelpCommand(Command):

    def __init__(self, client: 'NoteblockClient'):
        super(HelpCommand, self).__init__(client)

    def get_base_command(self) -> str:
        return "h"

    def get_alias(self):
        pass

    def get_help(self) -> str:
        return ";h : 도움말을 출력합니다."

    async def execute(self, message: discord.Message, args: typing.List[str]):
        msg = "지원되는 명령어 목록:"
        for command in self.client.get_commands():
            msg += command.get_help() + "\n"
        await message.channel.send(msg)
