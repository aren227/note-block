import discord

from music.buffered_audio import BufferedAudio


class SoundFile(BufferedAudio):

    def __init__(self, path):
        super().__init__()
        self.path = path

    def _create_audio_source(self) -> discord.AudioSource:
        return discord.FFmpegPCMAudio(self.path)
