import typing

import discord

from commands.command import Command

if typing.TYPE_CHECKING:
    from client import NoteblockClient


class RadioCommand(Command):

    def __init__(self, client: 'NoteblockClient'):
        super().__init__(client)

    def get_base_command(self) -> str:
        return "radio"

    def get_alias(self):
        return "r"

    def get_help(self) -> str:
        return ";**r**adio [이름/off] : 플레이리스트로 라디오 모드를 설정하거나 라디오 모드를 종료합니다."

    async def execute(self, message: discord.Message, args: typing.List[str]):
        if len(args) == 0:
            return False

        if args[0] == "off":
            player = self.client.get_player(message.guild)
            if player is not None and player.is_radio_mode():
                player.set_radio_mode(None)
                await message.channel.send("📻 라디오 모드를 종료합니다.")
            return True

        title = " ".join(args[0:])

        playlists = self.client.database.get_playlists(message.guild, title)

        if len(playlists) == 0:
            await message.channel.send("검색된 플레이리스트가 없습니다.")
            return True

        await self.client.selector.query_to_member(message.guild, message.author, [playlist['title'] for playlist in playlists],
                                                   playlists, self.start_radio_mode_with_playlist, message.channel,
                                                   "라디오 모드를 원하는 플레이리스트의 번호를 입력해주세요.")
        return True

    async def start_radio_mode_with_playlist(self, playlist_dict: dict, member: discord.Member, channel: discord.TextChannel):
        playlist = self.client.database.get_playlist(member.guild, playlist_dict['_id'])
        if playlist is None:
            await channel.send("플레이리스트 **[{}]**가 존재하지 않습니다.".format(playlist_dict['title']))
            return

        await self.client.try_to_connect_player(channel.guild, member, channel)

        player = self.client.get_player(member.guild)
        if player.is_connected():
            player.set_radio_mode(playlist.db_id)
            await channel.send("📻 플레이리스트 **[{}]**로 라디오 모드를 시작합니다.".format(playlist.get_title()))
