import sys
from PySide2.QtCore import QUrl
from PySide2.QtWebEngineWidgets import QWebEngineView, QWebEngineProfile
from PySide2.QtWidgets import QApplication

def callback_function(html):
    print(html[:1000])

def on_load_finished():
    web.page().runJavaScript("document.documentElement.outerHTML", 0, callback_function)

app = QApplication(sys.argv)
web = QWebEngineView()

default_profile = QWebEngineProfile.defaultProfile()
default_cookie = default_profile.cookieStore()
default_cookie.deleteAllCookies()

web.load(QUrl('https://www.productreview.com.au/listings/hotondo-homes?page=10'))
#web.show()
#web.resize(640, 480)
web.loadFinished.connect(on_load_finished)

sys.exit(app.exec_())
