import asyncio

import discord

from music.buffered_audio import BufferedAudio


class Music(BufferedAudio):

    def __init__(self, title: str, duration: int):
        super().__init__()

        self.title: str = title
        self.duration: int = duration

    def get_title(self) -> str:
        return self.title

    def get_duration(self) -> int:
        return self.duration

    def get_time_left(self) -> int:
        return max(int(self.get_duration() - self.get_play_time()), 0)

    def _create_audio_source(self):
        raise NotImplementedError
