import sys
import numpy as np
from PyQt5.QtWidgets import QApplication, QMainWindow, QSizePolicy
from windows.GraphDisplay import Ui_MainWindow

from SignalProcesing import Math, Function, Data3d
from NewSignal import NewFunctWindow
from stftWindow import stftFunctWindow
from cwtWindow import cwtFunctWindow

from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
from matplotlib.figure import Figure
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from matplotlib import cm

class AppWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.show()

        self.addToolBar(NavigationToolbar(self.ui.Display.canvas, self))
        self.function = None
        self.temp3d = None
        self.ui.DDDButton.hide()

        self.ui.newFunc.triggered.connect(self.new_function)
        self.ui.TimeButton.clicked.connect(lambda: self.call_Math("time"))
        self.ui.FreqButton.clicked.connect(lambda: self.call_Math("freq"))
        self.ui.STFTButton.clicked.connect(lambda: self.call_Math("stft"))
        self.ui.CWTButton.clicked.connect(lambda: self.call_Math("cwt"))
        self.ui.DDDButton.clicked.connect(self.plot3D_extra)

    def new_function(self):
        new_window = NewFunctWindow()
        if new_window.exec_():
            self.function = new_window.function

    def plot(self, x, y):
        self.ui.Display.canvas.ax.clear()
        self.ui.Display.canvas.ax.plot(x, y)
        self.ui.Display.canvas.draw()
        self.ui.DDDButton.hide()

    def plot3D(self, *args):
        self.ui.Display.canvas.ax.clear()
        self.ui.Display.canvas.ax.pcolormesh(*args)
        self.ui.Display.canvas.draw()
        self.ui.DDDButton.show()

    def call_Math(self, operation):
        if self.function is None:
            return
        if operation == "time":
            x, y = Math.time_domain(self.function)
            self.plot(x,y)
        elif operation == "freq":
            cut = self.ui.CutAt0.isChecked()
            x, y = Math.frequency_domain(self.function, cut)
            self.plot(x,y)
        elif operation == "stft":
            new_window = stftFunctWindow()
            if new_window.exec_():
                window = new_window.window
                persek = new_window.persek
                overlap = new_window.overlap
                _nfft = new_window.nfft
            try:
                x, y, z = Math.stft(self.function, window, persek, overlap, _nfft)
                self.temp3d = Data3d(x,y,z,'time','frequency', 'Amplitude')
                self.plot3D(x,y,z)
            except UnboundLocalError:
                return
        elif operation == "cwt":
            new_window = cwtFunctWindow()
            if new_window.exec_():
                scMin = new_window.scMin
                scMax = new_window.scMax
                wavelet = new_window.wavelet
            try:
                x, y, z = Math.cwt(self.function, scMin, scMax, wavelet)
                self.temp3d = Data3d(x, y, z ,'time','scale', 'Amplitude')
                self.plot3D(z)
            except UnboundLocalError:
                return

    def plot3D_extra(self):
        fig = plt.figure()
        ax = fig.add_subplot(111, projection='3d')
        x, y, z = self.temp3d.get_data()
        lx, ly, lz = self.temp3d.get_labels()
        x, y = np.meshgrid(x, y)
        ax.plot_surface(x, y, z, cmap=cm.coolwarm)
        ax.set(xlabel=lx, ylabel=ly, zlabel=lz)
        plt.show()

if __name__ == "__main__": 
    app = QApplication(sys.argv)
    w = AppWindow()
    w.show()
    sys.exit(app.exec_())