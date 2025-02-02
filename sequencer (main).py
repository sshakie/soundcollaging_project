from PyQt6.QtWidgets import *
from PyQt6 import QtWidgets, QtCore, QtGui
from PyQt6.QtCore import *
from PyQt6.QtGui import QFileSystemModel, QColor, QBrush, QPen, QDrag, QPixmap, QAction, QKeyEvent, QKeySequence
import sys, psutil, pygame, sqlite3, shutil, os, uuid, numpy
from soundmanager import SoundManager
from soundclip import SoundClip
from playlist import Playlist
from first_instument import Demo_Instrument
import soundfile as sf
from tkinter import messagebox

help = '''Sequencer v1.0.0 final
Горячие клавиши:

Клип:
CTRL + D / Двойное нажатие ЛКМ [Клонирование клипа]
Delete [Удалить клип]
Стрелочки [Перемещение клипа по сетке]

Плейлист:
Space [Включить/Выключить воспроизведение]
CTRL + Stop/Space [Остановить воспроизведение на месте]
Колёсико вверх/вниз [Перемещение по оси y]
SHIFT + Колёсико вверх/вниз [Перемещение по оси x]
CTRL + Колёсико вверх/вниз [Приближение/Отдаление]
ПКМ [Перемещение старта воспроизведения]
Два раза на Stop [Сбрасывает старт воспроизведения]

Интерфейс:
CAPSLOCK [Включение/Выключение метронома]
ALT [Включение/Выключение режима имитации миди клавиатуры]

Имитация миди клавиатуры:
Z X C V B N M < (нижний ряд) [Игра на иструменте по тональности]'''


