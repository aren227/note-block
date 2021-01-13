import asyncio
import functools

import discord
import typing
import youtube_dl

from music.music import Music


class YoutubeMusic(Music):

    def __init__(self, ytdl: youtube_dl.YoutubeDL, url: str, title: str, duration: int):
        super().__init__(title, duration)
        self.ytdl = ytdl
        self.url = url

    def _create_audio_source(self) -> discord.AudioSource:
        processed_info = self.ytdl.extract_info(self.url, download=False)

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
