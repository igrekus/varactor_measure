import itertools

import pyqtgraph as pg

from PyQt5.QtWidgets import QGridLayout, QWidget
from PyQt5.QtCore import Qt

from mytools.plotwidget import PlotWidget


class PrimaryPlotWidget(QWidget):
    main_states = [0, 1, 2, 4, 8, 16, 32, 63]

    params = {
        0: {
            '00': {
                'xlabel': 'F, ГГц',
                'xlim': [],
                'ylabel': 'S21, дБм',
                'ylim': []
            },
            '01': {
                'xlabel': 'F, ГГц',
                'xlim': [],
                'ylabel': 'КСВ вх, дБм',
                'ylim': []
            },
            '10': {
                'xlabel': 'F, ГГц',
                'xlim': [],
                'ylabel': 'КСВ вых, дБм',
                'ylim': []
            },
        },
    }

    def __init__(self, parent=None, result=None):
        super().__init__(parent)

        self._result = result
        self.only_main_states = False

        self._grid = QGridLayout()

        self._plotS21 = PlotWidget(parent=None, toolbar=True)
        self._plotVswrIn = PlotWidget(parent=None, toolbar=True)
        self._plotVswrOut = PlotWidget(parent=None, toolbar=True)

        self._grid.addWidget(self._plotS21, 0, 0)
        self._grid.addWidget(self._plotVswrIn, 0, 1)
        self._grid.addWidget(self._plotVswrOut, 1, 0)

        self._win = pg.GraphicsLayoutWidget(show=True)
        self._win.setBackground('w')
        self._testPlot = self._win.addPlot(row=1, col=0)
        self._label = pg.LabelItem(justify='right')
        self._label.setText('lollabel')
        self._win.addItem(self._label, row=0, col=0)
        self._grid.addWidget(self._win, 1, 1)

        # https://www.learnpyqt.com/tutorials/plotting-pyqtgraph/
        # https://pyqtgraph.readthedocs.io/en/latest/introduction.html#what-is-pyqtgraph
        # matplotlib colors ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd', '#8c564b', '#e377c2', '#7f7f7f', '#bcbd22', '#17becf']
        self._data1 = [30, 32, 34, 32, 33, 31, 29, 32, 35, 45]
        self._data2 = [50, 35, 44, 22, 38, 32, 27, 38, 32, 44]
        self._testPlot.plot(
            [1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
            self._data1,
            pen=pg.mkPen(
                color='#1f77b4',
                width=2,
            ),
            symbol='o',
            symbolSize=5,
            symbolBrush='#1f77b4',
            name='test plot 1'
        )
        self._testPlot.plot(
            [1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
            self._data2,
            pen=pg.mkPen(
                color='#ff7f0e',
                width=2,
            ),
            symbol='o',
            symbolSize=5,
            symbolBrush='#ff7f0e',
            name='test plot 2'
        )
        style = {'color': 'k', 'font-size': '15px'}
        self._testPlot.setLabel('left', 'y-s', **style)
        self._testPlot.setLabel('bottom', 'x-es', **style)

        self._testPlot.setXRange(0, 11, padding=0)
        self._testPlot.setYRange(20, 55, padding=0)

        self._testPlot.addLegend()
        self._testPlot.showGrid(x=True, y=True)

        self._vb = self._testPlot.vb
        self._vLine = pg.InfiniteLine(angle=90, movable=False)
        self._hLine = pg.InfiniteLine(angle=0, movable=False)
        self._testPlot.addItem(self._vLine, ignoreBounds=True)
        self._testPlot.addItem(self._hLine, ignoreBounds=True)
        self._proxy = pg.SignalProxy(self._testPlot.scene().sigMouseMoved, rateLimit=60, slot=self.mouseMoved)

        self.setLayout(self._grid)

        self._init()

    def mouseMoved(self, evt):
        pos = evt[0]
        if self._testPlot.sceneBoundingRect().contains(pos):
            mousePoint = self._vb.mapSceneToView(pos)
            index = int(mousePoint.x())
            if index > 0 and index < len(self._data1):
                self._label.setText("Test plot: <span style='font-size: 12pt'>x=%0.1f,   <span style='color: #1f77b4'>y1=%0.1f</span>,   <span style='color: #ff7f0e'>y2=%0.1f</span>" % (mousePoint.x(),  self._data1[index], self._data2[index]))
            self._vLine.setPos(mousePoint.x())
            self._hLine.setPos(mousePoint.y())

    def _init(self, dev_id=0):

        def setup_plot(plot, pars: dict):
            plot.set_tight_layout(True)
            plot.subplots_adjust(bottom=0.150)
            # plot.set_title(pars['title'])
            plot.set_xlabel(pars['xlabel'], labelpad=-2)
            plot.set_ylabel(pars['ylabel'], labelpad=-2)
            # plot.set_xlim(pars['xlim'][0], pars['xlim'][1])
            # plot.set_ylim(pars['ylim'][0], pars['ylim'][1])
            plot.grid(b=True, which='major', color='0.5', linestyle='-')
            plot.tight_layout()

        setup_plot(self._plotS21, self.params[dev_id]['00'])
        setup_plot(self._plotVswrIn, self.params[dev_id]['01'])
        setup_plot(self._plotVswrOut, self.params[dev_id]['10'])

    def clear(self):
        self._plotS21.clear()
        self._plotVswrIn.clear()
        self._plotVswrOut.clear()

    def plot(self, dev_id=0):
        print('plotting primary stats')
        self.clear()
        self._init(dev_id)

        freqs = self._result.freqs
        s21s = self._result.s21[:1]
        vswr_in = self._result.vswr_in[:1]
        vswr_out = self._result.vswr_out[:1]

        n = len(s21s)

        for xs, ys in zip(itertools.repeat(freqs, n), s21s):
            self._plotS21.plot(xs, ys)

        for xs, ys in zip(itertools.repeat(freqs, n), vswr_in):
            self._plotVswrIn.plot(xs, ys)

        for xs, ys in zip(itertools.repeat(freqs, n), vswr_out):
            self._plotVswrOut.plot(xs, ys)
