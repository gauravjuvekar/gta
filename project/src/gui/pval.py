#!/usr/bin/env python3

from gi.repository import Gtk
from gi.repository import Gdk
import pickle
import logging
logger = logging.getLogger(__name__)

import osmnx
import networkx as nx

import gui
import state
import pprint


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
                'plot_point': plot_point,
                'node': nearest_node}
            store.append([self.last_id, x, y])
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
                print(path, itr)
                pval_id = model.get_value(itr, 0)
                print("removing", pval_id)
                pval = self.pvals[pval_id]
                # import pdb
                # pdb.set_trace()
                pval['plot_point'][0].remove()
                del self.pvals[pval_id]
                # self.ax.remove()
                model.remove(itr)
            print("Redrawing canvas", pval_id)
            self.fig.canvas.draw()

    def pval__refresh(self, *args):
        print("Refreshed view")
        pair_dist = {}
        for key1 in self.pvals:
            pair_dist[key1] = {k
            for key2 in self.pvals:
                p1 = self.pvals[key1]['node']
                p2 = self.pvals[key2]['node']

                path = nx.shortest_path(
                    self.graph, source=p1, target=p2, weight='length')
                path_length = nx.shortest_path_length(
                    self.graph, source=p1, target=p2, weight='length')
                pair_dist[key1][key2] = {'length': path_length}
                                         # 'route': path}

        pprint.pprint(pair_dist)

        threshold = 100
        pairs = {}
        for key1 in pair_dist:
            if key1 == 0:
                continue
            direct = pair_dist[key1][0]['length']
            for key2 in pair_dist[key1]:
                if key2 == 0:
                    continue
                if key1 == key2:
                    continue
                combined = (pair_dist[key1][key2]['length'] +
                            pair_dist[key2][0]['length'])
                out_of_way = combined - direct
                if out_of_way < threshold:
                    pairs[(key1, key2)] = out_of_way

        print("with out_of_way threshold < 100m")
        print("Matchings: out of way distance")
        pprint.pprint(pairs)

    def pval__alpha_value_changed(self, *args):
        self.pval__refresh()

    def pval__method_changed(self, *args):
        self.pval__refresh()
