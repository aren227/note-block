import discord
import typing

from commands.command import Command

if typing.TYPE_CHECKING:
    from client import NoteblockClient


class SkipCommand(Command):

    def __init__(self, client: 'NoteblockClient'):
        super(SkipCommand, self).__init__(client)

    def get_base_command(self) -> str:
        return "s"

    def get_alias(self):
        pass

    def get_help(self) -> str:
        return ";s : 현재 재생되고 있는 음악을 건너뜁니다."

    async def execute(self, message: discord.Message, args: typing.List[str]):
        if not self.client.guild_has_player(message.guild):
            await message.channel.send("재생 중인 음악이 없습니다.")
            return True

        player = self.client.get_player(message.guild)
        if player.is_playing_music():
            await message.channel.send("**{}**을 건너뜁니다.".format(player.get_current_music().get_title()))
            player.clear_current_music()
        else:
            await message.channel.send("재생 중인 음악이 없습니다.")

        return True
