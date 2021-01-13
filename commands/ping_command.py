import discord
import typing

from commands.command import Command

if typing.TYPE_CHECKING:
    from client import NoteblockClient


class PingCommand(Command):

    def __init__(self, client: 'NoteblockClient'):
        super().__init__(client)

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
            msg = "지연 시간: **{}ms** / 평균 지연 시간: **{}ms**\n".format(int(player.voice_client.latency * 1000), int(player.voice_client.average_latency * 1000))
            if player.get_current_music() is not None:
                msg += "평균 음악 버퍼 크기: **{:.2f}**\n".format(player.get_current_music().buffer_size_average.get_average())
            await message.channel.send(msg)
        except Exception:
            await message.channel.send("지연 시간 데이터가 충분하지 않습니다. 조금 뒤에 다시 시도해주세요.")
        return True
