import asyncio
import functools

import discord
import typing
import youtube_dl

import music


class YoutubeMusic(music.Music):

    def __init__(self, ytdl: youtube_dl.YoutubeDL, url: str, title: str, duration: int):
        super(YoutubeMusic, self).__init__(title, duration)
        self.ytdl = ytdl
        self.url = url

    async def create_audio_source(self, loop: asyncio.AbstractEventLoop) -> typing.Optional[discord.AudioSource]:
        partial = functools.partial(self.ytdl.extract_info, self.url, download=False)
        processed_info = await loop.run_in_executor(None, partial)

        best_url = None
        best_bitrate = 0
        for fmt in processed_info['formats']:
            if 'audio only' in fmt['format'] and best_bitrate < fmt['abr'] <= 96000:
                best_url = fmt['url']
                best_bitrate = fmt['abr']

        print("Load URL =", best_url)
        print("Bitrate =", best_bitrate)

        return music.MusicAudioSource(
            self,
            discord.FFmpegPCMAudio(
                best_url,
                before_options='-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
            )
        )
