#!/usr/bin/env python3


class RuntimeState(object):
    def __init__(self, state=None, builder=None, filename=None):
        super(RuntimeState, self).__init__()
        self.builder = builder
        self.filename = filename
        self.unsaved_changes = False
