from PyQt6 import QtCore, QtGui, QtWidgets
import BrowserUI, MenuUI, HistoryUI
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtCore import QUrl
import sqlite3

class Browser(QtWidgets.QWidget, BrowserUI.Ui_Form):
    def __init__(self):
        super().__init__()
        self.webPage = QWebEngineView()
        layout = QtWidgets.QVBoxLayout()
        layout.addWidget(self.webPage)
        self.setupUi(self)
        self.SetUpFunctions()
        self.searchStart = "https://google.com/search?q="

    def SetUpFunctions(self):
        self.urlLineEdit.returnPressed.connect(self.OnEnterPressed)
        self.urlLineEdit2.returnPressed.connect(self.OnEnterPressed)
        self.reloadButton.clicked.connect(self.Reload)
        self.backButton.clicked.connect(self.Back)
        self.forwardButton.clicked.connect(self.Forward)
        self.searchButton.clicked.connect(self.OnEnterPressed)
        self.newTabButton.clicked.connect(self.CreateNewWindow)
        self.menuButton.clicked.connect(self.OpenMenu)
        self.webPage.loadFinished.connect(self.pageLoaded)
    
    def OnEnterPressed(self):
        self.webPage.setParent(None)
        self.webPage = QWebEngineView()
        self.gridLayout.addWidget(self.webPage, 2, 0)

        if (self.sender().objectName() == "urlLineEdit"):
            if ("https://" == self.urlLineEdit.text()[:8]):
                self.webPage.setUrl(QUrl(self.urlLineEdit.text()))
            else:
                self.webPage.setUrl(QUrl(self.searchStart + self.urlLineEdit.text()))
                searchHistory.append(self.urlLineEdit.text())
        else:
            if ("https://" == self.urlLineEdit2.text()[:8]):
                self.webPage.setUrl(QUrl(self.urlLineEdit2.text()))
            else:
                self.webPage.setUrl(QUrl(self.searchStart + self.urlLineEdit2.text()))
                searchHistory.append(self.urlLineEdit2.text())
        
    
    def CreateNewWindow(self):
        global windows
        newWindow = Browser()
        windows.append(newWindow)
        windows[-1].show()
    
    def Back(self):
        #print(self.webPage.url().toString())
        self.webPage.back()
    
    def Forward(self):
        self.webPage.forward()
    
    def Reload(self):
        self.webPage.reload()
    
    def OpenMenu(self):
        self.menu = Menu()
        self.menu.show()
    
    def pageLoaded(self):
        conn = sqlite3.connect('browser.db')
        cursor = conn.cursor()
        cursor.execute('INSERT INTO browsing_history (url, title) VALUES (?, ?)', (self.webPage.url().toString(), self.webPage.title()))
        conn.commit()
        conn.close()


class Menu(QtWidgets.QWidget, MenuUI.Ui_Form):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.SetUpFunctions()
        self.LoadSettingsIntoUI()
    
    def SetUpFunctions(self):
        self.browserHistoryButton.clicked.connect(self.OpenBrowserHistory)
        self.searchHistoryButton.clicked.connect(self.OpenSearchHistory)
        self.saveButton.clicked.connect(self.Save)
        self.backButton.clicked.connect(self.Close)
        self.clearBrowserHistoryButton.clicked.connect(self.ClearBrowserHistory)
        self.clearSearchHistoryButton.clicked.connect(self.ClearSearchHistory)
        self.searchSystem.addItems(["Google", "Yandex"])
    
    def OpenBrowserHistory(self):
        self.browserHistory = BrowserHistory()
        self.browserHistory.show()
    
    def OpenSearchHistory(self):
        self.searchHistory = SearchHistory()
        self.searchHistory.show()
    
    def Close(self):
        self.close()
    
    def Save(self):
        ### СОХРАНЕНИЕ НАСТРОЕК ###
        pass

    def LoadSettingsIntoUI(self):
        self.searchSystem.setCurrentIndex(0)
        self.saveBrowserHistoryFlag.setChecked(False)
        self.saveSearchHistoryFlag.setChecked(False)
        ### ЗДЕСЬ НУЖНО ЗАГРУЖАТЬ СОХРАНЕННЫЕ НАСТРОЙКИ В UI, НАПРИМЕР КАК В СТРОЧКАХ ВЫШЕ, ТОЛЬКО НУЖНО БРАТЬ АРГУМЕНИЫ ИЗ СОХРАНЕНИЯ ###
    
    def ClearBrowserHistory(self):
        clearDialog = ClearDialog()
        if clearDialog.exec():
            ### УДАЛЕНИЕ ИСТОРИИ БРАУЗЕРА ###
            pass
    
    def ClearSearchHistory(self):
        clearDialog = ClearDialog()
        if clearDialog.exec():
            ### УДАЛЕНИЕ ИСТОРИИ ПОИСКА ###
            pass


class BrowserHistory(QtWidgets.QWidget, HistoryUI.Ui_Form):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.SetUpFunctions()
    
    def SetUpFunctions(self):
        self.backButton.clicked.connect(self.Close)
        self.historyName.setText("История браузера")
        self.LoadBrowserHistory()
    
    def Close(self):
        self.close()
    
    def LoadBrowserHistory(self):
        ### Загрузка истории браузера ###
        for url in browserHistory:
            self.historyList.addItem(url)

class SearchHistory(QtWidgets.QWidget, HistoryUI.Ui_Form):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.SetUpFunctions()
        self.LoadSearchHistory()
    
    def SetUpFunctions(self):
        self.backButton.clicked.connect(self.Close)
        self.historyName.setText("История поиска")
    
    def Close(self):
        self.close()
    
    def LoadSearchHistory(self):
        ### Загрузка истории поиска ###
        for url in searchHistory:
            self.historyList.addItem(url)


class ClearDialog(QtWidgets.QDialog):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Подтверждение очистки истории")

        QBtn = QtWidgets.QDialogButtonBox.StandardButton.Yes | QtWidgets.QDialogButtonBox.StandardButton.No

        self.buttonBox = QtWidgets.QDialogButtonBox(QBtn)
        self.buttonBox.accepted.connect(self.accept)
        self.buttonBox.rejected.connect(self.reject)

        self.layout = QtWidgets.QVBoxLayout()
        message = QtWidgets.QLabel("Вы уверены что хотите очистить историю?")
        self.layout.addWidget(message)
        self.layout.addWidget(self.buttonBox)
        self.setLayout(self.layout)

def create_tables():
    conn = sqlite3.connect('browser.db')
    cursor = conn.cursor()

    # история поиска
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS search_history (
            id INTEGER PRIMARY KEY,
            query TEXT NOT NULL,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    # общая история
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS browsing_history (
            id INTEGER PRIMARY KEY,
            url TEXT NOT NULL,
            title TEXT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    # Настройки
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS settings (
            id INTEGER PRIMARY KEY,
            setting_name TEXT NOT NULL,
            setting_value TEXT NOT NULL
        )
    ''')

    conn.commit()
    conn.close()

if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    windows = []
    browserHistory = 
    searchHistory = []
    browser = Browser()
    windows.append(browser)
    windows[0].show()
    create_tables()
    app.exec()