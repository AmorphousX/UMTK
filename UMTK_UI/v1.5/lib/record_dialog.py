try:
    from PyQt6 import QtCore, QtWidgets, QtGui  # type: ignore
except ImportError:  # pragma: no cover
    from PySide6 import QtCore, QtWidgets, QtGui  # type: ignore

from .umtk_logic import UMTKLogic


class RecordingDialog(QtWidgets.QDialog):
    """Dialog to control data recording lifecycle."""

    startRecording = QtCore.pyqtSignal()
    pauseRecording = QtCore.pyqtSignal()
    resumeRecording = QtCore.pyqtSignal()
    stopRecording = QtCore.pyqtSignal()

    def __init__(self, logic: UMTKLogic, parent=None):
        super().__init__(parent)
        self.logic = logic
        self.setWindowTitle("Recording Control")
        self.setModal(False)
        self.setMinimumWidth(320)

        self.filename_edit = QtWidgets.QLineEdit()
        self.filename_edit.setPlaceholderText("Optional filename (no spaces)")

        self.status_label = QtWidgets.QLabel("Idle")
        self.elapsed_label = QtWidgets.QLabel("00:00")
        font = self.elapsed_label.font()
        font.setBold(True)
        self.elapsed_label.setFont(font)

        self.toggle_btn = QtWidgets.QPushButton("Start")
        self.toggle_btn.setIcon(self.style().standardIcon(QtWidgets.QStyle.StandardPixmap.SP_MediaPlay))
        self.stop_btn = QtWidgets.QPushButton("Stop")
        self.stop_btn.setIcon(self.style().standardIcon(QtWidgets.QStyle.StandardPixmap.SP_MediaStop))
        self.stop_btn.setEnabled(False)

        btn_row = QtWidgets.QHBoxLayout()
        btn_row.addWidget(self.toggle_btn)
        btn_row.addWidget(self.stop_btn)

        form = QtWidgets.QFormLayout()
        form.addRow("File Name:", self.filename_edit)
        form.addRow("Status:", self.status_label)
        form.addRow("Elapsed:", self.elapsed_label)

        layout = QtWidgets.QVBoxLayout(self)
        layout.addLayout(form)
        layout.addLayout(btn_row)

        self.toggle_btn.clicked.connect(self._toggle_recording)
        self.stop_btn.clicked.connect(self._stop)

        self.timer = QtCore.QTimer(self)
        self.timer.timeout.connect(self._refresh_elapsed)
        self.timer.start(500)

    # ---------- UI Actions ---------
    def _toggle_recording(self):
        if not self.logic.is_recording:
            # Start
            self.logic.start_recording(self.filename_edit.text() or None)
            self.status_label.setText("Recording")
            self.toggle_btn.setText("Pause")
            self.toggle_btn.setIcon(self.style().standardIcon(QtWidgets.QStyle.StandardPixmap.SP_MediaPause))
            self.stop_btn.setEnabled(True)
            self.startRecording.emit()
        elif self.logic.is_recording and not self.logic.is_paused:
            # Pause
            self.logic.pause_recording()
            self.status_label.setText("Paused")
            self.toggle_btn.setText("Resume")
            self.toggle_btn.setIcon(self.style().standardIcon(QtWidgets.QStyle.StandardPixmap.SP_MediaPlay))
            self.pauseRecording.emit()
        else:
            # Resume
            self.logic.resume_recording()
            self.status_label.setText("Recording")
            self.toggle_btn.setText("Pause")
            self.toggle_btn.setIcon(self.style().standardIcon(QtWidgets.QStyle.StandardPixmap.SP_MediaPause))
            self.resumeRecording.emit()

    def _stop(self):
        if self.logic.is_recording:
            self.logic.stop_recording(start_new=True)
        self.status_label.setText("Idle")
        self.toggle_btn.setText("Start")
        self.toggle_btn.setIcon(self.style().standardIcon(QtWidgets.QStyle.StandardPixmap.SP_MediaPlay))
        self.stop_btn.setEnabled(False)
        self.elapsed_label.setText("00:00")
        self.stopRecording.emit()

    def _refresh_elapsed(self):
        if self.logic.is_recording:
            secs = int(self.logic.elapsed_recording_time())
            mm = secs // 60
            ss = secs % 60
            self.elapsed_label.setText(f"{mm:02d}:{ss:02d}")
        else:
            self.elapsed_label.setText("00:00")

