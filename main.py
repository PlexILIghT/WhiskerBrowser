from PyQt6 import QtCore, QtGui, QtWidgets
import BrowserUI, MenuUI, HistoryUI
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtCore import QUrl, QSize
import sqlite3

class Browser(QtWidgets.QWidget, BrowserUI.Ui_Form):
    def __init__(self):
        global sessionSettings
        super().__init__()
        self.webPage = QWebEngineView()
        layout = QtWidgets.QVBoxLayout()
        layout.addWidget(self.webPage)
        self.setupUi(self)
        self.setWindowTitle(" ")
        self.SetUpFunctions()
        self.LoadIcons()

        self.SetSearchStart()

    def SetUpFunctions(self):
        self.urlLineEdit.returnPressed.connect(self.OnEnterPressed)
        self.urlLineEdit2.returnPressed.connect(self.OnEnterPressed)
        self.reloadButton.clicked.connect(self.Reload)
        self.backButton.clicked.connect(self.Back)
        self.forwardButton.clicked.connect(self.Forward)
        self.searchButton.clicked.connect(self.OnEnterPressed)
        self.newTabButton.clicked.connect(self.CreateNewWindow)
        self.menuButton.clicked.connect(self.OpenMenu)
        self.addToBookmarksButton.clicked.connect(self.AddToBookmarks)
        self.searchHistoryList.itemClicked.connect(self.LoadFromSearchHistory)
        self.LoadSearchHistory()
        self.bookmarksTab.setParent(None)
        self.bookmarkButton.setParent(None)
        self.bookmarksTab = QtWidgets.QToolBar(self)
        self.gridLayout.addWidget(self.bookmarksTab, 1, 0)
        self.LoadBookmarksTab()
    
    def OnEnterPressed(self):
        global sessionSettings, urlStarts
        self.webPage.setParent(None)
        self.webPage = QWebEngineView()
        self.gridLayout.addWidget(self.webPage, 2, 0)

        self.webPage.urlChanged.connect(self.UrlChanged)

        self.SetSearchStart()

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
        print("CHANGED URL")
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
        self.SetSearchStart()
        
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
        self.SetSearchStart()
        
        self.webPage.setUrl(QUrl(self.searchStart + self.searchHistoryList.currentItem().text()))

    def LoadBookmarksTab(self):
        conn = sqlite3.connect("browser.db")
        cursor = conn.cursor()
        bookmarks = list(cursor.execute("SELECT * FROM bookmarks"))
        conn.close()
        self.bookmarksTab.clear()
        for item in bookmarks:
            self.bookmarksTab.addAction(self.CreateAction(item))
    
    def CreateAction(self, item):
        action = QtWidgets.QWidgetAction(self)
        action.setText(item[1])
        action.triggered.connect(lambda : self.LoadFromBookmarksTab(item[2]))
        return action
    
    def AddToBookmarks(self):
        if (self.webPage.url().toString() != ""):
            print("ADDED TO BOOKMARKS")
            conn = sqlite3.connect("browser.db")
            cursor = conn.cursor()
            cursor.execute("INSERT INTO bookmarks (bookmarkName, bookmarkUrl) VALUES (?, ?)", (self.webPage.page().title(), self.webPage.url().toString()))
            conn.commit()
            conn.close()
            self.LoadBookmarksTab()
    
    def LoadFromBookmarksTab(self, url):
        self.webPage.setParent(None)
        self.webPage = QWebEngineView()
        self.gridLayout.addWidget(self.webPage, 2, 0)

        self.webPage.urlChanged.connect(self.UrlChanged)
        
        self.webPage.setUrl(QUrl(url))
    
    def SetSearchStart(self):
        if int(sessionSettings[0][2]) == 0:
            self.searchStart = "https://www.google.com/search?q="
        elif int(sessionSettings[0][2]) == 1:
            self.searchStart = "https://ya.ru/search/?text="
        elif int(sessionSettings[0][2]) == 2:
            self.searchStart = "https://www.bing.com/search?q="
        elif int(sessionSettings[0][2]) == 3:
            self.searchStart = "https://search.yahoo.com/search?p="
        elif int(sessionSettings[0][2]) == 4:
            self.searchStart = "https://duckduckgo.com/?t=h_&q="
    
    def LoadIcons(self):
        self.menuButton.setIcon(QtGui.QIcon("svgs/menu.svg"))
        self.menuButton.setIconSize(QSize(20, 20))

        self.reloadButton.setIcon(QtGui.QIcon("svgs/refresh.svg"))
        self.reloadButton.setIconSize(QSize(20, 20))

        self.backButton.setIcon(QtGui.QIcon("svgs/back1.svg"))
        self.backButton.setIconSize(QSize(20, 20))

        self.forwardButton.setIcon(QtGui.QIcon("svgs/forward.svg"))
        self.forwardButton.setIconSize(QSize(20, 20))

        self.addToBookmarksButton.setIcon(QtGui.QIcon("svgs/bookmark.svg"))
        self.addToBookmarksButton.setIconSize(QSize(20, 20))

        self.newTabButton.setIcon(QtGui.QIcon("svgs/newtab.svg"))
        self.newTabButton.setIconSize(QSize(20, 20))

        self.searchButton.setIcon(QtGui.QIcon("svgs/search.svg"))
        self.searchButton.setIconSize(QSize(35, 35))




