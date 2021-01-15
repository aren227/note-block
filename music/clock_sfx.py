import discord

from music.buffered_audio import BufferedAudio


def get_delay() -> float:
    return 6.48 + 3


class ClockSfx(BufferedAudio):

    def __init__(self):
        super().__init__()

    def _create_audio_source(self) -> discord.AudioSource:
        return discord.FFmpegPCMAudio('./sfx/clock_alert.wav')
