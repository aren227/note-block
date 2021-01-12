import asyncio

import discord
import typing

import youtube_dl

from commands.command import Command
from commands.earrape_command import EarrapeCommand
from commands.ping_command import PingCommand
from commands.play_command import PlayCommand
from commands.queue_command import QueueCommand
from player import Player
from commands.skip_command import SkipCommand


class NoteblockClient(discord.Client):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.ytdl = youtube_dl.YoutubeDL({
            'format': 'bestaudio/best',
            'extractaudio': True,
            'audioformat': 'mp3',
            'outtmpl': '%(extractor)s-%(id)s-%(title)s.%(ext)s',
            'restrictfilenames': True,
            'noplaylist': True,
            'nocheckcertificate': True,
            'ignoreerrors': False,
            'logtostderr': False,
            'quiet': True,
            'no_warnings': True,
            'default_search': 'auto',
            'source_address': '0.0.0.0',
        })

        self.players: typing.Dict[discord.Guild, Player] = {}

        self.commands: typing.Dict[str, Command] = {}

        self.register_command(PlayCommand(self, self.ytdl))
        self.register_command(SkipCommand(self))
        self.register_command(EarrapeCommand(self))
        self.register_command(QueueCommand(self))
        self.register_command(PingCommand(self))

        self.player_task = self.loop.create_task(self.player_task())

    def guild_has_player(self, guild: discord.Guild) -> bool:
        return guild in self.players

    def create_player(self, guild: discord.Guild):
        self.players[guild] = Player(guild, self.loop)

    def get_player(self, guild: discord.Guild) -> Player:
        return self.players[guild]

    async def try_to_connect_player(self, guild: discord.Guild, member: discord.Member, channel: discord.TextChannel):
        if not self.guild_has_player(guild):
            self.create_player(guild)

        player = self.get_player(guild)
        if not player.is_connected():
            if member.voice is None or member.voice.channel is None:
                await channel.send("먼저 음성 채널에 접속해주세요.")
                return
            await player.connect(member.voice.channel)

    def register_command(self, command: Command):
        self.commands[command.get_base_command()] = command

    async def on_message(self, message: discord.Message):
        if message.author == self.user:
            return

        if message.content.startswith(';'):
            spl = message.content.split(' ')
            if len(spl) == 0 or len(spl[0]) <= 1:
                return
            base = spl[0][1:]
            if base in self.commands:
                success = await self.commands[base].execute(message, spl[1:])
                if not success:
                    await message.channel.send(self.commands[base].get_help())

        for key in self.commands:
            await self.commands[key].on_message(message)

    async def player_task(self):
        while not self.is_closed():
            features = [asyncio.ensure_future(self.players[key].try_to_play_music()) for key in self.players]
            await asyncio.gather(*features)
            await asyncio.sleep(0.5)
