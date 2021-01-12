import discord
import numpy as np
import typing

from player.layer import Layer

if typing.TYPE_CHECKING:
    from player import Player


class Mixer(discord.AudioSource):

    def __init__(self, player: 'Player'):
        self.player = player

        self.layers: typing.Dict[str, Layer] = {}
        self.earrape: bool = False

        """Add default layers"""
        self.add_layer(Layer(self, "MUSIC", 1))
        self.add_layer(Layer(self, "EMOJI", 5))

    def read(self):
        # st = time.time()

        buf = np.zeros(960 * 2, dtype=np.int)
        for key in self.layers:
            buf = self.layers[key].read_buffer(buf)

        if self.earrape:
            buf *= 1200

        # Volume 25%
        final_buf = np.clip(buf // 4, -32768, 32767).astype(dtype='<i2').tobytes()
        """elapsed = int((time.time() - st) * 1000)
        if elapsed > 0:
            print(elapsed, "ms")"""
        return final_buf

    def is_opus(self):
        return False

    def add_layer(self, layer: Layer):
        if layer.get_name() in self.layers:
            raise ValueError("Same name of layer already exists.")

        self.layers[layer.get_name()] = layer

    def add_audio_source(self, layer_name: str, audio_source: discord.AudioSource):
        if layer_name not in self.layers:
            raise ValueError("Layer {} not exists.".format(layer_name))

        self.layers[layer_name].add_audio_source(audio_source)

    def clear_audio_sources(self, layer_name: str):
        if layer_name not in self.layers:
            raise ValueError("Layer {} not exists.".format(layer_name))

        self.layers[layer_name].clear_audio_sources()

    def audio_source_finished(self, layer: Layer, audio_source: discord.AudioSource):
        if layer.get_name() == "MUSIC":
            self.player.clear_current_music()

    def is_earraped(self):
        return self.earrape

    def set_earrape(self, earrape):
        self.earrape = earrape
