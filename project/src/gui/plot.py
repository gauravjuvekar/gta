#!/usr/bin/env python3

import logging
logger = logging.getLogger(__name__)

import gui

from gi.repository import Gtk
import matplotlib
import matplotlib.cm
import matplotlib.figure
import numpy as np

#Possibly this rendering backend is broken currently
#from matplotlib.backends.backend_gtk3agg import FigureCanvasGTK3Agg as FigureCanvas
from matplotlib.backends.backend_gtk3cairo import FigureCanvasGTK3Cairo as FigureCanvas
from matplotlib.backends.backend_gtk3 import NavigationToolbar2GTK3 as NavigationToolbar



import pickle
import networkx
import osmnx


class PlotHandler(gui.handlers.BaseHandlers):
    def __init__(self, *args, **kwargs):
        super(PlotHandler, self).__init__(*args, **kwargs)

        with open('osmnx_pune_1km', 'rb') as f:
            self.graph = pickle.load(f)

        builder = self.state.builder
        sw = builder.get_object('GraphArea')
        nav_box_holder = builder.get_object('plot_box')

        fig, ax = osmnx.plot_graph(self.graph, show=False)

        # fig = matplotlib.figure.Figure(figsize=(5, 5), dpi=100)
        # ax = fig.add_subplot(111, projection='polar')



        # N = 20
        # theta = np.linspace(0.0, 2 * np.pi, N, endpoint=False)
        # radii = 10 * np.random.rand(N)
        # width = np.pi / 4 * np.random.rand(N)

        # bars = ax.bar(theta, radii, width=width, bottom=0.0)

        # for r, bar in zip(radii, bars):
            # bar.set_facecolor(matplotlib.cm.jet(r / 10.))
            # bar.set_alpha(0.5)

        ax.plot()

        canvas = FigureCanvas(fig)
        window = builder.get_object('AppWin')
        toolbar = NavigationToolbar(canvas, window)
        nav_box_holder.pack_start(toolbar, False, True, 1)
        sw.add_with_viewport(canvas)
