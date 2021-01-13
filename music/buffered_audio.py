import queue
import time
from threading import Thread

import discord
import typing
import numpy as np

from utils.moving_average import MovingAverage


class BufferedAudio(Thread):

    def __init__(self):
        super().__init__()
        self.q: queue.Queue = queue.Queue()
        self.audio_source: typing.Optional[discord.AudioSource] = None
        self.play_time: float = 0
        self.finished = False

        self.buffer_size_average = MovingAverage(500)

    # None -> EOS
    def read(self) -> typing.Optional[np.ndarray]:
        self.buffer_size_average.push(self.q.qsize())

        # Buffer Underflow, just send empty audio
        if self.q.empty():
            if self.finished:
                return None

            return np.zeros(960 * 2, dtype='<i2')

        self.play_time += 0.02
        return self.q.get()

    def is_finished(self) -> bool:
        return self.finished

    def get_play_time(self) -> float:
        return self.play_time

    def _create_audio_source(self) -> discord.AudioSource:
        raise NotImplementedError

    # Fill the buffer
    def _read(self):
        if self.audio_source is None:
            self.audio_source = self._create_audio_source()

        bytes_buf = self.audio_source.read()
        if len(bytes_buf) == 0:
            self.finished = True
            return

        self.q.put(np.frombuffer(bytes_buf, dtype='<i2'))

    def run(self):
        target_buffer_size = 50

        while not self.finished:
            if self.q.qsize() > target_buffer_size:
                time.sleep(0.02)
                continue

            self._read()
