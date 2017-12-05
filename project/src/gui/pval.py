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
                plot_style = 'bo'
            plot_point = self.ax.plot(x, y, plot_style)
            self.ax.text(x, y, str(self.last_id), color="red", fontsize=12)
            self.fig.canvas.draw()

            self.pvals[self.last_id] = {
                'x': x, 'y': y,
                'plot_point': plot_point,
                'node': nearest_node}
            store.append([self.last_id, x, y, self.last_id, 0.0])
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
            pair_dist[key1] = {}
            for key2 in self.pvals:
                p1 = self.pvals[key1]['node']
                p2 = self.pvals[key2]['node']

                # path = nx.shortest_path(
                    # self.graph, source=p1, target=p2, weight='length')
                path_length = nx.shortest_path_length(
                    self.graph, source=p1, target=p2, weight='length')
                pair_dist[key1][key2] = {'length': path_length}
                                         # 'route': path}

        pprint.pprint(pair_dist)

        threshold = 200
        pairs = {}
        compatibility = nx.Graph()
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
                    compatibility.add_edge(key1, key2, neg_length=-out_of_way)

        print("With out_of_way threshold <", threshold, "m")
        print("Pairs: out of way distance")
        pprint.pprint(pairs)

        matching = nx.algorithms.matching.max_weight_matching(
            compatibility,
            maxcardinality=True,
            weight='neg_length')
        store = self.state.builder.get_object('location_store')

        for i, row in enumerate(store):
            store[i] = store[i][0:3] + [i, 0.0]

        print("Matching")
        pprint.pprint(matching)
        for start, end in matching.items():
            dist = compatibility.get_edge_data(start, end)['neg_length']
            dist = abs(dist)
            store[start] = store[start][0:3] + [end, dist]

        print("-" * 30)

    def pval__alpha_value_changed(self, *args):
        self.pval__refresh()

    def pval__method_changed(self, *args):
        self.pval__refresh()
