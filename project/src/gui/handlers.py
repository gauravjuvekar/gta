#!/usr/bin/env python3

import logging
logger = logging.getLogger(__name__)

import gui


class BaseHandlers(object):
    def __init__(self, app, runtime_state):
        super(BaseHandlers, self).__init__()
        self.app = app
        self.state = runtime_state

    def close(self, *args):
        if gui.file_save.save_if_unsaved_changes(self.state):
            self.app.window.destroy()
