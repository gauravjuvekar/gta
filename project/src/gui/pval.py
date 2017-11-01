#!/usr/bin/env python3

from gi.repository import Gtk
from gi.repository import Gdk
import pickle
import logging
logger = logging.getLogger(__name__)

import osmnx

import gui
import state


class PvalHandlers(gui.handlers.BaseHandlers):
    def __init__(self, *args, **kwargs):
        super(PvalHandlers, self).__init__(*args, **kwargs)
        self.last_id = 0
        self.pvals = dict()

    def pval__add(self, *args):
        store = self.state.builder.get_object('location_store')
        lat = self.state.builder.get_object('lat_entry')
        lon = self.state.builder.get_object('lon_entry')

        try:
            lat_val, lon_val = float(lat.get_text()), float(lon.get_text())
        except ValueError:
            pass
        else:
            nearest_node = osmnx.get_nearest_node(self.graph,
                                                  (lat_val, lon_val))
            x = self.graph.nodes[nearest_node]['x']
            y = self.graph.nodes[nearest_node]['y']
            if self.last_id == 0:
                plot_style = 'ro'
            else:
                plot_style = 'r+'
            plot_point = self.ax.plot(x, y, plot_style)
            self.fig.canvas.draw()

            self.pvals[self.last_id] = {
                'x': x, 'y': y,
                'plot_point': plot_point}
            store.append([x, y, self.last_id])
            self.last_id += 1
            lat.set_text('')
            lon.set_text('')
            self.state.unsaved_changes = True
            self.pval__refresh()

    def pval__key_released(self, widget, event, *args):
        keyname = Gdk.keyval_name(event.keyval)
        if keyname == 'Delete':
            view = self.state.builder.get_object('location_view')
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
