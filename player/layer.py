import discord
import numpy as np
import typing

if typing.TYPE_CHECKING:
    from player.mixer import Mixer


class Layer:

    def __init__(self, mixer: 'Mixer', name: str, max_audio_sources: int):
        self.mixer = mixer
        self.name = name
        self.max_audio_sources = max_audio_sources

        self.audio_sources: typing.List[discord.AudioSource] = []

    def get_name(self) -> str:
        return self.name

    def is_full(self) -> bool:
        return len(self.audio_sources) >= self.max_audio_sources

    def add_audio_source(self, audio_source: discord.AudioSource):
        if len(self.audio_sources) >= self.max_audio_sources:
            self.audio_sources.pop(0)

        self.audio_sources.append(audio_source)

    def clear_audio_sources(self):
        self.audio_sources.clear()

    def read_buffer(self, buffer: np.ndarray) -> np.ndarray:
        for i in range(len(self.audio_sources) - 1, -1, -1):
            bytes_buf = self.audio_sources[i].read()

            # Audio finished
            if len(bytes_buf) == 0:
                self.mixer.audio_source_finished(self, self.audio_sources.pop(i))
                continue

            buffer += np.frombuffer(bytes_buf, dtype='<i2')
        return buffer
