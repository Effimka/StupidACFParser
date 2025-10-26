from PyQt5 import QtCore, QtGui, QtWidgets
import config
from seleniumParser import StartSelenim, DriverShutdown, ParseData
from translator import initTranslator

class WorkerThread(QtCore.QThread):
    log = QtCore.pyqtSignal(str)
    error = QtCore.pyqtSignal(str)
    finished = QtCore.pyqtSignal(object)

    def __init__(self, target, *args, **kwargs):
        super().__init__()
        self.target = target
        self.args = args
        self.kwargs = kwargs
        self.fallback_fn = None

    def run(self):
        try:
            # Добавляем emit_log в kwargs если поддерживается
            if "emit_log" in self.target.__code__.co_varnames:
                self.kwargs["emit_log"] = self.log.emit
            result = self.target(*self.args, **self.kwargs)
            self.finished.emit(result)
        except Exception as e:
            import traceback
            tb = traceback.format_exc()
            self.error.emit(f"Ошибка: {e}\n{tb}")
            if self.fallback_fn:
                self.fallback_fn()


class Ui_AutoTranslatorWnd(object):
    def setupUi(self, AutoTranslatorWnd):
        AutoTranslatorWnd.setObjectName("AutoTranslatorWnd")
        AutoTranslatorWnd.resize(538, 748)
        self.Login_input = QtWidgets.QTextEdit(AutoTranslatorWnd)
        self.Login_input.setEnabled(True)
        self.Login_input.setGeometry(QtCore.QRect(110, 140, 151, 31))
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.Login_input.sizePolicy().hasHeightForWidth())
        self.Login_input.setSizePolicy(sizePolicy)
        self.Login_input.setObjectName("Login_input")
        self.Password_input = QtWidgets.QTextEdit(AutoTranslatorWnd)
        self.Password_input.setGeometry(QtCore.QRect(280, 140, 151, 31))
        self.Password_input.setObjectName("Password_input")
        self.label = QtWidgets.QLabel(AutoTranslatorWnd)
        self.label.setGeometry(QtCore.QRect(150, 110, 61, 21))
        font = QtGui.QFont()
        font.setPointSize(16)
        self.label.setFont(font)
        self.label.setObjectName("label")
        self.label_2 = QtWidgets.QLabel(AutoTranslatorWnd)
        self.label_2.setGeometry(QtCore.QRect(320, 110, 91, 21))
        font = QtGui.QFont()
        font.setPointSize(16)
        self.label_2.setFont(font)
        self.label_2.setObjectName("label_2")
        self.Start_btn = QtWidgets.QPushButton(AutoTranslatorWnd)
        self.Start_btn.setGeometry(QtCore.QRect(30, 690, 121, 31))
        self.Start_btn.setObjectName("Start_btn")
        self.ListOfLink = QtWidgets.QListWidget(AutoTranslatorWnd)
        self.ListOfLink.setGeometry(QtCore.QRect(70, 230, 411, 181))
        self.ListOfLink.setObjectName("ListOfLink")
        self.label_3 = QtWidgets.QLabel(AutoTranslatorWnd)
        self.label_3.setGeometry(QtCore.QRect(200, 200, 151, 21))
        font = QtGui.QFont()
        font.setPointSize(16)
        self.label_3.setFont(font)
        self.label_3.setObjectName("label_3")
        self.Link_input = QtWidgets.QLineEdit(AutoTranslatorWnd)
        self.Link_input.setGeometry(QtCore.QRect(70, 430, 191, 20))
        self.Link_input.setObjectName("Link_input")
        self.AddLink_btn = QtWidgets.QPushButton(AutoTranslatorWnd)
        self.AddLink_btn.setGeometry(QtCore.QRect(70, 460, 91, 31))
        self.AddLink_btn.setObjectName("AddLink_btn")
        self.RemLink_btn = QtWidgets.QPushButton(AutoTranslatorWnd)
        self.RemLink_btn.setGeometry(QtCore.QRect(170, 460, 91, 31))
        self.RemLink_btn.setObjectName("RemLink_btn")
        self.AdminLink_input = QtWidgets.QTextEdit(AutoTranslatorWnd)
        self.AdminLink_input.setGeometry(QtCore.QRect(170, 50, 181, 31))
        self.AdminLink_input.setObjectName("AdminLink_input")
        self.label_4 = QtWidgets.QLabel(AutoTranslatorWnd)
        self.label_4.setGeometry(QtCore.QRect(170, 20, 191, 21))
        font = QtGui.QFont()
        font.setPointSize(16)
        self.label_4.setFont(font)
        self.label_4.setObjectName("label_4")
        self.loglabel = QtWidgets.QLabel(AutoTranslatorWnd)
        self.loglabel.setGeometry(QtCore.QRect(70, 500, 401, 41))
        font = QtGui.QFont()
        font.setPointSize(11)
        self.loglabel.setFont(font)
        self.loglabel.setAlignment(QtCore.Qt.AlignCenter)
        self.loglabel.setObjectName("loglabel")
        self.LogList = QtWidgets.QListWidget(AutoTranslatorWnd)
        self.LogList.setGeometry(QtCore.QRect(70, 540, 421, 131))
        self.LogList.setObjectName("LogList")
        self.CloseBrowser_btn = QtWidgets.QPushButton(AutoTranslatorWnd)
        self.CloseBrowser_btn.setGeometry(QtCore.QRect(380, 690, 131, 31))
        self.CloseBrowser_btn.setObjectName("CloseBrowser_btn")
        self.TranslateStart_btn = QtWidgets.QPushButton(AutoTranslatorWnd)
        self.TranslateStart_btn.setGeometry(QtCore.QRect(210, 690, 121, 31))
        self.TranslateStart_btn.setObjectName("TranslateStart_btn")
        self.LanguageComboBox = QtWidgets.QComboBox(AutoTranslatorWnd)
        self.LanguageComboBox.setGeometry(QtCore.QRect(310, 460, 141, 31))
        self.LanguageComboBox.setObjectName("LanguageComboBox")
        self.label_5 = QtWidgets.QLabel(AutoTranslatorWnd)
        self.label_5.setGeometry(QtCore.QRect(310, 430, 151, 21))
        font = QtGui.QFont()
        font.setPointSize(16)
        self.label_5.setFont(font)
        self.label_5.setObjectName("label_5")

        self.retranslateUi(AutoTranslatorWnd)
        QtCore.QMetaObject.connectSlotsByName(AutoTranslatorWnd)

    def retranslateUi(self, AutoTranslatorWnd):
        _translate = QtCore.QCoreApplication.translate
        AutoTranslatorWnd.setWindowTitle(_translate("AutoTranslatorWnd", "Dialog"))
        self.label.setText(_translate("AutoTranslatorWnd", "Логин"))
        self.label_2.setText(_translate("AutoTranslatorWnd", "Пароль"))
        self.Start_btn.setText(_translate("AutoTranslatorWnd", "Открыть страницы"))
        self.label_3.setText(_translate("AutoTranslatorWnd", "Список ссылок"))
        self.AddLink_btn.setText(_translate("AutoTranslatorWnd", "Добавить"))
        self.RemLink_btn.setText(_translate("AutoTranslatorWnd", "Удалить"))
        self.label_4.setText(_translate("AutoTranslatorWnd", "Ссылка на админку"))
        self.loglabel.setText(_translate("AutoTranslatorWnd", "Статус"))
        self.CloseBrowser_btn.setText(_translate("AutoTranslatorWnd", "Закрыть браузер"))
        self.TranslateStart_btn.setText(_translate("AutoTranslatorWnd", "Запустить перевод"))
        self.label_5.setText(_translate("AutoTranslatorWnd", "Язык перевода"))

        self.TranslateStart_btn.setDisabled(True)
        self.CloseBrowser_btn.setDisabled(True)
        self.Start_btn.clicked.connect(self.open_tabs)
        self.TranslateStart_btn.clicked.connect(self.start_translate)
        self.CloseBrowser_btn.clicked.connect(self.close_browser)
        self.AddLink_btn.clicked.connect(self.add_link)
        self.RemLink_btn.clicked.connect(self.remove_link)

        for lang_name, lang_code in config.LANGUAGES.items():
            self.LanguageComboBox.addItem(lang_name, lang_code)


    def add_link(self):
        link = self.Link_input.text().strip()
        if link:
            self.ListOfLink.addItem(link)
            self.Link_input.clear()

    def remove_link(self):
        selected_items = self.ListOfLink.selectedItems()
        for item in selected_items:
            self.ListOfLink.takeItem(self.ListOfLink.row(item))

    def get_all_links(self):
        return [self.ListOfLink.item(i).text() for i in range(self.ListOfLink.count())]

    def add_log(self, msg: str):
        self.LogList.addItem(msg)
        self.LogList.scrollToBottom()

    def onTabsOpened(self, msg: str):
        self.add_log(msg)
        self.TranslateStart_btn.setDisabled(False)
        self.CloseBrowser_btn.setDisabled(False)

    def onTranslated(self, msg: str):
        self.add_log(msg)
        self.CloseBrowser_btn.setDisabled(False)

    def onFallback(self):
        DriverShutdown(self.add_log)
        self.TranslateStart_btn.setDisabled(False)
        self.CloseBrowser_btn.setDisabled(False)
        self.Start_btn.setDisabled(False)

    def onBrowserClosed(self, msg: str):
        self.add_log(msg)
        self.AdminLink_input.clear()
        self.Login_input.clear()
        self.Password_input.clear()
        self.ListOfLink.clear()
        self.Start_btn.setDisabled(False)
        self.TranslateStart_btn.setDisabled(False)
        self.CloseBrowser_btn.setDisabled(False)

    def open_tabs(self):
        adminLink = self.AdminLink_input.toPlainText()
        login = self.Login_input.toPlainText()
        password = self.Password_input.toPlainText()
        index = self.LanguageComboBox.currentIndex()
        target_lang = self.LanguageComboBox.itemData(index)
        status = config.setConfig(adminLink, login, password, self.get_all_links(), target_lang, self.add_log)
        if status == 0:
            self.Start_btn.setDisabled(True)
            self.add_log("Selenium старт....")
            self.worker = WorkerThread(StartSelenim)
            self.worker.log.connect(self.add_log)
            self.worker.error.connect(self.add_log)
            self.worker.finished.connect(lambda _: self.onTabsOpened("Все вкладки открыты ✅"))
            self.worker.fallback_fn = self.onFallback
            self.worker.start()
    
    def start_translate(self):
        self.add_log("Начинаем считывать данные с вкладок и переводить....")
        initTranslator()
        self.TranslateStart_btn.setDisabled(True)
        self.CloseBrowser_btn.setDisabled(True)
        self.Start_btn.setDisabled(True)
        self.worker = WorkerThread(ParseData)
        self.worker.log.connect(self.add_log)
        self.worker.error.connect(self.add_log)
        self.worker.finished.connect(lambda _: self.onTranslated("Данные считались ✅"))
        self.worker.fallback_fn = self.onFallback
        self.worker.start()
    
    def close_browser(self):
        self.add_log("Selenium закрывает браузер подождите....")
        self.TranslateStart_btn.setDisabled(True)
        self.CloseBrowser_btn.setDisabled(True)
        self.Start_btn.setDisabled(True)
        self.worker = WorkerThread(DriverShutdown)
        self.worker.log.connect(self.add_log)
        self.worker.error.connect(self.add_log)
        self.worker.finished.connect(lambda _: self.onBrowserClosed("Все вкладки открыты ✅ Нажмите кнопку для старта перевода"))
        self.worker.fallback_fn = self.onFallback
        self.worker.start()


if __name__ == "__main__":
    import sys    
    app = QtWidgets.QApplication(sys.argv)
    AutoTranslatorWnd = QtWidgets.QDialog()
    ui = Ui_AutoTranslatorWnd()
    ui.setupUi(AutoTranslatorWnd)
    AutoTranslatorWnd.show()
    sys.exit(app.exec_())
