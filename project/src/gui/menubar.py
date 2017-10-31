#!/usr/bin/env python3

from gi.repository import Gtk
import pickle
import logging
logger = logging.getLogger(__name__)

import gui
import state


class MenubarHandlers(gui.handlers.BaseHandlers):
    def menubar__file__new(self, *args):
        if not gui.file_save.save_if_unsaved_changes(self.state):
            return
        else:
            self.state.filename = None
            self.state.state = state.State()
            self.state.unsaved_changes = False
            self.notebook__refresh()

    def menubar__file__open(self, *args):
        if not gui.file_save.save_if_unsaved_changes(self.state):
            return
        else:
            dialog = Gtk.FileChooserDialog(
                "Open file",
                parent=self.state.builder.get_object("main_window"),
                action=Gtk.FileChooserAction.OPEN,
                buttons=(Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL,
                         Gtk.STOCK_OPEN, Gtk.ResponseType.ACCEPT))
            res = dialog.run()
            if res == Gtk.ResponseType.ACCEPT:
                file_name = dialog.get_filename()
            elif res in (Gtk.ResponseType.CANCEL,
                         Gtk.ResponseType.DELETE_EVENT):
                return
            else:
                raise RuntimeError()
            logger.debug("Opening file %s", file_name)
            dialog.destroy()
            with open(file_name, 'rb') as f:
                try:
                    # TODO
                    self.state.state = pickle.load(f)
                except pickle.UnpicklingError:
                    dialog = Gtk.MessageDialog(
                        "Cannot open that file",
                        parent=(self.state.
                                builder.get_object("main_window")),
                        flags=(Gtk.DialogFlags.MODAL |
                               Gtk.DialogFlags.DESTROY_WITH_PARENT),
                        message_type=Gtk.MessageType.ERROR,
                        buttons=(Gtk.STOCK_CLOSE, Gtk.ResponseType.CLOSE),
                        text="Error reading file {}".format(file_name),
                        title="Cannot open file")
                    dialog.run()
                    dialog.destroy()
                else:
                    self.state.filename = file_name
                    self.pval__refresh()

    def menubar__file__save(self, *args):
        gui.file_save.save(self.state)

    def menubar__file__saveas(self, *args):
        old_name = self.state.filename
        self.state.filename = None
        gui.file_save.save(self.state)
        self.state.filename = old_name

    def menubar__help_about(self, *args):
        dialog = self.state.builder.get_object("about_dialog")
        dialog.run()
        dialog.hide()
