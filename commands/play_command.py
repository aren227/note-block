import functools

import discord
import typing
import youtube_dl

from utils import time_format
from commands.command import Command
from music.youtube_music import YoutubeMusic

if typing.TYPE_CHECKING:
    from client import NoteblockClient


class PlayCommand(Command):

    def __init__(self, client: 'NoteblockClient', ytdl: youtube_dl.YoutubeDL):
        super().__init__(client)

        self.ytdl = ytdl

        self.member_queries: typing.Dict[discord.Member, QueryResults] = {}

    def get_base_command(self) -> str:
        return "p"

    def get_help(self) -> str:
        return ";p [검색어] : 유튜브에서 영상을 검색한 뒤 음악을 재생합니다."

    def set_search_results(self, member: discord.Member, results: 'QueryResults'):
        self.member_queries[member] = results

    def get_searched_results_string(self, results: typing.List[dict]) -> str:
        msg = ""
        for i in range(len(results)):
            msg += "{}. {}\n".format(i + 1, results[i]['title'])
        msg += "재생을 원하는 영상의 번호를 입력해주세요."
        return msg

    def has_queried(self, member: discord.Member):
        return member in self.member_queries

    def get_ith_video(self, member: discord.Member, index: int) -> typing.Optional[dict]:
        if member not in self.member_queries:
            return None

        if index < 1 or len(self.member_queries[member].results) < index:
            return None

        result = self.member_queries[member].results[index - 1]
        return result

    def get_query_and_response_messages(self, member: discord.Member) -> typing.Optional[typing.Tuple[discord.Message, discord.Message]]:
        if member not in self.member_queries:
            return None

        return self.member_queries[member].query_message, self.member_queries[member].response_message

    def pop_search_results(self, member: discord.Member):
        self.member_queries.pop(member, None)

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

        search_str = " ".join(args)

        partial = functools.partial(self.ytdl.extract_info, "ytsearch5: {}".format(search_str), download=False, process=False)
        results = await self.client.loop.run_in_executor(None, partial)
        results = list(results['entries'])

        response = await message.channel.send(self.get_searched_results_string(results))

        self.set_search_results(message.author, QueryResults(message, response, results))

        return True

    async def on_message(self, message: discord.Message):
        if not message.content.isdigit():
            return

        if not self.has_queried(message.author):
            return

        video = self.get_ith_video(message.author, int(message.content))
        if video is None:
            return

        print(video)

        # Streaming video
        if video['duration'] is None:
            await message.channel.send("해당 영상은 재생할 수 없습니다.")
            return

        await self.client.try_to_connect_player(message.guild, message.author, message.channel)

        query_message, response_message = self.get_query_and_response_messages(message.author)
        await query_message.delete()
        await response_message.edit(content="", embed=self.create_embed(message.author, video))
        await message.delete()

        player = self.client.get_player(message.guild)
        if player.is_connected():
            player.get_music_queue().add_music(YoutubeMusic(self.ytdl, "https://www.youtube.com/watch?v={}".format(video['id']), video['title'], int(video['duration'])))

            if not player.is_playing_music():
                player.play_next_music()


class QueryResults:

    def __init__(self, query_message: discord.Message, response_message: discord.Message, results: typing.List[dict]):
        self.query_message = query_message
        self.response_message = response_message
        self.results = results
