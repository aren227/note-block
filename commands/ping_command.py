import discord
import typing

from commands.command import Command

if typing.TYPE_CHECKING:
    from client import NoteblockClient


class PingCommand(Command):

    def __init__(self, client: 'NoteblockClient'):
        super(PingCommand, self).__init__(client)

    def get_base_command(self) -> str:
        return "ping"

    def get_alias(self):
        pass

    def get_help(self) -> str:
        return ";ping : 서버와의 지연 시간을 확인합니다."

    async def execute(self, message: discord.Message, args: typing.List[str]):
        if not self.client.guild_has_player(message.guild):
            return
        player = self.client.get_player(message.guild)
        try:
            await message.channel.send("지연 시간: **{}ms** / 평균 지연 시간: **{}ms**.".format(int(player.voice_client.latency * 1000), int(player.voice_client.average_latency * 1000)))
        except Exception:
            await message.channel.send("지연 시간 데이터가 충분하지 않습니다. 조금 뒤에 다시 시도해주세요.")
        return True
