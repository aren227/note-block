import discord
import typing

from utils import time_format
from commands.command import Command
from player.player import Player

if typing.TYPE_CHECKING:
    from client import NoteblockClient


class QueueCommand(Command):

    def __init__(self, client: 'NoteblockClient'):
        super().__init__(client)

    def get_base_command(self) -> str:
        return "q"

    def get_alias(self):
        pass

    def get_help(self) -> str:
        return ";q : 대기중인 모든 음악을 확인합니다."

    def get_queue_message(self, player: Player) -> str:
        msg = ""
        if player.is_radio_mode():
            msg += "📻 플레이리스트 **[{}]**\n".format(player.get_radio_playlist_title())

        msg += "**{}**곡 대기 중, 남은 재생 시간 **[{}]**".format(len(player.get_music_queue().get_all_music()), time_format.time_digits(player.get_total_time_left()))
        if player.is_playing_music():
            msg += "\n▶ {} [{}/{}]".format(player.get_current_music().get_title(),
                                           time_format.time_digits(int(player.get_current_music().get_play_time())),
                                           time_format.time_digits(player.get_current_music().get_duration()))

        musics = player.get_music_queue().get_all_music()
        for i in range(min(7, len(musics))):
            msg += "\n- {} [{}]".format(musics[i].get_title(),
                                        time_format.time_digits(musics[i].get_duration()))

        if len(msg) == 0:
            return "재생 중인 음악이 없습니다."
        return msg

    async def execute(self, message: discord.Message, args: typing.List[str]):
        if not self.client.guild_has_player(message.guild):
            await message.channel.send("재생 중인 음악이 없습니다.")
            return True

        player = self.client.get_player(message.guild)
        await message.channel.send(self.get_queue_message(player))

        return True
