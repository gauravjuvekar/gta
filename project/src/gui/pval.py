#!/usr/bin/env python3

from gi.repository import Gtk
from gi.repository import Gdk
import pickle
import logging
logger = logging.getLogger(__name__)

import gui
import state


class PvalHandlers(gui.handlers.BaseHandlers):
    def pval__add(self, *args):
        store = self.state.builder.get_object('pval_store')
        entry = self.state.builder.get_object('pval_entry')
        text = entry.get_text()
        try:
            values = [float(x.strip()) for x in text.split(',')]
        except ValueError:
            pass
        else:
            for val in values:
                store.append([val, 0])
            entry.set_text('')
            self.state.unsaved_changes = True
            self.pval__refresh()

    def pval__key_released(self, widget, event, *args):
        keyname = Gdk.keyval_name(event.keyval)
        if keyname == 'Delete':
            view = self.state.builder.get_object('pval_view')
            selection = view.get_selection()
            model, paths = selection.get_selected_rows()
            for path in reversed(paths):
                itr = model.get_iter(path)
                model.remove(itr)

    def pval__refresh(self, *args):
        print("Refreshed view")
        pass

    def pval__alpha_value_changed(self, *args):
        self.pval__refresh()

    def pval__method_changed(self, *args):
        self.pval__refresh()
