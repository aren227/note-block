import asyncio
import re

import discord
import typing

from commands.clock_command import ClockCommand
from commands.command import Command
from commands.earrape_command import EarrapeCommand
from commands.help_command import HelpCommand
from commands.ping_command import PingCommand
from commands.play_command import PlayCommand
from commands.play_list_command import PlayListCommand
from commands.play_playlist_command import PlayPlaylistCommand
from commands.queue_command import QueueCommand
from commands.radio_command import RadioCommand
from database import Database
from music.sound_file import SoundFile
from player.player import Player
from commands.skip_command import SkipCommand
from playlist_manager import PlayListManager
from selector import Selector
from sound_emoji import SoundEmoji


class NoteblockClient(discord.Client):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.players: typing.Dict[discord.Guild, Player] = {}

        self.commands: typing.Dict[str, Command] = {}

        self.register_command(PlayCommand(self))
        self.register_command(SkipCommand(self))
        self.register_command(EarrapeCommand(self))
        self.register_command(QueueCommand(self))
        self.register_command(PingCommand(self))
        self.register_command(HelpCommand(self))
        self.register_command(PlayListCommand(self))
        self.register_command(PlayPlaylistCommand(self))
        self.register_command(RadioCommand(self))
        self.register_command(ClockCommand(self))

        self.database = Database(self)

        self.selector = Selector(self)

        self.playlist_manager = PlayListManager(self, self.database)

        self.sound_emoji = SoundEmoji()

        self.player_task = self.loop.create_task(self.player_task())

    def guild_has_player(self, guild: discord.Guild) -> bool:
        return guild in self.players

    def create_player(self, guild: discord.Guild):
        self.players[guild] = Player(self, guild, self.loop)

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

    def get_commands(self) -> typing.List[Command]:
        return list(self.commands.values())

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
            return

        if len(message.attachments) > 0:
            emoji_id = self.sound_emoji.is_fully_emoji(message.content)
            if emoji_id is not None:
                await self.sound_emoji.register(message.guild, emoji_id, message.attachments[0])
                await message.channel.send("이모지 {}에 대한 소리가 등록되었습니다.".format(message.content))
                return

        if self.guild_has_player(message.guild):
            player = self.get_player(message.guild)
            emojis = self.sound_emoji.get_distinct_emojis(message.content)[:5]
            for emoji_id in emojis:
                path = self.sound_emoji.get_audio_file(message.guild, emoji_id)
                if path is not None:
                    sfx = SoundFile(path)
                    sfx.start()
                    player.get_mixer().add_audio_source("SFX", sfx)

        await self.selector.on_message(message)

    async def player_task(self):
        while not self.is_closed():
            for key in self.players:
                self.players[key].process_scheduled_audio()
                await self.players[key].try_reconnect()

            await asyncio.sleep(0.25)
