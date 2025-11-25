import sys
import os
from PyQt6 import QtCore
from PyQt6.QtWidgets import QApplication, QMainWindow, QFileDialog, QMessageBox, QTableWidgetItem
from ui.main_window import Ui_MainWindow
from db_bk import SessionLocal, init_db
from models_bk import Part
import csv


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.ui.parts_table.setHorizontalHeaderLabels([
            "ID", "Артикул", "Название", "Описание",
            "Цена", "Количество", "Фото"
        ])

        self.setWindowTitle("Inventory & Service Manager")

        init_db()
        self.session = SessionLocal()

        self.settings_path = "settings.ini"
        self.settings = QtCore.QSettings(
            self.settings_path, QtCore.QSettings.Format.IniFormat)

        self.load_settings()
        self.apply_theme()

        self.ui.menuList.currentRowChanged.connect(
            self.ui.stackedWidget.setCurrentIndex
        )

        self.ui.add_btn.clicked.connect(self.add_part)
        self.ui.delete_btn.clicked.connect(self.delete_p)
        self.ui.save_btn.clicked.connect(self.save_to_db)
        self.ui.load_btn.clicked.connect(self.load_from_db)
        self.ui.photo_btn.clicked.connect(self.add_photo)

        self.ui.actionExport.triggered.connect(self.export_csv)
        self.ui.actionExit.triggered.connect(self.close)
        self.ui.actionAbout.triggered.connect(self.about_app)

        self.ui.theme_combo.currentIndexChanged.connect(self.change_theme)

        self.load_from_db()
        self.update_stats()

    def change_theme(self):
        theme = self.ui.theme_combo.currentText()
        if theme == "Светлая":
            self.setStyleSheet("""
                QMainWindow { background-color: #f2f2f2; color: #fff; }
                QLabel, QLineEdit, QTableWidget, QPushButton, QComboBox {
                    background-color: #b0b3b5; color: #fff; border: 1px solid #555;
                }
                QTableWidget::item:selected { background-color: #a09898; }
                QPushButton:hover { background-color: #9b8c8c; }
            """)
        else:
            self.setStyleSheet("""
                QMainWindow { background-color: #2b2b2b; color: #fff; }
                QLabel, QLineEdit, QTableWidget, QPushButton, QComboBox {
                    background-color: #3c3f41; color: #fff; border: 1px solid #555;
                }
                QTableWidget::item:selected { background-color: #5a5a5a; }
                QPushButton:hover { background-color: #505050; }
            """)

    def load_settings(self):
        theme = self.settings.value("theme", "Светлая")
        index = self.ui.theme_combo.findText(theme)
        if index != -1:
            self.ui.theme_combo.setCurrentIndex(index)

    def apply_theme(self):
        theme = self.ui.theme_combo.currentText()

        if theme == "Тёмная":
            self.setStyleSheet("""
                QWidget {
                    background-color: #2b2b2b;
                    color: #e0e0e0;
                    font-size: 11pt;
                }
                QLineEdit, QComboBox, QTableWidget, QTextEdit {
                    background: #3a3a3a;
                    color: #e0e0e0;
                    border: 1px solid #555;
                }
                QPushButton {
                    background-color: #444;
                    color: #fff;
                    border: 1px solid #666;
                    padding: 4px;
                }
                QPushButton:hover {
                    background-color: #555;
                }
                QHeaderView::section {
                    background-color: #444;
                    color: #fff;
                }
            """)
        else:
            self.setStyleSheet("")  # default Qt theme

    def add_part(self):
        r = self.ui.parts_table.rowCount()
        self.ui.parts_table.insertRow(r)

        for q in range(7):
            if not self.ui.parts_table.item(r, q):
                self.ui.parts_table.setItem(r, q, QTableWidgetItem(""))
        self.update_stats()

    def delete_p(self):
        r = self.ui.parts_table.currentRow()
        if r != -1:
            self.ui.parts_table.removeRow(r)
        self.update_stats()
        
    def add_photo(self):
        r = self.ui.parts_table.currentRow()
        if r == -1:
            QMessageBox.warning(self, "Ошибка", "Сначала выберите строку.")
            return

        file, _ = QFileDialog.getOpenFileName(
            self, "Выбрать фото", "", "Изображения (*.png *.jpg *.jpeg)"
        )

        if file:
            self.ui.parts_table.setItem(r, 6, QTableWidgetItem(file))

    def save_to_db(self):
        self.session.query(Part).delete()

        for i in range(self.ui.parts_table.rowCount()):
            row = [self.ui.parts_table.item(i, c) for c in range(7)]

            def txt(item): return item.text() if item else ""

            part = Part(
                id=int(txt(row[0])) if txt(row[0]).isdigit() else None,
                code=txt(row[1]),
                name=txt(row[2]),
                description=txt(row[3]),
                price=float(txt(row[4])) if txt(row[4]) else 0.0,
                quantity=int(txt(row[5])) if txt(row[5]) else 0,
                photo=txt(row[6]),
            )

            self.session.add(part)

        self.session.commit()
        QMessageBox.information(self, "Готово", "Данные сохранены.")

    def load_from_db(self):
        self.ui.parts_table.setRowCount(0)
        s = self.session.query(Part).all()

        for p in s:
            r = self.ui.parts_table.rowCount()
            self.ui.parts_table.insertRow(r)

            self.ui.parts_table.setItem(r, 0, QTableWidgetItem(str(p.id)))
            self.ui.parts_table.setItem(r, 1, QTableWidgetItem(p.code))
            self.ui.parts_table.setItem(r, 2, QTableWidgetItem(p.name))
            self.ui.parts_table.setItem(r, 3, QTableWidgetItem(p.description))
            self.ui.parts_table.setItem(r, 4, QTableWidgetItem(str(p.price)))
            self.ui.parts_table.setItem(
                r, 5, QTableWidgetItem(str(p.quantity)))
            self.ui.parts_table.setItem(r, 6, QTableWidgetItem(p.photo))

    def export_csv(self):
        path, _ = QFileDialog.getSaveFileName(
            self, "Сохранить CSV", "", "CSV (*.csv)"
        )
        if not path:
            return

        with open(path, "w", newline="", encoding="utf-8") as f:
            wr = csv.writer(f)
            wr.writerow(["ID", "Артикул", "Название", "Описание",
                         "Цена", "Количество", "Фото"])

            for i in range(self.ui.parts_table.rowCount()):
                row = [
                    self.ui.parts_table.item(i, j).text()
                    if self.ui.parts_table.item(i, j)
                    else ""
                    for j in range(7)
                ]
                wr.writerow(row)

        QMessageBox.information(self, "OK", "Экспорт завершён.")

    def about_app(self):
        QMessageBox.information(
            self,
            "О программе",
            "Inventory & Service Manager\nВерсия 1.0"
        )

    def update_stats(self):
        total_items = 0
        total_cost = 0.0

        rows = self.ui.parts_table.rowCount()

        for r in range(rows):
            qty_item = self.ui.parts_table.item(r, 5)
            price_item = self.ui.parts_table.item(r, 4)

            if qty_item and price_item:
                try:
                    qty = int(qty_item.text())
                    price = float(price_item.text())
                except ValueError:
                    continue

                total_items += qty
                total_cost += qty * price

        avg_price = (total_cost / total_items) if total_items > 0 else 0

        self.ui.label_total_parts.setText(str(total_items))
        self.ui.label_total_value.setText(f"{total_cost:.2f}")
        self.ui.label_avg_price.setText(f"{avg_price:.2f}")



if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = MainWindow()
    win.show()
    sys.exit(app.exec())
