from PyQt6 import QtCore, QtGui, QtWidgets
import BrowserUI, MenuUI, HistoryUI
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtCore import QUrl
import sqlite3

class Browser(QtWidgets.QWidget, BrowserUI.Ui_Form):
    def __init__(self):
        global sessionSettings
        super().__init__()
        self.webPage = QWebEngineView()
        layout = QtWidgets.QVBoxLayout()
        layout.addWidget(self.webPage)
        self.setupUi(self)
        self.SetUpFunctions()
        if int(sessionSettings[0][2]) == 0:
            self.searchStart = "https://google.com/search?q="
        elif int(sessionSettings[0][2]) == 1:
            self.searchStart = "https://ya.ru/search/?text="

    def SetUpFunctions(self):
        self.urlLineEdit.returnPressed.connect(self.OnEnterPressed)
        self.urlLineEdit2.returnPressed.connect(self.OnEnterPressed)
        self.reloadButton.clicked.connect(self.Reload)
        self.backButton.clicked.connect(self.Back)
        self.forwardButton.clicked.connect(self.Forward)
        self.searchButton.clicked.connect(self.OnEnterPressed)
        self.newTabButton.clicked.connect(self.CreateNewWindow)
        self.menuButton.clicked.connect(self.OpenMenu)
        self.addToFavoriteButton.clicked.connect(self.AddToFavorites)
        self.searchHistoryList.itemDoubleClicked.connect(self.LoadFromSearchHistory)
        self.LoadSearchHistory()
        self.favoriteTab.setParent(None)
        self.favoriteButton.setParent(None)
        self.favoriteTab = QtWidgets.QToolBar(self)
        self.gridLayout.addWidget(self.favoriteTab, 1, 0)
        self.LoadFavoritesTab()
        #self.favoriteTab.actionTriggered.connect(self.LoadFromFavoritesTab)
    
    def OnEnterPressed(self):
        global sessionSettings, urlStarts
        self.webPage.setParent(None)
        self.webPage = QWebEngineView()
        self.gridLayout.addWidget(self.webPage, 2, 0)

        self.webPage.urlChanged.connect(self.UrlChanged)

        if int(sessionSettings[0][2]) == 0:
            self.searchStart = "https://google.com/search?q="
        elif int(sessionSettings[0][2]) == 1:
            self.searchStart = "https://ya.ru/search/?text="

        if (self.sender().objectName() == "urlLineEdit"):
            url = self.CheckUrlStart(self.urlLineEdit.text())
        else:
            url = self.CheckUrlStart(self.urlLineEdit2.text())
        
        self.webPage.setUrl(QUrl(url[0]))
        self.urlLineEdit.setText(url[0])

        if bool(sessionSettings[2][2] and url[1] != None):
            conn = sqlite3.connect("browser.db")
            cursor = conn.cursor()
            cursor.execute("INSERT INTO searchHistory (query) VALUES (?)", (url[1], ))
            conn.commit()
            conn.close()
        
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
        global sessionSettings
        print("CHANGED")
        self.urlLineEdit.setText(self.webPage.url().toString())
        if bool(sessionSettings[1][2]):
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
    
    def CheckUrlStart(self, prompt):
        global urlStarts
        if any([urlStart in prompt for urlStart in urlStarts]):
            return (prompt, None)
        else:
            return (self.searchStart + prompt, prompt)
    
    def LoadSearchHistory(self):
        conn = sqlite3.connect("browser.db")
        cursor = conn.cursor()
        searchHistory = list(cursor.execute("SELECT query FROM searchHistory"))
        conn.close()
        for item in searchHistory:
            self.searchHistoryList.addItem(item[0])
    
    def LoadFromSearchHistory(self):
        self.webPage.setParent(None)
        self.webPage = QWebEngineView()
        self.gridLayout.addWidget(self.webPage, 2, 0)

        self.webPage.urlChanged.connect(self.UrlChanged)
        
        self.webPage.setUrl(QUrl(self.searchStart + self.searchHistoryList.currentItem().text()))

    def LoadFavoritesTab(self):
        conn = sqlite3.connect("browser.db")
        cursor = conn.cursor()
        favorites = list(cursor.execute("SELECT * FROM favorites"))
        conn.close()
        for item in favorites:
            action = QtWidgets.QWidgetAction(self)
            action.setText(item[1])
            action.triggered.connect(lambda: self.LoadFromFavoritesTab(item[2]))
            self.favoriteTab.addAction(action)
    
    def AddToFavorites(self):
        print("ADDED")
        conn = sqlite3.connect("browser.db")
        cursor = conn.cursor()
        cursor.execute("INSERT INTO favorites (favoriteName, favoriteUrl) VALUES (?, ?)", (self.webPage.page().title(), self.webPage.url().toString()))
        conn.commit()
        conn.close()
    
    def LoadFromFavoritesTab(self, url):
        self.webPage.setParent(None)
        self.webPage = QWebEngineView()
        self.gridLayout.addWidget(self.webPage, 2, 0)

        self.webPage.urlChanged.connect(self.UrlChanged)
        
        print(url)
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
        global sessionSettings
        conn = sqlite3.connect("browser.db")
        cursor = conn.cursor()
        cursor.execute("UPDATE settings SET settingValue = ? WHERE settingName = 'searchSystem'", (self.searchSystem.currentIndex(), ))
        cursor.execute("UPDATE settings SET settingValue = ? WHERE settingName = 'saveBrowserHistoryFlag'", (self.saveBrowserHistoryFlag.isChecked(), ))
        cursor.execute("UPDATE settings SET settingValue = ? WHERE settingName = 'saveSearchHistoryFlag'", (self.saveSearchHistoryFlag.isChecked(), ))
        conn.commit()
        sessionSettings = list(cursor.execute("SELECT * FROM settings"))
        conn.close()

    def LoadSettingsIntoUI(self):
        conn = sqlite3.connect("browser.db")
        cursor = conn.cursor()
        settings = list(cursor.execute("SELECT * FROM settings"))
        self.searchSystem.setCurrentIndex(int(settings[0][2]))
        self.saveBrowserHistoryFlag.setChecked(bool(settings[1][2]))
        self.saveSearchHistoryFlag.setChecked(bool(settings[2][2]))
        conn.close()
    
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
    
    def SetUpFunctions(self):
        self.backButton.clicked.connect(self.Close)
        self.historyName.setText("История поиска")
        self.LoadSearchHistory()
        self.historyList.itemDoubleClicked.connect(self.OpenPage)
    
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


def CreateTables():
    conn = sqlite3.connect('browser.db')
    cursor = conn.cursor()

    # История поиска
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS searchHistory (
            id INTEGER PRIMARY KEY,
            query TEXT NOT NULL,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    # История посещений
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
            settingValue INTEGER
        )
    ''')

    # Закладки
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS favorites (
            id INTEGER PRIMARY KEY,
            favoriteName TEXT NOT NULL,
            favoriteUrl TEXT NOT NULL
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
    urlStarts = [
    "https://",
    "http://",
    "www."]
    
    CreateTables()

    conn = sqlite3.connect("browser.db")
    cursor = conn.cursor()
    sessionSettings = list(cursor.execute("SELECT * FROM settings"))
    conn.close()

    browser = Browser()
    windows.append(browser)
    windows[0].show()
    app.exec()