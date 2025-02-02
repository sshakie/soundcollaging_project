from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import *
from PyQt6 import QtWidgets, QtCore, QtGui
import sys
from soundmanager import SoundManager


class Ui_Form(object):
    def setupUi(self, Form):
        Form.setObjectName("Form")
        Form.resize(322, 202)
        self.select_piano = QtWidgets.QPushButton(parent=Form)
        self.select_piano.setGeometry(QtCore.QRect(20, 40, 121, 31))
        self.select_piano.setObjectName("select_piano")
        self.select_music_box = QtWidgets.QPushButton(parent=Form)
        self.select_music_box.setGeometry(QtCore.QRect(20, 70, 121, 31))
        self.select_music_box.setObjectName("select_music_box")
        self.select_guitar = QtWidgets.QPushButton(parent=Form)
        self.select_guitar.setGeometry(QtCore.QRect(20, 100, 121, 31))
        self.select_guitar.setObjectName("select_guitar")
        self.select_sine_pluck = QtWidgets.QPushButton(parent=Form)
        self.select_sine_pluck.setGeometry(QtCore.QRect(20, 130, 121, 31))
        self.select_sine_pluck.setObjectName("select_sine_pluck")
        self.select_bass = QtWidgets.QPushButton(parent=Form)
        self.select_bass.setGeometry(QtCore.QRect(20, 160, 121, 31))
        self.select_bass.setObjectName("select_bass")
        self.select_sine_wave = QtWidgets.QPushButton(parent=Form)
        self.select_sine_wave.setGeometry(QtCore.QRect(180, 40, 121, 31))
        self.select_sine_wave.setObjectName("select_sine_wave")
        self.select_flute = QtWidgets.QPushButton(parent=Form)
        self.select_flute.setGeometry(QtCore.QRect(180, 70, 121, 31))
        self.select_flute.setObjectName("select_flute")
        self.label = QtWidgets.QLabel(parent=Form)
        self.label.setGeometry(QtCore.QRect(20, 20, 121, 16))
        font = QtGui.QFont()
        font.setPointSize(14)
        font.setBold(True)
        font.setWeight(75)
        self.label.setFont(font)
        self.label.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        self.label.setObjectName("label")
        self.label_2 = QtWidgets.QLabel(parent=Form)
        self.label_2.setGeometry(QtCore.QRect(180, 20, 121, 16))
        font = QtGui.QFont()
        font.setPointSize(14)
        font.setBold(True)
        font.setWeight(75)
        self.label_2.setFont(font)
        self.label_2.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        self.label_2.setObjectName("label_2")

        self.retranslateUi(Form)
        QtCore.QMetaObject.connectSlotsByName(Form)

    def retranslateUi(self, Form):
        _translate = QtCore.QCoreApplication.translate
        Form.setWindowTitle(_translate("Form", "Instruments"))
        self.select_piano.setText(_translate("Form", "Piano"))
        self.select_music_box.setText(_translate("Form", "Music Box"))
        self.select_guitar.setText(_translate("Form", "Guitar"))
        self.select_sine_pluck.setText(_translate("Form", "Sine Pluck"))
        self.select_bass.setText(_translate("Form", "Bass"))
        self.select_sine_wave.setText(_translate("Form", "Sine"))
        self.select_flute.setText(_translate("Form", "Flute"))
        self.label.setText(_translate("Form", "Pluck"))
        self.label_2.setText(_translate("Form", "Wave"))


class Demo_Instrument(QMainWindow, Ui_Form):
    def __init__(self, sequencer):
        super().__init__()
        self.setupUi(self)
        self.setWindowFlags(
            Qt.WindowType.Window | Qt.WindowType.WindowCloseButtonHint | Qt.WindowType.WindowMinimizeButtonHint)
        self.sequencer = sequencer

        # Преднастройка
        self.selected = ''
        self.instrument_sound = SoundManager('files/demo_instrument/untitled - piano shot.wav')
        self.paths = ['untitled - piano shot', 'untitled - sine pluck', 'untitled - sine wave',
                      'untitled - music box shot', 'untitled - guitar shot', 'untitled - flute wave',
                      'untitled - bass shot']

        # Подключение кнопок
        self.select_piano.clicked.connect(self.new_selecting)
        self.select_music_box.clicked.connect(self.new_selecting)
        self.select_guitar.clicked.connect(self.new_selecting)
        self.select_sine_pluck.clicked.connect(self.new_selecting)
        self.select_bass.clicked.connect(self.new_selecting)
        self.select_sine_wave.clicked.connect(self.new_selecting)
        self.select_flute.clicked.connect(self.new_selecting)

    def new_selecting(self):  # отвечает за смену инструмента
        self.selected = self.sender().text()
        for i in range(len(self.paths)):
            if self.selected.lower() in self.paths[i]:
                self.instrument_sound = SoundManager(f'files/demo_instrument/{self.paths[i]}.wav')


def exception_hook(cls, exception, traceback):
    sys.__exception_hook__(cls, exception, traceback)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = Demo_Instrument()
    ex.show()
    sys.__excepthook__ = exception_hook
    sys.exit(app.exec())
