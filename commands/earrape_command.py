import discord
import typing

from commands.command import Command

if typing.TYPE_CHECKING:
    from client import NoteblockClient


class EarrapeCommand(Command):

    def __init__(self, client: 'NoteblockClient'):
        super().__init__(client)

    def get_base_command(self) -> str:
        return "e"

    def get_alias(self):
        pass

    def get_help(self) -> str:
        return ";e [on/off] : 시도하지 마세요."

    async def execute(self, message: discord.Message, args: typing.List[str]):
        if len(args) != 1 or args[0] not in ('on', 'off'):
            return False

        if not self.client.guild_has_player(message.guild):
            await message.channel.send("재생 중인 음악이 없습니다.")
            return True

        player = self.client.get_player(message.guild)
        if args[0] == 'on':
            player.get_mixer().set_earrape(True)
            await message.channel.send("E A R R A P E   **O N**")
        else:
            player.get_mixer().set_earrape(False)
            await message.channel.send("E A R R A P E   **O F F**")
        return True
