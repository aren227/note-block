import discord
import typing

from commands.command import Command

if typing.TYPE_CHECKING:
    from client import NoteblockClient


class PlayPlaylistCommand(Command):

    def __init__(self, client: 'NoteblockClient'):
        super().__init__(client)

    def get_base_command(self) -> str:
        return "playlist"

    def get_alias(self):
        return "pl"

    def get_help(self) -> str:
        return ";**p**lay**l**ist [이름] : 플레이리스트의 모든 음악을 재생 대기열에 추가합니다."

    async def execute(self, message: discord.Message, args: typing.List[str]):
        if len(args) == 0:
            return False

        list_title = " ".join(args)

        results = self.client.database.get_playlists(message.guild, list_title)

        if len(results) == 0:
            await message.channel.send("검색 결과가 없습니다.")
            return True

        await self.client.selector.query_to_member(message.guild, message.author, [playlist['title'] for playlist in results],
                                                   results, self.add_playlist_to_queue, message.channel,
                                                   "재생을 원하는 플레이리스트의 번호를 입력해주세요.")

        return True

    async def add_playlist_to_queue(self, playlist_dict: dict, member: discord.Member, channel: discord.TextChannel):
        playlist = self.client.database.get_playlist(member.guild, playlist_dict['_id'])
        if playlist is None:
            await channel.send("플레이리스트 **[{}]**가 존재하지 않습니다.".format(playlist_dict['title']))
            return

        await self.client.try_to_connect_player(channel.guild, member, channel)

        player = self.client.get_player(member.guild)
        for music in playlist.get_all_music():
            player.get_music_queue().add_music(music)

        if not player.is_playing_music():
            player.play_next_music()

        await channel.send("**[{}]**의 곡 **{}개**가 대기열에 추가되었습니다.".format(playlist.get_title(), len(playlist.get_all_music())))

