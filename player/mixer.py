import time
from threading import Thread

import discord
import numpy as np
import typing

from music.buffered_audio import BufferedAudio
from player.layer import Layer
from utils.moving_average import MovingAverage

if typing.TYPE_CHECKING:
    from player.player import Player


class Mixer(Thread):

    def __init__(self, player: 'Player'):
        super().__init__()

        self.player = player

        self.speaking = True

        self.layers: typing.Dict[str, Layer] = {}
        self.earrape: bool = False

        """Add default layers"""
        self.add_layer(Layer(self, "MUSIC", 1))
        self.add_layer(Layer(self, "EMOJI", 5))

    def _read(self) -> typing.Tuple[bytes, bool]:
        # At least one layer is playing
        should_send_packet = False
        buf = np.zeros(960 * 2, dtype=np.int)

        for key in self.layers:
            buf, layer_playing = self.layers[key].read_buffer(buf)

            should_send_packet |= layer_playing

        if self.earrape:
            buf *= 1200

        # Volume 25%
        final_buf = np.clip(buf // 4, -32768, 32767).astype(dtype='<i2').tobytes()

        return final_buf, should_send_packet

    def add_layer(self, layer: Layer):
        if layer.get_name() in self.layers:
            raise ValueError("Same name of layer already exists.")

        self.layers[layer.get_name()] = layer

    def add_audio_source(self, layer_name: str, audio_source: BufferedAudio):
        if layer_name not in self.layers:
            raise ValueError("Layer {} not exists.".format(layer_name))

        self.layers[layer_name].add_audio_source(audio_source)

    def clear_audio_sources(self, layer_name: str):
        if layer_name not in self.layers:
            raise ValueError("Layer {} not exists.".format(layer_name))

        self.layers[layer_name].clear_audio_sources()

    def audio_source_finished(self, layer: Layer):
        if layer.get_name() == "MUSIC":
            self.player.play_next_music()

    def is_earraped(self):
        return self.earrape

    def set_earrape(self, earrape):
        self.earrape = earrape

    def run(self):
        expected_packet_loss_rate = 0.001
        target_packet_buffer = 5

        packet_sent = 0
        time_start = time.time()
        packet_loss_timer = time.time()

        while self.player.voice_client.is_connected():
            target_packet_sent = int((time.time() - time_start) * 50)  # 1 packet = 20ms

            if packet_sent > target_packet_sent + target_packet_buffer:
                time.sleep(0.02)
                continue

            buf, should_send = self._read()
            if should_send:
                self.player.voice_client.send_audio_packet(buf, encode=True)

            if self.speaking != should_send:
                self.player.voice_client.ws.speak(1 if should_send else 0)
                self.speaking = should_send

            # Always increase this to sync with time_start
            packet_sent += 1

            # Send one more packet to fill discord server's buffer
            if time.time() - packet_loss_timer >= (1 / expected_packet_loss_rate) * 0.02:
                packet_sent -= 1
                packet_loss_timer = time.time()
