import typing

import discord

from music.music import Music


class PlayList:

    def __init__(self, guild: discord.Guild, title: str):
        self.guild = guild
        self.title = title

        self.play_list: typing.List[Music] = []

    def get_title(self) -> str:
        return self.title

    def add_music(self, music: Music):
        self.play_list.append(music)

    def find_music(self, music_id: str) -> typing.Optional[Music]:
        for music in self.play_list:
            if music.get_id() == music_id:
                return music
        return None

    def delete_music(self, music_id: str):
        for i in range(len(self.play_list)):
            if self.play_list[i].get_id() == music_id:
                self.play_list.pop(i)

    def get_all_music(self) -> typing.List[Music]:
        return self.play_list

    def get_play_time(self) -> int:
        total_time = 0
        for music in self.play_list:
            total_time += music.get_duration()
        return total_time
