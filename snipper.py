import sys
import signal

from PySide6.QtWidgets import QApplication, QWidget
from PySide6.QtCore import Qt, QRect, QObject, Signal
from PySide6.QtGui import QPainter, QColor, QRegion

from pynput import keyboard

HOTKEY = "<ctrl>+<shift>+x"

class Snipper(QWidget):

    def __init__(self,shot):
        super().__init__()
        self.shot = shot
        self.start = None
        self.end = None
        self.setWindowFlag(Qt.WindowStaysOnTopHint)
        self.showFullScreen()
        self.activateWindow()

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Escape:
            self.close()

    def paintEvent(self,event):
        painter = QPainter(self)
        painter.drawPixmap(0,0, self.shot)
        dim = QColor(0,0,0,120)
        region = QRegion(self.rect())

        if self.start is not None:
            selection = QRect(self.start, self.end).normalized()
            region = region.subtracted(QRegion(selection))

        painter.save()
        painter.setClipRegion(region)
        painter.fillRect(self.rect(), dim)
        painter.restore()

        if self.start is not None:
            painter.setPen(Qt.red)
            painter.drawRect(selection)

    def mousePressEvent(self, event):
        self.start = event.position().toPoint()
        self.end = self.start

    def mouseMoveEvent(self, event):
        self.end = event.position().toPoint()
        self.update()

    def mouseReleaseEvent(self,event):
        rect = QRect(self.start, self.end).normalized()
        scale = self.shot.devicePixelRatio()
        crop = self.shot.copy(QRect(rect.topLeft() * scale, rect.size() * scale))

        QApplication.clipboard().setPixmap(crop)
        self.close() 

class HotKeyBridge(QObject):
    pressed = Signal()

def start_snip():
    global window
    shot = app.primaryScreen().grabWindow(0)
    window = Snipper(shot)

app = QApplication(sys.argv)
app.setQuitOnLastWindowClosed(False)  # stay alive in between snips
signal.signal(signal.SIGINT, signal.SIG_DFL)  # let Ctrl+C in the terminal quit

window = None
bridge = HotKeyBridge()
bridge.pressed.connect(start_snip)

listener = keyboard.GlobalHotKeys({HOTKEY: bridge.pressed.emit})
listener.start()

print(f"Running. Press {HOTKEY} to snip, Esc to cancel, Ctrl+C here to quit.")
app.exec()