class Menu(QtWidgets.QWidget, MenuUI.Ui_Form):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.setWindowTitle(" ")
        self.SetUpFunctions()
        self.LoadSettingsIntoUI()
    
    def SetUpFunctions(self):
        self.browserHistoryButton.clicked.connect(self.OpenBrowserHistory)
        self.searchHistoryButton.clicked.connect(self.OpenSearchHistory)
        self.saveButton.clicked.connect(self.Save)
        self.backButton.clicked.connect(self.Close)
        self.clearBrowserHistoryButton.clicked.connect(self.ClearBrowserHistory)
        self.clearSearchHistoryButton.clicked.connect(self.ClearSearchHistory)
        self.bookmarksButton.clicked.connect(self.OpenBookmarks)
        self.clearBookmarksButton.clicked.connect(self.ClearBookmarks)
        self.searchSystem.addItems(["Google", "Yandex", "Bing", "Yahoo!", "DuckDuckGo"])
        self.LoadIcons()
    
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
    
    def OpenBookmarks(self):
        self.bookmarks = Bookmarks()
        self.bookmarks.show()
    
    def ClearBookmarks(self):
        clearDialog = ClearDialog()
        if clearDialog.exec():
            conn = sqlite3.connect("browser.db")
            cursor = conn.cursor()
            cursor.execute("DELETE FROM bookmarks")
            conn.commit()
            conn.close()
    
    def LoadIcons(self):
        self.searchSystem.setItemIcon(0, QtGui.QIcon("svgs/google.png"))
        self.searchSystem.setItemIcon(1, QtGui.QIcon("svgs/yandex.png"))
        self.searchSystem.setItemIcon(2, QtGui.QIcon("svgs/bing.png"))
        self.searchSystem.setItemIcon(3, QtGui.QIcon("svgs/yahoo.png"))
        self.searchSystem.setItemIcon(4, QtGui.QIcon("svgs/duckduckgo.png"))
        self.searchSystem.setIconSize(QSize(35, 35))



class BrowserHistory(QtWidgets.QWidget, HistoryUI.Ui_Form):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.setWindowTitle(" ")
        self.SetUpFunctions()
    
    def SetUpFunctions(self):
        self.backButton.clicked.connect(self.Close)
        self.historyName.setText("История браузера")
        self.LoadBrowserHistory()
        self.historyTable.itemDoubleClicked.connect(self.OpenPage)
        self.deleteSelectedButton.clicked.connect(self.DeleteSelected)
    
    def Close(self):
        self.close()
    
    def LoadBrowserHistory(self):
        conn = sqlite3.connect('browser.db')
        cursor = conn.cursor()
        data = list(cursor.execute("SELECT id, url, title, timestamp FROM browserHistory"))
        self.historyTable.setColumnCount(4)
        self.historyTable.setHorizontalHeaderLabels(("ID", "Ссылка", "Заголовок", "Время"))
        self.historyTable.setRowCount(len(data))
        for row in range(len(data)):
            for column in range(4):
                item = QtWidgets.QTableWidgetItem(str(data[row][column]))
                self.historyTable.setItem(row, column, item)
        self.historyTable.setColumnWidth(0, 60)
        self.historyTable.setColumnWidth(1, 400)
        self.historyTable.setColumnWidth(2, 400)
        self.historyTable.setColumnWidth(3, 200)
        self.historyTable.setColumnHidden(0, True)
    
    def OpenPage(self):
        url = self.historyTable.item(self.historyTable.currentRow(), 1).text()
        page = Browser()
        page.LoadUrl(url)
        windows.append(page)
        windows[-1].show()
    
    def DeleteSelected(self):
        if self.historyTable.item(self.historyTable.currentRow(), 0) != None:
            conn = sqlite3.connect('browser.db')
            cursor = conn.cursor()
            selectedID = int(self.historyTable.item(self.historyTable.currentRow(), 0).text())
            self.historyTable.removeRow(self.historyTable.currentRow())
            cursor.execute("DELETE FROM browserHistory WHERE id = ?", (selectedID, ))
            conn.commit()
            conn.close()



