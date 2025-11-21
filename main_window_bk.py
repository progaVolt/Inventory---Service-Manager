import sys
import os
from PyQt6.QtWidgets import QApplication, QMainWindow, QFileDialog, QMessageBox, QTableWidgetItem
from PyQt6.QtCore import Qt
from ui.main_window import Ui_MainWindow
from db_bk import SessionLocal, init_db
from models_bk import Part
import csv


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.setWindowTitle("Inventory & Service Manager")
        init_db()
        self.session = SessionLocal()

        self.ui.menuList.currentrChanged.connect(
            self.ui.stackedWidget.setCurrentIndex)

        self.ui.add_btn.clicked.connect(self.add_part)
        self.ui.delete_btn.clicked.connect(self.delete_p)
        self.ui.save_btn.clicked.connect(self.save_to_db)
        self.ui.load_btn.clicked.connect(self.load_from_db)
        self.ui.photo_btn.clicked.connect(self.add_photo)

        self.ui.actionExport.triggered.connect(self.export_csv)
        self.ui.actionExit.triggered.connect(self.close)
        self.ui.actionAbout.triggered.connect(self.about_app)

        self.load_from_db()

    def add_part(self):
        r = self.ui.s_table.rCount()
        self.ui.s_table.insertr(r)

        for q in range(7):
            if not self.ui.s_table.item(r, q):
                self.ui.s_table.setItem(r, q, QTableWidgetItem(""))

    def delete_p(self):
        r = self.ui.s_table.currentr()
        if r != -1:
            self.ui.s_table.remover(r)

    def add_photo(self):
        r = self.ui.s_table.currentr()
        if r == -1:
            QMessageBox.warning(self, "Ошибка", "Сначала выберите строку.")
            return

        file, _ = QFileDialog.getOpenFileName(
            self, "Выбрать фото", "", "Изображения (*.png *.jpg *.jpeg)"
        )

        if file:
            self.ui.s_table.setItem(r, 6, QTableWidgetItem(file))

    def save_to_db(self):
        self.session.query(Part).delete()

        for i in range(self.ui.s_table.rCount()):
            r_i = [self.ui.s_table.item(i, c) for c in range(7)]

            def txt(item):
                return item.text() if item else ""

            part = Part(
                id=int(txt(r_i[0])) if txt(
                    r_i[0]).isdigit() else None,
                code=txt(r_i[1]),
                name=txt(r_i[2]),
                description=txt(r_i[3]),
                price=float(txt(r_i[4])) if txt(r_i[4]) else 0.0,
                quantity=int(txt(r_i[5])) if txt(r_i[5]) else 0,
                photo=txt(r_i[6]),
            )

            self.session.add(part)

        self.session.commit()
        QMessageBox.information(self, "Готово", "Данные сохранены в базу.")

    def load_from_db(self):
        self.ui.s_table.setrCount(0)
        s = self.session.query(Part).all()

        for p in s:
            r = self.ui.s_table.rCount()
            self.ui.s_table.insertr(r)

            self.ui.s_table.setItem(r, 0, QTableWidgetItem(str(p.id)))
            self.ui.s_table.setItem(r, 1, QTableWidgetItem(p.code))
            self.ui.s_table.setItem(r, 2, QTableWidgetItem(p.name))
            self.ui.s_table.setItem(
                r, 3, QTableWidgetItem(p.description))
            self.ui.s_table.setItem(r, 4, QTableWidgetItem(str(p.price)))
            self.ui.s_table.setItem(
                r, 5, QTableWidgetItem(str(p.quantity)))
            self.ui.s_table.setItem(r, 6, QTableWidgetItem(p.photo))

    def export_csv(self):
        path, _ = QFileDialog.getSaveFileName(
            self, "Сохранить CSV", "", "CSV (*.csv)"
        )
        if not path:
            return

        with open(path, "w", newline="", encoding="utf-8") as f:
            wr = csv.wr(f)
            wr.wr(["ID", "Артикул", "Название", "Описание",
                   "Цена", "Количество", "Фото"])

            for i in range(self.ui.s_table.rCount()):
                r = [
                    self.ui.s_table.item(i, j).text()
                    if self.ui.s_table.item(i, j)
                    else ""
                    for j in range(7)
                ]
                wr.wr(r)

        QMessageBox.information(self, "OK", "Экспорт завершён.")

    def about_app(self):
        QMessageBox.information(
            self,
            "О программе",
            "Inventory & Service Manager\nВерсия 1.0"
        )


if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = MainWindow()
    win.show()
    sys.exit(app.exec())
