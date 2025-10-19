import faulthandler
import sys

from PySide6.QtGui import QIcon


# Make sure the main module is added
def add_main_module_to_path():
    path_to_add: str = None
    main_path: str = "com/github/dm0896665/main"
    for path in sys.path:
        if main_path in path.replace("\\", "/"):
            path_to_add = path.replace("\\", "/").replace(main_path, "")
    if path_to_add is not None:
        sys.path.append(path_to_add)

add_main_module_to_path()

from com.github.dm0896665.main.ui.screens.main_menu import MainMenu
from com.github.dm0896665.main.util.ui_util import UiUtil
from com.github.dm0896665.main.util.ui_objects import UiObjects

if __name__ == "__main__":
    faulthandler.enable()
    UiUtil()
    UiUtil.change_screen(MainMenu())
    UiObjects.window.setWindowIcon(QIcon(UiUtil.load_image_map("icon.png")))
    UiObjects.window.show()
    UiObjects.app.exec()