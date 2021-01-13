import typing


class MovingAverage:

    def __init__(self, size: int):
        if size < 1:
            raise ValueError("size must be greater than zero.")
        self.size: int = size

        self.queue: typing.List[typing.Optional[float]] = [None] * size
        self.queue_index: int = 0
        self.queue_size: int = 0

        self.total_sum: float = 0

    def push(self, data: float):
        if self.queue[self.queue_index] is not None:
            self.total_sum -= self.queue[self.queue_index]

        self.total_sum += data

        self.queue[self.queue_index] = data
        self.queue_index = (self.queue_index + 1) % self.size
        self.queue_size = min(self.queue_size + 1, self.size)

    def get_average(self) -> float:
        if self.queue_size == 0:
            return 0

        return self.total_sum / self.queue_size
