import asyncio

import discord


class Music:

    def __init__(self, title: str, duration: int):
        self.title: str = title
        self.duration: int = duration
        self.play_time: float = 0

    def get_title(self) -> str:
        return self.title

    def get_duration(self) -> int:
        return self.duration

    def get_play_time(self) -> float:
        return self.play_time

    def set_play_time(self, t: float):
        self.play_time = min(t, self.get_duration())

    def get_left_time(self) -> int:
        return max(int(self.get_duration() - self.get_play_time()), 0)

    async def create_audio_source(self, loop: asyncio.AbstractEventLoop):
        pass


# A Wrapper class tracking play time
class MusicAudioSource(discord.AudioSource):

    def __init__(self, music: Music, audio_source: discord.AudioSource):
        self.music = music
        self.audio_source = audio_source

    def read(self):
        self.music.set_play_time(self.music.get_play_time() + 0.02)
        return self.audio_source.read()

    def is_opus(self):
        return self.audio_source.is_opus()
