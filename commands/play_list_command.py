import typing

import discord

from commands.command import Command

if typing.TYPE_CHECKING:
    from client import NoteblockClient


class PlayListCommand(Command):

    def __init__(self, client: 'NoteblockClient'):
        super().__init__(client)

    def get_base_command(self) -> str:
        return "l"

    def get_help(self) -> str:
        return ";l new [이름] : 새로운 플레이리스트를 생성합니다.\n" \
               ";l add [검색어/링크] : 유튜브에서 영상을 검색한 뒤 플레이리스트에 추가합니다.\n" \
               ";l delete [검색어/링크] : 플레이리스트에서 음악을 제거합니다.\n" \
               ";l [이름] : 플레이리스트의 곡 목록을 확인합니다.\n" \
               ";l : 모든 플레이리스트를 확인합니다."

    async def execute(self, message: discord.Message, args: typing.List[str]) -> bool:
        if len(args) == 0:
            # TODO: Display all playlists
            raise NotImplementedError
        elif args[0] == "new":
            # TODO: Create a new playlist
            raise NotImplementedError
        elif args[0] == "add":
            # TODO: Add music to the playlist
            raise NotImplementedError
        elif args[0] == "delete":
            # TODO: Delete music in the playlist
            raise NotImplementedError
        else:
            # TODO: Display all music in the playlist
            raise NotImplementedError
