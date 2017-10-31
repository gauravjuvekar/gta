#!/usr/bin/env python3

import logging
import sys
log = logging.getLogger(__name__)

import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, GObject, Gio

import gui
import state


class Handlers(
        gui.plot.PlotHandler,
        gui.menubar.MenubarHandlers,
        gui.pval.PvalHandlers,
        gui.handlers.BaseHandlers):
    pass


class Pval(Gtk.Application):
    def __init__(
            self,
            application_id="com.pval.pval",
            flags=Gio.ApplicationFlags.FLAGS_NONE,
            glade_file="gui/ui.glade"):
        Gtk.Application.__init__(
            self,
            application_id=application_id,
            flags=flags)
        try:
            self.builder = Gtk.Builder.new_from_file(glade_file)
            self.handlers = Handlers(
                app=self,
                runtime_state=state.RuntimeState(builder=self.builder))
            self.builder.connect_signals(self.handlers)
        except GObject.GError:
            log.critical("Error reading glade file %s", glade_file)
            raise

    def do_activate(self):
        self.window = self.builder.get_object("AppWin")
        self.window.set_application(self)
        self.window.connect('destroy', self.on_quit)
        self.window.show_all()
        self.add_window(self.window)

    def do_startup(self):
        Gtk.Application.do_startup(self)

    def do_shutdown(self):
        Gtk.Application.do_shutdown(self)

    def on_quit(self, *args):
        self.quit()


def main():
    app = Pval()
    sys.exit(app.run(sys.argv))


if __name__ == "__main__":
    log_level = logging.WARNING
    format_str = "{levelname:8s} {asctime} {name}"
    format_str += ": {message}"

    logging.basicConfig(
        level=log_level,
        style='{',
        format=format_str)
    main()
