import time
from collections import deque


class RateLimiter:

    def __init__(self, limit, window):

        self.limit = limit
        self.window = window

        self.requests = deque()

    def allow(self):

        now = time.time()

        while self.requests and (
            now - self.requests[0]
        ) > self.window:

            self.requests.popleft()

        if len(self.requests) >= self.limit:
            return False

        self.requests.append(now)

        return True