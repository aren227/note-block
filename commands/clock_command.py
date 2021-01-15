import discord
import typing

from commands.command import Command

if typing.TYPE_CHECKING:
    from client import NoteblockClient


class ClockCommand(Command):

    def __init__(self, client: 'NoteblockClient'):
        super().__init__(client)

    def get_base_command(self) -> str:
        return "clock"

    def get_alias(self):
        pass

    def get_help(self) -> str:
        return ";clock [on/off] : 정각 알림을 설정합니다."

    async def execute(self, message: discord.Message, args: typing.List[str]):
        if len(args) != 1 or args[0] not in ('on', 'off'):
            return False

        await self.client.try_to_connect_player(message.guild, message.author, message.channel)

        player = self.client.get_player(message.guild)
        player.set_clock_alert(args[0] == 'on')

        if args[0] == 'on':
            await message.channel.send("⏰ 정각 알림이 설정되었습니다.")
        else:
            await message.channel.send("⏰ 정각 알림이 해제되었습니다.")
        return True
