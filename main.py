from PyQt6 import QtCore, QtGui, QtWidgets
from BrowserUI import BrowserUI
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtCore import QUrl

class Browser(QtWidgets.QWidget, BrowserUI):
    def __init__(self):
        super().__init__()
        self.setupUi()
        self.SetUpFunctions()

    def SetUpFunctions(self):
        self.urlLineEdit.returnPressed.connect(self.OnEnterPressed)
        self.reloadButton.clicked.connect(self.CreateNewWindow)
    
    def OnEnterPressed(self):
        view = QWebEngineView()
        layout = QtWidgets.QVBoxLayout()
        layout.addWidget(view)
        view.setUrl(QUrl(self.urlLineEdit.text()))
        self.webView.setLayout(layout)
    
    def CreateNewWindow(self):
        global windows
        newWindow = Browser()
        windows.append(newWindow)
        windows[-1].show()

    

if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    windows = []
    browser = Browser()
    windows.append(browser)
    windows[0].show()
    app.exec()