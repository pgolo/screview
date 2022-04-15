#ComponentEntryPoint excluded from build
"""Desktop GUI application"""

import os
import sys
import sys; sys.path.insert(0, '%s/../webapp' % (os.path.dirname(os.path.abspath(os.path.realpath(__file__)))))
import argparse

from PySide2.QtCore import QUrl, QFileInfo
from PySide2.QtGui import QIcon
from PySide2.QtWidgets import QApplication, QMainWindow, QFileDialog, QProgressBar, QMessageBox
from PySide2.QtWebEngineWidgets import QWebEnginePage, QWebEngineView, QWebEngineDownloadItem

import threading
import time
import requests

class StubWebEnginePage(QWebEnginePage):
    
    def acceptNavigationRequest(self, url, type, isMainFrame):
        return QWebEnginePage.acceptNavigationRequest(self, url, type, isMainFrame)

class MainWindow(QMainWindow):

    def download_state_changed(self, state):
        # Manage download state
        if state == QWebEngineDownloadItem.DownloadState.DownloadRequested:
            pass
        if state == QWebEngineDownloadItem.DownloadState.DownloadInProgress:
            self.progressBar.show()
        if state == QWebEngineDownloadItem.DownloadState.DownloadCompleted:
            self.msgBox.setText('Finished downloading')
            self.msgBox.show()
            self.progressBar.hide()
        if state == QWebEngineDownloadItem.DownloadState.DownloadInterrupted:
            self.msgBox.setText('Download failed - server disconnected.')
            self.msgBox.show()
            self.progressBar.hide()
        if state == QWebEngineDownloadItem.DownloadState.DownloadCancelled:
            self.msgBox.setText('Download failed - could not save file at the specified location.')
            self.msgBox.show()
            self.progressBar.hide()

    def download_progress(self, bytesReceived, bytesTotal):
        # Report progress
        self.progressBar.setMaximum(bytesTotal)
        self.progressBar.setValue(bytesReceived)

    def download_requested(self, download):
        # Specify file path and initiate download if necessary
        filename = os.path.basename(download.path())
        extension = QFileInfo(filename).suffix()
        path, _ = QFileDialog.getSaveFileName(self, "Save file", download.path(), '*.%s' % (extension))
        if path:
            download.stateChanged.connect(self.download_state_changed)
            download.downloadProgress.connect(self.download_progress)
            download.setPath(path)
            download.accept()

    def __init__(self):
        super(MainWindow, self).__init__()
        
        # Main window and central widget
        self.webEngineView = QWebEngineView()
        self.setCentralWidget(self.webEngineView)

        # Initialize navigation
        self.webEngineView.setPage(StubWebEnginePage(self.webEngineView))
        self.webEngineView.page().profile().downloadRequested.connect(self.download_requested)
        self.webEngineView.setUrl(QUrl('https://www.productreview.com.au/listings/hotondo-homes?page=10'))

if __name__ == '__main__':
    # Start UI application
    app = QApplication(sys.argv)
    mainWin = MainWindow()

    # All is good, proceed to GUI
    availableGeometry = app.desktop().availableGeometry(mainWin)
    mainWin.resize(availableGeometry.width() * 2 / 3, availableGeometry.height() * 2 / 3)
    mainWin.show()
    sys.exit(app.exec_())