class Ui_Sequencer(object):
    def setupUi(self, Sequencer):
        Sequencer.setObjectName("Sequencer")
        Sequencer.resize(1080, 627)
        Sequencer.setMaximumSize(QtCore.QSize(1081, 670))
        Sequencer.setContextMenuPolicy(QtCore.Qt.ContextMenuPolicy.NoContextMenu)
        self.exitButton = QtWidgets.QPushButton(parent=Sequencer)
        self.exitButton.setGeometry(QtCore.QRect(1060, 0, 21, 21))
        self.exitButton.setFocusPolicy(QtCore.Qt.FocusPolicy.NoFocus)
        self.exitButton.setObjectName("exitButton")
        self.line = QtWidgets.QFrame(parent=Sequencer)
        self.line.setGeometry(QtCore.QRect(0, 20, 1081, 16))
        self.line.setLineWidth(1)
        self.line.setFrameShape(QtWidgets.QFrame.Shape.HLine)
        self.line.setFrameShadow(QtWidgets.QFrame.Shadow.Sunken)
        self.line.setObjectName("line")
        self.collapseButton = QtWidgets.QPushButton(parent=Sequencer)
        self.collapseButton.setGeometry(QtCore.QRect(1040, 0, 21, 21))
        self.collapseButton.setFocusPolicy(QtCore.Qt.FocusPolicy.NoFocus)
        self.collapseButton.setObjectName("collapseButton")
        self.line_2 = QtWidgets.QFrame(parent=Sequencer)
        self.line_2.setGeometry(QtCore.QRect(0, 50, 1081, 16))
        self.line_2.setLineWidth(2)
        self.line_2.setFrameShape(QtWidgets.QFrame.Shape.HLine)
        self.line_2.setFrameShadow(QtWidgets.QFrame.Shadow.Sunken)
        self.line_2.setObjectName("line_2")
        self.sequence_volume = QtWidgets.QDial(parent=Sequencer)
        self.sequence_volume.setGeometry(QtCore.QRect(300, 0, 31, 31))
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Policy.Fixed, QtWidgets.QSizePolicy.Policy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.sequence_volume.sizePolicy().hasHeightForWidth())
        self.sequence_volume.setSizePolicy(sizePolicy)
        self.sequence_volume.setContextMenuPolicy(QtCore.Qt.ContextMenuPolicy.DefaultContextMenu)
        self.sequence_volume.setMaximum(100)
        self.sequence_volume.setSingleStep(10)
        self.sequence_volume.setPageStep(10)
        self.sequence_volume.setProperty("value", 80)
        self.sequence_volume.setTracking(True)
        self.sequence_volume.setOrientation(QtCore.Qt.Orientation.Horizontal)
        self.sequence_volume.setInvertedAppearance(False)
        self.sequence_volume.setInvertedControls(False)
        self.sequence_volume.setWrapping(False)
        self.sequence_volume.setNotchesVisible(False)
        self.sequence_volume.setObjectName("sequence_volume")
        self.playing_radio = QtWidgets.QRadioButton(parent=Sequencer)
        self.playing_radio.setGeometry(QtCore.QRect(340, 0, 61, 17))
        self.playing_radio.setFocusPolicy(QtCore.Qt.FocusPolicy.NoFocus)
        self.playing_radio.setChecked(False)
        self.playing_radio.setObjectName("playing_radio")
        self.stopping_radio = QtWidgets.QRadioButton(parent=Sequencer)
        self.stopping_radio.setGeometry(QtCore.QRect(340, 10, 61, 17))
        self.stopping_radio.setFocusPolicy(QtCore.Qt.FocusPolicy.NoFocus)
        self.stopping_radio.setChecked(True)
        self.stopping_radio.setObjectName("stopping_radio")
        self.bpm_box = QtWidgets.QSpinBox(parent=Sequencer)
        self.bpm_box.setGeometry(QtCore.QRect(400, 0, 42, 22))
        self.bpm_box.setMinimum(50)
        self.bpm_box.setMaximum(240)
        self.bpm_box.setProperty("value", 120)
        self.bpm_box.setObjectName("bpm_box")
        self.song_slider = QtWidgets.QSlider(parent=Sequencer)
        self.song_slider.setGeometry(QtCore.QRect(0, 30, 171, 22))
        self.song_slider.setMinimum(0)
        self.song_slider.setMaximum(100)
        self.song_slider.setPageStep(1)
        self.song_slider.setOrientation(QtCore.Qt.Orientation.Horizontal)
        self.song_slider.setObjectName("song_slider")
        self.metronomeButton = QtWidgets.QPushButton(parent=Sequencer)
        self.metronomeButton.setGeometry(QtCore.QRect(180, 30, 31, 23))
        self.metronomeButton.setCheckable(True)
        self.metronomeButton.setObjectName("metronomeButton")
        self.midiButton = QtWidgets.QPushButton(parent=Sequencer)
        self.midiButton.setGeometry(QtCore.QRect(210, 30, 31, 23))
        self.midiButton.setCheckable(True)
        self.midiButton.setObjectName("midiButton")
        self.edisonButton = QtWidgets.QPushButton(parent=Sequencer)
        self.edisonButton.setGeometry(QtCore.QRect(240, 30, 31, 23))
        self.edisonButton.setObjectName("edisonButton")
        self.edisonButton.setCheckable(True)
        self.note_box = QtWidgets.QComboBox(parent=Sequencer)
        self.note_box.setGeometry(QtCore.QRect(300, 30, 41, 22))
        self.note_box.setToolTip("")
        self.note_box.setAccessibleName("")
        self.note_box.setAccessibleDescription("")
        self.note_box.setEditable(False)
        self.note_box.setCurrentText("")
        self.note_box.setMaxVisibleItems(12)
        self.note_box.setMaxCount(12)
        self.note_box.setObjectName("note_box")
        self.harmony_box = QtWidgets.QComboBox(parent=Sequencer)
        self.harmony_box.setGeometry(QtCore.QRect(350, 30, 61, 22))
        self.harmony_box.setMaxVisibleItems(2)
        self.harmony_box.setMaxCount(2)
        self.harmony_box.setObjectName("harmony_box")
        self.browserView = QtWidgets.QTreeView(parent=Sequencer)
        self.browserView.setGeometry(QtCore.QRect(0, 90, 231, 451))
        self.browserView.setObjectName("browserView")
        self.move_zone = QtWidgets.QFrame(parent=Sequencer)
        self.move_zone.setGeometry(QtCore.QRect(450, 0, 571, 31))
        self.move_zone.setFrameShape(QtWidgets.QFrame.Shape.StyledPanel)
        self.move_zone.setFrameShadow(QtWidgets.QFrame.Shadow.Raised)
        self.move_zone.setObjectName("move_zone")
        self.playtime = QtWidgets.QLabel(parent=self.move_zone)
        self.playtime.setGeometry(QtCore.QRect(40, 0, 81, 21))
        font = QtGui.QFont()
        font.setPointSize(12)
        font.setBold(True)
        font.setWeight(75)
        self.playtime.setFont(font)
        self.playtime.setObjectName("playtime")
        self.voluming_label = QtWidgets.QLabel(parent=Sequencer)
        self.voluming_label.setGeometry(QtCore.QRect(950, 30, 121, 20))
        self.voluming_label.setLayoutDirection(QtCore.Qt.LayoutDirection.RightToLeft)
        self.voluming_label.setAlignment(
            QtCore.Qt.AlignmentFlag.AlignRight | QtCore.Qt.AlignmentFlag.AlignTrailing | QtCore.Qt.AlignmentFlag.AlignVCenter)
        self.voluming_label.setObjectName("voluming_label")
        self.choose_folder = QtWidgets.QPushButton(parent=Sequencer)
        self.choose_folder.setGeometry(QtCore.QRect(70, 60, 91, 21))
        self.choose_folder.setObjectName("choose_folder")
        self.verticalLayoutWidget = QtWidgets.QWidget(parent=Sequencer)
        self.verticalLayoutWidget.setGeometry(QtCore.QRect(0, 540, 231, 80))
        self.verticalLayoutWidget.setObjectName("verticalLayoutWidget")
        self.wf_layout = QtWidgets.QVBoxLayout(self.verticalLayoutWidget)
        self.wf_layout.setSizeConstraint(QtWidgets.QLayout.SizeConstraint.SetFixedSize)
        self.wf_layout.setContentsMargins(0, 0, 0, 0)
        self.wf_layout.setObjectName("wf_layout")
        self.projectButton = QtWidgets.QToolButton(parent=Sequencer)
        self.projectButton.setEnabled(True)
        self.projectButton.setGeometry(QtCore.QRect(0, 0, 61, 31))
        self.projectButton.setObjectName("projectButton")
        self.editButton = QtWidgets.QToolButton(parent=Sequencer)
        self.editButton.setGeometry(QtCore.QRect(60, 0, 61, 31))
        self.editButton.setObjectName("editButton")
        self.exportButton = QtWidgets.QToolButton(parent=Sequencer)
        self.exportButton.setGeometry(QtCore.QRect(240, 0, 61, 31))
        self.exportButton.setObjectName("exportButton")
        self.helpButton = QtWidgets.QToolButton(parent=Sequencer)
        self.helpButton.setGeometry(QtCore.QRect(180, 0, 61, 31))
        self.helpButton.setObjectName("helpButton")
        self.label = QtWidgets.QLabel(parent=Sequencer)
        self.label.setGeometry(QtCore.QRect(0, 440, 71, 191))
        self.label.setObjectName("label")
        self.darkmode = QtWidgets.QCheckBox(parent=Sequencer)
        self.darkmode.setGeometry(QtCore.QRect(420, 30, 91, 21))
        self.darkmode.setObjectName("darkmode")
        self.f_instr_Button = QtWidgets.QPushButton(parent=Sequencer)
        self.f_instr_Button.setGeometry(QtCore.QRect(270, 30, 31, 23))
        self.f_instr_Button.setObjectName("f_instr_Button")
        self.newButton = QtWidgets.QToolButton(parent=Sequencer)
        self.newButton.setEnabled(True)
        self.newButton.setGeometry(QtCore.QRect(120, 0, 61, 31))
        self.newButton.setObjectName("newButton")
        self.move_zone.raise_()
        self.exitButton.raise_()
        self.collapseButton.raise_()
        self.line_2.raise_()
        self.bpm_box.raise_()
        self.metronomeButton.raise_()
        self.midiButton.raise_()
        self.edisonButton.raise_()
        self.note_box.raise_()
        self.harmony_box.raise_()
        self.browserView.raise_()
        self.voluming_label.raise_()
        self.choose_folder.raise_()
        self.verticalLayoutWidget.raise_()
        self.line.raise_()
        self.projectButton.raise_()
        self.editButton.raise_()
        self.exportButton.raise_()
        self.helpButton.raise_()
        self.sequence_volume.raise_()
        self.label.raise_()
        self.song_slider.raise_()
        self.stopping_radio.raise_()
        self.playing_radio.raise_()
        self.darkmode.raise_()
        self.f_instr_Button.raise_()
        self.newButton.raise_()

        self.retranslateUi(Sequencer)
        self.note_box.setCurrentIndex(-1)
        QtCore.QMetaObject.connectSlotsByName(Sequencer)

    def retranslateUi(self, Sequencer):
        _translate = QtCore.QCoreApplication.translate
        Sequencer.setWindowTitle(_translate("Sequencer", "Sequencer"))
        self.exitButton.setText(_translate("Sequencer", "X"))
        self.collapseButton.setText(_translate("Sequencer", "_"))
        self.playing_radio.setText(_translate("Sequencer", "Play"))
        self.stopping_radio.setText(_translate("Sequencer", "Stop"))
        self.metronomeButton.setText(_translate("Sequencer", "🕰️"))
        self.midiButton.setText(_translate("Sequencer", "[=]"))
        self.edisonButton.setText(_translate("Sequencer", "🔘"))
        self.playtime.setText(_translate("Sequencer", "00:00:00"))
        self.voluming_label.setText(_translate("Sequencer", "Громкость - 80%"))
        self.choose_folder.setText(_translate("Sequencer", "Выбрать папку"))
        self.projectButton.setText(_translate("Sequencer", "PROJECT"))
        self.editButton.setText(_translate("Sequencer", "EDIT"))
        self.exportButton.setText(_translate("Sequencer", "EXPORT"))
        self.helpButton.setText(_translate("Sequencer", "HELP"))
        self.label.setText(_translate("Sequencer", "picture"))
        self.darkmode.setText(_translate("Sequencer", "Dark Mode"))
        self.f_instr_Button.setText(_translate("Sequencer", "🎹"))
        self.newButton.setText(_translate("Sequencer", "NEW"))


