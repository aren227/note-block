import discord
import typing

from commands.command import Command

if typing.TYPE_CHECKING:
    from client import NoteblockClient


class SoundEmojiCommand(Command):

    def __init__(self, client: 'NoteblockClient'):
        super().__init__(client)

    def get_base_command(self) -> str:
        return "soundemoji"

    def get_alias(self):
        return "se"

    def get_help(self) -> str:
        return ";**s**ound**e**moji : 소리가 등록된 이모지 목록을 출력합니다."

    async def execute(self, message: discord.Message, args: typing.List[str]):
        emojis = self.client.sound_emoji.get_supported_emojis(message.guild)
        msg = "총 {}개의 이모지에 소리가 등록되었습니다.\n".format(len(emojis))
        for emoji_id in emojis:
            msg += self.client.get_emoji(emoji_id) + " "
        await message.channel.send(msg)
