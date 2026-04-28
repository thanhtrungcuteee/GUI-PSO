# GUI_ver1.py — Improved UI for PSO Power System Optimizer
# Based on GUI_ver0.py with modernized layout, stylesheet, and UX improvements

from PyQt6 import QtCore, QtGui, QtWidgets
from PyQt6.QtWidgets import (QFileDialog, QScrollArea, QWidget,
                              QVBoxLayout, QHBoxLayout, QLabel, QFrame)
from PyQt6.QtCore import QObject, pyqtSignal
import json
import threading

# ─────────────────────────────────────────────────────────────
# Modern stylesheet (blue / white professional theme)
# ─────────────────────────────────────────────────────────────
STYLESHEET = """
/* ── Global ── */
QMainWindow, QWidget {
    background-color: #F0F4F8;
    font-family: 'Segoe UI', Arial, sans-serif;
    font-size: 10pt;
    color: #2C3E50;
}

/* ── Tab widget ── */
QTabWidget::pane {
    border: 2px solid #90CAF9;
    border-radius: 6px;
    background-color: #FFFFFF;
    top: -2px;
}
QTabBar::tab {
    background-color: #E3F2FD;
    color: #1565C0;
    border: 1px solid #90CAF9;
    border-bottom: none;
    border-radius: 5px 5px 0 0;
    padding: 6px 18px;
    margin-right: 3px;
    font-weight: bold;
    font-size: 10pt;
    min-width: 70px;
}
QTabBar::tab:selected {
    background-color: #1565C0;
    color: #FFFFFF;
    border-color: #1565C0;
}
QTabBar::tab:hover:!selected {
    background-color: #BBDEFB;
}

/* ── Group boxes ── */
QGroupBox {
    font-weight: bold;
    font-size: 10pt;
    border: 2px solid #90CAF9;
    border-radius: 8px;
    margin-top: 14px;
    background-color: #FFFFFF;
    color: #1565C0;
}
QGroupBox::title {
    subcontrol-origin: margin;
    left: 14px;
    padding: 0 8px;
    color: #1565C0;
    background-color: #FFFFFF;
}

/* ── Line edits ── */
QLineEdit {
    border: 1px solid #90CAF9;
    border-radius: 5px;
    padding: 4px 8px;
    background-color: #FFFFFF;
    color: #2C3E50;
    selection-background-color: #1565C0;
}
QLineEdit:focus {
    border: 2px solid #1565C0;
    background-color: #E3F2FD;
}

/* ── Spin boxes ── */
QSpinBox, QDoubleSpinBox {
    border: 1px solid #90CAF9;
    border-radius: 5px;
    padding: 3px 6px;
    background-color: #FFFFFF;
    color: #2C3E50;
}
QSpinBox:focus, QDoubleSpinBox:focus {
    border: 2px solid #1565C0;
}
QSpinBox::up-button, QDoubleSpinBox::up-button,
QSpinBox::down-button, QDoubleSpinBox::down-button {
    width: 16px;
}

/* ── Combo boxes ── */
QComboBox {
    border: 1px solid #90CAF9;
    border-radius: 5px;
    padding: 4px 8px;
    background-color: #FFFFFF;
    color: #2C3E50;
    min-width: 90px;
}
QComboBox:focus { border: 2px solid #1565C0; }
QComboBox::drop-down { border: none; width: 22px; }
QComboBox QAbstractItemView {
    border: 1px solid #90CAF9;
    selection-background-color: #1565C0;
    selection-color: #FFFFFF;
    background-color: #FFFFFF;
}

/* ── Checkboxes ── */
QCheckBox {
    spacing: 8px;
    color: #2C3E50;
}
QCheckBox::indicator {
    width: 16px;
    height: 16px;
    border: 2px solid #90CAF9;
    border-radius: 4px;
    background-color: #FFFFFF;
}
QCheckBox::indicator:checked {
    background-color: #1565C0;
    border-color: #1565C0;
}
QCheckBox::indicator:hover {
    border-color: #1976D2;
}

/* ── All buttons (default blue) ── */
QPushButton {
    border: none;
    border-radius: 5px;
    padding: 6px 16px;
    font-weight: bold;
    font-size: 10pt;
    color: #FFFFFF;
    background-color: #1565C0;
}
QPushButton:hover    { background-color: #1976D2; }
QPushButton:pressed  { background-color: #0D47A1; }
QPushButton:disabled { background-color: #BDBDBD; color: #757575; }

/* ── Browse buttons (⋮ kebab) ── */
QPushButton[objectName="sav"],
QPushButton[objectName="dyr"],
QPushButton[objectName="out"],
QPushButton[objectName="ref"] {
    background-color: #546E7A;
    padding: 0px 0px;
    font-size: 14pt;
    font-weight: bold;
    min-width: 0px;
    min-height: 0px;
    border-radius: 4px;
}
QPushButton[objectName="sav"]:hover,
QPushButton[objectName="dyr"]:hover,
QPushButton[objectName="out"]:hover,
QPushButton[objectName="ref"]:hover { background-color: #607D8B; }

/* ── RUN button ── */
QPushButton[objectName="run"] {
    background-color: #2E7D32;
    padding: 4px 12px;
    font-size: 11pt;
    border-radius: 6px;
    min-width: 80px;
    min-height: 0px;
    margin: 4px 2px;
}
QPushButton[objectName="run"]:hover    { background-color: #388E3C; }
QPushButton[objectName="run"]:disabled { background-color: #BDBDBD; }

/* ── CANCEL button ── */
QPushButton[objectName="cancel"] {
    background-color: #C62828;
    padding: 4px 12px;
    font-size: 11pt;
    border-radius: 6px;
    min-width: 80px;
    min-height: 0px;
    margin: 4px 2px;
}
QPushButton[objectName="cancel"]:hover { background-color: #D32F2F; }

/* ── HELP button ── */
QPushButton[objectName="pushButton_2"] {
    background-color: #546E7A;
    padding: 4px 12px;
    font-size: 11pt;
    border-radius: 6px;
    min-width: 80px;
    min-height: 0px;
    margin: 4px 2px;
}
QPushButton[objectName="pushButton_2"]:hover { background-color: #607D8B; }

/* ── Select All buttons ── */
QPushButton[objectName="GEN_select_all"],
QPushButton[objectName="AVR_select_all"],
QPushButton[objectName="GOV_select_all"],
QPushButton[objectName="PSS_select_all"] {
    background-color: #0288D1;
    padding: 4px 12px;
    font-size: 9pt;
    border-radius: 4px;
}
QPushButton[objectName="GEN_select_all"]:hover,
QPushButton[objectName="AVR_select_all"]:hover,
QPushButton[objectName="GOV_select_all"]:hover,
QPushButton[objectName="PSS_select_all"]:hover { background-color: #0277BD; }

/* ── Log output (dark terminal) ── */
QTextEdit {
    border: 1px solid #37474F;
    border-radius: 6px;
    background-color: #1E272E;
    color: #CFD8DC;
    font-family: 'Courier New', 'Consolas', monospace;
    font-size: 9pt;
    padding: 6px;
}

/* ── Scrollbars ── */
QScrollBar:vertical {
    border: none;
    background-color: #F0F4F8;
    width: 10px;
    margin: 0;
}
QScrollBar::handle:vertical {
    background-color: #90CAF9;
    border-radius: 5px;
    min-height: 24px;
}
QScrollBar::handle:vertical:hover { background-color: #1565C0; }
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical { height: 0; }

/* ── Status bar ── */
QStatusBar {
    background-color: #1565C0;
    color: #FFFFFF;
    font-size: 9pt;
    padding: 2px 8px;
}
QStatusBar::item { border: none; }

/* ── Menu bar ── */
QMenuBar {
    background-color: #1565C0;
    color: #FFFFFF;
    padding: 2px;
}
QMenuBar::item { padding: 4px 12px; border-radius: 3px; }
QMenuBar::item:selected { background-color: #1976D2; }

/* ── Labels (transparent background) ── */
QLabel { background: transparent; color: #2C3E50; }

/* ── Separator line ── */
QFrame[frameShape="4"],
QFrame[frameShape="5"] {
    color: #90CAF9;
}
"""


