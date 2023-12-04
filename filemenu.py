import sys
from PySide6.QtWidgets import QApplication, QMainWindow, QLabel, QVBoxLayout, QWidget, QHBoxLayout, QScrollArea, QFileDialog
from PySide6.QtGui import QPixmap, QAction
from PySide6.QtCore import Qt
import fitz
import json
import os
from pdfviewer import MainWindow


class ImageGridWindow(QMainWindow):
    def __init__(self, image_paths):
        super().__init__()

        self.setWindowTitle("Books")
        self.setGeometry(100, 100, 800, 600)
        icon = QPixmap('AIPDF_Reader/data/book_icon.png')
        self.setWindowIcon(icon)

        central_widget = QWidget(self)
        self.setCentralWidget(central_widget)

        layout = QVBoxLayout(central_widget)

        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True) 
        layout.addWidget(scroll_area)

        content_widget = QWidget(scroll_area)
        scroll_area.setWidget(content_widget) 

        content_layout = QVBoxLayout(content_widget)

        menubar = self.menuBar()
        file_menu = menubar.addMenu('Choose folder')
        open_action = QAction('Open', self)
        open_action.triggered.connect(self.open_folder_dialog)
        file_menu.addAction(open_action)

        for row in image_paths:
            row_layout = QHBoxLayout()

            for image_path in row:
                print("Loading image:", image_path)

                image_widget = QWidget()
                image_label = QLabel()

                pixmap = QPixmap(image_path)
                if pixmap.isNull():
                    print("Failed to load image:", image_path)
                else:
                    pixmap = pixmap.scaled(200, 200, Qt.AspectRatioMode.KeepAspectRatio)
                    image_label.setPixmap(pixmap)

                text_label = QLabel()
                text_label.setText(os.path.basename(pathes_relate_jpg[image_path]))

                widget_layout = QVBoxLayout()
                widget_layout.addWidget(image_label)
                widget_layout.addWidget(text_label)

                image_widget.setLayout(widget_layout)

                image_widget.mousePressEvent = self.create_mouse_press_event(image_path)

                row_layout.addWidget(image_widget)

            content_layout.addLayout(row_layout)

    def create_mouse_press_event(self, image_path):
        def mouse_press_event(event):
            viewer = MainWindow()
            viewer.back_action.triggered.connect(self.show)
            viewer.open_file_dialog(filename=pathes_relate_jpg[image_path])
            viewer.show()
            self.hide()
            print("Clicked image:", image_path)
        return mouse_press_event

    def open_folder_dialog(self):
        file_dialog = QFileDialog()
        folder_name = file_dialog.getExistingDirectory(self, "Open Folder", "")
        #file_settings = {"current_folder" : folder_name}
        with open('AIPDF_Reader/data/file_settings.json', 'r') as outfile:
            data = json.load(outfile)
            data["current_folder"] = folder_name
        outfile.close()
        with open('AIPDF_Reader/data/file_settings.json', 'w', encoding='utf8') as outfile:
            json.dump(data, outfile)
        self.update()
    
def find_pdfs(folder_path):
    pdf_files = []

    for root, dirs, files in os.walk(folder_path):
        for file in files:
            if file.endswith(".pdf"):
                pdf_path = os.path.join(root, file)
                pdf_files.append(pdf_path)

    return pdf_files

def pdf_to_jpg(pdf_path, output_path):
    with fitz.open(pdf_path) as doc:
        page = doc.load_page(0)
        pix = page.get_pixmap()
        pix.save(output_path, "jpeg")
        return pix


if __name__ == "__main__":
    app = QApplication(sys.argv)

    pdf_paths = []
    full_list = []
    page_jpg = []
    pathes_relate_jpg = {}

    with open('AIPDF_Reader/data/file_settings.json', 'r') as file:
        settings = json.load(file)

    if "current_folder" in settings:
        pdf_files = find_pdfs(settings["current_folder"])
    else:
        pdf_files = find_pdfs("D:/Books")
    
    for path in pdf_files:
        pdf_paths.append(path)

    print(pdf_paths)

    with open('AIPDF_Reader/data/paths.json', 'r') as file:
        data = json.load(file)

    book_number = 0 
    for path in pdf_paths:
        output_path = os.path.basename(path.replace(".pdf" , ".jpg"))
        if path not in data:
            pdf_to_jpg(path, output_path)
            page_jpg.append(output_path)
            pathes_relate_jpg[output_path] = path
            book_number += 1
            if book_number % 3 == 0:
                full_list.append(page_jpg)
                page_jpg = []
        else:
            page_jpg.append(output_path)
            pathes_relate_jpg[output_path] = path
            book_number += 1
            if book_number % 3 == 0:
                full_list.append(page_jpg)
                page_jpg = []
    if page_jpg: 
        full_list.append(page_jpg)

    #app_json = json.dumps(pathes_relate_jpg)
    
    with open('AIPDF_Reader/data/paths.json', 'w', encoding='utf8') as outfile:
        json.dump(pathes_relate_jpg, outfile)
    #full_list.append(page_jpg)
    window = ImageGridWindow(full_list)
    window.show()

    sys.exit(app.exec())