class Sequencer(QMainWindow, Ui_Sequencer):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)

        # Всё для секундомера (таймер будет включаться и заканчиваться каждую секунду, создавая секундомер)
        self.playing_radio.clicked.connect(self.start_play)
        self.stopping_radio.clicked.connect(self.stop_play)

        # Пред-настройка программы
        self.selected_file = None
        self.dragging = False
        self.twice = True
        self.browserView.setDragEnabled(True)
        self.note_box.addItems(['A', 'A#', 'B', 'C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#'])
        self.harmony_box.addItems(['Major', 'Minor'])
        self.bpm = self.bpm_box.value()
        self.global_volume = self.sequence_volume.value() / 100
        self.start_position = 0
        self.instrument = ''

        # Подключаю кнопки
        self.sequence_volume.valueChanged.connect(self.change_global_volume)
        self.bpm_box.valueChanged.connect(self.change_bpm)
        self.exitButton.clicked.connect(sys.exit)
        self.collapseButton.clicked.connect(self.showMinimized)
        self.song_slider.sliderMoved.connect(self.song_slider_moving)
        self.song_slider.sliderPressed.connect(self.song_slider_moving)
        self.f_instr_Button.clicked.connect(self.open_demo_instrument)
        self.edisonButton.clicked.connect(self.recording_process)

        # MIDI: всё для работы выбора тональности
        self.need_notes = ['A', 'B', 'C#', 'D', 'E', 'F#', 'G#', 'A6']
        self.notes = ['A', 'A#', 'B', 'C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A6', 'A#6', 'B6', 'C6', 'C#6',
                      'D6',
                      'D#6', 'E6', 'F6', 'F#6', 'G6', 'G#6']
        self.note_box.currentTextChanged.connect(self.tonal_changed)
        self.harmony_box.currentTextChanged.connect(self.tonal_changed)

        # Добавляю всё, что нужно для работы метроному
        self.hit = -1
        self.m_one = SoundManager('files/ui/m_first.wav')
        self.m_two = SoundManager('files/ui/m_second.wav')

        # Создаю браузер
        self.browserModel = QFileSystemModel()
        self.browserModel.setRootPath('')
        self.browserView.setModel(self.browserModel)
        self.browserView.setRootIndex(self.browserModel.index(''))
        self.choose_folder.clicked.connect(self.choosing_folder)
        self.browserView.setColumnHidden(1, True)
        self.browserView.setColumnHidden(2, True)
        self.browserView.setColumnHidden(3, True)
        self.browserView.header().hide()
        self.browserView.clicked.connect(self.play_selected_audio)
        self.browserView.setStyleSheet("QTreeView::item:selected{background-color: #99CCFF}")

        # Добавление Playlist'а на экран
        self.playlist = Playlist(self)
        self.playlist.setGeometry(240, 60, 841, 571)

        # добавление картинки
        picture = QPixmap('files/ui/cat.jpg')
        scaled_pixmap = picture.scaled(self.label.size(), Qt.AspectRatioMode.KeepAspectRatio)
        self.label.setPixmap(scaled_pixmap)

        # Все для работы темной темы
        self.darkmode.stateChanged.connect(self.enable_dark)

        # Добавление cpu график
        self.cpu_scene = QGraphicsScene(self)
        self.cpu_scene.setSceneRect(0, 0, 100, 20)

        # Сам прямоугольник
        self.cpu_graphic = QGraphicsRectItem(0, 0, 100, 20)
        self.cpu_graphic.setBrush(QBrush(QColor(255, 150, 255)))
        self.cpu_scene.addItem(self.cpu_graphic)

        # Текст загруженности цп
        self.cpu_text = QGraphicsTextItem('100')
        self.cpu_text.setDefaultTextColor(Qt.GlobalColor.black)
        self.cpu_scene.addItem(self.cpu_text)

        # Таймер через которое проверяется загруженность
        self.cpu_timer = QTimer(self)
        self.cpu_timer.timeout.connect(self.update_cpu)
        self.cpu_timer.start(1000)

        # Чтобы видно было сцену
        self.cpuView = QGraphicsView(self)
        self.cpuView.setScene(self.cpu_scene)
        self.cpuView.setGeometry(600, 0, 120, 23)

        # Добавление waveform график
        pygame.mixer.init()
        self.waveform_graphic = QGraphicsView(self)
        self.waveform_graphic.scene = QGraphicsScene(self)
        self.waveform_graphic.setGeometry(0, 540, 231, 81)
        self.waveform_graphic.scene.setSceneRect(0, 0, 231, 81)
        self.waveform = None

        # Чтобы видно было сцену + настройка её
        self.waveformView = QGraphicsView(self)
        self.waveformView.setScene(self.waveform_graphic.scene)
        self.waveformView.setGeometry(0, 540, 231, 81)
        self.waveformView.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.waveformView.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

        # Настройка tool кнопок (project)
        self.projectButton.setPopupMode(QToolButton.ToolButtonPopupMode.MenuButtonPopup)
        self.projectButton.setPopupMode(QToolButton.ToolButtonPopupMode.InstantPopup)
        file_menu = QMenu(self)
        save = QAction('Сохранить', self)
        save.setShortcut(QKeySequence(Qt.Modifier.CTRL | Qt.Key.Key_S))
        open = QAction('Открыть', self)
        open.setShortcut(QKeySequence(Qt.Modifier.CTRL | Qt.Key.Key_O))
        file_menu.addAction(save)
        file_menu.addAction(open)
        self.projectButton.setMenu(file_menu)

        # Настройка tool кнопок (edit)
        self.editButton.setPopupMode(QToolButton.ToolButtonPopupMode.MenuButtonPopup)
        self.editButton.setPopupMode(QToolButton.ToolButtonPopupMode.InstantPopup)
        edit_menu = QMenu(self)
        duplicate = QAction('Дублировать', self)
        delete = QAction('Удалить', self)
        edit_menu.addAction(duplicate)
        edit_menu.addAction(delete)
        self.editButton.setMenu(edit_menu)

        # Настройка tool кнопок (подключения)
        save.triggered.connect(self.save_project)
        open.triggered.connect(self.open_project)
        duplicate.triggered.connect(self.duplicate_clip)
        delete.triggered.connect(self.delete_clip)
        self.newButton.clicked.connect(self.new_project)
        self.helpButton.clicked.connect(self.opening_help)
        self.exportButton.clicked.connect(self.export_file)

    def new_project(self):  # Сбрасывает все
        # Диалог, который спрашивает уверен ли пользователь
        dialog = messagebox.askyesno("", "Вы уверены, что хотите закрыть данный проект?")
        if dialog is False:
            return

        # Сброс всех настроек проекта
        self.bpm = 120
        self.bpm_box.setValue(120)
        self.change_bpm()
        self.sequence_volume.setValue(80)
        self.change_global_volume()
        self.harmony_box.setCurrentText('Major')
        self.note_box.setCurrentText('A')
        self.tonal_changed()
        self.start_position = 0
        self.playlist.palochka.setX(self.start_position)
        self.playtime.setText('00:00:00')
        self.song_slider.setValue(0)
        self.metronomeButton.setChecked(False)

        for i in self.playlist.scene.items():
            if isinstance(i, SoundClip):
                i.sound.stop()
                self.playlist.scene.removeItem(i)
                del i

    def save_project(self):  # отвечает за сохранение проекта в файл
        # Запрос куда сохранять файл
        table_pass = f"{QFileDialog.getSaveFileName(self, 'Сохранить проект', QDir.rootPath(), 'SQLite Files (*.sqlite)')[0]}.sqlite"
        if not table_pass:
            return
        shutil.copy('for_copy.sqlite', table_pass)

        # Открытие базы данных
        file = sqlite3.connect(table_pass)
        cursor = file.cursor()

        # Удаление старых данных
        cursor.execute('DELETE FROM Service_inform')
        cursor.execute('INSERT INTO Service_inform (bpm, harmony, global_volume, note) VALUES (?, ?, ?, ?)', (
            self.bpm, self.harmony_box.currentText(), self.global_volume, self.note_box.currentText()))

        # Сохраняем все
        data = [i[0] for i in cursor.execute('SELECT "unique" FROM Soundclip').fetchall()]

        for i in self.playlist.scene.items():
            if isinstance(i, SoundClip):
                color = f'{i.r}-{i.g}-{i.b}'
                if i.unique not in data:
                    cursor.execute('INSERT INTO Soundclip ("unique", path, z, x, y, color) VALUES (?, ?, ?, ?, ?, ?)',
                                   (i.unique, i.filepath, i.z, i.x(), i.y(), color))
                else:
                    # Обновляем данные о клипе, если он уже существует в бд
                    cursor.execute('UPDATE Soundclip SET path = ?, x = ?, y = ?, z = ?, color = ? WHERE "unique" = ?',
                                   (i.filepath, i.x(), i.y(), color, i.unique))
        file.commit()
        file.close()

    def open_project(self):  # отвечает за открытие проекта из файла (помогли)
        # Диалог чтобы убедиться, что пользователь хочет закрыть проект
        dialog = messagebox.askyesno("", "Вы уверены, что хотите закрыть данный проект?")
        if dialog is False:
            return

        # Открытие проекта (установка всех настроек)
        get_project = f"{QFileDialog.getOpenFileName(self, "Открыть проект", QDir.rootPath(), "SQLite Files (*.sqlite)")[0]}"
        if get_project == '':
            return

        # Удаление всех настроек
        self.start_position = 0
        self.playlist.palochka.setX(self.start_position)
        self.playtime.setText('00:00:00')
        self.song_slider.setValue(0)
        for i in self.playlist.scene.items():
            if isinstance(i, SoundClip):
                i.sound.stop()
                self.playlist.scene.removeItem(i)
                del i

        file = sqlite3.connect(get_project)
        for i in file.cursor().execute('SELECT * FROM Service_inform'):
            bpm, harmony, global_vol, note = i
            self.bpm = bpm
            self.bpm_box.setValue(bpm)
            self.change_bpm()
            self.sequence_volume.setValue(int(global_vol * 100))
            self.change_global_volume()
            self.harmony_box.setCurrentText(harmony)
            self.note_box.setCurrentText(note)
            self.tonal_changed()

        for unique, filepath, z, x, y, color in file.cursor().execute(
                'SELECT "unique", path, z, x, y, color FROM Soundclip'):
            self.playlist.add_clip(filepath=filepath, x=x, y=y, z=z, unique=unique, color=color)

    def opening_help(self):  # Открывает "вики"
        messagebox.showinfo("Помощь", help)

    def export_file(self):  # Сохраняет всю работу в wav файл
        output = QFileDialog.getSaveFileName(self, "Экспортировать", QDir.homePath(), ".wav")
        if output == ('', ''):
            return
        output = f"{output[0]}.wav"

        # общие хар-ки
        samplerate = None
        total_samples = 0
        tracks = []

        for i in self.playlist.scene.items():
            if isinstance(i, SoundClip):
                sound = SoundManager(i.filepath)
                data, samplerate = sound.data, sound.samplerate

                start_time = i.x() / self.playlist.pixels_per_hit * (60 / self.bpm)
                start_sample = int(start_time * samplerate)
                end_sample = start_sample + len(data)
                if end_sample > total_samples:
                    total_samples = end_sample
                tracks.append((data, start_sample))

        all_sounds = numpy.zeros((total_samples, 2 if len(tracks[0][
                                                              0].shape) > 1 else 1))  # Создаем массив, который будет забит нулями длиной сэмплов для моно/стерео
        for clip_data, start_sample in tracks:
            all_sounds[start_sample:start_sample + len(
                clip_data)] += clip_data  # Здесь заполняем звуками этот массив, в общем складываем амплитуды всех звуков
        sf.write(output, all_sounds, samplerate)

    def duplicate_clip(self):  # Дублирует выделенный клип (имитирует нажатие)
        event = QKeyEvent(QKeyEvent.Type.KeyPress, Qt.Key.Key_D, Qt.KeyboardModifier.ControlModifier)
        QApplication.postEvent(QApplication.focusWidget(), event)
        super().keyPressEvent(event)

    def delete_clip(self):  # Удаляет выделенный клип (имитирует нажатие)
        event = QKeyEvent(QKeyEvent.Type.KeyPress, Qt.Key.Key_Delete, Qt.KeyboardModifier.NoModifier)
        QApplication.postEvent(QApplication.focusWidget(), event)
        super().keyPressEvent(event)

    def start_play(self):  # Кнопка воспроизведения
        self.playlist.palochka_timer.start(1000 // 100)
        if self.selected_file:
            self.selected_file.stop()
        self.twice = False

    def stop_play(self):  # Отключение воспроизведения
        self.playlist.palochka_timer.stop()
        if not self.playlist.controlling:  # Функция остановки на месте
            self.playlist.palochka.setX(self.start_position)
            self.hit = -1
            for i in self.playlist.scene.items():
                if isinstance(i, SoundClip):
                    i.sound.stop()
        elif self.playlist.controlling:
            for i in self.playlist.scene.items():
                if isinstance(i, SoundClip):
                    i.sound.stop()

        self.playlist.get_time()
        self.playlist.playing_sounds.clear()
        if self.selected_file:
            self.selected_file.stop()

        if not self.twice:  # Функция передвижения стартовой позиции на нули
            self.twice = True
        else:
            self.start_position = 0
            self.playlist.palochka.setX(self.start_position)
            self.playtime.setText('00:00:00')
            self.song_slider.setValue(0)

    def change_bpm(self):  # Смена кол-ва ударов в минуту и всё, что от него зависит
        self.bpm = self.bpm_box.value()
        self.playlist.update_clips_width()
        self.playlist.get_time()

    def change_global_volume(self):  # Устанавливает громкость всем звукам в приложении
        self.global_volume = (self.sequence_volume.value()) / 100
        self.voluming_label.setText(f'Громкость - {round(self.global_volume * 100)}%')
        self.m_one.set_volume(self.global_volume)
        self.m_two.set_volume(self.global_volume)
        if self.instrument != '':
            self.instrument.instrument_sound.set_volume(self.global_volume)
        if self.selected_file != None:
            self.selected_file.set_volume(self.global_volume)

        for i in self.playlist.items():
            if isinstance(i, SoundClip):
                i.sound.set_volume(self.global_volume)

    def metronome_player(self):  # Воспроизводит звуки метронома
        hit = (
                  int(self.playlist.palochka.x() // self.playlist.pixels_per_hit)) % 4  # нужно для сравнения прошлой и новой
        if hit != self.hit and self.metronomeButton.isChecked():
            if hit == 0:
                self.m_one.play()
            else:
                self.m_two.play()
        self.hit = (int(self.playlist.palochka.x() // self.playlist.pixels_per_hit)) % 4

    def tonal_changed(self):  # Создает список нот, которые входят в тональность при смене в боксах
        # Принцип в мажоре - 1, 3, 5, 6, 8, 10, 12, 13
        # Принцип в миноре - 1, 3, 4, 6, 8, 10, 12, 13
        a = self.notes.index(str(self.note_box.currentText()))
        if ''.join(self.harmony_box.currentText()) == 'Major':
            self.need_notes = [self.notes[a], self.notes[a + 2], self.notes[a + 4], self.notes[a + 5],
                               self.notes[a + 7], self.notes[a + 9], self.notes[a + 11], self.notes[a + 12]]
        else:
            self.need_notes = [self.notes[a], self.notes[a + 2], self.notes[a + 3], self.notes[a + 5],
                               self.notes[a + 7], self.notes[a + 9], self.notes[a + 11], self.notes[a + 12]]

    def choosing_folder(self):  # Функция кнопки "Выбрать папку"
        folder = QFileDialog.getExistingDirectory(self, "Выберите папку", QDir.rootPath())
        if folder:
            self.browserModel.setRootPath(folder)
            self.browserView.setRootIndex(self.browserModel.index(folder))  # Фун Фу

    def play_selected_audio(self, index):  # Включает звуки при нажатии на звук в браузере / отключение
        selected_path = self.browserModel.filePath(index)
        if QDir(selected_path).exists():
            if self.selected_file != None:
                self.selected_file.stop()
            return
        if selected_path.endswith(('.mp3', '.wav', '.ogg', '.flac')):  # проверка что это аудио файл
            if self.selected_file != None:
                self.selected_file.stop()
            self.selected_file = SoundManager(selected_path)
            self.selected_file.set_volume(self.global_volume)
            self.selected_file.play()

            # Показывает звуковую волну
            waveform = self.get_waveform(selected_path)
            self.set_waveform(waveform)
            self.waveform_graphic.update()

    def song_slider_moving(self):  # Нужно, чтобы при смене ползунка всё подстраивалось
        self.song_slider.setRange(-1, 101)  # Какие-то были проблемы с тем, что мин/макс = 1/99
        if 0 <= self.song_slider.value() <= 100:
            t = (1 / (self.bpm / 60)) * 1000
            a = self.song_slider.value()
            playtime = int(a * t)

            # Высчитывает время для таймера и все что связано с ним
            m = (playtime // 60000) % 60
            s = (playtime // 1000) % 60
            ms = playtime % 1000 // 10
            self.playlist.time_for_timer = f'{"0" * (2 - len(str(m)))}{str(m)}:{"0" * (2 - len(str(s)))}{str(s)}:{"0" * (2 - len(str(ms)))}{str(ms)}'
            self.playtime.setText(self.playlist.time_for_timer)
            t = playtime * (self.bpm / (60 * 1000))
            self.playlist.palochka.setX(t * self.playlist.pixels_per_hit)
            self.start_position = t * self.playlist.pixels_per_hit

    def keyPressEvent(self, event):  # Горячие клавиши (имитация миди-клавиатуры, вкл/выкл метронома)
        if self.midiButton.isChecked() and self.instrument and self.instrument.selected != '':
            if event.key() == Qt.Key.Key_Z:
                self.instrument.instrument_sound.play_note(
                    -(self.notes.index('C') - self.notes.index(self.need_notes[0]) + 1) * 100)
            elif event.key() == Qt.Key.Key_X:
                self.instrument.instrument_sound.play_note(
                    -(self.notes.index('C') - self.notes.index(self.need_notes[1])) * 100)
            elif event.key() == Qt.Key.Key_C:
                self.instrument.instrument_sound.play_note(
                    -(self.notes.index('C') - self.notes.index(self.need_notes[2])) * 100)
            elif event.key() == Qt.Key.Key_V:
                self.instrument.instrument_sound.play_note(
                    -(self.notes.index('C') - self.notes.index(self.need_notes[3])) * 100)
            elif event.key() == Qt.Key.Key_B:
                self.instrument.instrument_sound.play_note(
                    -(self.notes.index('C') - self.notes.index(self.need_notes[4])) * 100)
            elif event.key() == Qt.Key.Key_N:
                self.instrument.instrument_sound.play_note(
                    -(self.notes.index('C') - self.notes.index(self.need_notes[5])) * 100)
            elif event.key() == Qt.Key.Key_M:
                self.instrument.instrument_sound.play_note(
                    -(self.notes.index('C') - self.notes.index(self.need_notes[6])) * 100)
            elif event.key() == Qt.Key.Key_Comma:
                self.instrument.instrument_sound.play_note(
                    -(self.notes.index('C') - self.notes.index(self.need_notes[7])) * 100)
        if event.key() == Qt.Key.Key_CapsLock:  # Бинд метронома
            if self.metronomeButton.isChecked():
                self.metronomeButton.setChecked(False)
            else:
                self.metronomeButton.setChecked(True)
        elif event.key() == Qt.Key.Key_Alt:  # Бинд миди
            if self.midiButton.isChecked():
                self.midiButton.setChecked(False)
            else:
                self.midiButton.setChecked(True)
        elif event.modifiers() == Qt.KeyboardModifier.ControlModifier and event.key() == Qt.Key.Key_N:  # Бинд нового проекта
            self.new_project()
        elif event.modifiers() == Qt.KeyboardModifier.ControlModifier and event.key() == Qt.Key.Key_R:  # Бинд рендера проекта
            self.export_file()
        super().keyPressEvent(event)

    def mousePressEvent(self, event):  # Включает режим перетаскивания при нажатии на опр. зону
        if event.button() == Qt.MouseButton.LeftButton and self.move_zone.geometry().contains(event.pos()):
            self.dragging = True
            self.drag_position = event.globalPosition().toPoint() - self.pos()
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event):  # сдвиг окна
        if self.dragging:
            delta = event.globalPosition().toPoint() - self.drag_position
            self.move(delta)
        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):  # Выключает режим перетаскивания при нажатии на опр. зону
        if event.button() == Qt.MouseButton.LeftButton:
            self.dragging = False
        super().mouseReleaseEvent(event)

    def startDrag(self):  # Функция, отвечающая за работу перетаскивания файла из браузера
        mime_data = QMimeData()
        file = QDrag(self)
        file.setMimeData(mime_data)
        file.exec(Qt.DropAction.CopyAction)

    def enable_dark(self):  # Включает/Выключает темную тему приложения
        if self.darkmode.isChecked():
            self.setStyleSheet("""QWidget {background-color: #2e2e2e; color: white;}
                QPushButton {color: white;}
                QLabel {color: white;}
                QCheckBox {color: white;}
                QLineEdit {color: white; background-color: #444; border: 1px solid #555;}
                QCheckBox::indicator {width: 20px; height: 20px}""")
            for i in self.playlist.scene.items():
                if isinstance(i, SoundClip):
                    i.text.setDefaultTextColor(Qt.GlobalColor.white)
        else:
            self.setStyleSheet("""QWidget {background-color: #ffffff; color: black;}
                QPushButton {color: black;}
                QLabel {color: black;}
                QCheckBox {color: black;}
                QLineEdit {color: black; background-color: white; border: 1px solid #ccc;}
                QCheckBox::indicator {width: 20px; height: 20px}""")
            for i in self.playlist.scene.items():
                if isinstance(i, SoundClip):
                    i.text.setDefaultTextColor(Qt.GlobalColor.black)

    def update_cpu(self):  # Обновляет график при обновлении значения cpu
        cpu_usage = psutil.cpu_percent() / 100.0
        new_width = self.cpu_scene.sceneRect().width() * cpu_usage
        self.cpu_graphic.setRect(0, 0, new_width, self.cpu_scene.sceneRect().height())
        self.cpu_text.setPlainText(str(int(cpu_usage * 100)))
        self.cpu_text.setPos(self.cpu_graphic.x(), self.cpu_graphic.y())

    def get_waveform(self, path):  # Вытаскиваем амплитуды из звука
        data, samplerate = sf.read(path)
        if len(data.shape) > 1:  # Если звук в стерео, то берем только один канал, чтобы сделать звук в моно
            data = data[:, 0]
        return data

    def set_waveform(self, waveform):  # Строим график под сцену
        self.waveform_graphic.scene.clear()
        self.waveform = waveform
        seredina = self.waveformView.height() / 2
        samples_per_pixel = max(1, int(len(self.waveform) // self.waveformView.width()))

        points = []
        for i in range(0, len(self.waveform),
                       samples_per_pixel):  # здесь мы записываем точки, который мы будем брать смотря на размер сцены
            segment = self.waveform[i:i + samples_per_pixel]
            min_amp = min(segment)
            max_amp = max(segment)
            x = i // samples_per_pixel

            y_min = seredina - (min_amp * seredina)
            y_max = seredina - (max_amp * seredina)
            # у нас чтобы отобразить правильно волну, нужно можно сказать разрезать график пополам
            # мы разрезаем амплитуды так, чтобы всё входило в нашу сцену
            points.append((x, y_min))
            points.append((x, y_max))

        # строим waveform'у
        for i in range(len(points) - 1):
            x1, y1 = points[i]
            x2, y2 = points[i + 1]
            line = QGraphicsLineItem(x1, y1, x2, y2)
            line.setPen(QPen(QColor(100, 200, 100)))
            self.waveform_graphic.scene.addItem(line)

    def open_demo_instrument(self):  # открывает форму - инструмент
        self.instrument = Demo_Instrument(self)
        self.instrument.show()
        self.instrument.instrument_sound.set_volume(self.global_volume)

    def recording_process(self):  # Включаем/Выключаем запись
        try:
            if not self.instrument.instrument_sound.is_recording:
                self.instrument.instrument_sound.start_recording()
                self.is_recording = True
            else:
                save_path = os.path.join(f'{os.path.dirname(__file__)}\\recorded', f'{uuid.uuid4()}.wav')
                if save_path:
                    self.instrument.instrument_sound.stop_recording(save_path)
                    self.playlist.add_clip(f'recorded/{save_path.split('\\')[-1]}')
                self.is_recording = False
        except:
            self.edisonButton.setChecked(False)
            return 'ошибка'


def exception_hook(cls, exception, traceback):
    sys.__exception_hook__(cls, exception, traceback)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = Sequencer()
    ex.show()
    sys.__excepthook__ = exception_hook
    sys.exit(app.exec())
