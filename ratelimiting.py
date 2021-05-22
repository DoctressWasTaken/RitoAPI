from datetime import datetime, timedelta


class LimitBlocked(Exception):
    """Exception triggered by a broken ratelimit."""

    def __init__(self, header):
        self.header = header


class Limit:

    def __init__(self, max, duration):
        self.duration = int(duration)
        self.start = datetime.now()
        self.end = self.start - timedelta(seconds=2 * self.duration)  # Init with already timedout bucket
        self.max = int(max)
        self.count = 0

    async def requested(self):
        now = datetime.now()
        if now > self.end:
            print("Recreating bucket. Old bucket had %s/%s" % (self.count, self.max))
            self.start = now
            self.end = self.start + timedelta(seconds=self.duration)
            self.count = 0
        self.count += 1
        if self.count > self.max:
            raise LimitBlocked(header=["%s:%s" % (self.max, self.duration), "%s:%s" % (self.count, self.duration)])
        return ["%s:%s" % (self.max, self.duration), "%s:%s" % (self.count, self.duration)]
