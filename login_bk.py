import sys
import sqlite3
from PyQt6 import QtWidgets
from ui.login_form import Ui_Dialog
from ui.register_form import Ui_RegisterDialog
from main_window_bk import MainWindow


class RegisterWindow(QtWidgets.QDialog):
    def __init__(self):
        super().__init__()
        self.ui = Ui_RegisterDialog()
        self.ui.setupUi(self)
        self.setWindowTitle("Регистрация")

        self.ui.pasw_lineEdit.setEchoMode(
            QtWidgets.QLineEdit.EchoMode.pasw)
        self.ui.register_pushButton.clicked.connect(self.register_user)
        self.ui.cancel_pushButton.clicked.connect(self.close)

    def register_user(self):
        login = self.ui.login_lineEdit.text().strip()
        pasw = self.ui.pasw_lineEdit.text().strip()

        if not login or not pasw:
            self.ui.status_label.setText("Заполните все поля!")
            return

        conn = sqlite3.connect("service.db")
        cur = conn.cursor()

        try:
            cur.execute(
                "INSERT INTO users (login, pasw) VALUES (?, ?)", (login, pasw))
            conn.commit()
            self.ui.status_label.setText("Регистрация успешна!")
        except sqlite3.IntegrityError:
            self.ui.status_label.setText("Такой пользователь уже существует!")
        finally:
            conn.close()


class LoginWindow(QtWidgets.QDialog):
    def __init__(self):
        super().__init__()
        self.ui = Ui_Dialog()
        self.ui.setupUi(self)
        self.setWindowTitle("Авторизация")

        self.ui.pasw_lineEdit.setEchoMode(QtWidgets.QLineEdit.EchoMode.pasw)
        self.ui.status_label.setVisible(False)

        self.ui.enter_pushButton.clicked.connect(self.login)
        self.ui.cancel_pushButton.clicked.connect(self.close)
        self.ui.register_pushButton.clicked.connect(self.open_register)

    def login(self):
        login = str(self.ui.login_lineEdit.text().strip())
        pasw = str(self.ui.pasw_lineEdit.text().strip())

        if self.check_user_in_db(login, pasw):
            self.ui.status_label.setVisible(False)
            self.accept()
        else:
            self.ui.status_label.setVisible(True)

    def check_user_in_db(self, login, pasw) -> bool:
        try:
            conn = sqlite3.connect("service.db")
            cur = conn.cursor()
            cur.execute(
                "SELECT * FROM users WHERE login=? AND pasw=?", (login, pasw))
            user = cur.fetchone()
            conn.close()
            return user is not None
        except Exception as e:
            print("Ошибка при проверке пользователя:", e)
            return False

    def open_register(self):
        reg_window = RegisterWindow()
        reg_window.exec()


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)

    conn = sqlite3.connect("service.db")
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            login TEXT UNIQUE,
            pasw TEXT
        )
    """)
    conn.commit()
    conn.close()

    login_window = LoginWindow()
    if login_window.exec():
        main_window = MainWindow()
        main_window.show()
        sys.exit(app.exec())
    else:
        sys.exit(0)
