from datetime import datetime

import typing

from music.buffered_audio import BufferedAudio


class ScheduledAudio:

    def __init__(self, start_time: datetime, audio: BufferedAudio):
        self.start_time = start_time
        self.audio = audio

    def is_repeating(self) -> bool:
        return False
