import typing

import discord
from bson import ObjectId
from pymongo import MongoClient

from music.music import Music
from music.youtube_music import YoutubeMusic
from play_list import PlayList

if typing.TYPE_CHECKING:
    from client import NoteblockClient


class Database:

    def __init__(self, client: 'NoteblockClient'):
        self.client = client
        self.database = MongoClient('localhost', 27017)

    def create_music_from_dict(self, dt: dict) -> typing.Optional[Music]:
        if dt['source'] == 'youtube':
            return YoutubeMusic(dt['video_id'], dt['title'], dt['duration'])
        return None

    def get_dict_from_music(self, music: Music) -> typing.Optional[dict]:
        if isinstance(music, YoutubeMusic):
            return {
                'source': 'youtube',
                'video_id': music.video_id,
                'title': music.title,
                'duration': music.duration
            }

        return None

    def create_playlist_from_dict(self, guild: discord.Guild, dt: dict) -> PlayList:
        if guild.id != dt['guild_id']:
            raise ValueError("Given guild must equal to playlist's guild")

        playlist = []
        for m_dt in dt['playlist']:
            music = self.create_music_from_dict(m_dt)
            if music is not None:
                playlist.append(music)

        return PlayList(guild, dt['title'], playlist, dt['_id'])

    def get_dict_from_playlist(self, playlist: PlayList) -> dict:
        return {
            'guild_id': playlist.guild.id,
            'title': playlist.title,
            'playlist': [self.get_dict_from_music(music) for music in playlist.play_list],
            'playlist_length': len(playlist.play_list)
        }

    # Returns only _id, title and playlist_length.
    def get_playlists(self, guild: discord.Guild, title: str = '') -> typing.List[dict]:
        results = self.database.noteblock.playlist.find({
            'guild_id': guild.id,
            'title': {
                '$regex': '.*{}.*'.format(title)
            }
        }, {
            '_id': 1,
            'title': 1,
            'playlist_length': 1
        })
        return list(results)

    def get_playlist(self, guild: discord.Guild, _id: ObjectId) -> typing.Optional[PlayList]:
        result = self.database.noteblock.playlist.find_one({
            '_id': _id
        })
        if result is None:
            return None

        return self.create_playlist_from_dict(guild, result)

    def add_playlist(self, playlist: PlayList):
        db_id = self.database.noteblock.playlist.insert_one(self.get_dict_from_playlist(playlist)).inserted_id
        playlist.db_id = db_id

    def update_playlist(self, playlist: PlayList):
        if playlist.db_id is None:
            raise ValueError("Playlist must be inserted into db first.")

        self.database.noteblock.playlist.update_one({
            '_id': playlist.db_id
        }, {
            '$set': {
                'title': playlist.title,
                'playlist': [self.get_dict_from_music(music) for music in playlist.play_list],
                'playlist_length': len(playlist.play_list)
            }
        })

    def delete_playlist(self, playlist: PlayList):
        self.database.noteblock.playlist.delete_one({
            '_id': playlist.db_id
        })
