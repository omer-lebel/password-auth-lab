import time

class Timer:
    def __init__(self):
        self.start = time.time()

    def elapsed(self):
        return time.time() - self.start

    def expired(self, max_seconds):
        return self.elapsed() >= max_seconds
