#-*- coding:utf-8 -*-

import ntpath
import os
import sys
import chardet
from fnmatch import fnmatch
from sami import Sami

from PySide2.QtCore import QSize, Qt
from PySide2.QtGui import QIcon
from PySide2.QtWidgets import *


# Extended TreeWidget Class for Drag & Drop capability.
class ScrollMessageBox(QMessageBox):
    def __init__(self, *args, **kwargs):
        QMessageBox.__init__(self, *args, **kwargs)
        chldn = self.children()
        scrll = QScrollArea(self)
        scrll.setWidgetResizable(True)
        grd = self.findChild(QGridLayout)
        lbl = QLabel(chldn[1].text(), self)
        lbl.setWordWrap(True)
        scrll.setWidget(lbl)
        scrll.setMinimumSize(400, 200)
        scrll.setStyleSheet('background:transparent; border:0;')
        grd.addWidget(scrll, 0, 1)
        chldn[1].setText('')
        self.exec_()


class App(QMainWindow):
    def __init__(self):
        super().__init__()
        self.init_ui()
        self.attach_event()
        self.setAcceptDrops(True)
        
    def init_ui(self):
        # Define & Configure Components
        normal_button_size = QSize(80, 24)
        icon_button_size = QSize(24, 24)
        icon_size = QSize(18, 18)
        
        self.central_widget = QWidget()
        self.central_layout = QGridLayout()
        self.central_widget.setLayout(self.central_layout)

        self.tab_group_widget = QTabWidget()
        self.tab_group_widget.setMinimumSize(400, 0)
        self.tab_group_widget.setFixedHeight(150)
        self.tab1_name = '스폰서 변환'
        self.tab2_name = '싱크 조절(초)'
        self.tab3_name = '싱크 조절(%)'

        self.tab_page_1 = QWidget()
        self.tab_grid_1 = QGridLayout()
        self.tab1_search_label = QLabel('검색 텍스트')
        self.tab1_search = QLineEdit()
        self.tab1_sponsor = QWidget()
        self.tab1_sponsor_layout = QHBoxLayout()
        self.tab1_sponsor_layout.setContentsMargins(0, 0, 0, 0)
        self.tab1_sponsor_label = QLabel('스폰서 영상 길이')
        self.tab1_sponsor_value = QDoubleSpinBox()
        self.tab1_sponsor_value.setFixedWidth(60)
        self.tab1_sponsor_value.setMinimum(-1000000000)
        self.tab1_sponsor_value.setValue(10)
        self.tab1_offset = QWidget()
        self.tab1_offset_layout = QHBoxLayout()
        self.tab1_offset_layout.setContentsMargins(0, 0, 0, 0)
        self.tab1_offset_label = QLabel('라인 오프셋')
        self.tab1_offset_value = QSpinBox()
        self.tab1_offset_value.setMinimum(-1000000000)
        self.tab1_offset_value.setValue(2)
        self.tab1_offset_value.setFixedWidth(50)
        self.tab1_ignore = QWidget()
        self.tab1_ignore_layout = QHBoxLayout()
        self.tab1_ignore_layout.setContentsMargins(0, 0, 0, 0)
        self.tab1_ignore_label1 = QLabel('시작부터')
        self.tab1_ignore_value = QSpinBox()
        self.tab1_ignore_value.setFixedWidth(50)
        self.tab1_ignore_value.setValue(5)
        self.tab1_ignore_label2 = QLabel('줄 ')
        self.tab1_ignore_sec = QSpinBox()
        self.tab1_ignore_sec.setFixedWidth(60)
        self.tab1_ignore_sec.setMaximum(1000)
        self.tab1_ignore_sec.setValue(90)
        self.tab1_ignore_label3 = QLabel('초 무시하기')
        self.tab1_add_button = QPushButton('추가하기')

        self.tab_page_2 = QWidget()
        self.tab_grid_2 = QGridLayout()
        self.tab2_shift = QWidget()
        self.tab2_shift_layout = QHBoxLayout()
        self.tab2_shift_layout.setContentsMargins(0, 0, 0, 0)
        self.tab2_shift_label1 = QLabel('자막 싱크')
        self.tab2_shift_value = QDoubleSpinBox()
        self.tab2_shift_value.setFixedWidth(60)
        self.tab2_shift_label2 = QLabel('초 ')
        self.tab2_slow_radio = QRadioButton('느리게')
        self.tab2_slow_radio.setChecked(True)
        self.tab2_fast_radio = QRadioButton('빠르게')
        self.tab2_add_button = QPushButton('추가하기')

        self.tab_page_3 = QWidget()
        self.tab_grid_3 = QGridLayout()
        self.tab3_speed_label1 = QLabel('자막 싱크')
        self.tab3_speed_value = QSpinBox()
        self.tab3_speed_value.setFixedWidth(70)
        self.tab3_speed_value.setRange(1, 1000)
        self.tab3_speed_value.setValue(100)
        self.tab3_speed_label2 = QLabel('%')
        self.tab3_add_button = QPushButton('추가하기')

        self.que_label = QLabel('작업 목록')
        self.que_label.setFixedHeight(24)
        self.que_widget = QWidget()
        self.que_widget.setFixedHeight(110)
        self.que_layout = QGridLayout()
        self.que_layout.setContentsMargins(0, 0, 0, 0)
        self.que_list = QTreeWidget()
        self.que_list.setHeaderLabels(['작업', '옵션'])
        self.que_delete_button = QPushButton(QIcon('./assets/remove.png'), '')
        self.que_delete_button.setFixedSize(icon_button_size)
        self.que_delete_button.setIconSize(icon_size)
        self.que_delete_button.setToolTip('목록 삭제')
        self.que_up_button = QPushButton(QIcon('./assets/up.png'), '')
        self.que_up_button.setIconSize(icon_size)
        self.que_up_button.setFixedSize(icon_button_size)
        self.que_up_button.setToolTip('위로')
        self.que_down_button = QPushButton(QIcon('./assets/down.png'), '')
        self.que_down_button.setIconSize(icon_size)
        self.que_down_button.setFixedSize(icon_button_size)
        self.que_down_button.setToolTip('아래로')
        self.que_clear_button = QPushButton(QIcon('./assets/clear.png'), '')
        self.que_clear_button.setIconSize(icon_size)
        self.que_clear_button.setFixedSize(icon_button_size)
        self.que_clear_button.setToolTip('비우기')

        self.file_label = QLabel('파일 목록')
        self.file_label.setFixedHeight(24)
        self.file_widget = QWidget()
        self.file_layout = QGridLayout()
        self.file_layout.setContentsMargins(0, 0, 0, 0)
        self.file_list = QTreeWidget()
        self.file_list.setAcceptDrops(True)
        self.file_list.setHeaderLabels(['이름', '경로'])
        self.file_file_open = QPushButton(QIcon('./assets/file.png'), '')
        self.file_file_open.setFixedSize(icon_button_size)
        self.file_file_open.setIconSize(icon_size)
        self.file_file_open.setToolTip('파일 열기')
        self.file_dir_open = QPushButton(QIcon('./assets/folder.png'), '')
        self.file_dir_open.setFixedSize(icon_button_size)
        self.file_dir_open.setIconSize(icon_size)
        self.file_dir_open.setToolTip('폴더 열기')
        self.file_delete = QPushButton(QIcon('./assets/remove.png'), '')
        self.file_delete.setFixedSize(icon_button_size)
        self.file_delete.setIconSize(icon_size)
        self.file_delete.setToolTip('목록 삭제')
        self.file_clear = QPushButton(QIcon('./assets/clear.png'), '')
        self.file_clear.setFixedSize(icon_button_size)
        self.file_clear.setIconSize(icon_size)
        self.file_clear.setToolTip('비우기')
        self.file_encode = QPushButton(QIcon('./assets/encode.png'), '')
        self.file_encode.setFixedSize(icon_button_size)
        self.file_encode.setIconSize(icon_size)
        self.file_encode.setToolTip('인코딩 설정')

        self.save_widget = QGroupBox('저장 옵션')
        self.save_widget.setMinimumSize(400, 0)
        self.save_widget.setFixedHeight(82)
        self.save_layout = QGridLayout()
        self.save_orig_radio = QRadioButton('원본 위치에 저장')
        self.save_orig_radio.setChecked(True)
        self.save_strip = QCheckBox('싱크 꼬임 무시')
        self.save_strip.setToolTip('싱크 꼬임을 무시하고 모든 자막을 보존합니다.')
        self.save_dir_radio = QRadioButton('다른 위치에 저장')
        self.save_dir_line = QLineEdit()
        self.save_dir_find = QPushButton('...')
        self.save_dir_find.setFixedWidth(40)

        self.ok_button = QPushButton('적용')
        self.ok_button.setFixedSize(normal_button_size)
        self.cancel_button = QPushButton('취소')
        self.cancel_button.setFixedSize(normal_button_size)

        # Display GUI Components
        self.central_layout.addWidget(self.tab_group_widget, 0, 0, 1, 3)
        self.central_layout.addWidget(self.que_label, 1, 0, 1, 3)
        self.central_layout.addWidget(self.que_widget, 2, 0, 1, 3)
        self.central_layout.addWidget(self.file_label, 3, 0, 1, 3)
        self.central_layout.addWidget(self.file_widget, 4, 0, 1, 3)
        self.central_layout.addWidget(self.save_widget, 5, 0, 1, 3)
        self.central_layout.addWidget(self.ok_button, 6, 1, 1, 1)
        self.central_layout.addWidget(self.cancel_button, 6, 2, 1, 1)

        self.tab_group_widget.addTab(self.tab_page_1, QIcon(), self.tab1_name)
        self.tab_group_widget.addTab(self.tab_page_2, QIcon(), self.tab2_name)
        self.tab_group_widget.addTab(self.tab_page_3, QIcon(), self.tab3_name)

        self.tab_page_1.setLayout(self.tab_grid_1)
        self.tab_grid_1.addWidget(self.tab1_search_label, 0, 0, 1, 1)
        self.tab_grid_1.addWidget(self.tab1_search, 0, 1, 1, 2)
        self.tab_grid_1.addWidget(self.tab1_sponsor, 1, 1, 1, 1)
        self.tab_grid_1.addWidget(self.tab1_offset, 1, 2, 1, 1)
        self.tab_grid_1.addWidget(self.tab1_ignore, 2, 1, 1, 2)
        self.tab_grid_1.addWidget(self.tab1_add_button, 3, 0, 1, 3)
        self.tab1_sponsor.setLayout(self.tab1_sponsor_layout)
        self.tab1_sponsor_layout.addWidget(self.tab1_sponsor_label)
        self.tab1_sponsor_layout.addWidget(self.tab1_sponsor_value)
        self.tab1_sponsor_layout.addStretch(1)
        self.tab1_offset.setLayout(self.tab1_offset_layout)
        self.tab1_offset_layout.addWidget(self.tab1_offset_label)
        self.tab1_offset_layout.addWidget(self.tab1_offset_value)
        self.tab1_offset_layout.addStretch(1)
        self.tab1_ignore.setLayout(self.tab1_ignore_layout)
        self.tab1_ignore_layout.addWidget(self.tab1_ignore_label1)
        self.tab1_ignore_layout.addWidget(self.tab1_ignore_value)
        self.tab1_ignore_layout.addWidget(self.tab1_ignore_label2)
        self.tab1_ignore_layout.addWidget(self.tab1_ignore_sec)
        self.tab1_ignore_layout.addWidget(self.tab1_ignore_label3)
        self.tab1_ignore_layout.addStretch(1)

        self.tab_page_2.setLayout(self.tab_grid_2)
        self.tab_grid_2.setRowStretch(0, 1)
        self.tab_grid_2.addWidget(self.tab2_shift, 1, 0, 2, 1)
        self.tab_grid_2.addWidget(self.tab2_slow_radio, 1, 1, 1, 1)
        self.tab_grid_2.addWidget(self.tab2_fast_radio, 2, 1, 1, 1)
        self.tab_grid_2.setColumnStretch(2, 1)
        self.tab_grid_2.setRowStretch(3, 1)
        self.tab_grid_2.addWidget(self.tab2_add_button, 4, 0, 1, 3)
        self.tab2_shift.setLayout(self.tab2_shift_layout)
        self.tab2_shift_layout.addWidget(self.tab2_shift_label1)
        self.tab2_shift_layout.addWidget(self.tab2_shift_value)
        self.tab2_shift_layout.addWidget(self.tab2_shift_label2)

        self.tab_page_3.setLayout(self.tab_grid_3)
        self.tab_grid_3.setRowStretch(0, 1)
        self.tab_grid_3.addWidget(self.tab3_speed_label1, 1, 0, 1, 1)
        self.tab_grid_3.addWidget(self.tab3_speed_value, 1, 1, 1, 1)
        self.tab_grid_3.addWidget(self.tab3_speed_label2, 1, 2, 1, 1)
        self.tab_grid_3.setColumnStretch(3, 1)
        self.tab_grid_3.setRowStretch(2, 1)
        self.tab_grid_3.addWidget(self.tab3_add_button, 3, 0, 1, 4)

        self.que_widget.setLayout(self.que_layout)
        self.que_layout.addWidget(self.que_list, 0, 0, 4, 1)
        self.que_layout.addWidget(self.que_delete_button, 0, 1, 1, 1)
        self.que_layout.addWidget(self.que_up_button, 1, 1, 1, 1)
        self.que_layout.addWidget(self.que_down_button, 2, 1, 1, 1)
        self.que_layout.addWidget(self.que_clear_button, 3, 1, 1, 1)

        self.file_widget.setLayout(self.file_layout)
        self.file_layout.addWidget(self.file_list, 0, 0, 6, 1)
        self.file_layout.addWidget(self.file_file_open, 0, 1, 1, 1)
        self.file_layout.addWidget(self.file_dir_open, 1, 1, 1, 1)
        self.file_layout.addWidget(self.file_delete, 2, 1, 1, 1)
        self.file_layout.addWidget(self.file_clear, 3, 1, 1, 1)
        self.file_layout.addWidget(self.file_encode, 5, 1, 1, 1)

        self.save_widget.setLayout(self.save_layout)
        self.save_layout.addWidget(self.save_orig_radio, 0, 0, 1, 1)
        self.save_layout.setColumnStretch(1, 1)
        self.save_layout.addWidget(self.save_strip, 0, 2, 1, 2)
        self.save_layout.addWidget(self.save_dir_radio, 1, 0, 1, 1)
        self.save_layout.addWidget(self.save_dir_line, 1, 1, 1, 2)
        self.save_layout.addWidget(self.save_dir_find, 1, 3, 1, 1)

        self.setWindowTitle('Batch SAMI Sync v0.1')
        self.setCentralWidget(self.central_widget)
        self.adjustSize()
        self.show()

    def attach_event(self):
        # Default encoding hack
        self.encoding = '자동'

        # Define and Connect event handlers
        def tab1_add():
            sponsor_text = self.tab1_search.text()
            sponsor_time = self.tab1_sponsor_value.value()
            line_offset = self.tab1_offset_value.value()
            line_ignore = self.tab1_ignore_value.value()
            time_ignore = self.tab1_ignore_sec.value()
            data = [1, sponsor_time, sponsor_text, line_offset, line_ignore, time_ignore]
            item = QTreeWidgetItem(self.que_list, [self.tab1_name, '스폰서 영상 시간 : ' + str(sponsor_time) + '초, 오프셋 : ' + str(line_offset) + '줄, 시작부터 ' + str(line_ignore) + '번째 줄, ' + str(time_ignore) + '초 무시 - 검색어 : ' + sponsor_text])
            item.setData(2, 2, data)

        def tab2_add():
            shift_time = self.tab2_shift_value.value()
            shift_direction = self.tab2_fast_radio.isChecked()
            direction_text = '빠르게' if shift_direction else '느리게'
            data = [2, shift_time, shift_direction]
            item = QTreeWidgetItem(self.que_list, [self.tab2_name, '자막 싱크 ' + str(shift_time) + '초 ' + direction_text])
            item.setData(2, 2, data)

        def tab3_add():
            speed_rate = self.tab3_speed_value.value()
            data = [3, speed_rate]
            item = QTreeWidgetItem(self.que_list, [self.tab3_name, '자막 속도 ' + str(speed_rate) + '%'])
            item.setData(2, 2, data)

        def file_open():
            selected = QFileDialog.getOpenFileNames(self, "자막 파일 선택", "", "SAMI Files (*.smi);;All Files (*)")
            for file in selected[0]:
                name = ntpath.basename(file)
                Utils.insert_list(self.file_list, name, file)

        def dir_open():
            selected = QFileDialog.getExistingDirectory(self, "자막 폴더 선택")
            for paths, subdirs, files in os.walk(selected):
                for file in files:
                    if fnmatch(file, '*.smi'):
                        name = ntpath.basename(file)
                        Utils.insert_list(self.file_list, name, file)

        def open_encode_dialog():
            self.dialog = QInputDialog(self)
            self.dialog.setWindowTitle('인코딩 설정')
            self.dialog.setLabelText('텍스트 인코딩 설정')
            self.dialog.setComboBoxItems(['자동', 'EUC-KR', 'UTF-8', 'UTF-16LE', 'UTF-16BE', '직접 입력'])
            self.dialog.show()

            self.dialog.textValueChanged.connect(type_encode)
            self.dialog.textValueSelected.connect(set_encode)

        def type_encode(text):
            if text == '직접 입력':
                self.dialog.setComboBoxItems([])
                self.dialog.setComboBoxEditable(True)

        def set_encode(text):
            self.encoding = text

        def save_dir():
            selected = QFileDialog.getExistingDirectory(self, "저장 위치 선택")
            self.save_dir_line.setText(selected)

        def apply():
            ques = Utils.read_list(self.que_list, False)
            files = Utils.read_list(self.file_list, False)
            strip = False if self.save_strip.isChecked() else True
            log = []
            for file in files:
                try:
                    text = Utils.launch_que(file[1], ques, self.encoding, strip)
                    if len(text):
                        if self.save_orig_radio.isChecked():
                            savepath = file[1]
                        else:
                            savepath = self.save_dir_line.text() + '/' + file[0]
                        Utils.save_file(savepath, text)
                except Exception as e:
                    log.append(file[0] + ' 처리 오류 : ' + str(e))
            if log:
                ScrollMessageBox(QMessageBox.Warning, 'Batch SAMI Sync', "\n".join(log))

            else:
                QMessageBox.information(self, 'Batch SAMI Sync', '변환 완료!')

        self.tab1_add_button.clicked.connect(tab1_add)
        self.tab2_add_button.clicked.connect(tab2_add)
        self.tab3_add_button.clicked.connect(tab3_add)
        self.que_delete_button.clicked.connect(lambda: Utils.delete_list(self.que_list))
        self.que_clear_button.clicked.connect(lambda: Utils.clear_list(self.que_list))
        self.que_up_button.clicked.connect(lambda: Utils.up_list(self.que_list))
        self.que_down_button.clicked.connect(lambda: Utils.down_list(self.que_list))
        self.file_file_open.clicked.connect(file_open)
        self.file_dir_open.clicked.connect(dir_open)
        self.file_delete.clicked.connect(lambda: Utils.delete_list(self.file_list))
        self.file_clear.clicked.connect(lambda: Utils.clear_list(self.file_list))
        self.file_encode.clicked.connect(open_encode_dialog)
        self.save_dir_find.clicked.connect(save_dir)
        self.ok_button.clicked.connect(apply)
        self.cancel_button.clicked.connect(sys.exit)

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls:
            event.accept()
        else:
            event.ignore()

    def dragMoveEvent(self, event):
        if event.mimeData().hasUrls():
            event.setDropAction(Qt.CopyAction)
            event.accept()
        else:
            event.ignore()

    def dropEvent(self, event):
        if event.mimeData().hasUrls():
            event.setDropAction(Qt.CopyAction)
            event.accept()
            for url in event.mimeData().urls():
                if url.isLocalFile():
                    file = str(url.toLocalFile())
                    if fnmatch(file, '*.smi'):
                        name = ntpath.basename(file)
                        Utils.insert_list(self.file_list, name, file)
        else:
            event.ignore()


