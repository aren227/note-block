import asyncio
import typing

from music import Music

if typing.TYPE_CHECKING:
    from player import Player


class MusicQueue:

    def __init__(self, player: 'Player'):
        self.player = player

        self.queue: typing.List[Music] = []

    def is_empty(self) -> bool:
        return len(self.queue) == 0

    async def add_music(self, music: Music):
        self.queue.append(music)

    def next_music(self) -> typing.Optional[Music]:
        if self.is_empty():
            return None
        return self.queue.pop(0)

    def get_remaining_time(self) -> int:
        total_time = 0
        for music in self.queue:
            total_time += music.get_duration()
        return total_time

    def get_all_music(self) -> typing.List[Music]:
        return self.queue
