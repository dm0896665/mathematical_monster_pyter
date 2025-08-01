from com.github.dm0896665.main.ui.screens.main_menu import MainMenu
from com.github.dm0896665.main.util.ui_util import UiUtil

if __name__ == "__main__":
    UiUtil()
    UiUtil.change_screen(MainMenu())
    UiUtil.window.show()
    UiUtil.app.exec()