class SearchHistory(QtWidgets.QWidget, HistoryUI.Ui_Form):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.setWindowTitle(" ")
        self.SetUpFunctions()
    
    def SetUpFunctions(self):
        self.backButton.clicked.connect(self.Close)
        self.historyName.setText("История поиска")
        self.LoadSearchHistory()
        self.historyTable.itemDoubleClicked.connect(self.OpenPage)
        self.deleteSelectedButton.clicked.connect(self.DeleteSelected)
    
    def Close(self):
        self.close()
    
    def LoadSearchHistory(self):
        conn = sqlite3.connect('browser.db')
        cursor = conn.cursor()
        data = list(cursor.execute("SELECT id, query, timestamp FROM searchHistory"))
        self.historyTable.setColumnCount(3)
        self.historyTable.setHorizontalHeaderLabels(("ID", "Запрос", "Время"))
        self.historyTable.setRowCount(len(data))
        for row in range(len(data)):
            for column in range(3):
                item = QtWidgets.QTableWidgetItem(str(data[row][column]))
                self.historyTable.setItem(row, column, item)
        self.historyTable.setColumnWidth(0, 60)
        self.historyTable.setColumnWidth(1, 400)
        self.historyTable.setColumnWidth(2, 400)
        self.historyTable.setColumnHidden(0, True)
    
    def OpenPage(self):
        url = self.historyTable.item(self.historyTable.currentRow(), 1).text()
        page = Browser()
        page.LoadUrl(page.searchStart + url)
        windows.append(page)
        windows[-1].show()
    
    def DeleteSelected(self):
        if self.historyTable.item(self.historyTable.currentRow(), 0) != None:
            conn = sqlite3.connect('browser.db')
            cursor = conn.cursor()
            selectedID = int(self.historyTable.item(self.historyTable.currentRow(), 0).text())
            self.historyTable.removeRow(self.historyTable.currentRow())
            cursor.execute("DELETE FROM searchHistory WHERE id = ?", (selectedID, ))
            conn.commit()
            conn.close()



class Bookmarks(QtWidgets.QWidget, HistoryUI.Ui_Form):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.setWindowTitle(" ")
        self.SetUpFunctions()
    
    def SetUpFunctions(self):
        self.backButton.clicked.connect(self.Close)
        self.historyName.setText("Закладки")
        self.LoadBookmarks()
        self.historyTable.itemDoubleClicked.connect(self.OpenPage)
        self.deleteSelectedButton.clicked.connect(self.DeleteSelected)
    
    def Close(self):
        self.close()
    
    def LoadBookmarks(self):
        conn = sqlite3.connect('browser.db')
        cursor = conn.cursor()
        data = list(cursor.execute("SELECT id, bookmarkName, bookmarkUrl FROM bookmarks"))
        self.historyTable.setColumnCount(3)
        self.historyTable.setHorizontalHeaderLabels(("ID", "Название", "Ссылка"))
        self.historyTable.setRowCount(len(data))
        for row in range(len(data)):
            for column in range(3):
                item = QtWidgets.QTableWidgetItem(str(data[row][column]))
                self.historyTable.setItem(row, column, item)
        self.historyTable.setColumnWidth(0, 60)
        self.historyTable.setColumnWidth(1, 400)
        self.historyTable.setColumnWidth(2, 400)
        self.historyTable.setColumnHidden(0, True)
    
    def OpenPage(self):
        url = self.historyTable.item(self.historyTable.currentRow(), 2).text()
        page = Browser()
        page.LoadUrl(url)
        windows.append(page)
        windows[-1].show()
    
    def DeleteSelected(self):
        if self.historyTable.item(self.historyTable.currentRow(), 0) != None:
            conn = sqlite3.connect('browser.db')
            cursor = conn.cursor()
            selectedID = int(self.historyTable.item(self.historyTable.currentRow(), 0).text())
            self.historyTable.removeRow(self.historyTable.currentRow())
            cursor.execute("DELETE FROM bookmarks WHERE id = ?", (selectedID, ))
            conn.commit()
            conn.close()



class ClearDialog(QtWidgets.QDialog):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Подтверждение очистки")

        QBtn = QtWidgets.QDialogButtonBox.StandardButton.Yes | QtWidgets.QDialogButtonBox.StandardButton.No

        self.buttonBox = QtWidgets.QDialogButtonBox(QBtn)
        self.buttonBox.accepted.connect(self.accept)
        self.buttonBox.rejected.connect(self.reject)

        self.layout = QtWidgets.QVBoxLayout()
        message = QtWidgets.QLabel("Вы уверены что хотите очистить?")
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
        CREATE TABLE IF NOT EXISTS bookmarks (
            id INTEGER PRIMARY KEY,
            bookmarkName TEXT NOT NULL,
            bookmarkUrl TEXT NOT NULL
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
    "http://"]
    
    CreateTables()

    conn = sqlite3.connect("browser.db")
    cursor = conn.cursor()
    sessionSettings = list(cursor.execute("SELECT * FROM settings"))
    conn.close()

    browser = Browser()
    windows.append(browser)
    windows[0].show()
    app.exec()