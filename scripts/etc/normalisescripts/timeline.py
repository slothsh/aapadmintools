#!/usr/bin/env python3

import random
from timecode import Timecode, TimecodeError

FPS_DEFAULT = 25


def __event_default_read__(data):
    return data


class TimelineEvent:
    def __init__(self,
                 data,
                 fps=FPS_DEFAULT,
                 read=__event_default_read__,
                 tcin=Timecode(FPS_DEFAULT, start_seconds=1),
                 tcout=Timecode(FPS_DEFAULT, start_seconds=2)):

        if 'id' in data:
            self._id = data['id']
        else:
            self._id = hash(random.random())

        self._fps = fps
        self._tcin = tcin
        self._tcout = tcout
        self._data = data
        self._read = read

    def duration(self):
        lo = min(self._tcin, self._tcout)
        hi = max(self._tcin, self._tcout)
        return hi - lo

    def __repr__(self):
        return str(self)

    def __str__(self):
        return f'{self._id}\t{self._tcin}\t{self._tcout}\t{self.duration()}\t{self._read(self._data)}'

    def __eq__(self, rhs):
        return self.duration() == rhs.duration()

    def __ne__(self, rhs):
        return not self == rhs

    _id = ''
    _fps = FPS_DEFAULT
    _tcin = Timecode(FPS_DEFAULT, start_seconds=1)
    _tcout = Timecode(FPS_DEFAULT, start_seconds=2)
    _data = []
    _read = __event_default_read__


class TimelineEntity:
    def __init__(self, events):
        self._events = events
    _events = []


class Timeline:
    def __init__(self, entities, fps=25):
        self._fps = fps
        self._entities = entities

    _fps = FPS_DEFAULT
    _entities = []