# ─────────────────────────────────────────────────────────────
# Signal emitter for thread-safe GUI updates
# ─────────────────────────────────────────────────────────────
class LogEmitter(QObject):
    log_signal = pyqtSignal(str)


# ─────────────────────────────────────────────────────────────
# Main UI class
# ─────────────────────────────────────────────────────────────
class Ui_MainWindow(object):

    # ── helpers ──────────────────────────────────────────────
    def load_json(self):
        try:
            with open('Model.json', "r") as f:
                return json.load(f)
        except Exception as e:
            print(f"ERROR loading Model.json: {e}")
            return {}

    def _make_label(self, parent, text, x, y, w=120, h=22, bold=False, size=10, align=None):
        lbl = QtWidgets.QLabel(parent=parent)
        lbl.setGeometry(QtCore.QRect(x, y, w, h))
        font = QtGui.QFont()
        font.setPointSize(size)
        font.setBold(bold)
        lbl.setFont(font)
        lbl.setText(text)
        if align:
            lbl.setAlignment(align)
        return lbl

    def _make_browse_btn(self, parent, obj_name, x, y, slot):
        """Browse button sized to exactly match lineedit height (26px), width 22px."""
        btn = QtWidgets.QPushButton(parent=parent)
        btn.setGeometry(QtCore.QRect(x, y, 22, 26))
        btn.setObjectName(obj_name)
        btn.setText("⋮")
        font_btn = QtGui.QFont()
        font_btn.setPointSize(13)
        font_btn.setBold(True)
        btn.setFont(font_btn)
        btn.clicked.connect(slot)
        return btn

    def _make_file_row(self, parent, label_text, obj_name, default_text,
                       browse_slot, ly, label_w=70, total_w=820):
        """Create label + lineedit + browse button row inside a groupbox."""
        lbl = self._make_label(parent, label_text, 16, ly, label_w, 26)

        edit = QtWidgets.QLineEdit(parent=parent)
        edit.setGeometry(QtCore.QRect(label_w + 20, ly, total_w - label_w - 70, 26))
        edit.setObjectName(obj_name)
        edit.setText(default_text)
        font = QtGui.QFont()
        font.setPointSize(9)
        edit.setFont(font)

        btn = self._make_browse_btn(parent, obj_name + "_btn",
                                    total_w - 44, ly, browse_slot)
        # give browse buttons their matching objectName for QSS
        btn.setObjectName(obj_name.split("_")[0])
        return edit

    # ─────────────────────────────────────────────────────────
    # Reusable widget factories (no absolute coords)
    # ─────────────────────────────────────────────────────────
    def _lbl(self, text, bold=False, size=10):
        lbl = QtWidgets.QLabel(text)
        f = QtGui.QFont(); f.setPointSize(size); f.setBold(bold)
        lbl.setFont(f)
        return lbl

    def _browse_btn(self, obj_name, slot):
        btn = QtWidgets.QPushButton("⋮")
        btn.setObjectName(obj_name)
        btn.setFixedSize(22, 26)
        f = QtGui.QFont(); f.setPointSize(13); f.setBold(True)
        btn.setFont(f)
        btn.clicked.connect(slot)
        return btn

    def _hline(self):
        f = QFrame(); f.setFrameShape(QFrame.Shape.HLine)
        f.setFixedHeight(2)
        f.setStyleSheet("background-color:#90CAF9; border:none;")
        return f

    # ── setupUi ──────────────────────────────────────────────
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(1000, 720)
        MainWindow.setMinimumSize(860, 580)
        MainWindow.setStyleSheet(STYLESHEET)

        self.centralwidget = QtWidgets.QWidget(parent=MainWindow)
        root = QVBoxLayout(self.centralwidget)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        # ── font reused across all groupboxes ─────────────────
        font_gb = QtGui.QFont()
        font_gb.setPointSize(11)
        font_gb.setBold(True)

        # ── Header ────────────────────────────────────────────
        header_frame = QFrame()
        header_frame.setFixedHeight(46)
        header_frame.setStyleSheet(
            "background-color:#1565C0; border-bottom:2px solid #0D47A1;")
        hdr_lay = QHBoxLayout(header_frame)
        hdr_lay.setContentsMargins(0, 0, 0, 0)
        self.label = QtWidgets.QLabel("Công cụ tối ưu tham số PSO – PSSE")
        ft = QtGui.QFont(); ft.setPointSize(16); ft.setBold(True)
        self.label.setFont(ft)
        self.label.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        self.label.setStyleSheet("color:#FFFFFF; background:transparent;")
        hdr_lay.addWidget(self.label)
        root.addWidget(header_frame)

        # ── Tab widget ────────────────────────────────────────
        self.tab_box = QtWidgets.QTabWidget()
        self.tab_box.setObjectName("tab_box")
        root.addWidget(self.tab_box, stretch=1)

        # ═══════════════════════════════════════════════════════
        #   TAB 1 – Input
        # ═══════════════════════════════════════════════════════
        self.tab = QtWidgets.QWidget()
        t1 = QVBoxLayout(self.tab)
        t1.setContentsMargins(8, 8, 8, 8)
        t1.setSpacing(8)

        # top row: file paths (stretch) + control buttons (fixed)
        top_row = QHBoxLayout(); top_row.setSpacing(8)

        # ── Group: Đường dẫn file ─────────────────────────────
        self.groupBox = QtWidgets.QGroupBox("Đường dẫn file")
        self.groupBox.setFont(font_gb)
        fg = QtWidgets.QGridLayout(self.groupBox)
        fg.setContentsMargins(12, 22, 12, 12)
        fg.setHorizontalSpacing(6)
        fg.setVerticalSpacing(10)
        fg.setColumnStretch(1, 1)

        for row, (lbl_txt, edit_attr, btn_attr, slot) in enumerate([
            ("SAV file:", "sav_text", "sav", self.select_sav_file),
            ("DYR file:", "dyr_text", "dyr", self.select_dyr_file),
            ("OUT file:", "out_text", "out", self.select_out_file),
        ]):
            fg.addWidget(self._lbl(lbl_txt), row, 0)
            edit = QtWidgets.QLineEdit()
            edit.setObjectName(edit_attr)
            setattr(self, edit_attr, edit)
            fg.addWidget(edit, row, 1)
            btn = self._browse_btn(btn_attr, slot)
            setattr(self, btn_attr, btn)
            fg.addWidget(btn, row, 2)

        top_row.addWidget(self.groupBox, stretch=1)

        # ── Group: Điều khiển ─────────────────────────────────
        self.btn_group = QtWidgets.QGroupBox("Điều khiển")
        self.btn_group.setFont(font_gb)
        self.btn_group.setFixedWidth(220)
        bg = QVBoxLayout(self.btn_group)
        bg.setContentsMargins(12, 18, 12, 12)
        bg.setSpacing(0)

        self.run = QtWidgets.QPushButton("▶  RUN")
        self.run.setObjectName("run")
        self.run.setFixedHeight(32)
        self.run.clicked.connect(self.run_py)
        bg.addWidget(self.run)
        bg.addWidget(self._hline())

        self.pushButton_2 = QtWidgets.QPushButton("?  HELP")
        self.pushButton_2.setObjectName("pushButton_2")
        self.pushButton_2.setFixedHeight(32)
        bg.addWidget(self.pushButton_2)
        bg.addWidget(self._hline())

        self.cancel = QtWidgets.QPushButton("✕  CANCEL")
        self.cancel.setObjectName("cancel")
        self.cancel.setFixedHeight(32)
        self.cancel.clicked.connect(self.stop)
        bg.addWidget(self.cancel)
        bg.addStretch()

        top_row.addWidget(self.btn_group)
        t1.addLayout(top_row)

        # ── Group: Log ────────────────────────────────────────
        self.groupBox_2 = QtWidgets.QGroupBox("Nhật ký thực thi (Log)")
        self.groupBox_2.setFont(font_gb)
        lg = QVBoxLayout(self.groupBox_2)
        lg.setContentsMargins(8, 20, 8, 8)
        self.log_output = QtWidgets.QTextEdit()
        self.log_output.setReadOnly(True)
        self.log_output.setObjectName("log_output")
        lg.addWidget(self.log_output)
        t1.addWidget(self.groupBox_2, stretch=1)

        self.tab_box.addTab(self.tab, "  Input  ")

        # ═══════════════════════════════════════════════════════
        #   TAB 2 – PSSE Setting
        # ═══════════════════════════════════════════════════════
        self.tab_2 = QtWidgets.QWidget()
        t2 = QVBoxLayout(self.tab_2)
        t2.setContentsMargins(8, 8, 8, 8)
        t2.setSpacing(8)

        top2 = QHBoxLayout(); top2.setSpacing(8)

        # ── Group: Thông tin máy phát ─────────────────────────
        self.groupBox_3 = QtWidgets.QGroupBox("Thông tin máy phát")
        self.groupBox_3.setFont(font_gb)
        g3 = QtWidgets.QGridLayout(self.groupBox_3)
        g3.setContentsMargins(12, 22, 12, 12)
        g3.setHorizontalSpacing(8)
        g3.setVerticalSpacing(10)
        g3.setColumnStretch(1, 1); g3.setColumnStretch(3, 1)

        g3.addWidget(self._lbl("Bus ID:"), 0, 0)
        self.Bus_id = QtWidgets.QLineEdit("293210")
        self.Bus_id.setObjectName("Bus_id")
        g3.addWidget(self.Bus_id, 0, 1)
        g3.addWidget(self._lbl("Gen ID:"), 0, 2)
        self.gen_id = QtWidgets.QLineEdit("1")
        self.gen_id.setObjectName("gen_id")
        g3.addWidget(self.gen_id, 0, 3)

        g3.addWidget(self._lbl("Thời gian mô phỏng (s):"), 1, 0)
        self.simulation_time = QtWidgets.QSpinBox()
        self.simulation_time.setObjectName("simulation_time")
        self.simulation_time.setValue(10)
        g3.addWidget(self.simulation_time, 1, 1, 1, 3)

        g3.addWidget(self._lbl("Thời gian sự cố (s):"), 2, 0)
        self.time_fault = QtWidgets.QSpinBox()
        self.time_fault.setObjectName("time_fault")
        self.time_fault.setValue(2)
        g3.addWidget(self.time_fault, 2, 1, 1, 3)

        g3.addWidget(self._lbl("Bước nhảy sự cố:"), 3, 0)
        self.step_fault = QtWidgets.QSpinBox()
        self.step_fault.setObjectName("step_fault")
        g3.addWidget(self.step_fault, 3, 1, 1, 3)

        g3.setRowStretch(4, 1)
        top2.addWidget(self.groupBox_3, stretch=1)

        # ── Group: Convert tải ───────────────────────────────
        self.groupBox_6 = QtWidgets.QGroupBox("Convert tải")
        self.groupBox_6.setFont(font_gb)
        g6 = QtWidgets.QGridLayout(self.groupBox_6)
        g6.setContentsMargins(12, 22, 12, 12)
        g6.setHorizontalSpacing(8)
        g6.setVerticalSpacing(10)
        g6.setColumnStretch(1, 1); g6.setColumnStretch(2, 1)

        self.checkBox_2 = QtWidgets.QCheckBox("LOAD")
        self.checkBox_2.setObjectName("checkBox_2")
        g6.addWidget(self.checkBox_2, 0, 0, 1, 3)

        hdr_p = QtWidgets.QLabel("Công suất P")
        hdr_p.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        hdr_p.setStyleSheet("font-weight:bold; color:#1565C0;")
        g6.addWidget(hdr_p, 1, 1)
        hdr_q = QtWidgets.QLabel("Công suất Q")
        hdr_q.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        hdr_q.setStyleSheet("font-weight:bold; color:#1565C0;")
        g6.addWidget(hdr_q, 1, 2)

        g6.addWidget(self._lbl("% Hằng số dòng điện:"), 2, 0)
        self.spinBox_5 = QtWidgets.QSpinBox(); self.spinBox_5.setObjectName("spinBox_5")
        g6.addWidget(self.spinBox_5, 2, 1)
        self.spinBox_7 = QtWidgets.QSpinBox(); self.spinBox_7.setObjectName("spinBox_7")
        g6.addWidget(self.spinBox_7, 2, 2)

        g6.addWidget(self._lbl("% Hằng số tổng dẫn:"), 3, 0)
        self.spinBox_6 = QtWidgets.QSpinBox(); self.spinBox_6.setObjectName("spinBox_6")
        g6.addWidget(self.spinBox_6, 3, 1)
        self.spinBox_8 = QtWidgets.QSpinBox(); self.spinBox_8.setObjectName("spinBox_8")
        g6.addWidget(self.spinBox_8, 3, 2)

        g6.setRowStretch(4, 1)
        top2.addWidget(self.groupBox_6, stretch=1)
        t2.addLayout(top2)

        # ── Group: Thông số động lực học ─────────────────────
        self.groupBox_5 = QtWidgets.QGroupBox("Thông số động lực học")
        self.groupBox_5.setFont(font_gb)
        g5 = QtWidgets.QGridLayout(self.groupBox_5)
        g5.setContentsMargins(12, 22, 12, 12)
        g5.setHorizontalSpacing(8)
        g5.setVerticalSpacing(10)
        g5.setColumnStretch(1, 1); g5.setColumnStretch(3, 1)

        self.checkBox = QtWidgets.QCheckBox("Network Solution")
        self.checkBox.setObjectName("checkBox")
        g5.addWidget(self.checkBox, 0, 0, 1, 4)

        g5.addWidget(self._lbl("Iterations:"), 1, 0)
        self.iteration = QtWidgets.QSpinBox()
        self.iteration.setObjectName("iteration"); self.iteration.setValue(25)
        g5.addWidget(self.iteration, 1, 1)
        g5.addWidget(self._lbl("Tolerance:"), 1, 2)
        self.tolerance = QtWidgets.QLineEdit()
        self.tolerance.setObjectName("tolerance")
        g5.addWidget(self.tolerance, 1, 3)

        self.checkBox_3 = QtWidgets.QCheckBox("Simulation Parameters")
        self.checkBox_3.setObjectName("checkBox_3")
        g5.addWidget(self.checkBox_3, 2, 0, 1, 4)

        g5.addWidget(self._lbl("DELT:"), 3, 0)
        self.DELT = QtWidgets.QLineEdit("0.01"); self.DELT.setObjectName("DELT")
        g5.addWidget(self.DELT, 3, 1)
        g5.addWidget(self._lbl("Freq. Filter:"), 3, 2)
        self.freq = QtWidgets.QLineEdit(); self.freq.setObjectName("freq")
        g5.addWidget(self.freq, 3, 3)

        t2.addWidget(self.groupBox_5)
        t2.addStretch()

        self.tab_box.addTab(self.tab_2, "  PSSE Setting  ")

        # ═══════════════════════════════════════════════════════
        #   TAB 3 – PSO Setting
        # ═══════════════════════════════════════════════════════
        self.tab_4 = QtWidgets.QWidget()
        t4 = QHBoxLayout(self.tab_4)
        t4.setContentsMargins(8, 8, 8, 8)
        t4.setSpacing(8)

        # ── Group: Thông số PSO ───────────────────────────────
        self.PSO_box = QtWidgets.QGroupBox("Thông số PSO")
        self.PSO_box.setFont(font_gb)
        self.PSO_box.setFixedWidth(270)
        pg = QtWidgets.QGridLayout(self.PSO_box)
        pg.setContentsMargins(12, 22, 12, 12)
        pg.setHorizontalSpacing(8); pg.setVerticalSpacing(10)
        pg.setColumnStretch(1, 1)

        pg.addWidget(self._lbl("Số vòng lặp:"), 0, 0)
        self.iteration_2 = QtWidgets.QSpinBox()
        self.iteration_2.setObjectName("iteration_2")
        self.iteration_2.setMaximum(9999); self.iteration_2.setValue(25)
        pg.addWidget(self.iteration_2, 0, 1)

        pg.addWidget(self._lbl("Số hạt:"), 1, 0)
        self.particle = QtWidgets.QSpinBox()
        self.particle.setObjectName("particle")
        self.particle.setMaximum(1000); self.particle.setValue(10)
        pg.addWidget(self.particle, 1, 1)

        for row, (lbl_txt, attr, val) in enumerate([
            ("c1:", "c1", 2.00), ("c2:", "c2", 2.00),
            ("wmax:", "wmax", 1.40), ("wmin:", "wmin", 0.40),
        ], start=2):
            pg.addWidget(self._lbl(lbl_txt), row, 0)
            dsb = QtWidgets.QDoubleSpinBox()
            dsb.setObjectName(attr); dsb.setValue(val)
            pg.addWidget(dsb, row, 1)
            setattr(self, attr, dsb)

        pg.setRowStretch(6, 1)
        t4.addWidget(self.PSO_box)

        # ── Group: REF ────────────────────────────────────────
        self.REF_box = QtWidgets.QGroupBox("Tín hiệu tham chiếu & mục tiêu tối ưu")
        self.REF_box.setFont(font_gb)
        rf = QVBoxLayout(self.REF_box)
        rf.setContentsMargins(12, 22, 12, 12)
        rf.setSpacing(10)

        # ref file row
        ref_row = QHBoxLayout(); ref_row.setSpacing(6)
        ref_row.addWidget(self._lbl("REF file:"))
        self.ref_text = QtWidgets.QLineEdit()
        self.ref_text.setObjectName("ref_text")
        ref_row.addWidget(self.ref_text, stretch=1)
        self.ref = self._browse_btn("ref", self.select_ref_file)
        ref_row.addWidget(self.ref)
        rf.addLayout(ref_row)

        rf.addWidget(self._hline())

        tuning_lbl = self._lbl("Tuning theo đường đồ thị:", bold=True)
        rf.addWidget(tuning_lbl)

        sig_row = QHBoxLayout(); sig_row.setSpacing(12)
        sig_row.addWidget(self._lbl("Chọn tín hiệu:"))
        for txt, obj in [("P","ref_check_P"),("Q","ref_check_Q"),
                          ("Vt","ref_check_Vt"),("Ef","ref_check_Ef"),("If","ref_check_If")]:
            cb = QtWidgets.QCheckBox(txt); cb.setObjectName(obj)
            setattr(self, obj, cb)
            sig_row.addWidget(cb)
        sig_row.addStretch()
        rf.addLayout(sig_row)

        rf.addWidget(self._hline())

        dist_row = QHBoxLayout(); dist_row.setSpacing(8)
        dist_row.addWidget(self._lbl("Loại nhiễu loạn:"))
        self.disturbance = QtWidgets.QComboBox()
        self.disturbance.setObjectName("disturbance")
        self.disturbance.addItems(["No load", "Step response", "Impulse"])
        dist_row.addWidget(self.disturbance)
        dist_row.addStretch()
        rf.addLayout(dist_row)
        rf.addStretch()

        t4.addWidget(self.REF_box, stretch=1)
        self.tab_box.addTab(self.tab_4, "  PSO Setting  ")

        # ═══════════════════════════════════════════════════════
        #   Model tabs: GEN / AVR / GOV / PSS
        # ═══════════════════════════════════════════════════════
        self.tab_Gen = QtWidgets.QWidget()
        self._setup_model_tab(
            tab=self.tab_Gen,
            title_text="Thông số máy phát (GEN)",
            check_attr="GEN_check",  check_text="Sử dụng GEN",
            list_attr="GEN_list",    list_items=["GENROU", "GENSAL"],
            label_attr="GEN_label",  label_text="GEN Model:",
            gb_attr="groupBox_8",    gb_title="Tham số GEN",
            scroll_attr="scroll_GEN",
            scroll_widget_attr="scroll_GEN_widget",
            scroll_layout_attr="scroll_GEN_layout",
            param_widgets_attr="GEN_param_widgets",
            select_all_attr="GEN_select_all",
            check_cb=self._on_GEN_check_changed_cb,
            model_cb=self._on_GEN_model_changed_cb,
            select_all_cb=self.on_GEN_select_all,
        )
        self.tab_box.addTab(self.tab_Gen, "  GEN  ")

        self.tab_AVR = QtWidgets.QWidget()
        self._setup_model_tab(
            tab=self.tab_AVR,
            title_text="Thông số bộ điều chỉnh điện áp (AVR)",
            check_attr="AVR_check",  check_text="Sử dụng AVR",
            list_attr="AVR_list",    list_items=["ST6B", "DC1A", "SEXS"],
            label_attr="AVR_label",  label_text="AVR Model:",
            gb_attr="groupBox_10",   gb_title="Tham số AVR",
            scroll_attr="scroll_AVR",
            scroll_widget_attr="scroll_AVR_widget",
            scroll_layout_attr="scroll_AVR_layout",
            param_widgets_attr="AVR_param_widgets",
            select_all_attr="AVR_select_all",
            check_cb=self._on_AVR_check_changed_cb,
            model_cb=self._on_AVR_model_changed_cb,
            select_all_cb=self.on_AVR_select_all,
        )
        self.tab_box.addTab(self.tab_AVR, "  AVR  ")

        self.tab_GOV = QtWidgets.QWidget()
        self._setup_model_tab(
            tab=self.tab_GOV,
            title_text="Thông số bộ điều tốc (GOV)",
            check_attr="GOV_check",  check_text="Sử dụng GOV",
            list_attr="GOV_list",    list_items=["IEESGO"],
            label_attr="GOV_label",  label_text="GOV Model:",
            gb_attr="groupBox_11",   gb_title="Tham số GOV",
            scroll_attr="scroll_GOV",
            scroll_widget_attr="scroll_GOV_widget",
            scroll_layout_attr="scroll_GOV_layout",
            param_widgets_attr="GOV_param_widgets",
            select_all_attr="GOV_select_all",
            check_cb=self._on_GOV_check_changed_cb,
            model_cb=self._on_GOV_model_changed_cb,
            select_all_cb=self.on_GOV_select_all,
        )
        self.tab_box.addTab(self.tab_GOV, "  GOV  ")

        self.tab_PSS = QtWidgets.QWidget()
        self._setup_model_tab(
            tab=self.tab_PSS,
            title_text="Thông số bộ ổn định hệ thống điện (PSS)",
            check_attr="PSS_check",  check_text="Sử dụng PSS",
            list_attr="PSS_list",    list_items=["PSS2B"],
            label_attr="PSS_label",  label_text="PSS Model:",
            gb_attr="groupBox_13",   gb_title="Tham số PSS",
            scroll_attr="scroll_PSS",
            scroll_widget_attr="scroll_PSS_widget",
            scroll_layout_attr="scroll_PSS_layout",
            param_widgets_attr="PSS_param_widgets",
            select_all_attr="PSS_select_all",
            check_cb=self._on_PSS_check_changed_cb,
            model_cb=self._on_PSS_model_changed_cb,
            select_all_cb=self.on_PSS_select_all,
        )
        self.tab_box.addTab(self.tab_PSS, "  PSS  ")

        # ── Central widget & bars ─────────────────────────────
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(parent=MainWindow)
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(parent=MainWindow)
        self.statusbar.setObjectName("statusbar")
        self.statusbar.showMessage("Sẵn sàng")
        MainWindow.setStatusBar(self.statusbar)
        MainWindow.setWindowTitle("Công cụ tối ưu tham số PSO – PSSE")
        self.tab_box.setCurrentIndex(0)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    # ─────────────────────────────────────────────────────────
    # Generic helper: build a model parameter tab (GEN/AVR/GOV/PSS)
    # ─────────────────────────────────────────────────────────
    # ─────────────────────────────────────────────────────────
    # Generic helper: build a model parameter tab (GEN/AVR/GOV/PSS)
    # ─────────────────────────────────────────────────────────
    def _setup_model_tab(self, tab, title_text,
                          check_attr, check_text,
                          list_attr, list_items,
                          label_attr, label_text,
                          gb_attr, gb_title,
                          scroll_attr, scroll_widget_attr, scroll_layout_attr,
                          param_widgets_attr,
                          select_all_attr,
                          check_cb, model_cb, select_all_cb):
        font_gb = QtGui.QFont()
        font_gb.setPointSize(11)
        font_gb.setBold(True)

        tab_vbox = QVBoxLayout(tab)
        tab_vbox.setContentsMargins(8, 8, 8, 8)
        tab_vbox.setSpacing(8)

        # ── Top control strip ─────────────────────────────────
        strip = QtWidgets.QGroupBox(title_text)
        strip.setFont(font_gb)
        strip.setFixedHeight(72)
        strip_hbox = QHBoxLayout(strip)
        strip_hbox.setContentsMargins(12, 16, 12, 8)
        strip_hbox.setSpacing(12)

        check = QtWidgets.QCheckBox(check_text)
        setattr(self, check_attr, check)
        strip_hbox.addWidget(check)

        lbl = QtWidgets.QLabel(label_text)
        setattr(self, label_attr, lbl)
        strip_hbox.addWidget(lbl)

        combo = QtWidgets.QComboBox()
        combo.setObjectName(list_attr)
        combo.setFixedWidth(130)
        for item in list_items:
            combo.addItem(item)
        setattr(self, list_attr, combo)
        strip_hbox.addWidget(combo)

        strip_hbox.addStretch()

        sel_all = QtWidgets.QPushButton("Select All")
        sel_all.setObjectName(select_all_attr)
        sel_all.setFixedWidth(100)
        sel_all.clicked.connect(select_all_cb)
        setattr(self, select_all_attr, sel_all)
        strip_hbox.addWidget(sel_all)

        tab_vbox.addWidget(strip)

        # Initially hide model controls
        lbl.hide()
        combo.hide()
        sel_all.hide()

        # ── Parameters group box ──────────────────────────────
        gb = QtWidgets.QGroupBox(gb_title)
        gb.setFont(font_gb)
        setattr(self, gb_attr, gb)

        gb_vbox = QVBoxLayout(gb)
        gb_vbox.setContentsMargins(8, 20, 8, 8)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        setattr(self, scroll_attr, scroll)

        sw = QWidget()
        sl = QVBoxLayout(sw)
        sl.setAlignment(QtCore.Qt.AlignmentFlag.AlignTop)
        scroll.setWidget(sw)
        setattr(self, scroll_widget_attr, sw)
        setattr(self, scroll_layout_attr, sl)

        gb_vbox.addWidget(scroll)
        tab_vbox.addWidget(gb, stretch=1)

        gb.hide()
        scroll.hide()

        setattr(self, param_widgets_attr, {})
        check.stateChanged.connect(check_cb)
        combo.currentTextChanged.connect(model_cb)

    # ─────────────────────────────────────────────────────────
    # File dialog slots
    # ─────────────────────────────────────────────────────────
    def select_sav_file(self):
        path, _ = QFileDialog.getOpenFileName(None, "Chọn file SAV", "",
                                               "SAV Files (*.sav);;All Files (*)")
        if path:
            self.sav_text.setText(path)

    def select_dyr_file(self):
        path, _ = QFileDialog.getOpenFileName(None, "Chọn file DYR", "",
                                               "DYR Files (*.dyr);;All Files (*)")
        if path:
            self.dyr_text.setText(path)

    def select_out_file(self):
        path, _ = QFileDialog.getOpenFileName(None, "Chọn file OUT", "",
                                               "OUT Files (*.out);;All Files (*)")
        if path:
            self.out_text.setText(path)

    def select_ref_file(self):
        path, _ = QFileDialog.getOpenFileName(None, "Chọn file tham chiếu", "",
                                               "Data Files (*.csv *.xlsx);;All Files (*)")
        if path:
            self.ref_text.setText(path)

    # ─────────────────────────────────────────────────────────
    # GEN callbacks
    # ─────────────────────────────────────────────────────────
    def _on_GEN_check_changed_cb(self, state):
        checked = state == QtCore.Qt.CheckState.Checked.value
        self.GEN_label.setVisible(checked)
        self.GEN_list.setVisible(checked)
        self.GEN_select_all.setVisible(checked)
        if checked:
            self._on_GEN_model_changed_cb(self.GEN_list.currentText())
        else:
            self.groupBox_8.hide()
            self.scroll_GEN.hide()

    # keep original names so old code (if any) still works
    def on_GEN_check_changed(self, state):
        self._on_GEN_check_changed_cb(state)

    def _on_GEN_model_changed_cb(self, model_name):
        self._build_param_grid(
            scroll_layout=self.scroll_GEN_layout,
            param_widgets=self.GEN_param_widgets,
            check_widget=self.GEN_check,
            groupbox=self.groupBox_8,
            scroll=self.scroll_GEN,
            json_section='GEN',
            model_name=model_name,
            prefix='GEN',
        )

    def on_GEN_model_changed(self, model_name):
        self._on_GEN_model_changed_cb(model_name)

    def on_GEN_select_all(self):
        for w in self.GEN_param_widgets.values():
            w['checkbox'].setChecked(True)

    # ─────────────────────────────────────────────────────────
    # AVR callbacks
    # ─────────────────────────────────────────────────────────
    def _on_AVR_check_changed_cb(self, state):
        checked = state == QtCore.Qt.CheckState.Checked.value
        self.AVR_label.setVisible(checked)
        self.AVR_list.setVisible(checked)
        self.AVR_select_all.setVisible(checked)
        if checked:
            self._on_AVR_model_changed_cb(self.AVR_list.currentText())
        else:
            self.groupBox_10.hide()
            self.scroll_AVR.hide()

    def on_AVR_check_changed(self, state):
        self._on_AVR_check_changed_cb(state)

    def _on_AVR_model_changed_cb(self, model_name):
        self._build_param_grid(
            scroll_layout=self.scroll_AVR_layout,
            param_widgets=self.AVR_param_widgets,
            check_widget=self.AVR_check,
            groupbox=self.groupBox_10,
            scroll=self.scroll_AVR,
            json_section='AVR',
            model_name=model_name,
            prefix='AVR',
        )

    def on_AVR_model_changed(self, model_name):
        self._on_AVR_model_changed_cb(model_name)

    def on_AVR_select_all(self):
        for w in self.AVR_param_widgets.values():
            w['checkbox'].setChecked(True)

    # ─────────────────────────────────────────────────────────
    # GOV callbacks
    # ─────────────────────────────────────────────────────────
    def _on_GOV_check_changed_cb(self, state):
        checked = state == QtCore.Qt.CheckState.Checked.value
        self.GOV_label.setVisible(checked)
        self.GOV_list.setVisible(checked)
        self.GOV_select_all.setVisible(checked)
        if checked:
            self._on_GOV_model_changed_cb(self.GOV_list.currentText())
        else:
            self.groupBox_11.hide()
            self.scroll_GOV.hide()

    def on_GOV_check_changed(self, state):
        self._on_GOV_check_changed_cb(state)

    def _on_GOV_model_changed_cb(self, model_name):
        self._build_param_grid(
            scroll_layout=self.scroll_GOV_layout,
            param_widgets=self.GOV_param_widgets,
            check_widget=self.GOV_check,
            groupbox=self.groupBox_11,
            scroll=self.scroll_GOV,
            json_section='GOV',
            model_name=model_name,
            prefix='GOV',
        )

    def on_GOV_model_changed(self, model_name):
        self._on_GOV_model_changed_cb(model_name)

    def on_GOV_select_all(self):
        for w in self.GOV_param_widgets.values():
            w['checkbox'].setChecked(True)

    # ─────────────────────────────────────────────────────────
    # PSS callbacks
    # ─────────────────────────────────────────────────────────
    def _on_PSS_check_changed_cb(self, state):
        checked = state == QtCore.Qt.CheckState.Checked.value
        self.PSS_label.setVisible(checked)
        self.PSS_list.setVisible(checked)
        self.PSS_select_all.setVisible(checked)
        if checked:
            self._on_PSS_model_changed_cb(self.PSS_list.currentText())
        else:
            self.groupBox_13.hide()
            self.scroll_PSS.hide()

    def on_PSS_check_changed(self, state):
        self._on_PSS_check_changed_cb(state)

    def _on_PSS_model_changed_cb(self, model_name):
        self._build_param_grid(
            scroll_layout=self.scroll_PSS_layout,
            param_widgets=self.PSS_param_widgets,
            check_widget=self.PSS_check,
            groupbox=self.groupBox_13,
            scroll=self.scroll_PSS,
            json_section='PSS',
            model_name=model_name,
            prefix='PSS',
        )

    def on_PSS_model_changed(self, model_name):
        self._on_PSS_model_changed_cb(model_name)

    def on_PSS_select_all(self):
        for w in self.PSS_param_widgets.values():
            w['checkbox'].setChecked(True)

    # ─────────────────────────────────────────────────────────
    # Generic parameter grid builder (replaces repeated code)
    # ─────────────────────────────────────────────────────────
    def _build_param_grid(self, scroll_layout, param_widgets, check_widget,
                           groupbox, scroll, json_section, model_name, prefix):
        # Clear existing widgets
        while scroll_layout.count():
            item = scroll_layout.takeAt(0)
            w = item.widget()
            if w:
                w.setParent(None)
        param_widgets.clear()

        if not check_widget.isChecked() or not model_name:
            groupbox.hide()
            scroll.hide()
            return

        model_data = self.load_json()
        section = model_data.get('Model_dynamic', {}).get(json_section, {})

        if model_name not in section:
            groupbox.hide()
            scroll.hide()
            return

        params = section[model_name]
        if not params:
            groupbox.hide()
            scroll.hide()
            return

        groupbox.show()
        scroll.show()

        grid_widget = QWidget()
        grid_layout = QtWidgets.QGridLayout(grid_widget)
        grid_layout.setContentsMargins(12, 8, 12, 8)
        grid_layout.setHorizontalSpacing(12)
        grid_layout.setVerticalSpacing(6)

        # ── Header row ────────────────────────────────────────
        hdr_param = QLabel("Tham số")
        hdr_param.setStyleSheet("font-weight: bold; color: #1565C0;")
        hdr_default = QLabel("Giá trị mặc định")
        hdr_default.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        hdr_default.setStyleSheet("font-weight: bold; color: #1565C0;")
        hdr_range = QLabel("Phạm vi tìm kiếm [Min  —  Max]")
        hdr_range.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        hdr_range.setStyleSheet("font-weight: bold; color: #1565C0;")

        grid_layout.addWidget(hdr_param,   0, 0)
        grid_layout.addWidget(hdr_default, 0, 1)
        grid_layout.addWidget(hdr_range,   0, 2, 1, 3)

        # ── Separator ─────────────────────────────────────────
        sep = QFrame()
        sep.setFrameShape(QFrame.Shape.HLine)
        sep.setStyleSheet("color: #90CAF9;")
        grid_layout.addWidget(sep, 1, 0, 1, 5)

        for row_idx, (param_name, pv) in enumerate(params.items(), start=2):
            initial = pv.get('initial', 0)
            lb      = pv.get('lb', 0)
            ub      = pv.get('ub', 100)
            idx     = pv.get('idx', 0)

            cb = QtWidgets.QCheckBox(param_name)
            cb.setObjectName(f"{prefix}_{model_name}_{param_name}")

            init_edit = QtWidgets.QLineEdit(f"{initial:.4f}")
            init_edit.setFixedWidth(90)
            init_edit.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
            init_edit.setObjectName(f"{prefix}_{model_name}_{param_name}_init")

            min_edit = QtWidgets.QLineEdit(f"{lb:.4f}")
            min_edit.setFixedWidth(90)
            min_edit.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
            min_edit.setObjectName(f"{prefix}_{model_name}_{param_name}_min")

            dash = QLabel("—")
            dash.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
            dash.setStyleSheet("color: #607D8B;")

            max_edit = QtWidgets.QLineEdit(f"{ub:.4f}")
            max_edit.setFixedWidth(90)
            max_edit.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
            max_edit.setObjectName(f"{prefix}_{model_name}_{param_name}_max")

            # Hidden until checkbox checked
            for w in (init_edit, min_edit, dash, max_edit):
                w.hide()

            grid_layout.addWidget(cb,        row_idx, 0)
            grid_layout.addWidget(init_edit,  row_idx, 1)
            grid_layout.addWidget(min_edit,   row_idx, 2)
            grid_layout.addWidget(dash,       row_idx, 3)
            grid_layout.addWidget(max_edit,   row_idx, 4)

            cb.stateChanged.connect(
                lambda st, ie=init_edit, mne=min_edit, dl=dash, mxe=max_edit:
                [w.setVisible(st == QtCore.Qt.CheckState.Checked.value)
                 for w in (ie, mne, dl, mxe)]
            )

            param_widgets[param_name] = {
                'checkbox':  cb,
                'initial':   initial,
                'min':       lb,
                'max':       ub,
                'init_edit': init_edit,
                'min_edit':  min_edit,
                'max_edit':  max_edit,
                'idx':       idx,
            }

        scroll_layout.addWidget(grid_widget)

    # ─────────────────────────────────────────────────────────
    # Collect all inputs
    # ─────────────────────────────────────────────────────────
    def get_all_inputs(self):
        selected_targets = [
            sig for sig, cb in [("P",  self.ref_check_P),
                                  ("Q",  self.ref_check_Q),
                                  ("Vt", self.ref_check_Vt),
                                  ("Ef", self.ref_check_Ef),
                                  ("If", self.ref_check_If)]
            if cb.isChecked()
        ]

        input_data = {
            "paths": {
                "sav_file": self.sav_text.text(),
                "dyr_file": self.dyr_text.text(),
                "out_file": self.out_text.text(),
                "ref_file": self.ref_text.text(),
            },
            "psse_setting": {
                "bus_id":     self.Bus_id.text(),
                "gen_id":     self.gen_id.text(),
                "sim_time":   self.simulation_time.value(),
                "fault_time": self.time_fault.value(),
                "fault_step": self.step_fault.value(),
                "delt":       float(self.DELT.text()) if self.DELT.text() else 0.01,
            },
            "pso_params": {
                "iterations":   self.iteration_2.value(),
                "particles":    self.particle.value(),
                "c1":           self.c1.value(),
                "c2":           self.c2.value(),
                "wmax":         self.wmax.value(),
                "wmin":         self.wmin.value(),
                "tuning_target": selected_targets,
                "disturbance":  self.disturbance.currentText(),
            },
        }

        for attr, key, widgets_attr in [
            ("GEN_check", "gen_model", "GEN_param_widgets"),
            ("AVR_check", "avr_model", "AVR_param_widgets"),
            ("GOV_check", "gov_model", "GOV_param_widgets"),
            ("PSS_check", "pss_model", "PSS_param_widgets"),
        ]:
            check = getattr(self, attr)
            if check.isChecked():
                list_widget = getattr(self, attr.replace("_check", "_list"))
                model_name = list_widget.currentText()
                param_widgets = getattr(self, widgets_attr)
                selected_params = {}
                for p_name, w in param_widgets.items():
                    if w['checkbox'].isChecked():
                        selected_params[p_name] = {
                            "init": float(w['init_edit'].text()),
                            "min":  float(w['min_edit'].text()),
                            "max":  float(w['max_edit'].text()),
                            "idx":  int(w['idx']),
                        }
                input_data[key] = {"model": model_name, "parameters": selected_params}

        return input_data

    # ─────────────────────────────────────────────────────────
    # Log emitter (thread-safe)
    # ─────────────────────────────────────────────────────────
    def setup_log_emitter(self):
        self.log_emitter = LogEmitter()
        self.log_emitter.log_signal.connect(self._append_log)

    def _append_log(self, msg):
        self.log_output.append(msg)
        self.log_output.verticalScrollBar().setValue(
            self.log_output.verticalScrollBar().maximum())

    # ─────────────────────────────────────────────────────────
    # Run / Stop
    # ─────────────────────────────────────────────────────────
    def run_py(self):
        from PSO_from_GUI import run_optimization, cancel_pso, reset_pso_flag
        all_input = self.get_all_inputs()
        self.log_output.clear()
        self.run.setEnabled(False)
        self.cancel.setEnabled(True)
        self.statusbar.showMessage("Đang tối ưu hóa…")
        reset_pso_flag()

        if not hasattr(self, 'log_emitter'):
            self.setup_log_emitter()

        def log_cb(msg):
            self.log_emitter.log_signal.emit(msg)

        def run_in_thread():
            try:
                run_optimization(all_input, log_cb=log_cb,
                                  do_plot=True, cancel_check_cb=cancel_pso)
            except KeyboardInterrupt:
                log_cb("<font color='#FF7043'><b>!!! Đã hủy quá trình tối ưu !!!</b></font>")
            except Exception as e:
                log_cb(f"<font color='#FF7043'><b>Lỗi: {e}</b></font>")
            finally:
                self.run.setEnabled(True)
                self.cancel.setEnabled(True)
                log_cb("<font color='#66BB6A'><b>──── Hoàn tất ────</b></font>")
                self.log_emitter.log_signal.emit("__STATUS__DONE__")

        self.worker_thread = threading.Thread(target=run_in_thread, daemon=True)
        self.worker_thread.start()

    def _on_done_signal(self, msg):
        if msg == "__STATUS__DONE__":
            self.statusbar.showMessage("Hoàn tất")
        else:
            self._append_log(msg)

    def stop(self):
        from PSO_from_GUI import cancel_pso
        cancel_pso()
        self.log_output.append(
            "<font color='#FF7043'><b>!!! Đang hủy quá trình tối ưu… !!!</b></font>")
        self.statusbar.showMessage("Đang hủy…")


# ─────────────────────────────────────────────────────────────
# Entry point
# ─────────────────────────────────────────────────────────────
if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    app.setStyle("Fusion")          # solid base before QSS
    MainWindow = QtWidgets.QMainWindow()
    ui = Ui_MainWindow()
    ui.setupUi(MainWindow)
    MainWindow.show()
    sys.exit(app.exec())
