import asyncio
import functools

import discord
import typing
import youtube_dl

from ytdl import ytdl
from music.music import Music


class YoutubeMusic(Music):

    def __init__(self, video_id: str, title: str, duration: int):
        super().__init__(title, duration)
        self.video_id = video_id

    def _create_audio_source(self) -> discord.AudioSource:
        processed_info = ytdl.extract_info("https://www.youtube.com/watch?v={}".format(self.video_id), download=False)

        best_url = None
        best_bitrate = 0
        for fmt in processed_info['formats']:
            if 'audio only' in fmt['format'] and best_bitrate < fmt['abr']:
                best_url = fmt['url']
                best_bitrate = fmt['abr']

        print("Load URL =", best_url)
        print("Bitrate =", best_bitrate)

        return discord.FFmpegPCMAudio(
            best_url,
            before_options='-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
        )

    def get_id(self) -> str:
        return "youtube:" + self.video_id
