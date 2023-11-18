from PyQt5 import QtWidgets, uic
from PyQt5.QtCore import QObject, QThread, pyqtSignal
import sys
import json
from bs4 import BeautifulSoup
from requests import get
import os.path
from win10toast_click import ToastNotifier
import webbrowser
import time


page_of_main = 0
number_of_main = []
dict_of_flats = {}
new_url = []


def remove_useless_words(text):
    text = text.replace("do negocjacji", "").replace("Odświeżono dnia", "").replace("zł", "").replace(" ", "")
    return text


def urls_difference(dict0, dict1):
    difference = set(dict0) - set(dict1)
    content = []
    if difference != set():
        for element in difference:
            content.append(element)
        print_new_links(content)
        return difference
    else:
        return False


def open_url():
    for elements in new_url:
        try:
            webbrowser.open_new("https://www.olx.pl" + elements)
        except:
            print('Failed to open URL. Unsupported variable type.')


def new_url_not():
    toaster = ToastNotifier()
    communicate_url = ""
    for element in new_url:
        communicate_url += element + " "
    toaster.show_toast("Znaleziono nowe ogłoszenia!", "kliknij by wyświetlić", duration=5, threaded=True,
                       callback_on_click=open_url)


def print_new_links(new_flats):
    content = ""
    for key in new_flats:
        if "otodom" in key:
            content = content + f"<a href='"  + key + "'>link</a>\n"

        else :
            content = content + f"<a href='"+"https://www.olx.pl"+key+"'>link</a>\n"
    window.print_label_2(content)


def scrap(url):
    global new_url
    main_url = url
    page = get(main_url)
    bs = BeautifulSoup(page.content, "html.parser")
    for pagination in bs.find_all("a", class_="css-1mi714g"):
        number_of_main.append(pagination.text)
    for _ in number_of_main:
        page = get(main_url)
        bs = BeautifulSoup(page.content, "html.parser")
        for offer in bs.find_all("a", class_="css-1bbgabe"):
            link = offer["href"]
            parameter = []
            parameter.append(remove_useless_words(offer.find("p", class_="css-wpfvmn-Text eu5v0x0").text))
            parameter.append(remove_useless_words(offer.find("p", class_="css-p6wsjo-Text eu5v0x0").text))
            dict_of_flats[link] = parameter
    file_in = dict_of_flats
    if os.path.exists("offers.json"):
        with open("offers.json", "r") as file:
            file_out = json.load(file)

        if file_out != file_in:
            print("overwrited")
            window.print_label("Znaleziono !")

            with open("offers.json", "w") as file:
                file.write(json.dumps(file_in))
                new_url = urls_difference(file_in, file_out)
                if new_url:
                    new_url_not()
        else:
            window.print_label("Wyszukuje...")
            print("kontynuuje...")

    else:
        with open("offers.json", "w") as file:
            file.write(json.dumps(file_in))


def start_searching(url_input):
    print("rozpoczęto")
    while True:
        scrap(str(url_input))
        time.sleep(5)


#      ---------- Ui here ---------
class Worker(QObject):
    finished = pyqtSignal()
    progress = pyqtSignal(int)

    def run(self):
        # """Long-running task."""
        urlll = window.input.toPlainText()
        start_searching(urlll)
        self.finished.emit()


class Ui(QtWidgets.QMainWindow):
    def __init__(self):
        super(Ui, self).__init__()
        uic.loadUi("OLX-scrap.ui", self)
        self.show()
        self.pushButton.clicked.connect(self.runLongTask)
        self.input = self.findChild(QtWidgets.QTextEdit, "textEdit")
        self.label1 = self.findChild(QtWidgets.QLabel, "label")
        self.label2 = self.findChild(QtWidgets.QLabel, "label2")

    def print_label(self, notif):
        info = notif
        self.label1.setText(info)
        self.label.repaint()


    def print_label_2(self, notif):
        info = notif
        self.label2.setText(info)
        self.label.repaint()

    def after_click(self):
        info = "Rozpoczęto wyszukiwanie..."
        self.label1.setText(info)
        self.label.repaint()
        # url = self.input.toPlainText()
        # print(url)
        # start_searching(url)

    def runLongTask(self):
        # Step 2: Create a QThread object
        print("start")
        self.thread = QThread()
        # Step 3: Create a worker object
        self.worker = Worker()
        # Step 4: Move worker to the thread
        self.worker.moveToThread(self.thread)
        # Step 5: Connect signals and slots
        self.thread.started.connect(self.worker.run)
        self.worker.finished.connect(self.thread.quit)
        self.worker.finished.connect(self.worker.deleteLater)
        self.thread.finished.connect(self.thread.deleteLater)
        # do usuniecia
        # Step 6: Start the thread
        self.thread.start()

        # Final resets
        self.pushButton.setEnabled(False)



app = QtWidgets.QApplication(sys.argv)
app.processEvents()
window = Ui()

app.exec_()
