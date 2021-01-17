import os
import re

import discord
import typing


emoji_regex = re.compile(r'<:\w+:(\d+)>')


class SoundEmoji:

    def __init__(self):
        pass

    async def register(self, guild: discord.Guild, emoji_id: int, audio_file: discord.Attachment):
        path = self.get_folder_path(guild, emoji_id)
        os.makedirs(path, exist_ok=True)

        for file in os.listdir(path):
            os.remove(path + "/" + file)

        await audio_file.save(open(path + "/" + audio_file.filename, 'wb'))

    def get_folder_path(self, guild: discord.Guild, emoji_id: int):
        return './emoji_sounds/{}/{}'.format(guild.id, emoji_id)

    def get_audio_file(self, guild: discord.Guild, emoji_id: int) -> typing.Optional[str]:
        path = self.get_folder_path(guild, emoji_id)
        if not os.path.exists(path):
            return None
        files = os.listdir(path)
        print(files)
        if len(files) == 0:
            return None
        return path + "/" + files[0]

    def is_fully_emoji(self, content: str) -> typing.Optional[int]:
        match = emoji_regex.fullmatch(content)
        if match:
            return int(match.group(1))
        return None

    def get_distinct_emojis(self, content: str) -> typing.List[int]:
        results = []
        for match in emoji_regex.finditer(content):
            results.append(int(match.group(1)))
        return list(set(results))
