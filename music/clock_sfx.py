import discord

from music.buffered_audio import BufferedAudio
from music.sound_file import SoundFile


def get_delay() -> float:
    return 6.48


class ClockSfx(SoundFile):

    def __init__(self):
        super().__init__('./sfx/clock_alert.wav')
