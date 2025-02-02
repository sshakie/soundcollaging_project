from PyQt6.QtWidgets import *
from PyQt6.QtCore import *
from PyQt6.QtGui import QColor, QPen, QCursor
from soundmanager import SoundManager
from soundclip import SoundClip


class Playlist(QGraphicsView):
    def __init__(self, sequencer):
        super().__init__(sequencer)
        self.sequencer = sequencer
        self.scene = QGraphicsScene(self)
        self.setScene(self.scene)
        self.setAcceptDrops(True)

        # Преднастройка
        self.pixels_per_hit = 40
        self.playing_sounds = {}
        self.draw_grid()
        self.palochka_timer = QTimer()
        self.palochka_timer.timeout.connect(self.move_palochka)
        self.controlling = False

    def draw_grid(self):  # Рисует/перерисовывает сетку в плейлисте
        for i in self.scene.items():
            if isinstance(i, QGraphicsLineItem):
                self.scene.removeItem(i)

        pen = QPen(QColor(100, 100, 100, 80))
        pen2 = QPen(QColor(100, 100, 100, 150))
        pen3 = QPen(QColor(100, 100, 100, 50))
        for x in range(0, 4000, int(self.pixels_per_hit)):  # Сетка ударов
            self.scene.addLine(round(x), 0, round(x), 3000, pen)
        for x in range(0, 4000, int(self.pixels_per_hit * 4)):  # Сетка тактов
            self.scene.addLine(round(x), 0, round(x), 3000, pen2)
        for y in range(0, 3000, 50):
            self.scene.addLine(0, round(y), 4000, round(y), pen)
        if self.pixels_per_hit >= 50:
            for x in range(0, 4000, int(round(self.pixels_per_hit / 2))):  # Сетка ударов
                self.scene.addLine(round(x), 0, round(x), 3000, pen3)

        if not hasattr(self, 'palochka'):
            self.palochka = QGraphicsRectItem(0, 0, 4, 3000)
            self.scene.addItem(self.palochka)

    def move_palochka(self):  # Отвечает за движение полоски воспроизведения
        self.palochka.setX(self.palochka.x() + (self.sequencer.bpm * self.pixels_per_hit / (60 * 100)))
        self.get_time()
        self.sequencer.metronome_player()
        if self.palochka.x() >= 4000:
            self.palochka.setX(0)
            for i in self.scene.items():
                if isinstance(i, SoundClip):
                    i.sound.stop()

        # Воспроизводит звуки при столкновении с клипом
        for i in self.scene.items():
            if isinstance(i, SoundClip):
                if self.palochka.x() >= i.x() and self.palochka.x() <= i.x() + i.rect().width():
                    if i.unique not in self.playing_sounds:
                        self.playing_sounds[i.unique] = True
                        poss = (self.palochka.x() - i.x()) / self.pixels_per_hit * (
                                60 / self.sequencer.bpm)  # вычисляем смещение, если клип проигрывается не сначала
                        self.play_sound(i.filepath, i.unique, poss)
                else:
                    if i.unique in self.playing_sounds:
                        del self.playing_sounds[i.unique]

    def get_time(self):  # Получение значения секундомера по положению полоски воспроизведения
        playtime = int(round((self.palochka.x() * 1000 * 60) / (self.sequencer.bpm * self.pixels_per_hit)))
        m = (playtime // 60000) % 60
        s = (playtime // 1000) % 60
        ms = playtime % 1000 // 10
        self.time_for_timer = f'{"0" * (2 - len(str(m)))}{str(m)}:{"0" * (2 - len(str(s)))}{str(s)}:{"0" * (2 - len(str(ms)))}{str(ms)}'
        self.sequencer.playtime.setText(self.time_for_timer)

        # Сдвигает визуально ползунок
        t = (1 / (self.sequencer.bpm / 60)) * 1000
        self.sequencer.song_slider.setValue(int(playtime // t))

    def add_clip(self, filepath, x=0, y=0, z=0, unique=0, color=None):  # Отвечает за создание клипов-звуков
        if z:  # если клип был загружен из проекта
            duration = SoundManager(filepath).get_audio_duration()
            S = (self.sequencer.bpm * self.pixels_per_hit / 60) * duration
            if S > 4000:  # если клип больше длины плейлиста
                S = 4000
            clip = SoundClip(self.palochka.x(), 5, S, 40, filepath, self, self.sequencer, color=color)
            clip.unique = unique
            clip.z = z
            if z != 1:
                clip.text.setPlainText(f'{filepath.split('/')[-1]} ({z})')
            clip.setX(max(0, x / self.pixels_per_hit) * self.pixels_per_hit)
            clip.setY(max(0, round(y / 50) * 50))
            self.scene.addItem(clip)
            return

        duration = SoundManager(filepath).get_audio_duration()
        S = (self.sequencer.bpm * self.pixels_per_hit / 60) * duration
        if S > 4000:  # если клип больше длины плейлиста
            S = 4000
        if x == 0 and y == 0:
            clip = SoundClip(self.palochka.x(), 5, S, 40, filepath, self, self.sequencer)
        else:  # Используется, если перетаскивается файл
            clip = SoundClip(0, 5, S, 40, filepath, self, self.sequencer)
            clip.setX(max(0, round(x / self.pixels_per_hit) * self.pixels_per_hit))
            clip.setY(max(0, round(y / 50) * 50))
        self.scene.addItem(clip)

    def dragEnterEvent(self, event):  # Триггер на появление перетаскиваемого файла в окне
        if event.mimeData().hasUrls():
            event.acceptProposedAction()

    def dragMoveEvent(self, event):  # Триггер на появление перетаскиваемого файла в окне 2
        if event.mimeData().hasUrls():
            event.acceptProposedAction()

    def dropEvent(self, event):  # Если файл всё таки добавляется на плейлист, то добавляется клип
        files = event.mimeData().urls()
        for file in files:
            filepath = file.toLocalFile()
            x, y = list(map(float, str(self.mapToScene(self.mapFromGlobal(QCursor.pos())))[21:-1].split(', ')))
            if filepath.endswith(('.wav', '.mp3', '.ogg', '.flac')):  # убеждаем, что это аудио файл
                self.add_clip(filepath, x, y)

    def play_sound(self, filepath, unique, poss=0):  # Функция воспроизведения звука и добавление его в словарь
        for i in self.scene.items():
            if isinstance(i, SoundClip) and i.filepath == filepath and i.unique == unique:
                if poss > 0.01:  # Если клип проигрывается не с начала
                    i.sound.play_delayed(int(poss * 1000), self.sequencer.global_volume)
                else:
                    i.sound.play()
                self.playing_sounds[unique] = i.sound

    def update_clips_width(self):  # Активируется при увеличении бпм, меняет размер клипов
        for i in self.scene.items():
            if isinstance(i, SoundClip):
                duration = SoundManager(i.filepath).get_audio_duration()
                new_S = (self.sequencer.bpm * self.pixels_per_hit / 60) * duration
                if new_S > 4000:  # если длина клипа больше длины плейлиста
                    new_S = 4000
                i.setRect(0, 5, new_S, i.rect().height())

    def keyPressEvent(self, event):  # Горячие клавиши (play/stop)
        if event.key() == Qt.Key.Key_Control:  # триггер клавиши ctrl (не помню зачем, но нужно было)
            self.controlling = True
        if event.key() == Qt.Key.Key_Space:  # бинд на воспроизведение/остановку
            if not self.sequencer.playing_radio.isChecked():
                self.sequencer.playing_radio.setChecked(True)
                self.sequencer.start_play()
            else:
                self.sequencer.stopping_radio.setChecked(True)
                self.sequencer.stop_play()
        super().keyPressEvent(event)

    def keyReleaseEvent(self, event):  # Триггер, когда отжат ctrl
        if event.key() == Qt.Key.Key_Control:
            self.controlling = False
        super().keyReleaseEvent(event)

    def mousePressEvent(self, event):  # Передвижение полоски воспроизведения со всеми сопутствующими на пкм
        if event.button() == Qt.MouseButton.RightButton:
            x, y = list(map(float, str(self.mapToScene(self.mapFromGlobal(QCursor.pos())))[21:-1].split(', ')))
            self.palochka.setX(round(x / self.pixels_per_hit) * self.pixels_per_hit)
            v = (self.sequencer.bpm * self.pixels_per_hit / 60)
            self.get_time()
            self.sequencer.start_position = self.palochka.x()
        super().mousePressEvent(event)

    def zoom_x(self, scale):  # Функция, отвечающая за увеличении сетки (эффект приближения)
        if self.palochka.x() >= 4000 / self.pixels_per_hit + scale:  # если палочка ушла за границы сцены, то возвращает её на нулевые координаты
            self.palochka.setX(0)

        old_pixels_per_hit = self.pixels_per_hit
        self.pixels_per_hit += scale

        self.palochka.setX(self.palochka.x() * (self.pixels_per_hit / old_pixels_per_hit))

        for i in self.scene.items():  # возвращаем все клипы на свои места с новой длиной
            if isinstance(i, SoundClip):
                new_width = i.rect().width() * (self.pixels_per_hit / old_pixels_per_hit)
                i.setRect(i.rect().x(), i.rect().y(), new_width, i.rect().height())
                i.setX(i.x() * (self.pixels_per_hit / old_pixels_per_hit))

        self.draw_grid()

    def wheelEvent(self, event):  # Бинды (приближение/отдаление, передвижение вправо/влево)
        if event.modifiers() == Qt.KeyboardModifier.ShiftModifier:  # бинд на перемещение влево
            if event.angleDelta().y() > 0:
                self.horizontalScrollBar().setValue(self.horizontalScrollBar().value() - 20)
            elif event.angleDelta().y() < 0:  # бинд на перемещение направо
                self.horizontalScrollBar().setValue(self.horizontalScrollBar().value() + 20)
        elif self.controlling and event.angleDelta().y() < 0:  # бинд на отдаление
            if self.pixels_per_hit > 20:
                self.zoom_x(-20)
        elif self.controlling and event.angleDelta().y() > 0:  # бинд на приближение
            if self.pixels_per_hit < 100:
                self.zoom_x(20)
        else:
            super().wheelEvent(event)
