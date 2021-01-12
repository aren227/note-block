import asyncio
import traceback

import discord
import typing

from player.mixer import Mixer
from music.music import Music
from music_queue import MusicQueue


class Player:

    def __init__(self, guild: discord.Guild, loop: asyncio.AbstractEventLoop):
        self.guild: discord.Guild = guild
        self.loop: asyncio.AbstractEventLoop = loop

        self.current_music: typing.Optional[Music] = None
        self.music_queue: MusicQueue = MusicQueue(self)

        self.mixer: Mixer = Mixer(self)

        self.voice_client: typing.Optional[discord.VoiceClient] = None

    def is_connected(self) -> bool:
        if self.voice_client is None:
            return False
        return self.voice_client.is_connected()

    async def connect(self, voice_channel: discord.VoiceChannel):
        if self.guild != voice_channel.guild:
            raise ValueError("Can't connect to voice channel of different guild!")
        self.voice_client = await voice_channel.connect()
        self.voice_client.play(self.mixer)

        # Inject custom encoder
        encoder = discord.opus.Encoder()
        encoder.set_bitrate(96)
        encoder.set_fec(False)
        encoder.set_expected_packet_loss_percent(0)
        encoder.set_bandwidth('full')
        encoder.set_signal_type('music')

        self.voice_client.encoder = encoder

    async def disconnect(self):
        await self.voice_client.disconnect()

    def get_music_queue(self) -> MusicQueue:
        return self.music_queue

    def is_playing_music(self) -> bool:
        return self.is_connected() and self.current_music is not None

    def get_current_music(self):
        if not self.is_playing_music():
            return None
        return self.current_music

    def clear_current_music(self):
        self.current_music = None
        self.mixer.clear_audio_sources("MUSIC")

    def get_total_time_left(self) -> int:
        total_time = 0
        if self.current_music is not None:
            total_time += self.current_music.get_left_time()
        total_time += self.music_queue.get_remaining_time()
        return total_time

    async def try_to_play_music(self):
        if not self.is_connected():
            return

        if self.is_playing_music():
            return

        music = self.music_queue.next_music()
        if music is None:
            return

        self.current_music = music

        print("Play", self.current_music.get_title())

        try:
            audio_source = await music.create_audio_source(self.loop)

            self.mixer.add_audio_source("MUSIC", audio_source)
        except:
            traceback.print_exc()
            # TODO: Handle exception properly

    def get_mixer(self):
        return self.mixer
