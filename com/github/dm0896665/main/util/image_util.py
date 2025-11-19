import sys

from PySide6 import QtCore
from PySide6.QtGui import QPixmap, QImage
from PySide6.QtWidgets import QGraphicsPixmapItem, QGraphicsScene, QGraphicsView


class ImageUtil:
    @staticmethod
    def load_player_image(image_file_name, graphics_view=None):
        return ImageUtil.load_image('player/' + image_file_name + ".png", graphics_view)

    @staticmethod
    def load_monster_image(image_file_name, graphics_view=None):
        return ImageUtil.load_image('monsters/' + image_file_name + ".png", graphics_view)

    @staticmethod
    def load_image(image_file_name, graphics_view: QGraphicsView=None) -> QGraphicsScene:
        pic: QGraphicsPixmapItem = QGraphicsPixmapItem()
        pic.setTransformationMode(QtCore.Qt.SmoothTransformation)

        image_map: QPixmap = ImageUtil.load_image_map(image_file_name)
        if image_map is None:
            return None

        pic.setPixmap(image_map)

        scene: QGraphicsScene = QGraphicsScene()
        scene.addItem(pic)

        if graphics_view is not None:
            graphics_view.setScene(scene)

        return scene

    @staticmethod
    def load_image_map(image_file_name) -> QPixmap:
        if not sys.path[0].endswith('images'):
            image_file_name = "com/github/dm0896665/resources/images/" + image_file_name

        image_qt: QImage = QImage()
        image_loaded: bool = image_qt.load(image_file_name)

        if not image_loaded:
            return None

        return QPixmap.fromImage(image_qt)