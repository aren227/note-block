import typing

import discord
from bson import ObjectId

from database import Database
from play_list import PlayList

if typing.TYPE_CHECKING:
    from client import NoteblockClient


class PlayListManager:

    def __init__(self, client: 'NoteblockClient', database: Database):
        self.client = client
        self.database = database

        self.guilds: typing.Dict[discord.Guild, typing.Dict[discord.Member, ObjectId]] = {}

    def set_member_playlist(self, member: discord.Member, playlist: PlayList):
        if playlist.db_id is None:
            raise ValueError("Playlist must be inserted into db first.")

        if member.guild not in self.guilds:
            self.guilds[member.guild] = {}

        self.guilds[member.guild][member] = playlist.db_id

    def set_member_playlist_with_id(self, member: discord.Member, _id: ObjectId):
        playlist = self.database.get_playlist(member.guild, _id)
        if playlist is not None:
            self.set_member_playlist(member, playlist)

    def get_member_playlist(self, member: discord.Member) -> typing.Optional[PlayList]:
        if member.guild not in self.guilds:
            return None

        if member not in self.guilds[member.guild]:
            return None

        return self.database.get_playlist(member.guild, self.guilds[member.guild][member])

    def delete_member_playlist(self, member: discord.Member):
        if member.guild not in self.guilds:
            return

        self.guilds[member.guild].pop(member, None)

    def create_playlist(self, member: discord.Member, title: str):
        playlist = PlayList(member.guild, title, [])
        self.database.add_playlist(playlist)

        self.set_member_playlist(member, playlist)

    def update_playlist(self, playlist: PlayList):
        self.database.update_playlist(playlist)

    def delete_playlist(self, playlist: PlayList):
        self.database.delete_playlist(playlist)

    def get_all_playlist(self, guild: discord.Guild):
        return self.database.get_playlists(guild)
