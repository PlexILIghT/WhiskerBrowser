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
    
    def OnEnterPressed(self):
        self.webPage.setParent(None)
        self.webPage = QWebEngineView()
        self.gridLayout.addWidget(self.webPage, 2, 0)

        self.webPage.urlChanged.connect(self.UrlChanged)

        if (self.sender().objectName() == "urlLineEdit"):
            if ("https://" == self.urlLineEdit.text()[:8]):
                self.webPage.setUrl(QUrl(self.urlLineEdit.text()))
            else:
                self.webPage.setUrl(QUrl(self.searchStart + self.urlLineEdit.text()))
        else:
            if ("https://" == self.urlLineEdit2.text()[:8]):
                self.webPage.setUrl(QUrl(self.urlLineEdit2.text()))
            else:
                self.webPage.setUrl(QUrl(self.searchStart + self.urlLineEdit2.text()))
        
        
    
    def CreateNewWindow(self):
        global windows
        newWindow = Browser()
        windows.append(newWindow)
        windows[-1].show()
    
    def Back(self):
        self.webPage.back()
    
    def Forward(self):
        self.webPage.forward()
    
    def Reload(self):
        self.webPage.reload()
    
    def OpenMenu(self):
        self.menu = Menu()
        self.menu.show()
    
    def UrlChanged(self):
        print("CHANGED")
        conn = sqlite3.connect('browser.db')
        cursor = conn.cursor()
        cursor.execute('INSERT INTO browserHistory (url, title) VALUES (?, ?)', (self.webPage.url().toString(), self.webPage.title()))
        conn.commit()
        conn.close()
    
    def LoadUrl(self, url):
        self.webPage.setParent(None)
        self.webPage = QWebEngineView()
        self.gridLayout.addWidget(self.webPage, 2, 0)

        self.webPage.urlChanged.connect(self.UrlChanged)
        
        self.webPage.setUrl(QUrl(url))


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
            conn = sqlite3.connect("browser.db")
            cursor = conn.cursor()
            cursor.execute("DELETE FROM browserHistory")
            conn.commit()
            conn.close()
    
    def ClearSearchHistory(self):
        clearDialog = ClearDialog()
        if clearDialog.exec():
            conn = sqlite3.connect("browser.db")
            cursor = conn.cursor()
            cursor.execute("DELETE FROM searchHistory")
            conn.commit()
            conn.close()


class BrowserHistory(QtWidgets.QWidget, HistoryUI.Ui_Form):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.SetUpFunctions()
    
    def SetUpFunctions(self):
        self.backButton.clicked.connect(self.Close)
        self.historyName.setText("История браузера")
        self.LoadBrowserHistory()
        self.historyList.itemDoubleClicked.connect(self.OpenPage)
    
    def Close(self):
        self.close()
    
    def LoadBrowserHistory(self):
        conn = sqlite3.connect('browser.db')
        cursor = conn.cursor()
        data = cursor.execute("SELECT url FROM browserHistory")
        for row in data:
            self.historyList.addItem(row[0])
    
    def OpenPage(self):
        url = self.historyList.currentItem().text()
        page = Browser()
        page.LoadUrl(url)
        windows.append(page)
        windows[-1].show()


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
        conn = sqlite3.connect('browser.db')
        cursor = conn.cursor()
        data = cursor.execute("SELECT query FROM searchHistory")
        for row in data:
            self.historyList.addItem(row[0])
    
    def OpenPage(self):
        url = self.historyList.currentItem().text()
        page = Browser()
        page.LoadUrl(page.startPage + url)
        windows.append(page)
        windows[-1].show()


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
        CREATE TABLE IF NOT EXISTS searchHistory (
            id INTEGER PRIMARY KEY,
            query TEXT NOT NULL,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    # общая история
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS browserHistory (
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
            settingName TEXT NOT NULL,
            settingValue TEXT NOT NULL
        )
    ''')

    settingsExist = cursor.execute("SELECT * FROM settings")
    if list(settingsExist) == []:
        cursor.executemany("INSERT INTO settings (id, settingName, settingValue) VALUES (?, ?, ?)", defaultSettings)
    conn.commit()
    conn.close()

if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    windows = []
    defaultSettings = [
    (0, "searchSystem", 0),
    (1, "saveBrowserHistoryFlag", 1),
    (2, "saveSearchHistoryFlag", 1)]
    browser = Browser()
    windows.append(browser)
    windows[0].show()
    create_tables()
    app.exec()