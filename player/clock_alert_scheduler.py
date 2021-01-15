from datetime import datetime, timedelta
from math import ceil

import discord

from music.clock_sfx import ClockSfx, get_delay
from player.scheduled_audio import ScheduledAudio


def get_next_alert_time() -> datetime:
    now = datetime.now()
    seconds = now.minute * 60 + now.second + now.microsecond * 1e-6
    delta = ceil(seconds / 3600) * 3600 - get_delay() - seconds
    if delta < 0:
        delta += 3600
    return now + timedelta(seconds=delta)


class ClockAlertScheduler(ScheduledAudio):

    def __init__(self):
        super().__init__(
            get_next_alert_time(),
            ClockSfx()
        )

    def is_repeating(self) -> bool:
        self.start_time = get_next_alert_time()
        self.audio = ClockSfx()
        return True