# Class only for wrapping independent utility functions to manage them easily.
# You can treat this class just like a collection of App()'s static methods
class Utils:
    @staticmethod
    def clear_list(tree: QTreeWidget):
        tree.clear()

    @staticmethod
    def delete_list(tree: QTreeWidget):
        selected = tree.currentItem()
        if selected:
            index = tree.indexOfTopLevelItem(selected)
            tree.takeTopLevelItem(index)

    @staticmethod
    def up_list(tree: QTreeWidget):
        selected = tree.currentItem()
        if selected:
            index = tree.indexOfTopLevelItem(selected)
            name = selected.text(0)
            desc = selected.text(1)
            data = selected.data(2, 2)
            new = QTreeWidgetItem([name, desc])
            new.setData(2, 2, data)
            tree.takeTopLevelItem(index)
            tree.insertTopLevelItem(index - 1, new)
            tree.setCurrentItem(new)

    @staticmethod
    def down_list(tree: QTreeWidget):
        selected = tree.currentItem()
        if selected:
            index = tree.indexOfTopLevelItem(selected)
            name = selected.text(0)
            desc = selected.text(1)
            data = selected.data(2, 2)
            new = QTreeWidgetItem([name, desc])
            new.setData(2, 2, data)
            tree.takeTopLevelItem(index)
            tree.insertTopLevelItem(index + 1, new)
            tree.setCurrentItem(new)

    @staticmethod
    def read_list(tree: QTreeWidget, remove: bool):
        iterator = QTreeWidgetItemIterator(tree)
        items = []
        while iterator.value():
            item = iterator.value()
            items.append([item.text(0), item.text(1), item.data(2, 2)])
            if remove:
                tree.takeTopLevelItem(tree.indexOfTopLevelItem(item))
            iterator += 1
        return items

    @staticmethod
    def insert_list(tree: QTreeWidget, col0: str, col1: str):
        searched = tree.findItems(col1, Qt.MatchExactly, 1)
        if not searched:
            item = QTreeWidgetItem([col0, col1])
            tree.addTopLevelItem(item)

    @staticmethod
    def launch_que(path: str, ques: list, encoding: str, strip: bool):
        def auto_encode(byte):
            result = chardet.detect(byte)
            return result['encoding']

        with open(path, "rb") as f:
            data = f.read()
        encode_group = {
            '자동': auto_encode(data[:10]),
            'EUC-KR': 'euc-kr',
            'UTF-8': 'utf-8',
            'UTF-16LE': 'utf-16-le',
            'UTF-16BE': 'utf-16-be'
        }
        encode = encode_group[encoding] if encode_group[encoding] else encoding
        encode_log = {encode}
        try:
            with open(path, "rt", encoding=encode) as f:
                text = f.read()
        except UnicodeDecodeError:
            try:
                encode = auto_encode(data)
                encode_log.add(encode)
                with open(path, "rt", encoding=encode) as f:
                    text = f.read()
            except UnicodeDecodeError:
                raise Exception('자막 열기 실패 - 인코딩이 ' + ', '.join(encode_log) + '가 아닙니다.')
        subtitle = Sami.parse(text)
        for que in ques:
            func_data = que[2]
            if func_data[0] == 1:
                subtitle = subtitle.sponsorSwitcher(func_data[1], func_data[2], func_data[3], func_data[4], func_data[5], strip)
            elif func_data[0] == 2:
                time = func_data[1] if func_data[2] else (func_data[1] * -1)
                subtitle = subtitle.shiftStamp(time, 0, strip)
            elif func_data[0] == 3:
                subtitle = subtitle.changeSpeed(func_data[1])
            else:
                raise Exception('알 수 없는 오류')
        return subtitle.stringify()

    @staticmethod
    def save_file(path: str, text: str):
        try:
            with open(path, "w", encoding='utf-8') as f:
                f.write(text)
        except UnicodeEncodeError:
            with open(path, "w", encoding='utf-16') as f:
                f.write(text)
        except Exception as E:
            raise Exception('파일을 저장할 수 없습니다. - ' + str(E))


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = App()
    sys.exit(app.exec_())
