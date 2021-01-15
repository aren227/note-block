import asyncio
import random
import traceback
from datetime import datetime, timedelta
from math import ceil

import discord
import typing

from bson import ObjectId

from music.clock_sfx import ClockSfx
from play_list import PlayList
from player.clock_alert_scheduler import ClockAlertScheduler
from player.mixer import Mixer
from music.music import Music
from music_queue import MusicQueue
from player.scheduled_audio import ScheduledAudio

if typing.TYPE_CHECKING:
    from client import NoteblockClient


class Player:

    def __init__(self, client: 'NoteblockClient', guild: discord.Guild, loop: asyncio.AbstractEventLoop):
        self.client = client
        self.guild: discord.Guild = guild
        self.loop: asyncio.AbstractEventLoop = loop

        self.current_music: typing.Optional[Music] = None
        self.music_queue: MusicQueue = MusicQueue(self)

        self.mixer: typing.Optional[Mixer] = None

        self.voice_client: typing.Optional[discord.VoiceClient] = None

        self.radio_mode: typing.Optional[ObjectId] = None

        self.scheduled_audio: typing.List[ScheduledAudio] = []

    def is_connected(self) -> bool:
        if self.voice_client is None:
            return False
        return self.voice_client.is_connected()

    async def connect(self, voice_channel: discord.VoiceChannel):
        if self.guild != voice_channel.guild:
            raise ValueError("Can't connect to voice channel of different guild!")
        self.voice_client = await voice_channel.connect()

        # Inject custom encoder
        encoder = discord.opus.Encoder()
        encoder.set_bitrate(96)
        encoder.set_fec(False)
        encoder.set_expected_packet_loss_percent(0)
        encoder.set_bandwidth('full')
        encoder.set_signal_type('music')

        self.voice_client.encoder = encoder

        self.mixer = Mixer(self)
        self.mixer.start()

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
            total_time += self.current_music.get_time_left()
        total_time += self.music_queue.get_remaining_time()
        return total_time

    def play_next_music(self):
        if not self.is_connected():
            return

        self.current_music = self.music_queue.next_music()

        if self.current_music is not None:
            try:
                self.current_music.start()
                self.mixer.add_audio_source("MUSIC", self.current_music)
            except:
                traceback.print_exc()
                # TODO: Handle exception properly
        else:
            self.clear_current_music()

            if self.is_radio_mode():
                self.fill_queue_with_playlist(self.radio_mode)

                if len(self.music_queue.get_all_music()) > 0:
                    self.play_next_music()

    def get_mixer(self) -> typing.Optional[Mixer]:
        return self.mixer

    def is_radio_mode(self) -> bool:
        return self.radio_mode is not None

    def get_radio_playlist_title(self) -> typing.Optional[str]:
        if not self.is_radio_mode():
            return None

        playlist = self.client.database.get_playlist(self.guild, self.radio_mode)
        if playlist is None:
            return None

        return playlist.get_title()

    def fill_queue_with_playlist(self, playlist_id: ObjectId, shuffle: bool = True):
        playlist = self.client.database.get_playlist(self.guild, playlist_id)
        if playlist is None:
            self.set_radio_mode(None)

        music = list(playlist.get_all_music())
        if shuffle:
            random.shuffle(music)

        for m in music:
            self.music_queue.add_music(m)

    def set_radio_mode(self, playlist_id: typing.Optional[ObjectId]):
        self.radio_mode = playlist_id

        self.clear_current_music()
        self.music_queue.clear()

        if playlist_id is not None:
            self.fill_queue_with_playlist(playlist_id)
            self.play_next_music()

    def add_scheduled_audio(self, scheduled_audio: ScheduledAudio):
        self.scheduled_audio.append(scheduled_audio)

    def process_scheduled_audio(self):
        now = datetime.now()
        for i in range(len(self.scheduled_audio) - 1, -1, -1):
            if now >= self.scheduled_audio[i].start_time:
                self.scheduled_audio[i].audio.start()
                self.mixer.add_audio_source('SFX', self.scheduled_audio[i].audio)

                if not self.scheduled_audio[i].is_repeating():
                    self.scheduled_audio.pop(i)

    def add_next_clock_alert(self):
        self.add_scheduled_audio(ClockAlertScheduler())

    def set_clock_alert(self, alert: bool):
        for i in range(len(self.scheduled_audio) - 1, -1, -1):
            if isinstance(self.scheduled_audio[i], ClockAlertScheduler):
                self.scheduled_audio.pop(i)

        if alert:
            self.add_next_clock_alert()
