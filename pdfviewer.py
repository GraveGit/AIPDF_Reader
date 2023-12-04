from PySide6.QtCore import QUrl, Qt
from PySide6.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QLineEdit, QFileDialog, QPushButton
from PySide6.QtGui import QAction, QPixmap
from PySide6.QtWebEngineWidgets import QWebEngineView
from PySide6.QtWebEngineCore import QWebEnginePage
import fitz
import modelqa
import unicodedata
import json
'''
class SearchLineEdit(QLineEdit):
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window

    def keyPressEvent(self, event):
        super().keyPressEvent(event)
        if event.key() == Qt.Key_Tab:
            self.main_window.search_text(self.text())
'''
class QuestionLineEdit(QLineEdit):
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window

    def keyPressEvent(self, event):
        super().keyPressEvent(event)
        if event.key() == Qt.Key_Return:
            MainWindow().answer_question(self.text())

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("PDF Viewer")
        icon = QPixmap('AIPDF_Reader/data/book_icon.png')
        self.setWindowIcon(icon)
        self.setGeometry(0, 28, 1000, 750)

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        
        self.layout = QVBoxLayout()
        self.central_widget.setLayout(self.layout)
        
        self.webView = QWebEngineView()
        self.webView.settings().setAttribute(self.webView.settings().WebAttribute.PluginsEnabled, True)
        self.webView.settings().setAttribute(self.webView.settings().WebAttribute.PdfViewerEnabled, True)
        self.layout.addWidget(self.webView)
        
        #self.search_input = SearchLineEdit(self)
        #self.search_input.setPlaceholderText("Enter text to search...")
        self.question_input = QuestionLineEdit(self)
        self.question_input.setPlaceholderText("Enter your question...")
        #self.layout.addWidget(self.search_input)
        self.layout.addWidget(self.question_input)

        self.create_file_menu()

    def create_file_menu(self):
        menubar = self.menuBar()
        file_menu = menubar.addMenu('Choose PDF')
        open_action = QAction('Open', self)
        open_action.triggered.connect(self.open_file_dialog)
        file_menu.addAction(open_action)

        self.back_action = QAction('Back', self)
        self.back_action.triggered.connect(self.close)
        menubar.addAction(self.back_action)

    def open_file_dialog(self, filename):
        file_dialog = QFileDialog()
        #filename, _ = file_dialog.getOpenFileName(self, "Open PDF", "", "PDF Files (*.pdf)")
        if filename:
            self.webView.setUrl(QUrl("file:///" + filename.replace('\\', '/')))
        current_file = filename
        clean_text = ''.join(char for char in current_file if unicodedata.category(char) != 'Cc')
        #file_settings = {"current_file" : clean_text}
        with open('AIPDF_Reader/data/file_settings.json', 'r') as outfile:
            data = json.load(outfile)
            data["current_file"] = clean_text
        outfile.close()
        with open('AIPDF_Reader/data/file_settings.json', 'w', encoding='utf8') as outfile:
            json.dump(data, outfile)

    def search_text(self, text):
        flag = QWebEnginePage.FindFlag.FindCaseSensitively
        if text:
            self.webView.page().findText(text, flag)
        else:
            self.webView.page().stopFinding()

    def answer_question(self, question):
        with open('AIPDF_Reader/data/file_settings.json', 'r') as file:
            data = json.load(file)
        doc = fitz.open(data["current_file"])
        content = ''
        for page in doc:
            page_text = page.get_text().replace('\n', '')
            clean_text = ''.join(char for char in page_text if unicodedata.category(char) != 'Cc')
            content += clean_text
        doc.close()
        print(data["current_file"])
        modelqa.answer_question(text=content, question_line=question )
            
if __name__ == '__main__':
    import sys
    app = QApplication(sys.argv)
    win = MainWindow()
    win.show()
    sys.exit(app.exec())
