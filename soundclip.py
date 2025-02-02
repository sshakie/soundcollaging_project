from PyQt6.QtWidgets import *
from PyQt6.QtCore import *
from PyQt6.QtGui import QColor, QBrush
import uuid
from random import *
from soundmanager import SoundManager


class SoundClip(QGraphicsRectItem):
    def __init__(self, x, y, width, height, filepath, playlist, sequencer, z=1, color=None):
        super().__init__(x, y, width, height)
        self.setFlags(
            QGraphicsRectItem.GraphicsItemFlag.ItemIsMovable | QGraphicsRectItem.GraphicsItemFlag.ItemIsSelectable | QGraphicsRectItem.GraphicsItemFlag.ItemIsFocusable)

        # Преднастройка
        self.playlist = playlist
        self.sequencer = sequencer
        self.filepath = filepath
        self.unique = str(uuid.uuid4())
        self.z = z
        self.sound = SoundManager(filepath)
        self.sound.set_volume(self.sequencer.global_volume)

        # Покраска клипа в случайный цвет (если не дублируется)
        if color == None:
            self.r, self.g, self.b = randint(100, 230), randint(100, 230), randint(100, 230)
        else:
            self.r, self.g, self.b = list(map(int, color.split('-')))
        self.setBrush(QBrush(QColor(self.r, self.g, self.b)))

        # Добавляет цифру в конце, показав какая это копия
        if z != 1:
            self.text = QGraphicsTextItem(f'{self.filepath.split('/')[-1]} ({z})', self)
        else:
            self.text = QGraphicsTextItem(str(self.filepath.split('/')[-1]), self)
        if self.sequencer.darkmode.isChecked():
            self.text.setDefaultTextColor(Qt.GlobalColor.white)
        else:
            self.text.setDefaultTextColor(Qt.GlobalColor.black)
        self.text.setPos(self.x() + 5, self.y() + 12)

    def mousePressEvent(self, event):  # Выделяет/убирает выделение клип при нажатии на него + готовность к передвижению
        self.setSelected(True)
        self.dragging_offset = event.scenePos() - self.pos()
        for item in self.scene().items():
            if isinstance(item, SoundClip) and item != self:
                item.setSelected(False)

    def mouseMoveEvent(self, event):  # Меняет координаты клипа при передвижении
        self.setPos(event.scenePos() - self.dragging_offset)

    def mouseReleaseEvent(self, event):  # Примагничивает к сетке клип
        grid_size_x = self.playlist.pixels_per_hit
        if self.playlist.pixels_per_hit >= 50:
            grid_size_x = self.playlist.pixels_per_hit // 2
        grid_size_y = 50
        new_x = round(self.x() / grid_size_x) * grid_size_x
        new_y = round(self.y() / grid_size_y) * grid_size_y
        new_x = max(0, new_x)
        new_y = max(0, new_y)
        self.setX(new_x)
        self.setY(new_y)

    def mouseDoubleClickEvent(self, event):  # Дубликация клипа
        duplicate_clip = SoundClip(0, 5, self.rect().width(), self.rect().height(), self.filepath, self.playlist,
                                   self.sequencer, (self.z + 1), f'{self.r}-{self.g}-{self.b}')
        duplicate_clip.setPos(self.x(), self.y())
        self.scene().addItem(duplicate_clip)

    def keyPressEvent(self, event):  # Горячие клавиши (удаление, дубликат, передвижение на стрелочки)
        if event.key() == Qt.Key.Key_Delete and self.isSelected():  # бинд удаления
            self.scene().removeItem(self)
            del self
        elif event.modifiers() == Qt.KeyboardModifier.ControlModifier and event.key() == Qt.Key.Key_D and self.isSelected():  # бинд дублирования
            duplicate_clip = SoundClip(0, 5, self.rect().width(), self.rect().height(), self.filepath, self.playlist,
                                       self.sequencer, (self.z + 1),
                                       f'{self.r}-{self.g}-{self.b}')
            duplicate_clip.setPos(self.x(), self.y())
            self.scene().addItem(duplicate_clip)

        # Бинды перемещения на стрелочки
        elif event.key() == Qt.Key.Key_Right and self.isSelected():
            self.setX(self.x() + self.playlist.pixels_per_hit)
        elif event.key() == Qt.Key.Key_Left and self.isSelected() and self.x() > 0:
            self.setX(self.x() - self.playlist.pixels_per_hit)
        elif event.key() == Qt.Key.Key_Up and self.isSelected() and self.y() > 0:
            self.setY(self.y() - 50)
        elif event.key() == Qt.Key.Key_Down and self.isSelected():
            self.setY(self.y() + 50)
        else:
            super().keyPressEvent(event)
