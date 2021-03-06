import functools

import discord
import typing
import re

from utils import time_format
from commands.command import Command
from music.youtube_music import YoutubeMusic
from ytdl import ytdl

if typing.TYPE_CHECKING:
    from client import NoteblockClient


class PlayCommand(Command):

    def __init__(self, client: 'NoteblockClient'):
        super().__init__(client)

    def get_base_command(self) -> str:
        return "play"

    def get_alias(self):
        return "p"

    def get_help(self) -> str:
        return ";**p**lay [검색어/링크] : 유튜브에서 영상을 검색한 뒤 음악을 재생합니다."

    def create_embed(self, member: discord.Member, video: dict) -> discord.Embed:
        embed = discord.Embed(title=video['title'], url="https://www.youtube.com/watch?v={}".format(video['id']))
        embed.set_author(name=str(member), icon_url=member.avatar_url)
        embed.set_image(url="https://img.youtube.com/vi/{}/0.jpg".format(video['id']))
        embed.add_field(name="길이", value=time_format.time_digits(int(video['duration'])))

        delay = 0
        if self.client.guild_has_player(member.guild):
            delay += self.client.get_player(member.guild).get_total_time_left()

        if delay == 0:
            embed.add_field(name="대기열", value="지금 재생")
        else:
            embed.add_field(name="대기열", value="약 {} 뒤 재생".format(time_format.time_approximated(delay)))

        embed.colour = 0xff0000
        return embed

    async def execute(self, message: discord.Message, args: typing.List[str]) -> bool:
        if len(args) == 0:
            return False

        if self.client.guild_has_player(message.guild):
            player = self.client.get_player(message.guild)
            if player.is_radio_mode():
                await message.channel.send("라디오 모드에서는 명령어 **;play**를 통해 곡을 추가할 수 없습니다.\n"
                                           "**;list add**로 현재 재생중인 플레이리스트에 곡을 추가하거나 **;radio off**로 라디오 모드를 종료해주세요.\n"
                                           "현재 재생중인 플레이리스트는 **[{}]**입니다.".format(player.get_radio_playlist_title()))
                return True

        search_str = " ".join(args)

        # Add to queue directly
        if search_str.startswith("https://www.youtube.com/watch?v="):
            vid = re.search(r'v=([_\-0-9a-zA-Z]+)', search_str).group(1)
            partial = functools.partial(ytdl.extract_info, vid, download=False, process=False)
            result = await self.client.loop.run_in_executor(None, partial)
            await self.add_video(result, message.author, message.channel)
            return True

        partial = functools.partial(ytdl.extract_info, "ytsearch5: {}".format(search_str), download=False, process=False)
        results = await self.client.loop.run_in_executor(None, partial)
        results = list(results['entries'])

        await self.client.selector.query_to_member(message.guild, message.author, [video['title'] for video in results],
                                                   results, self.add_video, message.channel,
                                                   "재생을 원하는 영상의 번호를 입력해주세요.")
        return True

    async def add_video(self, video: dict, member: discord.Member, channel: discord.TextChannel):
        # Streaming video
        if video['duration'] is None:
            await channel.send("해당 영상은 재생할 수 없습니다.")
            return

        await self.client.try_to_connect_player(channel.guild, member, channel)

        player = self.client.get_player(channel.guild)
        if player.is_connected():
            if player.is_radio_mode():
                await channel.send("라디오 모드에서는 **;list add**를 사용해서 플레이리스트에 직접 추가해주세요.")
                return

            player.get_music_queue().add_music(
                YoutubeMusic(video['id'], video['title'], int(video['duration'])))

            if not player.is_playing_music():
                player.play_next_music()

            await channel.send(embed=self.create_embed(member, video))
