import functools
import re
import typing

import discord

from commands.command import Command
from music.music import Music
from music.youtube_music import YoutubeMusic
from play_list import PlayList
from utils import time_format
from ytdl import ytdl

if typing.TYPE_CHECKING:
    from client import NoteblockClient


class PlayListCommand(Command):

    def __init__(self, client: 'NoteblockClient'):
        super().__init__(client)

    def get_base_command(self) -> str:
        return "l"

    def get_help(self) -> str:
        return ";l new [이름] : 새로운 플레이리스트를 생성하고 생성된 플레이리스트를 __사용중__으로 설정합니다.\n" \
               ";l use [이름] : 해당 플레이리스트를 __사용중__으로 설정합니다." \
               ";l add [검색어/링크] : 유튜브에서 영상을 검색한 뒤 __사용중__인 플레이리스트에 추가합니다.\n" \
               ";l delete [검색어/링크] : __사용중__인 플레이리스트에서 음악을 제거합니다.\n" \
               ";l delete : __사용중__인 플레이리스트를 제거합니다.\n" \
               ";l q : 사용중인 플레이리스트의 곡 목록을 확인합니다.\n" \
               ";l : 모든 플레이리스트와 사용중인 플레이리스트를 확인합니다."

    async def execute(self, message: discord.Message, args: typing.List[str]) -> bool:
        if len(args) == 0:
            results = self.client.playlist_manager.get_all_playlist(message.guild)

            msg = "총 {}개의 플레이리스트가 존재합니다.".format(len(results))

            playlist = self.client.playlist_manager.get_member_playlist(message.author)
            if playlist is not None:
                msg += " 사용중인 플레이리스트: **[{}]**".format(playlist.get_title())

            for i in range(min(7, len(results))):
                msg += "\n{}. **{}** [{}곡]".format(i + 1, results[i]['title'], results[i]['playlist_length'])

            await message.channel.send(msg)

        elif args[0] == "new":
            if len(args) == 1 or len(" ".join(args[1:])) == 0:
                await message.channel.send("플레이리스트의 이름을 입력해주세요.")
                return True

            title = " ".join(args[1:])
            self.client.playlist_manager.create_playlist(message.author, title)

            await message.channel.send("플레이리스트 **[{}]**가 생성되었습니다.\n현재 사용중인 플레이리스트는 **[{}]**입니다.".format(title, title))

        elif args[0] == "use":
            if len(args) == 1 or len(" ".join(args[1:])) == 0:
                await message.channel.send("플레이리스트의 이름을 입력해주세요. **;l**로 모든 플레이리스트를 확인할 수 있습니다.")
                return True

            title = " ".join(args[1:])

            results = self.client.database.get_playlists(message.guild, title)

            if len(results) == 0:
                await message.channel.send("플레이리스트 검색 결과가 없습니다.")
                return True

            await self.client.selector.query_to_member(message.guild, message.author,
                                                 [playlist['title'] for playlist in results],
                                                 results,
                                                 self.use_playlist,
                                                 message.channel,
                                                 "사용을 원하는 플레이리스트의 번호를 입력해주세요.")
        elif args[0] == "add":
            playlist = self.client.playlist_manager.get_member_playlist(message.author)

            if len(args) == 1 or len(" ".join(args[1:])) == 0:
                await message.channel.send("검색어를 입력해주세요.")
                return True

            if playlist is None:
                await message.channel.send("먼저 **;l use [이름]**으로 플레이리스트를 선택해주세요.")
                return True

            search_str = " ".join(args[1:])

            # TODO: Duplicate play_command.py
            # Add to queue directly
            if search_str.startswith("https://www.youtube.com/watch?v="):
                vid = re.search(r'v=([_\-0-9a-zA-Z]+)', search_str).group(1)
                partial = functools.partial(ytdl.extract_info, vid, download=False, process=False)
                result = await self.client.loop.run_in_executor(None, partial)
                await self.add_video_to_playlist(result, message.author, message.channel)
                return True

            partial = functools.partial(ytdl.extract_info, "ytsearch5: {}".format(search_str), download=False,
                                        process=False)
            results = await self.client.loop.run_in_executor(None, partial)
            results = list(results['entries'])

            await self.client.selector.query_to_member(message.guild, message.author, [video['title'] for video in results],
                                                 results, self.add_video_to_playlist, message.channel,
                                                 "플레이리스트에 추가할 영상의 번호를 입력해주세요.")

        elif args[0] == "delete":
            playlist = self.client.playlist_manager.get_member_playlist(message.author)
            if playlist is None:
                await message.channel.send("먼저 **;l use [이름]**으로 플레이리스트를 선택해주세요.")
                return True

            if len(args) == 1:
                self.client.playlist_manager.delete_playlist(playlist)
                await message.channel.send("플레이리스트 **[{}]**가 제거되었습니다.".format(playlist.get_title()))
                return True

            else:
                search_str = " ".join(args[1:])

                results = playlist.search_music(search_str)
                if len(results) == 0:
                    await message.channel.send("검색 결과가 없습니다.")
                    return True

                await self.client.selector.query_to_member(message.guild, message.author, [music.get_title() for music in results],
                                                     results, self.delete_video_in_playlist, message.channel,
                                                     "플레이리스트에서 삭제할 영상의 번호를 입력해주세요.")
        elif args[0] == "q":
            playlist = self.client.playlist_manager.get_member_playlist(message.author)
            if playlist is None:
                await message.channel.send("먼저 **;l use [이름]**으로 플레이리스트를 선택해주세요.")
                return True

            msg = "플레이리스트 **[{}]**, 총 {}곡 [{}]".format(playlist.get_title(), len(playlist.get_all_music()), time_format.time_digits(playlist.get_play_time()))
            for i in range(min(7, len(playlist.get_all_music()))):
                msg += "\n{}. **{}** [{}]".format(i + 1, playlist.get_all_music()[i].get_title(), time_format.time_digits(playlist.get_all_music()[i].get_duration()))

            await message.channel.send(msg)

        else:
            return False

        return True

    async def use_playlist(self, playlist: dict, member: discord.Member, channel: discord.TextChannel):
        self.client.playlist_manager.set_member_playlist_with_id(member, playlist['_id'])

        playlist = self.client.playlist_manager.get_member_playlist(member)

        if playlist is None:
            await channel.send("선택하려는 플레이리스트가 존재하지 않습니다.")
        else:
            await channel.send("현재 사용중인 플레이리스트는 **[{}]**입니다.".format(playlist.get_title()))

    def create_embed(self, member: discord.Member, video: dict, playlist: PlayList) -> discord.Embed:
        embed = discord.Embed(title=video['title'], url="https://www.youtube.com/watch?v={}".format(video['id']))
        embed.set_author(name=str(member), icon_url=member.avatar_url)
        embed.set_image(url="https://img.youtube.com/vi/{}/0.jpg".format(video['id']))
        embed.add_field(name="길이", value=time_format.time_digits(int(video['duration'])))

        delay = 0
        if self.client.guild_has_player(member.guild):
            delay += self.client.get_player(member.guild).get_total_time_left()

        embed.add_field(name="플레이리스트", value=playlist.get_title())

        embed.colour = 0xff0000
        return embed

    async def add_video_to_playlist(self, video: dict, member: discord.Member, channel: discord.TextChannel):
        # Streaming video
        if video['duration'] is None:
            await channel.send("해당 영상은 재생할 수 없습니다.")
            return

        playlist = self.client.playlist_manager.get_member_playlist(member)
        if playlist is None:
            await channel.send("먼저 **;l use [이름]**으로 플레이리스트를 선택해주세요.")
            return True

        music = YoutubeMusic(video['id'], video['title'], int(video['duration']))

        playlist.add_music(music)
        self.client.playlist_manager.update_playlist(playlist)

        if self.client.guild_has_player(member.guild):
            player = self.client.get_player(member.guild)
            if player.is_radio_mode() and player.radio_mode == playlist.db_id:
                player.music_queue.add_music(music)

        await channel.send(embed=self.create_embed(member, video, playlist))

    async def delete_video_in_playlist(self, music: Music, member: discord.Member, channel: discord.TextChannel):
        playlist = self.client.playlist_manager.get_member_playlist(member)
        if playlist is None:
            await channel.send("먼저 **;l use [이름]**으로 플레이리스트를 선택해주세요.")
            return True

        playlist.delete_music(music.get_id())
        self.client.playlist_manager.update_playlist(playlist)

        await channel.send("플레이리스트 **[{}]**애서 **{}**가 삭제되었습니다.".format(playlist.get_title(), music.get_title()))
