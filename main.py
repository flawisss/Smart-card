import sys
import sqlite3
from PIL import Image
from PyQt5 import uic
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QApplication, QMainWindow, QTableWidgetItem, QFileDialog, QLabel, QMessageBox


SIZE = [460, 270]
QCOORD = [590, 170]
ACOORD = [590, 540]


class Rememberer(QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi('rememberer.ui', self)
        self.conn = sqlite3.connect('decks.sqlite')
        self.cursor = self.conn.cursor()
        Rememberer.setFixedSize(self, 1200, 900)

        self.counter = 0
        self.qpic = None
        self.apic = None

        self.all_objects = [self.add_apic_btn, self.add_qpic_btn, self.answer_browser, self.answer_label,
                            self.answer_text, self.decks_box, self.decks_label, self.delete_btn, self.go_btn,
                            self.repeat_btn, self.learn_btn, self.make_card_btn, self.name_of_deck_label,
                            self.name_of_deck_text, self.question_browser, self.question_label, self.question_text,
                            self.show_answer_btn, self.table_of_decks, self.hard_btn, self.normal_btn]
        self.show_decks_menu()

        self.decks_btn.clicked.connect(self.show_decks_menu)
        self.make_deck_btn.clicked.connect(self.show_make_card_menu)
        self.stats_btn.clicked.connect(self.show_stats_menu)
        self.learn_btn.clicked.connect(self.learn)
        self.make_card_btn.clicked.connect(self.make_card)
        self.delete_btn.clicked.connect(self.delete)
        self.add_qpic_btn.clicked.connect(self.add_qpic)
        self.add_apic_btn.clicked.connect(self.add_apic)
        self.show_answer_btn.clicked.connect(self.show_answer)
        self.go_btn.clicked.connect(self.go)
        self.hard_btn.clicked.connect(self.hard)
        self.normal_btn.clicked.connect(self.normal)
        self.repeat_btn.clicked.connect(self.repeat)

    def show_menu(self, menu):
        for object in self.all_objects:
            if object not in menu:
                object.hide()
            else:
                object.show()

    def show_decks_menu(self):
        self.reload()
        self.load_box()
        decks_menu_objects = [self.decks_box, self.decks_label, self.delete_btn, self.learn_btn]
        self.show_menu(decks_menu_objects)

    def show_make_card_menu(self):
        self.reload()
        make_card_menu_objects = [self.add_apic_btn, self.add_qpic_btn, self.answer_label, self.answer_text,
                                  self.make_card_btn, self.name_of_deck_label, self.name_of_deck_text,
                                  self.question_label, self.question_text]
        self.show_menu(make_card_menu_objects)

    def show_learn_menu(self):
        show_learn_menu_objects = [self.answer_browser, self.answer_label, self.question_browser,
                                   self.question_label, self.show_answer_btn]
        self.show_menu(show_learn_menu_objects)

    def show_stats_menu(self):
        self.reload()
        self.load_table()
        show_stats_menu_objects = [self.table_of_decks]
        self.show_menu(show_stats_menu_objects)

    def load_table(self):
        labels = ['Имя', 'Всего карточек', 'Выучено']
        decks = self.cursor.execute(f"""SELECT * FROM decks""").fetchall()

        self.table_of_decks.setRowCount(len(decks))
        self.table_of_decks.setColumnCount(len(labels))
        self.table_of_decks.setHorizontalHeaderLabels(labels)
        self.table_of_decks.setColumnWidth(0, 500)
        self.table_of_decks.setColumnWidth(1, 200)
        self.table_of_decks.setColumnWidth(2, 200)

        for i in range(len(decks)):
            self.table_of_decks.setItem(i, 0, QTableWidgetItem(decks[i][0]))
            self.table_of_decks.setItem(i, 1, QTableWidgetItem(str(decks[i][1])))
            self.table_of_decks.setItem(i, 2, QTableWidgetItem(str(decks[i][2])))

    def make_card(self):
        qtext = self.question_text.toPlainText()
        atext = self.answer_text.toPlainText()
        deck_name = self.name_of_deck_text.text()
        # добавляем в бд нашу карточку
        self.cursor.execute(f"""INSERT INTO cards(deck_name, qtext, qpic, atext, apic) VALUES('{deck_name}', '{qtext}',
         '{self.qpic}', '{atext}', '{self.apic}')""")
        self.conn.commit()

        list_of_deck_names = list(map(lambda x: x[0], self.cursor.execute(f"""SELECT deck FROM decks""").fetchall()))
        # если такая колода уже сущестует
        if deck_name in list_of_deck_names:
            self.cursor.execute(f"""UPDATE decks
                                    SET all_cards = all_cards + 1
                                    WHERE deck = '{deck_name}'""")
        # если такой колоды не существует
        else:
            self.cursor.execute(f"""INSERT INTO decks VALUES('{deck_name}', 1, 0)""")
        self.conn.commit()
        # откат
        self.question_text.clear()
        self.answer_text.clear()
        if self.qpic:
            self.qimage.hide()
            self.qpic = None
        if self.apic:
            self.aimage.hide()
            self.apic = None

    def delete(self):
        deck = self.decks_box.currentText()
        self.cursor.execute(f"""DELETE FROM decks WHERE deck == '{deck}'""")
        self.conn.commit()
        self.cursor.execute(f"""DELETE FROM cards WHERE deck_name == '{deck}'""")
        self.conn.commit()
        self.load_table()
        self.load_box()

    def add_qpic(self):
        # редактируем размер картинки
        self.qpic = QFileDialog.getOpenFileName(
            self, 'Выбрать картинку', '',
            'Картинка (*.jpg);;Все файлы (*)')[0]
        img = Image.open(self.qpic)
        img.thumbnail(size=(SIZE[0], SIZE[1]))
        img.save(self.qpic)
        # отображаем картинку на экране
        self.qpixmap = QPixmap(self.qpic)
        self.qimage = QLabel(self)
        self.qimage.move(QCOORD[0], QCOORD[1])
        self.qimage.resize(SIZE[0], SIZE[1])
        self.qimage.setPixmap(self.qpixmap)
        self.qimage.show()

    def add_apic(self):
        self.apic = QFileDialog.getOpenFileName(
            self, 'Выбрать картинку', '',
            'Картинка (*.jpg);;Все файлы (*)')[0]
        # редактируем размер картинки
        img = Image.open(self.apic)
        img.thumbnail(size=(SIZE[0], SIZE[1]))
        img.save(self.apic)
        # отображаем картинку на экране
        self.apixmap = QPixmap(self.apic)
        self.aimage = QLabel(self)
        self.aimage.move(ACOORD[0], ACOORD[1])
        self.aimage.resize(SIZE[0], SIZE[1])
        self.aimage.setPixmap(self.apixmap)
        self.aimage.show()

    def learn(self):
        self.show_learn_menu()
        deck_name = self.decks_box.currentText()
        deck_data = sorted(self.cursor.execute(f"""SELECT * FROM cards WHERE deck_name = '{deck_name}'""").fetchall(),
                           key=lambda x: x[5])
        learn_stats = list(map(lambda x: x[5], deck_data))
        if all(level == 3 for level in learn_stats):
            self.show_decks_menu()
            msg = QMessageBox()
            msg.setWindowTitle("Поздравляем!")
            msg.setText("Вы выучили всю колоду карт!")
            msg.setIcon(QMessageBox.Information)

            msg.exec_()
        else:
            card_data = list(deck_data[0])
            self.question_browser.setText(card_data[1])
            if card_data[2] != 'None':
                self.qpic = card_data[2]
                # отображаем картинку на экране
                self.qpixmap = QPixmap(self.qpic)
                self.qimage = QLabel(self)
                self.qimage.move(QCOORD[0], QCOORD[1])
                self.qimage.resize(SIZE[0], SIZE[1])
                self.qimage.setPixmap(self.qpixmap)
                self.qimage.show()

    def show_answer(self):
        question = self.question_browser.toPlainText()
        card_data = list(*self.cursor.execute(f"""SELECT * FROM cards WHERE qtext = '{question}'""").fetchall())
        self.repeat_btn.show()
        self.go_btn.show()
        self.normal_btn.show()
        self.hard_btn.show()
        self.answer_browser.setText(card_data[3])
        if card_data[4] != 'None':
            self.apic = card_data[4]
            # отображаем картинку на экране
            self.apixmap = QPixmap(self.apic)
            self.aimage = QLabel(self)
            self.aimage.move(QCOORD[0], QCOORD[1])
            self.aimage.resize(SIZE[0], SIZE[1])
            self.aimage.setPixmap(self.apixmap)
            self.aimage.show()

    def load_box(self):
        self.decks_box.clear()
        deck_names = list(map(lambda x: x[0], self.cursor.execute(f"""SELECT deck FROM decks""").fetchall()))
        for deck_name in deck_names:
            self.decks_box.addItem(deck_name)

    def repeat(self):
        self.repeat_btn.hide()
        self.go_btn.hide()
        self.normal_btn.hide()
        self.hard_btn.hide()
        self.answer_browser.clear()

    def go(self):
        # откат
        if self.qpic:
            self.qimage.hide()
            self.qpic = None
        if self.apic:
            self.aimage.hide()
            self.apic = None
        self.answer_browser.clear()
        # обновление статистики карточки и колоды
        question = self.question_browser.toPlainText()
        self.cursor.execute(f"""UPDATE cards
        SET learn_level = 3
        WHERE qtext = '{question}'""")
        deck_name = self.decks_box.currentText()
        self.cursor.execute(f"""UPDATE decks
        SET learned_cards = learned_cards + 1
        WHERE deck = '{deck_name}'""")
        self.conn.commit()
        # зауск следующей карты
        self.counter += 1
        self.learn()

    def hard(self):
        # откат
        if self.qpic:
            self.qimage.hide()
            self.qpic = None
        if self.apic:
            self.aimage.hide()
            self.apic = None
        self.answer_browser.clear()
        # обновление статистики карточки
        question = self.question_browser.toPlainText()
        self.cursor.execute(f"""UPDATE cards
        SET learn_level = 1
        WHERE qtext = '{question}'""")
        self.conn.commit()
        # зауск следующей карты
        self.counter += 1
        self.learn()

    def normal(self):
        # откат
        if self.qpic:
            self.qimage.hide()
            self.qpic = None
        if self.apic:
            self.aimage.hide()
            self.apic = None
        self.answer_browser.clear()
        # обновление статистики карточки
        question = self.question_browser.toPlainText()
        self.cursor.execute(f"""UPDATE cards
        SET learn_level = 2
        WHERE qtext = '{question}'""")
        self.conn.commit()
        # зауск следующей карты
        self.counter += 1
        self.learn()

    def reload(self):
        if self.qpic:
            self.qimage.hide()
            self.qpic = None
        if self.apic:
            self.aimage.hide()
            self.apic = None
        self.counter = 0


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = Rememberer()
    ex.show()
    sys.exit(app.exec_())
