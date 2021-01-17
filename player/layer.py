import discord
import numpy as np
import typing

from music.buffered_audio import BufferedAudio

if typing.TYPE_CHECKING:
    from player.mixer import Mixer


class Layer:

    def __init__(self, mixer: 'Mixer', name: str, max_audio_sources: int):
        self.mixer = mixer
        self.name = name
        self.max_audio_sources = max_audio_sources

        self.audio_sources: typing.List[BufferedAudio] = []

    def get_name(self) -> str:
        return self.name

    def is_full(self) -> bool:
        return len(self.audio_sources) >= self.max_audio_sources

    def add_audio_source(self, audio_source: BufferedAudio):
        if len(self.audio_sources) >= self.max_audio_sources:
            self.audio_sources.pop(0)

        self.audio_sources.append(audio_source)

    def delete_audio_source(self, audio_source: BufferedAudio):
        self.audio_sources.remove(audio_source)

    def clear_audio_sources(self):
        self.audio_sources.clear()

    def read_buffer(self, buffer: np.ndarray) -> typing.Tuple[np.ndarray, bool]:
        # At least one audio is playing
        playing = False

        for i in range(len(self.audio_sources) - 1, -1, -1):
            buf = self.audio_sources[i].read()

            # Audio finished
            if buf is None:
                self.audio_sources.pop(i)
                self.mixer.audio_source_finished(self)
                continue

            buffer += buf
            playing = True

        return buffer, playing
