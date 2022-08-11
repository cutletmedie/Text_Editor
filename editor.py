import sys
import os
from PyQt5 import QtWidgets, QtCore, QtGui
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtPrintSupport import *


class Window(QMainWindow):
    """Main Window."""
    def __init__(self, full_filename=None):
        super(Window, self).__init__()
        self.app_name = "Текстовый редактор"
        self.text_edit = QTextEdit(self)
        self.status = QStatusBar()
        self.init_file_settings(full_filename)
        self.initUI()

    def init_file_settings(self, full_filename=None):
        if full_filename:
            self.filename = "{}".format(full_filename.split('.')[0])
            with open(full_filename, 'r') as f:
                self.path = os.path.realpath(f.name)
                text = f.read()
                self.text_edit.setPlainText(text)
            self.filename = "{}".format(full_filename.split('.')[0])
            self.file_opened = True
            self.changed = False
            self.change_title()
        else:
            self.new_file(True)

    def initUI(self):
        self.resize(800, 600)

        self.setCentralWidget(self.text_edit)
        self.text_edit.setTabStopWidth(33)
        self.text_edit.setLineWrapMode(0)
        if not self.changed:
            self.text_edit.textChanged.connect(lambda: self.change_title(True))

        self.status.addPermanentWidget(QLabel("Как же я устала, кто бы знал"))
        self.cursor_position()
        self.status.messageChanged.connect(self.cursor_position)
        self.text_edit.cursorPositionChanged.connect(self.cursor_position)
        self.setStatusBar(self.status)

        self.init_combobox()
        self.init_menubar()

    def init_menubar(self):
        menu_bar = self.menuBar()

        file_menu = menu_bar.addMenu("&Файл")

        file_menu.addAction(self.new_action)
        file_menu.addAction(self.open_action)
        file_menu.addAction(self.save_action)
        file_menu.addAction(self.saveas_action)
        file_menu.addSeparator()
        file_menu.addAction(self.exit_action)

        edit_menu = menu_bar.addMenu("&Правка")

        edit_menu.addAction(self.undo_action)
        edit_menu.addSeparator()
        edit_menu.addAction(self.cut_action)
        edit_menu.addAction(self.copy_action)
        edit_menu.addAction(self.paste_action)
        edit_menu.addAction(self.clear_action)

        format_menu = menu_bar.addMenu("&Формат")

        format_menu.addAction(self.wrap_action)

    def init_combobox(self):
        # Выпадающий список Файла
        self.new_action = QAction("Создать", self)
        self.new_action.setShortcut("CTRL+N")
        self.new_action.triggered.connect(self.new_file)

        self.open_action = QAction("Открыть...", self)
        self.open_action.setShortcut("CTRL+O")
        self.open_action.triggered.connect(self.open_file)

        self.save_action = QAction("Сохранить", self)
        self.save_action.setShortcut("CTRL+S")
        self.save_action.triggered.connect(self.save_file)

        self.saveas_action = QAction("Сохранить как...", self)
        self.saveas_action.setShortcut("CTRL+SHIFT+S")
        self.saveas_action.triggered.connect(self.saveas_file)

        self.exit_action = QAction("Выход", self)
        self.exit_action.triggered.connect(self.closeEvent)

        # Выпадающий список Правки
        self.undo_action = QAction("Отменить", self)
        self.undo_action.setShortcut("CTRL+Z")
        self.undo_action.triggered.connect(self.text_edit.undo)

        self.cut_action = QAction("Вырезать", self)
        self.cut_action.setShortcut("CTRL+X")
        self.cut_action.triggered.connect(self.text_edit.cut)

        self.copy_action = QAction("Копировать", self)
        self.copy_action.setShortcut("CTRL+C")
        self.copy_action.triggered.connect(self.text_edit.copy)

        self.paste_action = QAction("Вставить", self)
        self.paste_action.setShortcut("CTRL+V")
        self.paste_action.triggered.connect(self.text_edit.paste)

        self.clear_action = QAction("Очистить", self)
        self.clear_action.triggered.connect(self.text_edit.clear)

        # Выпадающий список Формата
        self.wrap_action = QAction("Перенос по словам", self)
        self.wrap_action.setCheckable(True)
        self.wrap_action.setChecked(False)
        self.wrap_action.triggered.connect(lambda:
                                           self.text_edit.setLineWrapMode(
                                               (self.text_edit.lineWrapMode()+1) % 2))

    def change_title(self, changed=False):
        changes = ""
        if changed:
            self.changed = True
            changes = "*"
        separator = " – "
        self.setWindowTitle(self.app_name + separator + self.filename + changes)

    def cursor_position(self):
        cursor = self.text_edit.textCursor()

        line = cursor.blockNumber() + 1
        column = cursor.columnNumber() + 1

        self.status.showMessage("Стр {}, стлб {}".format(line, column))

    def closeEvent(self, event):
        if self.changed:
            if not self.changes_dialog():
                event.accept()
            else:
                event.ignore()
                if not self.changed:
                    event.accept()
        else:
            print("hi")
            event.accept()

    def new_file(self, discard_changes=False):
        if discard_changes or not self.changed:
            self.path = None
            self.filename = "Безымянный"
            self.file_opened = False
            self.text_edit.clear()
            self.changed = False
            self.change_title()
        else:
            if not self.changes_dialog():
                self.new_file(True)
            elif not self.changed:
                self.new_file()

    def open_file(self, discard_changes=False):
        if not self.changed or discard_changes:
            path = QFileDialog.getOpenFileName(self, "Открыть файл", "", "Текстовый файл (*.txt)")[0]
            if path:
                self.path = path
                with open(path, 'r') as file:
                    text = file.read()
                    self.text_edit.setPlainText(text)
                    file.close()
                self.filename = path[path.rfind('/') + 1:path.rfind(".")]
                self.change_title()
                self.file_opened = True
                self.changed = False
        else:
            if not self.changes_dialog():
                self.open_file(True)

    def save_file(self):
        if self.file_opened:
            with open(self.path, 'w') as file:
                text = str(self.text_edit.toPlainText())
                file.write(text)
                file.close()
            self.filename = self.path[self.path.rfind('/')+1:self.path.rfind(".")]
            self.change_title()
            self.changed = False
        else:
            self.saveas_file()

    def saveas_file(self):
        path = QFileDialog.getSaveFileName(self, "Открыть файл", "", "Текстовый файл (*.txt)")[0]
        if path:
            self.path = path
            with open(path, 'w') as file:
                text = str(self.text_edit.toPlainText())
                file.write(text)
            self.filename = path[path.rfind('/') + 1:path.rfind(".")]
            self.change_title()
            self.file_opened = True
            self.changed = False

    def changes_dialog(self):
        choice = QMessageBox()
        choice.setWindowTitle('Блокнот')
        choice.setIcon(QMessageBox.Question)
        choice.setText('Вы хотите сохранить изменения в файле "{}"?'.format(self.filename))
        choice.setStandardButtons(QMessageBox.Yes | QMessageBox.No | QMessageBox.Cancel)
        buttonY = choice.button(QMessageBox.Yes)
        buttonY.setText('Сохранить')
        buttonN = choice.button(QMessageBox.No)
        buttonN.setText('Не сохранять')
        buttonClose = choice.button(QMessageBox.Cancel)
        buttonClose.setText('Отменить')
        choice.exec_()

        if choice.clickedButton() == buttonY:
            self.save_file()
        elif choice.clickedButton() == buttonN:
            return False
        return True


def application():
    app = QApplication(sys.argv)
    if len(sys.argv) == 2:
        window = Window(sys.argv[1])
    elif len(sys.argv) == 1:
        window = Window()
    else:
        print("Ты че, дурак, блин?")
        return
    window.show()
    app.exec_()


if __name__ == "__main__":
    application()
