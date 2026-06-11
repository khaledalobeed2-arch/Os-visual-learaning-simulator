#!/usr/bin/env python3
"""
╔══════════════════════════════════════════════════════════════════════════════╗
║          OS CONCEPTS VISUAL SIMULATOR — Professional Edition                ║
║          Threading · Processes · Race Conditions · Deadlock · Starvation    ║
╚══════════════════════════════════════════════════════════════════════════════╝
"""

import sys
import time
import random
import threading
import queue
from collections import deque
from typing import Self
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QCheckBox, QScrollArea, QFrame, QGraphicsView,
    QGraphicsScene, QGraphicsRectItem, QGraphicsEllipseItem, QGraphicsTextItem,
    QGraphicsLineItem, QGraphicsPathItem, QSizePolicy, QSpacerItem,
    QStackedWidget, QSlider, QSpinBox, QGroupBox, QGridLayout,
    QProgressBar, QGraphicsDropShadowEffect, QGraphicsOpacityEffect
)
from PyQt6.QtCore import (
    Qt, QTimer, QThread, pyqtSignal, QPropertyAnimation, QEasingCurve,
    QRectF, QPointF, QLineF, QSequentialAnimationGroup, QParallelAnimationGroup,
    QObject, pyqtProperty, QRect
)
from PyQt6.QtGui import (
    QPainter, QColor, QPen, QBrush, QFont, QFontMetrics, QPainterPath,
    QLinearGradient, QRadialGradient, QConicalGradient, QPalette,
    QPixmap, QIcon, QPolygonF, QTransform
)


# ─────────────────────────────────────────────────────────────────────────────
#  THEME CONSTANTS
# ─────────────────────────────────────────────────────────────────────────────
BG_DEEP      = "#0A0E1A"
BG_PANEL     = "#0F1525"
BG_CARD      = "#141B2D"
BG_ELEVATED  = "#1A2240"
ACCENT_CYAN  = "#00D4FF"
ACCENT_BLUE  = "#0066FF"
ACCENT_PURPLE= "#8B5CF6"
ACCENT_GREEN = "#10B981"
ACCENT_YELLOW= "#F59E0B"
ACCENT_RED   = "#EF4444"
ACCENT_ORANGE= "#F97316"
TEXT_PRIMARY = "#F0F4FF"
TEXT_SECONDARY="#8892B0"
TEXT_DIM     = "#4A5568"
BORDER_COLOR = "#1E2D50"
GLOW_CYAN    = "#00D4FF44"
GLOW_BLUE    = "#0066FF33"
GLOW_RED     = "#EF444433"
GLOW_GREEN   = "#10B98133"

THREAD_COLORS = [
    "#00D4FF", "#8B5CF6", "#10B981", "#F59E0B",
    "#EF4444", "#F97316", "#EC4899", "#06B6D4"
]

STYLESHEET = f"""
QMainWindow, QWidget {{
    background-color: {BG_DEEP};
    color: {TEXT_PRIMARY};
    font-family: 'Consolas', 'Courier New', monospace;
}}
QScrollBar:vertical {{
    background: {BG_PANEL};
    width: 6px;
    border-radius: 3px;
}}
QScrollBar::handle:vertical {{
    background: {ACCENT_BLUE};
    border-radius: 3px;
    min-height: 20px;
}}
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
    height: 0;
}}
QScrollBar:horizontal {{
    background: {BG_PANEL};
    height: 6px;
    border-radius: 3px;
}}
QScrollBar::handle:horizontal {{
    background: {ACCENT_BLUE};
    border-radius: 3px;
}}
QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {{
    width: 0;
}}
QToolTip {{
    background: {BG_ELEVATED};
    color: {TEXT_PRIMARY};
    border: 1px solid {ACCENT_CYAN};
    padding: 6px 10px;
    border-radius: 6px;
    font-size: 12px;
}}
QCheckBox {{
    color: {TEXT_PRIMARY};
    font-size: 13px;
    spacing: 8px;
}}
QCheckBox::indicator {{
    width: 18px;
    height: 18px;
    border-radius: 4px;
    border: 2px solid {ACCENT_BLUE};
    background: {BG_CARD};
}}
QCheckBox::indicator:checked {{
    background: {ACCENT_BLUE};
    border-color: {ACCENT_CYAN};
}}
QSlider::groove:horizontal {{
    height: 4px;
    background: {BG_ELEVATED};
    border-radius: 2px;
}}
QSlider::handle:horizontal {{
    width: 14px;
    height: 14px;
    margin: -5px 0;
    border-radius: 7px;
    background: {ACCENT_CYAN};
}}
QSlider::sub-page:horizontal {{
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
        stop:0 {ACCENT_BLUE}, stop:1 {ACCENT_CYAN});
    border-radius: 2px;
}}
QSpinBox {{
    background: {BG_ELEVATED};
    border: 1px solid {BORDER_COLOR};
    border-radius: 6px;
    color: {TEXT_PRIMARY};
    padding: 4px 8px;
    font-size: 13px;
}}
QSpinBox::up-button, QSpinBox::down-button {{
    background: {BG_ELEVATED};
    border: none;
    width: 16px;
}}
"""


# ─────────────────────────────────────────────────────────────────────────────
#  REUSABLE STYLED WIDGETS
# ─────────────────────────────────────────────────────────────────────────────

class GlowButton(QPushButton):
    def __init__(self, text, color=ACCENT_CYAN, parent=None):
        super().__init__(text, parent)
        self._color = color
        self._hover = False
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setFixedHeight(38)
        self._update_style()

    def _update_style(self):
        c = self._color
        r = int(c[1:3], 16)
        g = int(c[3:5], 16)
        b = int(c[5:7], 16)
        glow = f"rgba({r},{g},{b},0.3)"
        hover_bg = f"rgba({r},{g},{b},0.25)"
        self.setStyleSheet(f"""
            QPushButton {{
                background: rgba({r},{g},{b},0.12);
                color: {c};
                border: 1px solid rgba({r},{g},{b},0.5);
                border-radius: 8px;
                padding: 0 18px;
                font-size: 13px;
                font-weight: bold;
                letter-spacing: 0.5px;
                font-family: 'Consolas', monospace;
            }}
            QPushButton:hover {{
                background: {hover_bg};
                border-color: {c};
            }}
            QPushButton:pressed {{
                background: rgba({r},{g},{b},0.35);
            }}
            QPushButton:disabled {{
                opacity: 0.4;
            }}
        """)


class NavButton(QPushButton):
    def __init__(self, icon_char, text, color=ACCENT_CYAN, parent=None):
        super().__init__(parent)
        self._color = color
        self._text = text
        self._icon_char = icon_char
        self._active = False
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setFixedHeight(52)
        self._update_style()

    def set_active(self, active):
        self._active = active
        self._update_style()

    def _update_style(self):
        c = self._color
        r = int(c[1:3], 16)
        g = int(c[3:5], 16)
        b = int(c[5:7], 16)
        if self._active:
            self.setStyleSheet(f"""
                QPushButton {{
                    background: rgba({r},{g},{b},0.18);
                    color: {c};
                    border: none;
                    border-left: 3px solid {c};
                    border-radius: 0px;
                    padding: 0 16px;
                    font-size: 13px;
                    font-weight: bold;
                    text-align: left;
                    font-family: 'Consolas', monospace;
                }}
            """)
        else:
            self.setStyleSheet(f"""
                QPushButton {{
                    background: transparent;
                    color: {TEXT_SECONDARY};
                    border: none;
                    border-left: 3px solid transparent;
                    border-radius: 0px;
                    padding: 0 16px;
                    font-size: 13px;
                    text-align: left;
                    font-family: 'Consolas', monospace;
                }}
                QPushButton:hover {{
                    background: rgba({r},{g},{b},0.08);
                    color: {c};
                    border-left: 3px solid rgba({r},{g},{b},0.5);
                }}
            """)
        self.setText(f"  {self._icon_char}  {self._text}")


class SectionLabel(QLabel):
    def __init__(self, text, parent=None):
        super().__init__(text, parent)
        self.setStyleSheet(f"""
            color: {TEXT_DIM};
            font-size: 10px;
            font-weight: bold;
            letter-spacing: 2px;
            padding: 12px 16px 4px 16px;
            font-family: 'Consolas', monospace;
        """)


class CardWidget(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet(f"""
            QFrame {{
                background: {BG_CARD};
                border: 1px solid {BORDER_COLOR};
                border-radius: 12px;
            }}
        """)


class StatBadge(QLabel):
    def __init__(self, label, value, color=ACCENT_CYAN, parent=None):
        super().__init__(parent)
        self._label = label
        self._color = color
        self.set_value(value)

    def set_value(self, value):
        r = int(self._color[1:3], 16)
        g = int(self._color[3:5], 16)
        b = int(self._color[5:7], 16)
        self.setText(f"{self._label}: {value}")
        self.setStyleSheet(f"""
            background: rgba({r},{g},{b},0.12);
            color: {self._color};
            border: 1px solid rgba({r},{g},{b},0.4);
            border-radius: 6px;
            padding: 4px 10px;
            font-size: 12px;
            font-weight: bold;
            font-family: 'Consolas', monospace;
        """)


class EventLogWidget(QScrollArea):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWidgetResizable(True)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self._container = QWidget()
        self._layout = QVBoxLayout(self._container)
        self._layout.setContentsMargins(6, 6, 6, 6)
        self._layout.setSpacing(2)
        self._layout.addStretch()
        self.setWidget(self._container)
        self.setStyleSheet(f"""
            QScrollArea {{
                background: {BG_DEEP};
                border: 1px solid {BORDER_COLOR};
                border-radius: 8px;
            }}
            QWidget {{
                background: {BG_DEEP};
            }}
        """)
        self._entries = []
        self._max_entries = 200

    def add_event(self, message, level="INFO"):
        color_map = {
            "INFO":    ACCENT_CYAN,
            "SUCCESS": ACCENT_GREEN,
            "WARNING": ACCENT_YELLOW,
            "ERROR":   ACCENT_RED,
            "LOCK":    ACCENT_PURPLE,
            "WAIT":    ACCENT_ORANGE,
            "SYSTEM":  TEXT_SECONDARY,
        }
        color = color_map.get(level, ACCENT_CYAN)
        ts = time.strftime("%H:%M:%S")

        entry = QLabel()
        prefix = {"INFO":"●","SUCCESS":"✓","WARNING":"⚠","ERROR":"✗","LOCK":"⚿","WAIT":"⏳","SYSTEM":"◈"}.get(level,"●")
        entry.setText(f"<span style='color:{TEXT_DIM};font-size:10px;'>{ts}</span> "
                      f"<span style='color:{color};'>{prefix}</span> "
                      f"<span style='color:{TEXT_PRIMARY};font-size:12px;'>{message}</span>")
        entry.setWordWrap(True)
        entry.setStyleSheet(f"""
            padding: 3px 6px;
            border-radius: 4px;
            font-family: 'Consolas', monospace;
        """)

        self._layout.insertWidget(self._layout.count() - 1, entry)
        self._entries.append(entry)

        if len(self._entries) > self._max_entries:
            old = self._entries.pop(0)
            self._layout.removeWidget(old)
            old.deleteLater()

        QTimer.singleShot(50, lambda: self.verticalScrollBar().setValue(
            self.verticalScrollBar().maximum()
        ))

    def clear_log(self):
        for e in self._entries:
            self._layout.removeWidget(e)
            e.deleteLater()
        self._entries.clear()


# ─────────────────────────────────────────────────────────────────────────────
#  THREAD VISUAL BLOCK
# ─────────────────────────────────────────────────────────────────────────────

class ThreadBlock(QWidget):
    def __init__(self, tid, color, parent=None):
        super().__init__(parent)
        self.tid = tid
        self.color = color
        self.state = "IDLE"   # IDLE, RUNNING, WAITING, BLOCKED, DONE
        self._pulse = 0.0
        self.setFixedSize(120, 90)

        self._timer = QTimer()
        self._timer.timeout.connect(self._animate)
        self._timer.start(50)

    def _animate(self):
        if self.state == "RUNNING":
            self._pulse = (self._pulse + 0.15) % (2 * 3.14159)
        self.update()

    def set_state(self, state):
        self.state = state
        self.update()

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)

        color_map = {
            "IDLE":    (self.color, 0.15),
            "RUNNING": (ACCENT_GREEN, 0.3),
            "WAITING": (ACCENT_YELLOW, 0.2),
            "BLOCKED": (ACCENT_RED, 0.25),
            "DONE":    (TEXT_DIM, 0.1),
        }
        c_hex, alpha = color_map.get(self.state, (self.color, 0.15))
        r = int(c_hex[1:3], 16)
        g = int(c_hex[3:5], 16)
        b = int(c_hex[5:7], 16)

        # Glow
        if self.state == "RUNNING":
            import math
            glow_alpha = int(60 + 40 * math.sin(self._pulse))
            glow_color = QColor(r, g, b, glow_alpha)
            glow_pen = QPen(glow_color, 3)
            p.setPen(glow_pen)
            p.setBrush(Qt.BrushStyle.NoBrush)
            p.drawRoundedRect(2, 2, self.width()-4, self.height()-4, 10, 10)

        # Background
        bg = QColor(r, g, b, int(alpha * 255))
        p.setBrush(QBrush(bg))
        border_color = QColor(r, g, b, 200)
        p.setPen(QPen(border_color, 1.5))
        p.drawRoundedRect(5, 5, self.width()-10, self.height()-10, 8, 8)

        # State indicator dot
        dot_colors = {
            "IDLE": QColor(TEXT_DIM),
            "RUNNING": QColor(ACCENT_GREEN),
            "WAITING": QColor(ACCENT_YELLOW),
            "BLOCKED": QColor(ACCENT_RED),
            "DONE": QColor(TEXT_DIM),
        }
        p.setBrush(QBrush(dot_colors.get(self.state, QColor(TEXT_DIM))))
        p.setPen(Qt.PenStyle.NoPen)
        p.drawEllipse(self.width()-18, 12, 8, 8)

        # Thread ID
        p.setPen(QPen(QColor(c_hex)))
        font = QFont("Consolas", 9, QFont.Weight.Bold)
        p.setFont(font)
        p.drawText(QRect(5, 15, self.width()-10, 20), Qt.AlignmentFlag.AlignCenter, f"T-{self.tid}")

        # State text
        p.setPen(QPen(QColor(TEXT_PRIMARY)))
        font2 = QFont("Consolas", 8)
        p.setFont(font2)
        p.drawText(QRect(5, 38, self.width()-10, 18), Qt.AlignmentFlag.AlignCenter, self.state)

        # Progress bar if running
        if self.state == "RUNNING":
            import math
            prog = (math.sin(self._pulse) + 1) / 2
            bar_w = int((self.width() - 20) * prog)
            p.setBrush(QBrush(QColor(r, g, b, 180)))
            p.setPen(Qt.PenStyle.NoPen)
            p.drawRoundedRect(10, self.height()-20, self.width()-20, 6, 3, 3)
            p.setBrush(QBrush(QColor(r, g, b, 255)))
            if bar_w > 0:
                p.drawRoundedRect(10, self.height()-20, bar_w, 6, 3, 3)

        p.end()


# ─────────────────────────────────────────────────────────────────────────────
#  SIMULATION BASE CLASS
# ─────────────────────────────────────────────────────────────────────────────

class BaseSimulation(QWidget):
    log_signal = pyqtSignal(str, str)

    def __init__(self, title, description, color=ACCENT_CYAN, parent=None):
        super().__init__(parent)
        self.sim_title = title
        self.description = description
        self.color = color
        self._running = False
        self._threads = []

        # Safe defaults so subclass visualization code can run during __init__.
        self._worker = None
        self._thread_blocks = []
        self._producer_blocks = []
        self._consumer_blocks = []
        self._bars = []
        self._timeline = None
        self._shared_display = None
        self._buffer_widget = None
        self._sem_display = None
        self._cs_widget = None
        self._mem_widget = None
        self._core_widgets = []
        self._deadlock_view = None
        self._n_threads = 4
        self._n_prod_val = 2
        self._n_cons_val = 2
        self._buf_size = 8

        self._build_ui()

    def _build_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # Header
        header = QWidget()
        header.setFixedHeight(80)
        r = int(self.color[1:3], 16)
        g = int(self.color[3:5], 16)
        b = int(self.color[5:7], 16)
        header.setStyleSheet(f"""
            background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                stop:0 rgba({r},{g},{b},0.2), stop:1 rgba({r},{g},{b},0.02));
            border-bottom: 1px solid rgba({r},{g},{b},0.3);
        """)
        h_layout = QHBoxLayout(header)
        h_layout.setContentsMargins(24, 0, 24, 0)

        title_col = QVBoxLayout()
        title_lbl = QLabel(self.sim_title)
        title_lbl.setStyleSheet(f"color: {self.color}; font-size: 20px; font-weight: bold; font-family: 'Consolas', monospace;")
        desc_lbl = QLabel(self.description)
        desc_lbl.setStyleSheet(f"color: {TEXT_SECONDARY}; font-size: 12px; font-family: 'Consolas', monospace;")
        title_col.addWidget(title_lbl)
        title_col.addWidget(desc_lbl)
        h_layout.addLayout(title_col)
        h_layout.addStretch()

        # Control buttons
        self._btn_start = GlowButton("▶  START", ACCENT_GREEN)
        self._btn_start.setFixedWidth(110)
        self._btn_stop = GlowButton("■  STOP", ACCENT_RED)
        self._btn_stop.setFixedWidth(110)
        self._btn_stop.setEnabled(False)
        self._btn_reset = GlowButton("↺  RESET", ACCENT_YELLOW)
        self._btn_reset.setFixedWidth(110)

        self._btn_start.clicked.connect(self.start)
        self._btn_stop.clicked.connect(self.stop)
        self._btn_reset.clicked.connect(self.reset)

        h_layout.addWidget(self._btn_start)
        h_layout.addSpacing(8)
        h_layout.addWidget(self._btn_stop)
        h_layout.addSpacing(8)
        h_layout.addWidget(self._btn_reset)

        main_layout.addWidget(header)

        # Content area
        content = QWidget()
        content_layout = QHBoxLayout(content)
        content_layout.setContentsMargins(16, 16, 16, 16)
        content_layout.setSpacing(16)

        # Visualization area
        self._vis_area = QWidget()
        self._vis_area.setStyleSheet(f"""
            background: {BG_DEEP};
            border: 1px solid {BORDER_COLOR};
            border-radius: 10px;
        """)
        self._setup_visualization(self._vis_area)
        content_layout.addWidget(self._vis_area, 3)

        # Right panel
        right_panel = QWidget()
        right_panel.setFixedWidth(280)
        right_layout = QVBoxLayout(right_panel)
        right_layout.setContentsMargins(0, 0, 0, 0)
        right_layout.setSpacing(12)

        # Controls card
        self._controls_card = CardWidget()
        self._controls_layout = QVBoxLayout(self._controls_card)
        self._controls_layout.setContentsMargins(14, 14, 14, 14)
        self._controls_layout.setSpacing(10)
        controls_title = QLabel("⚙  CONTROLS")
        controls_title.setStyleSheet(f"color: {self.color}; font-size: 11px; font-weight: bold; letter-spacing: 1.5px; font-family: 'Consolas', monospace;")
        self._controls_layout.addWidget(controls_title)
        self._setup_controls(self._controls_card, self._controls_layout)
        right_layout.addWidget(self._controls_card)

        # Stats card
        self._stats_card = CardWidget()
        self._stats_layout = QVBoxLayout(self._stats_card)
        self._stats_layout.setContentsMargins(14, 14, 14, 14)
        self._stats_layout.setSpacing(8)
        stats_title = QLabel("◈  STATISTICS")
        stats_title.setStyleSheet(f"color: {self.color}; font-size: 11px; font-weight: bold; letter-spacing: 1.5px; font-family: 'Consolas', monospace;")
        self._stats_layout.addWidget(stats_title)
        self._setup_stats(self._stats_card, self._stats_layout)
        right_layout.addWidget(self._stats_card)
        right_layout.addStretch()
        content_layout.addWidget(right_panel)

        main_layout.addWidget(content, 1)

        # Event log
        log_container = QWidget()
        log_container.setFixedHeight(180)
        log_layout = QVBoxLayout(log_container)
        log_layout.setContentsMargins(16, 0, 16, 12)
        log_layout.setSpacing(6)

        log_header = QHBoxLayout()
        log_title = QLabel("◈  EVENT LOG")
        log_title.setStyleSheet(f"color: {TEXT_SECONDARY}; font-size: 11px; font-weight: bold; letter-spacing: 1.5px; font-family: 'Consolas', monospace;")
        btn_clear = GlowButton("✕  CLEAR", TEXT_DIM)
        btn_clear.setFixedWidth(90)
        btn_clear.setFixedHeight(28)
        log_header.addWidget(log_title)
        log_header.addStretch()
        log_header.addWidget(btn_clear)
        log_layout.addLayout(log_header)

        self.event_log = EventLogWidget()
        btn_clear.clicked.connect(self.event_log.clear_log)
        log_layout.addWidget(self.event_log)

        main_layout.addWidget(log_container)

        self.log_signal.connect(self.event_log.add_event)

    def log(self, msg, level="INFO"):
        self.log_signal.emit(msg, level)

    def _setup_visualization(self, parent): pass
    def _setup_controls(self, card, layout): pass
    def _setup_stats(self, card, layout): pass
    def start(self): pass
    def stop(self): pass
    def reset(self): pass

    def _set_running(self, running):
        self._running = running
        self._btn_start.setEnabled(not running)
        self._btn_stop.setEnabled(running)


# ─────────────────────────────────────────────────────────────────────────────
#  1. THREADS & CONCURRENCY SIMULATION
# ─────────────────────────────────────────────────────────────────────────────

class ThreadConcurrencyWorker(QThread):
    update_signal = pyqtSignal(int, str)  # tid, state
    log_signal = pyqtSignal(str, str)
    finished = pyqtSignal()

    def __init__(self, n_threads, speed):
        super().__init__()
        self.n_threads = n_threads
        self.speed = speed
        self._stop_event = threading.Event()

    def stop(self): self._stop_event.set()

    def run(self):
        states = ["IDLE"] * self.n_threads
        tasks = [random.randint(3, 10) for _ in range(self.n_threads)]

        for tid in range(self.n_threads):
            self.update_signal.emit(tid, "IDLE")
            self.log_signal.emit(f"Thread T-{tid} initialized", "SYSTEM")

        time.sleep(0.5)

        while not self._stop_event.is_set():
            # Context switch simulation
            active = [i for i in range(self.n_threads) if states[i] != "DONE"]
            if not active:
                break

            # On single core: only 1 runs at a time (concurrency)
            for tid in range(self.n_threads):
                if states[tid] == "DONE":
                    continue
                if self._stop_event.is_set():
                    break

                # Context switch
                for i in range(self.n_threads):
                    if i != tid and states[i] != "DONE":
                        self.update_signal.emit(i, "WAITING")

                self.update_signal.emit(tid, "RUNNING")
                self.log_signal.emit(f"Context Switch → T-{tid} running (CPU quantum)", "INFO")
                time.sleep(0.3 / self.speed)

                tasks[tid] -= 1
                if tasks[tid] <= 0:
                    states[tid] = "DONE"
                    self.update_signal.emit(tid, "DONE")
                    self.log_signal.emit(f"T-{tid} completed its task ✓", "SUCCESS")
                else:
                    states[tid] = "WAITING"
                    self.update_signal.emit(tid, "WAITING")

                time.sleep(0.1 / self.speed)

            if all(s == "DONE" for s in states):
                self.log_signal.emit("All threads completed!", "SUCCESS")
                break

        self.finished.emit()


class ThreadConcurrencySimulation(BaseSimulation):
    def __init__(self, parent=None):
        super().__init__("THREADS & CONCURRENCY",
                         "Context switching · CPU time-sharing · Concurrency vs Parallelism",
                         ACCENT_CYAN, parent)
        self._worker = None
        self._thread_blocks = []
        self._n_threads = 4

    def _setup_visualization(self, parent):
        self._vis_layout = QVBoxLayout(parent)
        self._vis_layout.setContentsMargins(20, 20, 20, 20)
        self._vis_layout.setSpacing(16)

        # CPU label
        cpu_label = QLabel("◈  CPU CORE (Single Core — Concurrency)")
        cpu_label.setStyleSheet(f"color: {ACCENT_CYAN}; font-size: 12px; font-weight: bold; font-family: 'Consolas', monospace;")
        self._vis_layout.addWidget(cpu_label)

        # Threads container
        self._threads_row = QWidget()
        self._threads_row_layout = QHBoxLayout(self._threads_row)
        self._threads_row_layout.setContentsMargins(0, 0, 0, 0)
        self._threads_row_layout.setSpacing(14)
        self._threads_row_layout.addStretch()
        self._vis_layout.addWidget(self._threads_row)

        # Timeline
        timeline_label = QLabel("◈  EXECUTION TIMELINE")
        timeline_label.setStyleSheet(f"color: {TEXT_SECONDARY}; font-size: 11px; font-family: 'Consolas', monospace;")
        self._vis_layout.addWidget(timeline_label)

        self._timeline = TimelineWidget()
        self._vis_layout.addWidget(self._timeline)
        self._vis_layout.addStretch()

        self._rebuild_threads()

    def _rebuild_threads(self):
        # Clear
        for block in self._thread_blocks:
            block.setParent(None)
            block.deleteLater()
        self._thread_blocks.clear()

        while self._threads_row_layout.count() > 1:
            item = self._threads_row_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        for i in range(self._n_threads):
            block = ThreadBlock(i, THREAD_COLORS[i % len(THREAD_COLORS)])
            self._thread_blocks.append(block)
            self._threads_row_layout.insertWidget(i, block)

    def _setup_controls(self, card, layout):
        n_label = QLabel("Number of Threads:")
        n_label.setStyleSheet(f"color: {TEXT_SECONDARY}; font-size: 12px; font-family: 'Consolas', monospace;")
        layout.addWidget(n_label)

        row = QHBoxLayout()
        self._n_spin = QSpinBox()
        self._n_spin.setRange(2, 6)
        self._n_spin.setValue(4)
        self._n_spin.valueChanged.connect(self._on_n_changed)
        row.addWidget(self._n_spin)
        layout.addLayout(row)

        speed_label = QLabel("Simulation Speed:")
        speed_label.setStyleSheet(f"color: {TEXT_SECONDARY}; font-size: 12px; font-family: 'Consolas', monospace;")
        layout.addWidget(speed_label)

        self._speed_slider = QSlider(Qt.Orientation.Horizontal)
        self._speed_slider.setRange(1, 5)
        self._speed_slider.setValue(2)
        layout.addWidget(self._speed_slider)

    def _setup_stats(self, card, layout):
        self._stat_active = StatBadge("ACTIVE", "0", ACCENT_GREEN)
        self._stat_waiting = StatBadge("WAITING", "0", ACCENT_YELLOW)
        self._stat_done = StatBadge("DONE", "0", ACCENT_CYAN)
        self._stat_switches = StatBadge("SWITCHES", "0", ACCENT_PURPLE)
        layout.addWidget(self._stat_active)
        layout.addWidget(self._stat_waiting)
        layout.addWidget(self._stat_done)
        layout.addWidget(self._stat_switches)
        self._switches = 0

    def _on_n_changed(self, v):
        self._n_threads = v
        if not self._running:
            self._rebuild_threads()

    def _update_thread(self, tid, state):
        if tid < len(self._thread_blocks):
            self._thread_blocks[tid].set_state(state)

        counts = {"IDLE": 0, "RUNNING": 0, "WAITING": 0, "BLOCKED": 0, "DONE": 0}
        for b in self._thread_blocks:
            counts[b.state] = counts.get(b.state, 0) + 1

        self._stat_active.set_value(counts.get("RUNNING", 0))
        self._stat_waiting.set_value(counts.get("WAITING", 0))
        self._stat_done.set_value(counts.get("DONE", 0))

        if state == "RUNNING":
            self._switches += 1
            self._stat_switches.set_value(self._switches)
            self._timeline.add_tick(tid, THREAD_COLORS[tid % len(THREAD_COLORS)])

    def start(self):
        if self._running: return
        self._set_running(True)
        self._switches = 0
        self._stat_switches.set_value(0)
        self.log("Simulation started", "SYSTEM")
        for b in self._thread_blocks:
            b.set_state("IDLE")

        speed = self._speed_slider.value()
        self._worker = ThreadConcurrencyWorker(self._n_threads, speed)
        self._worker.update_signal.connect(self._update_thread)
        self._worker.log_signal.connect(self.event_log.add_event)
        self._worker.finished.connect(self._on_done)
        self._worker.start()

    def stop(self):
        if self._worker:
            self._worker.stop()
        self._set_running(False)

    def reset(self):
        self.stop()
        if self._worker:
            self._worker.wait(500)
        self._timeline.reset()
        self._rebuild_threads()
        self._switches = 0
        self._stat_switches.set_value(0)
        self._stat_active.set_value(0)
        self._stat_waiting.set_value(0)
        self._stat_done.set_value(0)
        self.event_log.clear_log()
        self.log("Simulation reset", "SYSTEM")

    def _on_done(self):
        self._set_running(False)
        self.log("All threads completed execution", "SUCCESS")


class TimelineWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumHeight(80)
        self._ticks = []  # list of (tid, color)
        self._max_ticks = 60

    def add_tick(self, tid, color):
        self._ticks.append((tid, color))
        if len(self._ticks) > self._max_ticks:
            self._ticks.pop(0)
        self.update()

    def reset(self):
        self._ticks.clear()
        self.update()

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)

        w = self.width()
        h = self.height()

        p.fillRect(0, 0, w, h, QColor(BG_DEEP))

        if not self._ticks:
            p.setPen(QPen(QColor(TEXT_DIM)))
            p.setFont(QFont("Consolas", 10))
            p.drawText(QRect(0, 0, w, h), Qt.AlignmentFlag.AlignCenter, "Start simulation to see timeline...")
            p.end()
            return

        tick_w = max(4, w // self._max_ticks)
        row_h = (h - 20) // 8  # max 8 threads

        for i, (tid, color) in enumerate(self._ticks):
            x = i * tick_w
            y = 10 + tid * row_h
            r = int(color[1:3], 16)
            g = int(color[3:5], 16)
            b = int(color[5:7], 16)
            p.setBrush(QBrush(QColor(r, g, b, 220)))
            p.setPen(Qt.PenStyle.NoPen)
            p.drawRoundedRect(x, y, tick_w - 1, max(4, row_h - 2), 2, 2)

        p.end()


# ─────────────────────────────────────────────────────────────────────────────
#  2. RACE CONDITION SIMULATION
# ─────────────────────────────────────────────────────────────────────────────

class RaceConditionWorker(QThread):
    update_signal = pyqtSignal(int, str, int)  # tid, state, shared_val
    log_signal = pyqtSignal(str, str)
    finished = pyqtSignal(int, int)  # actual, expected

    def __init__(self, n_threads, iterations, use_mutex, speed):
        super().__init__()
        self.n_threads = n_threads
        self.iterations = iterations
        self.use_mutex = use_mutex
        self.speed = speed
        self._stop = threading.Event()
        self.shared_var = 0
        self._lock = threading.Lock()

    def stop(self): self._stop.set()

    def _increment(self, tid):
        if self.use_mutex:
            self.log_signal.emit(f"T-{tid} acquiring mutex lock...", "LOCK")
            with self._lock:
                self.update_signal.emit(tid, "RUNNING", self.shared_var)
                self.log_signal.emit(f"T-{tid} entered critical section", "SUCCESS")
                # Simulate read-modify-write
                temp = self.shared_var
                time.sleep(0.001 / self.speed)
                self.shared_var = temp + 1
                self.update_signal.emit(tid, "RUNNING", self.shared_var)
                self.log_signal.emit(f"T-{tid} incremented → {self.shared_var}", "INFO")
        else:
            # No lock — race condition!
            self.update_signal.emit(tid, "RUNNING", self.shared_var)
            temp = self.shared_var
            time.sleep(0.001 / self.speed)
            # Another thread may have modified shared_var here!
            self.shared_var = temp + 1
            self.log_signal.emit(f"T-{tid} wrote {self.shared_var} (race!)", "WARNING")
            self.update_signal.emit(tid, "RUNNING", self.shared_var)

    def run(self):
        self.shared_var = 0
        threads = []
        expected = self.n_threads * self.iterations

        def worker(tid):
            for _ in range(self.iterations):
                if self._stop.is_set(): return
                self._increment(tid)
                time.sleep(0.02 / self.speed)
            self.update_signal.emit(tid, "DONE", self.shared_var)
            self.log_signal.emit(f"T-{tid} finished all {self.iterations} iterations", "SUCCESS")

        self.log_signal.emit(f"Starting {self.n_threads} threads, {self.iterations} iterations each", "SYSTEM")
        self.log_signal.emit(f"Expected final value: {expected}", "SYSTEM")
        self.log_signal.emit(f"Mutex: {'ENABLED ✓' if self.use_mutex else 'DISABLED ✗'}", "LOCK" if self.use_mutex else "WARNING")

        for i in range(self.n_threads):
            t = threading.Thread(target=worker, args=(i,))
            threads.append(t)
            self.update_signal.emit(i, "IDLE", 0)

        for t in threads:
            t.start()
        for t in threads:
            t.join()

        self.finished.emit(self.shared_var, expected)


class RaceConditionSimulation(BaseSimulation):
    def __init__(self, parent=None):
        super().__init__("RACE CONDITION",
                         "Shared variable corruption · Mutex protection · Critical section",
                         ACCENT_RED, parent)
        self._worker = None
        self._thread_blocks = []
        self._n_threads = 3

    def _setup_visualization(self, parent):
        layout = QVBoxLayout(parent)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(16)

        # Thread blocks
        t_label = QLabel("◈  THREADS")
        t_label.setStyleSheet(f"color: {ACCENT_RED}; font-size: 12px; font-weight: bold; font-family: 'Consolas', monospace;")
        layout.addWidget(t_label)

        self._threads_row = QWidget()
        self._threads_row_layout = QHBoxLayout(self._threads_row)
        self._threads_row_layout.setContentsMargins(0, 0, 0, 0)
        self._threads_row_layout.setSpacing(14)
        self._threads_row_layout.addStretch()
        layout.addWidget(self._threads_row)

        # Shared variable display
        shared_label = QLabel("◈  SHARED VARIABLE")
        shared_label.setStyleSheet(f"color: {ACCENT_YELLOW}; font-size: 12px; font-weight: bold; font-family: 'Consolas', monospace;")
        layout.addWidget(shared_label)

        self._shared_display = SharedVarWidget()
        self._shared_display.setFixedHeight(100)
        layout.addWidget(self._shared_display)

        # Result
        self._result_label = QLabel("")
        self._result_label.setStyleSheet(f"font-size: 14px; font-family: 'Consolas', monospace; padding: 8px;")
        self._result_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self._result_label)
        layout.addStretch()

        self._rebuild_threads()

    def _rebuild_threads(self):
        for b in self._thread_blocks:
            b.setParent(None)
            b.deleteLater()
        self._thread_blocks.clear()
        while self._threads_row_layout.count() > 1:
            item = self._threads_row_layout.takeAt(0)
            if item.widget(): item.widget().deleteLater()

        for i in range(self._n_threads):
            block = ThreadBlock(i, THREAD_COLORS[i % len(THREAD_COLORS)])
            self._thread_blocks.append(block)
            self._threads_row_layout.insertWidget(i, block)

    def _setup_controls(self, card, layout):
        lbl1 = QLabel("Threads:")
        lbl1.setStyleSheet(f"color:{TEXT_SECONDARY};font-size:12px;font-family:'Consolas',monospace;")
        layout.addWidget(lbl1)
        self._n_spin = QSpinBox()
        self._n_spin.setRange(2, 5)
        self._n_spin.setValue(3)
        self._n_spin.valueChanged.connect(lambda v: setattr(self, '_n_threads', v) or self._rebuild_threads() if not self._running else None)
        layout.addWidget(self._n_spin)

        lbl2 = QLabel("Iterations each:")
        lbl2.setStyleSheet(f"color:{TEXT_SECONDARY};font-size:12px;font-family:'Consolas',monospace;")
        layout.addWidget(lbl2)
        self._iter_spin = QSpinBox()
        self._iter_spin.setRange(5, 100)
        self._iter_spin.setValue(20)
        layout.addWidget(self._iter_spin)

        self._mutex_cb = QCheckBox("  Enable Mutex (Fix Race Condition)")
        self._mutex_cb.setStyleSheet(f"color:{TEXT_PRIMARY};font-size:13px;font-family:'Consolas',monospace;")
        layout.addWidget(self._mutex_cb)

        lbl3 = QLabel("Speed:")
        lbl3.setStyleSheet(f"color:{TEXT_SECONDARY};font-size:12px;font-family:'Consolas',monospace;")
        layout.addWidget(lbl3)
        self._speed_slider = QSlider(Qt.Orientation.Horizontal)
        self._speed_slider.setRange(1, 10)
        self._speed_slider.setValue(5)
        layout.addWidget(self._speed_slider)

    def _setup_stats(self, card, layout):
        self._stat_shared = StatBadge("SHARED VAR", "0", ACCENT_YELLOW)
        self._stat_expected = StatBadge("EXPECTED", "-", ACCENT_GREEN)
        self._stat_errors = StatBadge("LOST UPDATES", "0", ACCENT_RED)
        layout.addWidget(self._stat_shared)
        layout.addWidget(self._stat_expected)
        layout.addWidget(self._stat_errors)

    def _update(self, tid, state, shared_val):
        if tid < len(self._thread_blocks):
            self._thread_blocks[tid].set_state(state)
        self._shared_display.set_value(shared_val)
        self._stat_shared.set_value(shared_val)

    def start(self):
        if self._running: return
        self._result_label.setText("")
        self._set_running(True)
        use_mutex = self._mutex_cb.isChecked()
        n = self._n_spin.value()
        iters = self._iter_spin.value()
        speed = self._speed_slider.value()
        expected = n * iters
        self._stat_expected.set_value(expected)

        self._worker = RaceConditionWorker(n, iters, use_mutex, speed)
        self._worker.update_signal.connect(self._update)
        self._worker.log_signal.connect(self.event_log.add_event)
        self._worker.finished.connect(self._on_done)
        self._worker.start()

    def _on_done(self, actual, expected):
        self._set_running(False)
        lost = expected - actual
        self._stat_errors.set_value(max(0, lost))
        if actual == expected:
            self._result_label.setStyleSheet(f"color:{ACCENT_GREEN};font-size:14px;font-family:'Consolas',monospace;font-weight:bold;padding:8px;")
            self._result_label.setText(f"✓  CORRECT — Final: {actual} = Expected: {expected}  (Mutex protected!)")
            self.log(f"Result: {actual}/{expected} — No race condition!", "SUCCESS")
        else:
            self._result_label.setStyleSheet(f"color:{ACCENT_RED};font-size:14px;font-family:'Consolas',monospace;font-weight:bold;padding:8px;")
            self._result_label.setText(f"✗  RACE CONDITION — Got: {actual}, Expected: {expected}  (Lost {lost} updates!)")
            self.log(f"Race condition detected! Lost {lost} updates.", "ERROR")

    def stop(self):
        if self._worker: self._worker.stop()
        self._set_running(False)

    def reset(self):
        self.stop()
        if self._worker: self._worker.wait(500)
        self._rebuild_threads()
        self._shared_display.set_value(0)
        self._stat_shared.set_value(0)
        self._stat_errors.set_value(0)
        self._result_label.setText("")
        self.event_log.clear_log()
        self.log("Reset", "SYSTEM")


class SharedVarWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._value = 0
        self._prev = 0
        self._flash = 0.0
        self._timer = QTimer()
        self._timer.timeout.connect(self._tick)
        self._timer.start(50)

    def set_value(self, v):
        self._prev = self._value
        self._value = v
        self._flash = 1.0
        self.update()

    def _tick(self):
        if self._flash > 0:
            self._flash = max(0, self._flash - 0.1)
            self.update()

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        w, h = self.width(), self.height()

        # Box
        flash_r = int(self._flash * 239)
        flash_g = int(self._flash * 68)
        flash_b = int(self._flash * 68)
        base_r, base_g, base_b = 245, 158, 11
        r = min(255, base_r + flash_r)
        g = max(0, base_g - flash_g)
        b = max(0, base_b - flash_b)

        bw = 180
        bx = (w - bw) // 2
        by = (h - 70) // 2

        grad = QLinearGradient(bx, by, bx, by + 70)
        grad.setColorAt(0, QColor(r, g, b, 40))
        grad.setColorAt(1, QColor(r, g, b, 15))
        p.setBrush(QBrush(grad))
        p.setPen(QPen(QColor(r, g, b, 180), 2))
        p.drawRoundedRect(bx, by, bw, 70, 10, 10)

        # Label
        p.setPen(QPen(QColor(r, g, b, 200)))
        p.setFont(QFont("Consolas", 9))
        p.drawText(QRect(bx, by + 8, bw, 20), Qt.AlignmentFlag.AlignCenter, "shared_var")

        # Value
        p.setPen(QPen(QColor(r, g, b)))
        p.setFont(QFont("Consolas", 26, QFont.Weight.Bold))
        p.drawText(QRect(bx, by + 28, bw, 36), Qt.AlignmentFlag.AlignCenter, str(self._value))
        p.end()


# ─────────────────────────────────────────────────────────────────────────────
#  3. PRODUCER-CONSUMER SIMULATION
# ─────────────────────────────────────────────────────────────────────────────

class ProducerConsumerWorker(QThread):
    buffer_update = pyqtSignal(list)  # buffer contents
    producer_state = pyqtSignal(int, str)
    consumer_state = pyqtSignal(int, str)
    log_signal = pyqtSignal(str, str)
    stats_update = pyqtSignal(int, int)  # produced, consumed
    finished = pyqtSignal()

    def __init__(self, n_prod, n_cons, buf_size, speed):
        super().__init__()
        self.n_prod = n_prod
        self.n_cons = n_cons
        self.buf_size = buf_size
        self.speed = speed
        self._stop = threading.Event()
        self.buffer = []
        self._lock = threading.Lock()
        self._not_full = threading.Condition(self._lock)
        self._not_empty = threading.Condition(self._lock)
        self._produced = 0
        self._consumed = 0

    def stop(self): self._stop.set()

    def run(self):
        threads = []
        item_id = [0]

        def producer(pid):
            while not self._stop.is_set():
                with self._not_full:
                    while len(self.buffer) >= self.buf_size and not self._stop.is_set():
                        self.producer_state.emit(pid, "WAITING")
                        self.log_signal.emit(f"Producer P-{pid} waiting (buffer full)", "WAIT")
                        self._not_full.wait(timeout=0.5)
                    if self._stop.is_set(): break
                    self.producer_state.emit(pid, "RUNNING")
                    item = f"I{item_id[0]}"
                    item_id[0] += 1
                    self.buffer.append(item)
                    self._produced += 1
                    self.buffer_update.emit(list(self.buffer))
                    self.stats_update.emit(self._produced, self._consumed)
                    self.log_signal.emit(f"P-{pid} produced {item} → buffer [{len(self.buffer)}/{self.buf_size}]", "SUCCESS")
                    self._not_empty.notify_all()
                time.sleep(random.uniform(0.3, 0.8) / self.speed)
            self.producer_state.emit(pid, "DONE")

        def consumer(cid):
            while not self._stop.is_set():
                with self._not_empty:
                    while len(self.buffer) == 0 and not self._stop.is_set():
                        self.consumer_state.emit(cid, "WAITING")
                        self.log_signal.emit(f"Consumer C-{cid} waiting (buffer empty)", "WAIT")
                        self._not_empty.wait(timeout=0.5)
                    if self._stop.is_set(): break
                    self.consumer_state.emit(cid, "RUNNING")
                    item = self.buffer.pop(0)
                    self._consumed += 1
                    self.buffer_update.emit(list(self.buffer))
                    self.stats_update.emit(self._produced, self._consumed)
                    self.log_signal.emit(f"C-{cid} consumed {item} ← buffer [{len(self.buffer)}/{self.buf_size}]", "INFO")
                    self._not_full.notify_all()
                time.sleep(random.uniform(0.4, 1.0) / self.speed)
            self.consumer_state.emit(cid, "DONE")

        for i in range(self.n_prod):
            t = threading.Thread(target=producer, args=(i,), daemon=True)
            threads.append(t)
        for i in range(self.n_cons):
            t = threading.Thread(target=consumer, args=(i,), daemon=True)
            threads.append(t)

        for t in threads: t.start()

        while not self._stop.is_set():
            time.sleep(0.1)

        self.finished.emit()


class ProducerConsumerSimulation(BaseSimulation):
    def __init__(self, parent=None):
        super().__init__("PRODUCER — CONSUMER",
                         "Bounded buffer · Semaphore/Condition Variables · Synchronization",
                         ACCENT_GREEN, parent)
        self._worker = None
        self._buf_size = 8
        self._producer_blocks = []
        self._consumer_blocks = []

    def _setup_visualization(self, parent):
        layout = QVBoxLayout(parent)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(16)

        # Main area with producers, buffer, consumers
        main_row = QHBoxLayout()

        # Producers
        prod_col = QVBoxLayout()
        prod_lbl = QLabel("◈  PRODUCERS")
        prod_lbl.setStyleSheet(f"color:{ACCENT_GREEN};font-size:11px;font-weight:bold;font-family:'Consolas',monospace;")
        prod_col.addWidget(prod_lbl)
        self._prod_container = QWidget()
        self._prod_layout = QVBoxLayout(self._prod_container)
        self._prod_layout.setSpacing(8)
        self._prod_layout.setContentsMargins(0,0,0,0)
        prod_col.addWidget(self._prod_container)
        prod_col.addStretch()
        main_row.addLayout(prod_col)

        # Arrow
        arrow_lbl = QLabel("→")
        arrow_lbl.setStyleSheet(f"color:{ACCENT_CYAN};font-size:24px;font-weight:bold;")
        arrow_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_row.addWidget(arrow_lbl)

        # Buffer
        buf_col = QVBoxLayout()
        buf_lbl = QLabel("◈  BUFFER")
        buf_lbl.setStyleSheet(f"color:{ACCENT_YELLOW};font-size:11px;font-weight:bold;font-family:'Consolas',monospace;")
        buf_col.addWidget(buf_lbl)
        self._buffer_widget = BufferWidget(self._buf_size)
        buf_col.addWidget(self._buffer_widget)
        buf_col.addStretch()
        main_row.addLayout(buf_col)

        # Arrow
        arrow_lbl2 = QLabel("→")
        arrow_lbl2.setStyleSheet(f"color:{ACCENT_CYAN};font-size:24px;font-weight:bold;")
        arrow_lbl2.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_row.addWidget(arrow_lbl2)

        # Consumers
        cons_col = QVBoxLayout()
        cons_lbl = QLabel("◈  CONSUMERS")
        cons_lbl.setStyleSheet(f"color:{ACCENT_ORANGE};font-size:11px;font-weight:bold;font-family:'Consolas',monospace;")
        cons_col.addWidget(cons_lbl)
        self._cons_container = QWidget()
        self._cons_layout = QVBoxLayout(self._cons_container)
        self._cons_layout.setSpacing(8)
        self._cons_layout.setContentsMargins(0,0,0,0)
        cons_col.addWidget(self._cons_container)
        cons_col.addStretch()
        main_row.addLayout(cons_col)

        layout.addLayout(main_row)
        layout.addStretch()

        self._rebuild_actors()

    def _rebuild_actors(self):
        for b in self._producer_blocks + self._consumer_blocks:
            b.setParent(None); b.deleteLater()
        self._producer_blocks.clear()
        self._consumer_blocks.clear()
        while self._prod_layout.count():
            item = self._prod_layout.takeAt(0)
            if item.widget(): item.widget().deleteLater()
        while self._cons_layout.count():
            item = self._cons_layout.takeAt(0)
            if item.widget(): item.widget().deleteLater()

        n_prod = getattr(self, '_n_prod_val', 2)
        n_cons = getattr(self, '_n_cons_val', 2)

        for i in range(n_prod):
            b = ThreadBlock(i, ACCENT_GREEN)
            b.set_state("IDLE")
            self._producer_blocks.append(b)
            self._prod_layout.addWidget(b)

        for i in range(n_cons):
            b = ThreadBlock(i, ACCENT_ORANGE)
            b.set_state("IDLE")
            self._consumer_blocks.append(b)
            self._cons_layout.addWidget(b)

    def _setup_controls(self, card, layout):
        for lbl_text, attr, mn, mx, default in [
            ("Producers:", '_n_prod_val', 1, 4, 2),
            ("Consumers:", '_n_cons_val', 1, 4, 2),
            ("Buffer Size:", '_buf_size', 3, 12, 8),
        ]:
            lbl = QLabel(lbl_text)
            lbl.setStyleSheet(f"color:{TEXT_SECONDARY};font-size:12px;font-family:'Consolas',monospace;")
            layout.addWidget(lbl)
            spin = QSpinBox()
            spin.setRange(mn, mx)
            spin.setValue(default)
            setattr(self, f'_spin_{attr}', spin)
            spin.valueChanged.connect(lambda v, a=attr: setattr(self, a, v))
            layout.addWidget(spin)

        self._n_prod_val = 2
        self._n_cons_val = 2

        lbl4 = QLabel("Speed:")
        lbl4.setStyleSheet(f"color:{TEXT_SECONDARY};font-size:12px;font-family:'Consolas',monospace;")
        layout.addWidget(lbl4)
        self._speed_slider = QSlider(Qt.Orientation.Horizontal)
        self._speed_slider.setRange(1, 5)
        self._speed_slider.setValue(2)
        layout.addWidget(self._speed_slider)

    def _setup_stats(self, card, layout):
        self._stat_produced = StatBadge("PRODUCED", "0", ACCENT_GREEN)
        self._stat_consumed = StatBadge("CONSUMED", "0", ACCENT_ORANGE)
        self._stat_buffer = StatBadge("IN BUFFER", "0", ACCENT_YELLOW)
        layout.addWidget(self._stat_produced)
        layout.addWidget(self._stat_consumed)
        layout.addWidget(self._stat_buffer)

    def start(self):
        if self._running: return
        self._buf_size = getattr(self, '_buf_size', 8)
        self._buffer_widget.resize_buffer(self._buf_size)
        self._rebuild_actors()
        self._set_running(True)

        self._worker = ProducerConsumerWorker(
            self._n_prod_val, self._n_cons_val, self._buf_size,
            self._speed_slider.value()
        )
        self._worker.buffer_update.connect(self._on_buffer)
        self._worker.producer_state.connect(lambda i, s: self._producer_blocks[i].set_state(s) if i < len(self._producer_blocks) else None)
        self._worker.consumer_state.connect(lambda i, s: self._consumer_blocks[i].set_state(s) if i < len(self._consumer_blocks) else None)
        self._worker.stats_update.connect(self._on_stats)
        self._worker.log_signal.connect(self.event_log.add_event)
        self._worker.finished.connect(lambda: self._set_running(False))
        self._worker.start()

    def _on_buffer(self, contents):
        self._buffer_widget.set_contents(contents)
        self._stat_buffer.set_value(len(contents))

    def _on_stats(self, produced, consumed):
        self._stat_produced.set_value(produced)
        self._stat_consumed.set_value(consumed)

    def stop(self):
        if self._worker: self._worker.stop()
        self._set_running(False)

    def reset(self):
        self.stop()
        if self._worker: self._worker.wait(500)
        self._buffer_widget.set_contents([])
        self._rebuild_actors()
        self._stat_produced.set_value(0)
        self._stat_consumed.set_value(0)
        self._stat_buffer.set_value(0)
        self.event_log.clear_log()
        self.log("Reset", "SYSTEM")


class BufferWidget(QWidget):
    def __init__(self, size=8, parent=None):
        super().__init__(parent)
        self._size = size
        self._contents = []
        self.setMinimumHeight(120)
        self.setMinimumWidth(300)

    def resize_buffer(self, size):
        self._size = size
        self._contents = []
        self.update()

    def set_contents(self, contents):
        self._contents = contents[:self._size]
        self.update()

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        w, h = self.width(), self.height()

        cell_w = min(60, (w - 20) // self._size)
        cell_h = 70
        total_w = cell_w * self._size
        start_x = (w - total_w) // 2
        start_y = (h - cell_h) // 2

        for i in range(self._size):
            x = start_x + i * cell_w
            y = start_y
            filled = i < len(self._contents)

            if filled:
                r, g, b = 16, 185, 129
                p.setBrush(QBrush(QColor(r, g, b, 60)))
                p.setPen(QPen(QColor(r, g, b, 180), 1.5))
            else:
                p.setBrush(QBrush(QColor(30, 45, 80, 80)))
                p.setPen(QPen(QColor(BORDER_COLOR), 1))

            p.drawRect(x, y, cell_w - 2, cell_h)

            if filled:
                p.setPen(QPen(QColor(ACCENT_GREEN)))
                p.setFont(QFont("Consolas", 8, QFont.Weight.Bold))
                p.drawText(QRect(x, y, cell_w - 2, cell_h), Qt.AlignmentFlag.AlignCenter, self._contents[i])

        # Capacity label
        p.setPen(QPen(QColor(TEXT_SECONDARY)))
        p.setFont(QFont("Consolas", 10))
        p.drawText(QRect(0, start_y + cell_h + 5, w, 20), Qt.AlignmentFlag.AlignCenter,
                   f"{len(self._contents)} / {self._size} slots used")
        p.end()


# ─────────────────────────────────────────────────────────────────────────────
#  4. DEADLOCK SIMULATION
# ─────────────────────────────────────────────────────────────────────────────

class DeadlockWorker(QThread):
    state_update = pyqtSignal(dict)  # {tid: state, resource_holder: dict}
    log_signal = pyqtSignal(str, str)
    deadlock_detected = pyqtSignal()
    finished = pyqtSignal()

    def __init__(self, n_threads, speed):
        super().__init__()
        self.n_threads = n_threads
        self.speed = speed
        self._stop = threading.Event()
        self.resources = [threading.Lock() for _ in range(n_threads)]
        self.resource_holders = [-1] * n_threads  # which thread holds resource i
        self.thread_waiting_for = [-1] * n_threads  # which resource thread i waits for
        self._lock = threading.Lock()

    def stop(self):
        self._stop.set()
        # Release all resources on stop
        for r in self.resources:
            try:
                r.release()
            except Exception:
                pass

    def run(self):
        """Deliberately create a deadlock: Thread i holds resource i, waits for resource (i+1)%n"""
        acquired = [-1] * self.n_threads
        barrier = threading.Barrier(self.n_threads)
        states = ["IDLE"] * self.n_threads

        def worker(tid):
            first_res = tid
            second_res = (tid + 1) % self.n_threads

            if self._stop.is_set(): return
            states[tid] = "RUNNING"
            self.log_signal.emit(f"T-{tid} started, wants R{first_res} then R{second_res}", "INFO")
            self._emit(states, acquired)

            # Acquire first resource
            self.log_signal.emit(f"T-{tid} acquiring R{first_res}...", "LOCK")
            self.resources[first_res].acquire()
            if self._stop.is_set():
                try: self.resources[first_res].release()
                except: pass
                return
            acquired[tid] = first_res
            with self._lock:
                self.resource_holders[first_res] = tid
            self.log_signal.emit(f"T-{tid} acquired R{first_res} ✓", "SUCCESS")
            self._emit(states, acquired)

            # Barrier: all threads have first resource — now deadlock will happen
            try:
                barrier.wait(timeout=5)
            except: pass

            if self._stop.is_set():
                try: self.resources[first_res].release()
                except: pass
                return

            # Try to acquire second resource (will deadlock!)
            states[tid] = "BLOCKED"
            with self._lock:
                self.thread_waiting_for[tid] = second_res
            self.log_signal.emit(f"T-{tid} trying to acquire R{second_res} (BLOCKED!)", "WARNING")
            self._emit(states, acquired)

            # Detect cycle
            QTimer.singleShot(100, self.deadlock_detected.emit)

            # Block indefinitely (deadlock)
            self.resources[second_res].acquire()  # This will never complete
            acquired[tid] = second_res

        threads = []
        for i in range(self.n_threads):
            t = threading.Thread(target=worker, args=(i,), daemon=True)
            threads.append(t)

        for t in threads: t.start()

        # Wait for stop signal
        while not self._stop.is_set():
            time.sleep(0.1)

        self.finished.emit()

    def _emit(self, states, acquired):
        data = {
            "states": list(states),
            "acquired": list(acquired),
            "holders": list(self.resource_holders),
            "waiting": list(self.thread_waiting_for),
        }
        self.state_update.emit(data)


class DeadlockSimulation(BaseSimulation):
    def __init__(self, parent=None):
        super().__init__("DEADLOCK",
                         "Circular wait · Resource starvation · Deadlock detection",
                         ACCENT_RED, parent)
        self._worker = None
        self._deadlock_state = None

    def _setup_visualization(self, parent):
        layout = QVBoxLayout(parent)
        layout.setContentsMargins(20, 20, 20, 20)

        self._deadlock_view = DeadlockGraphWidget()
        layout.addWidget(self._deadlock_view)

    def _setup_controls(self, card, layout):
        lbl = QLabel("Number of Threads/Resources:")
        lbl.setStyleSheet(f"color:{TEXT_SECONDARY};font-size:12px;font-family:'Consolas',monospace;")
        layout.addWidget(lbl)
        self._n_spin = QSpinBox()
        self._n_spin.setRange(2, 4)
        self._n_spin.setValue(3)
        layout.addWidget(self._n_spin)

        info = QLabel("ⓘ  Each thread will acquire\nits resource then wait\nfor the next — creating\na circular deadlock.")
        info.setStyleSheet(f"color:{ACCENT_YELLOW};font-size:11px;font-family:'Consolas',monospace;padding:6px;border:1px solid {BORDER_COLOR};border-radius:6px;")
        layout.addWidget(info)

    def _setup_stats(self, card, layout):
        self._stat_status = StatBadge("STATUS", "IDLE", ACCENT_CYAN)
        self._stat_blocked = StatBadge("BLOCKED", "0", ACCENT_RED)
        self._stat_holding = StatBadge("HOLDING", "0", ACCENT_YELLOW)
        layout.addWidget(self._stat_status)
        layout.addWidget(self._stat_blocked)
        layout.addWidget(self._stat_holding)

    def start(self):
        if self._running: return
        n = self._n_spin.value()
        self._set_running(True)
        self._deadlock_view.set_n(n)
        self.log(f"Starting deadlock simulation with {n} threads", "SYSTEM")

        self._worker = DeadlockWorker(n, 2)
        self._worker.state_update.connect(self._on_state)
        self._worker.log_signal.connect(self.event_log.add_event)
        self._worker.deadlock_detected.connect(self._on_deadlock)
        self._worker.finished.connect(lambda: self._set_running(False))
        self._worker.start()

    def _on_state(self, data):
        self._deadlock_view.update_state(data)
        blocked = sum(1 for s in data["states"] if s == "BLOCKED")
        holding = sum(1 for h in data["holders"] if h >= 0)
        self._stat_blocked.set_value(blocked)
        self._stat_holding.set_value(holding)

    def _on_deadlock(self):
        self._stat_status.set_value("⚠ DEADLOCK!")
        self._deadlock_view.set_deadlock(True)
        self.log("DEADLOCK DETECTED! Circular wait established!", "ERROR")
        self.log("All threads are blocked waiting for each other's resources", "ERROR")

    def stop(self):
        if self._worker: self._worker.stop()
        self._set_running(False)

    def reset(self):
        self.stop()
        if self._worker: self._worker.wait(1000)
        self._deadlock_view.set_deadlock(False)
        self._deadlock_view.clear()
        self._stat_status.set_value("IDLE")
        self._stat_blocked.set_value(0)
        self._stat_holding.set_value(0)
        self.event_log.clear_log()
        self.log("Reset", "SYSTEM")


class DeadlockGraphWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._n = 3
        self._state = {}
        self._deadlock = False
        self._flash = 0.0
        self._timer = QTimer()
        self._timer.timeout.connect(self._tick)
        self._timer.start(80)

    def set_n(self, n):
        self._n = n
        self._state = {}
        self._deadlock = False
        self.update()

    def set_deadlock(self, dl):
        self._deadlock = dl
        self._flash = 1.0
        self.update()

    def clear(self):
        self._state = {}
        self._deadlock = False
        self._flash = 0.0
        self.update()

    def update_state(self, data):
        self._state = data
        self.update()

    def _tick(self):
        if self._flash > 0:
            self._flash = max(0, self._flash - 0.03)
            self.update()

    def _get_positions(self, w, h, n, is_thread):
        import math
        positions = []
        radius = min(w, h) * 0.28
        cx, cy = w // 2, h // 2
        offset = 0 if is_thread else math.pi / n
        for i in range(n):
            angle = 2 * math.pi * i / n - math.pi / 2 + offset
            x = cx + radius * math.cos(angle)
            y = cy + radius * math.sin(angle)
            positions.append((x, y))
        return positions

    def paintEvent(self, event):
        import math
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        w, h = self.width(), self.height()
        p.fillRect(0, 0, w, h, QColor(BG_DEEP))

        n = self._n
        t_pos = self._get_positions(w, h, n, True)
        r_pos = self._get_positions(w, h, n, False)

        if not t_pos or not r_pos:
            p.end(); return

        holders = self._state.get("holders", [-1] * n)
        waiting = self._state.get("waiting", [-1] * n)
        states = self._state.get("states", ["IDLE"] * n)

        # Draw resource-holder edges (solid)
        p.setPen(QPen(QColor(ACCENT_GREEN), 2))
        for ri, holder in enumerate(holders):
            if holder >= 0 and ri < len(r_pos) and holder < len(t_pos):
                rx, ry = r_pos[ri]
                tx, ty = t_pos[holder]
                p.drawLine(int(rx), int(ry), int(tx), int(ty))
                # Arrowhead
                self._draw_arrow(p, rx, ry, tx, ty, QColor(ACCENT_GREEN))

        # Draw waiting edges (dashed red)
        pen = QPen(QColor(ACCENT_RED), 2, Qt.PenStyle.DashLine)
        p.setPen(pen)
        for tid, ri in enumerate(waiting):
            if ri >= 0 and tid < len(t_pos) and ri < len(r_pos):
                tx, ty = t_pos[tid]
                rx, ry = r_pos[ri]
                p.drawLine(int(tx), int(ty), int(rx), int(ry))

        # Deadlock glow
        if self._deadlock:
            import math as m
            glow_a = int(80 + 60 * m.sin(self._flash * m.pi * 10))
            glow_pen = QPen(QColor(239, 68, 68, glow_a), 4)
            p.setPen(glow_pen)
            p.setBrush(Qt.BrushStyle.NoBrush)
            cx, cy = w // 2, h // 2
            radius = min(w, h) * 0.38
            p.drawEllipse(int(cx - radius), int(cy - radius), int(radius * 2), int(radius * 2))

        # Draw thread nodes
        for i, (x, y) in enumerate(t_pos):
            state = states[i] if i < len(states) else "IDLE"
            color_map = {"IDLE": ACCENT_CYAN, "RUNNING": ACCENT_GREEN, "BLOCKED": ACCENT_RED, "DONE": TEXT_DIM}
            c = color_map.get(state, ACCENT_CYAN)
            r2 = int(c[1:3], 16); g2 = int(c[3:5], 16); b2 = int(c[5:7], 16)

            p.setBrush(QBrush(QColor(r2, g2, b2, 60)))
            p.setPen(QPen(QColor(r2, g2, b2), 2))
            p.drawEllipse(int(x)-25, int(y)-25, 50, 50)
            p.setPen(QPen(QColor(c)))
            p.setFont(QFont("Consolas", 9, QFont.Weight.Bold))
            p.drawText(QRect(int(x)-25, int(y)-10, 50, 20), Qt.AlignmentFlag.AlignCenter, f"T-{i}")
            p.setFont(QFont("Consolas", 7))
            p.setPen(QPen(QColor(TEXT_SECONDARY)))
            p.drawText(QRect(int(x)-25, int(y)+8, 50, 15), Qt.AlignmentFlag.AlignCenter, state[:4])

        # Draw resource nodes (diamonds)
        for i, (x, y) in enumerate(r_pos):
            c = ACCENT_YELLOW
            r2 = int(c[1:3], 16); g2 = int(c[3:5], 16); b2 = int(c[5:7], 16)
            pts = [QPointF(x, y-22), QPointF(x+22, y), QPointF(x, y+22), QPointF(x-22, y)]
            poly = QPolygonF(pts)
            p.setBrush(QBrush(QColor(r2, g2, b2, 50)))
            p.setPen(QPen(QColor(r2, g2, b2), 2))
            p.drawPolygon(poly)
            p.setPen(QPen(QColor(c)))
            p.setFont(QFont("Consolas", 9, QFont.Weight.Bold))
            p.drawText(QRect(int(x)-22, int(y)-10, 44, 20), Qt.AlignmentFlag.AlignCenter, f"R{i}")

        # Center label
        if self._deadlock:
            p.setPen(QPen(QColor(ACCENT_RED)))
            p.setFont(QFont("Consolas", 11, QFont.Weight.Bold))
            p.drawText(QRect(w//2-80, h//2-15, 160, 30), Qt.AlignmentFlag.AlignCenter, "⚠  DEADLOCK!")

        p.end()

    def _draw_arrow(self, p, x1, y1, x2, y2, color):
        import math
        angle = math.atan2(y2 - y1, x2 - x1)
        mid_x = (x1 + x2) / 2
        mid_y = (y1 + y2) / 2
        size = 8
        p.setBrush(QBrush(color))
        p.setPen(Qt.PenStyle.NoPen)
        pts = [
            QPointF(mid_x + size * math.cos(angle), mid_y + size * math.sin(angle)),
            QPointF(mid_x + size * math.cos(angle + 2.5), mid_y + size * math.sin(angle + 2.5)),
            QPointF(mid_x + size * math.cos(angle - 2.5), mid_y + size * math.sin(angle - 2.5)),
        ]
        p.drawPolygon(QPolygonF(pts))


# ─────────────────────────────────────────────────────────────────────────────
#  5. STARVATION SIMULATION
# ─────────────────────────────────────────────────────────────────────────────

class StarvationWorker(QThread):
    update_signal = pyqtSignal(list)   # list of (tid, state, cpu_time, priority)
    log_signal = pyqtSignal(str, str)
    finished = pyqtSignal()

    def __init__(self, n_threads, speed):
        super().__init__()
        self.n_threads = n_threads
        self.speed = speed
        self._stop = threading.Event()

    def stop(self): self._stop.set()

    def run(self):
        # Priorities: last thread has lowest priority
        priorities = list(range(self.n_threads, 0, -1))  # High = large number
        cpu_times = [0] * self.n_threads
        states = ["IDLE"] * self.n_threads

        self.log_signal.emit("Priority scheduling: higher number = higher priority", "SYSTEM")
        for i in range(self.n_threads):
            self.log_signal.emit(f"T-{i} priority = {priorities[i]}", "INFO")

        time.sleep(0.5 / self.speed)

        tick = 0
        while not self._stop.is_set():
            # Find highest priority thread that's runnable
            best = -1
            best_pri = -1
            for i in range(self.n_threads):
                if priorities[i] > best_pri and not self._stop.is_set():
                    best = i
                    best_pri = priorities[i]

            if best < 0: break

            for i in range(self.n_threads):
                states[i] = "RUNNING" if i == best else "WAITING"

            cpu_times[best] += 1
            self.update_signal.emit([(i, states[i], cpu_times[i], priorities[i]) for i in range(self.n_threads)])

            if tick % 10 == 0:
                self.log_signal.emit(f"T-{best} (P={priorities[best]}) running — T-{self.n_threads-1} (P=1) starving!", "WARNING")

            tick += 1
            time.sleep(0.15 / self.speed)

            # Occasionally boost low-priority thread to show aging
            if tick % 30 == 0:
                for i in range(self.n_threads):
                    if priorities[i] == 1:
                        priorities[i] = self.n_threads + 1  # Aging boost
                        self.log_signal.emit(f"AGING: T-{i} priority boosted! (Anti-starvation)", "SUCCESS")

        self.finished.emit()


class StarvationSimulation(BaseSimulation):
    def __init__(self, parent=None):
        super().__init__("STARVATION",
                         "Priority scheduling · Low-priority thread neglect · Aging solution",
                         ACCENT_ORANGE, parent)
        self._worker = None
        self._thread_data = []
        self._bars = []

    def _setup_visualization(self, parent):
        layout = QVBoxLayout(parent)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(12)

        lbl = QLabel("◈  CPU TIME DISTRIBUTION  (Priority Scheduling)")
        lbl.setStyleSheet(f"color:{ACCENT_ORANGE};font-size:12px;font-weight:bold;font-family:'Consolas',monospace;")
        layout.addWidget(lbl)

        self._bar_container = QWidget()
        self._bar_layout = QVBoxLayout(self._bar_container)
        self._bar_layout.setSpacing(10)
        layout.addWidget(self._bar_container)

        note = QLabel("ⓘ  T-0 has highest priority (greedy). T-N has lowest priority and starves.\n    After 30 ticks, Aging kicks in and boosts the starving thread.")
        note.setStyleSheet(f"color:{TEXT_SECONDARY};font-size:11px;font-family:'Consolas',monospace;padding:8px;border:1px solid {BORDER_COLOR};border-radius:6px;")
        note.setWordWrap(True)
        layout.addWidget(note)
        layout.addStretch()

        self._rebuild_bars(4)

    def _rebuild_bars(self, n):
        for b in self._bars:
            b.setParent(None); b.deleteLater()
        self._bars.clear()
        while self._bar_layout.count():
            item = self._bar_layout.takeAt(0)
            if item.widget(): item.widget().deleteLater()

        for i in range(n):
            row = QWidget()
            row_layout = QHBoxLayout(row)
            row_layout.setContentsMargins(0, 0, 0, 0)
            row_layout.setSpacing(8)

            lbl = QLabel(f"T-{i}")
            lbl.setFixedWidth(30)
            lbl.setStyleSheet(f"color:{THREAD_COLORS[i%len(THREAD_COLORS)]};font-size:12px;font-weight:bold;font-family:'Consolas',monospace;")
            row_layout.addWidget(lbl)

            bar = QProgressBar()
            bar.setRange(0, 100)
            bar.setValue(0)
            c = THREAD_COLORS[i % len(THREAD_COLORS)]
            r2 = int(c[1:3], 16); g2 = int(c[3:5], 16); b2 = int(c[5:7], 16)
            bar.setStyleSheet(f"""
                QProgressBar {{ background: {BG_ELEVATED}; border-radius: 6px; height: 22px; text-align: center; color: white; font-size: 11px; font-family: 'Consolas'; border: 1px solid {BORDER_COLOR}; }}
                QProgressBar::chunk {{ background: qlineargradient(x1:0,y1:0,x2:1,y2:0, stop:0 rgba({r2},{g2},{b2},200), stop:1 rgba({r2},{g2},{b2},150)); border-radius: 5px; }}
            """)
            row_layout.addWidget(bar, 1)

            pri_lbl = QLabel(f"P={n-i}")
            pri_lbl.setFixedWidth(40)
            pri_lbl.setStyleSheet(f"color:{ACCENT_YELLOW};font-size:11px;font-family:'Consolas',monospace;")
            row_layout.addWidget(pri_lbl)

            state_lbl = QLabel("IDLE")
            state_lbl.setFixedWidth(70)
            state_lbl.setStyleSheet(f"color:{TEXT_DIM};font-size:11px;font-family:'Consolas',monospace;")
            row_layout.addWidget(state_lbl)

            self._bar_layout.addWidget(row)
            self._bars.append((bar, pri_lbl, state_lbl))

    def _setup_controls(self, card, layout):
        lbl = QLabel("Number of Threads:")
        lbl.setStyleSheet(f"color:{TEXT_SECONDARY};font-size:12px;font-family:'Consolas',monospace;")
        layout.addWidget(lbl)
        self._n_spin = QSpinBox()
        self._n_spin.setRange(2, 6)
        self._n_spin.setValue(4)
        layout.addWidget(self._n_spin)

        lbl2 = QLabel("Speed:")
        lbl2.setStyleSheet(f"color:{TEXT_SECONDARY};font-size:12px;font-family:'Consolas',monospace;")
        layout.addWidget(lbl2)
        self._speed_slider = QSlider(Qt.Orientation.Horizontal)
        self._speed_slider.setRange(1, 5)
        self._speed_slider.setValue(2)
        layout.addWidget(self._speed_slider)

    def _setup_stats(self, card, layout):
        self._stat_starvation = StatBadge("STARVING", "0", ACCENT_RED)
        self._stat_running = StatBadge("RUNNING", "-", ACCENT_GREEN)
        self._stat_aging = StatBadge("AGING", "OFF", ACCENT_YELLOW)
        layout.addWidget(self._stat_starvation)
        layout.addWidget(self._stat_running)
        layout.addWidget(self._stat_aging)

    def start(self):
        if self._running: return
        n = self._n_spin.value()
        self._rebuild_bars(n)
        self._set_running(True)

        self._worker = StarvationWorker(n, self._speed_slider.value())
        self._worker.update_signal.connect(self._on_update)
        self._worker.log_signal.connect(self.event_log.add_event)
        self._worker.finished.connect(lambda: self._set_running(False))
        self._worker.start()

    def _on_update(self, data):
        max_cpu = max((d[2] for d in data), default=1) or 1
        starving = 0
        running_id = -1

        for i, (tid, state, cpu_time, priority) in enumerate(data):
            if i < len(self._bars):
                bar, pri_lbl, state_lbl = self._bars[i]
                bar.setValue(int(cpu_time / max_cpu * 100))
                bar.setFormat(f"{cpu_time} ticks")
                pri_lbl.setText(f"P={priority}")
                color_map = {"RUNNING": ACCENT_GREEN, "WAITING": ACCENT_YELLOW, "IDLE": TEXT_DIM}
                c = color_map.get(state, TEXT_DIM)
                state_lbl.setStyleSheet(f"color:{c};font-size:11px;font-family:'Consolas',monospace;")
                state_lbl.setText(state)
                if state == "RUNNING": running_id = tid
                if cpu_time == 0 and state == "WAITING": starving += 1

        self._stat_starving_val = starving
        self._stat_starvation.set_value(starving)
        if running_id >= 0:
            self._stat_running.set_value(f"T-{running_id}")

    def stop(self):
        if self._worker: self._worker.stop()
        self._set_running(False)

    def reset(self):
        self.stop()
        if self._worker: self._worker.wait(500)
        n = self._n_spin.value()
        self._rebuild_bars(n)
        self._stat_starvation.set_value(0)
        self._stat_running.set_value("-")
        self.event_log.clear_log()
        self.log("Reset", "SYSTEM")


# ─────────────────────────────────────────────────────────────────────────────
#  6. SEMAPHORE SIMULATION
# ─────────────────────────────────────────────────────────────────────────────

class SemaphoreWorker(QThread):
    update_signal = pyqtSignal(list, int)  # [(tid, state)], semaphore_value
    log_signal = pyqtSignal(str, str)
    finished = pyqtSignal()

    def __init__(self, n_threads, max_concurrent, speed):
        super().__init__()
        self.n_threads = n_threads
        self.max_concurrent = max_concurrent
        self.speed = speed
        self._stop = threading.Event()
        self._sem = threading.Semaphore(max_concurrent)
        self._sem_val = max_concurrent
        self._sem_lock = threading.Lock()

    def stop(self): self._stop.set()

    def run(self):
        states = ["IDLE"] * self.n_threads
        active_count = [0]
        lock = threading.Lock()

        self.log_signal.emit(f"Semaphore initialized: permits = {self.max_concurrent}", "SYSTEM")

        def worker(tid):
            while not self._stop.is_set():
                # Wait (acquire)
                states[tid] = "WAITING"
                self.log_signal.emit(f"T-{tid} → sem.acquire() (waiting for permit)", "WAIT")
                self._emit(states)

                acquired = self._sem.acquire(timeout=1)
                if not acquired or self._stop.is_set():
                    continue

                with self._sem_lock:
                    self._sem_val -= 1

                with lock:
                    active_count[0] += 1

                states[tid] = "RUNNING"
                self.log_signal.emit(f"T-{tid} acquired permit! [active={active_count[0]}/{self.max_concurrent}]", "SUCCESS")
                self._emit(states)

                # Critical section
                time.sleep(random.uniform(0.5, 1.5) / self.speed)
                if self._stop.is_set():
                    self._sem.release()
                    break

                # Signal (release)
                with self._sem_lock:
                    self._sem_val += 1
                self._sem.release()
                with lock:
                    active_count[0] -= 1

                states[tid] = "IDLE"
                self.log_signal.emit(f"T-{tid} released permit [active={active_count[0]}/{self.max_concurrent}]", "INFO")
                self._emit(states)
                time.sleep(random.uniform(0.1, 0.3) / self.speed)

        threads = [threading.Thread(target=worker, args=(i,), daemon=True) for i in range(self.n_threads)]
        for t in threads: t.start()
        while not self._stop.is_set():
            time.sleep(0.05)
        self.finished.emit()

    def _emit(self, states):
        with self._sem_lock:
            val = self._sem_val
        self.update_signal.emit([(i, states[i]) for i in range(len(states))], val)


class SemaphoreSimulation(BaseSimulation):
    def __init__(self, parent=None):
        super().__init__("SEMAPHORE",
                         "Resource counting · Concurrent access control · Wait/Signal",
                         ACCENT_PURPLE, parent)
        self._worker = None
        self._thread_blocks = []

    def _setup_visualization(self, parent):
        layout = QVBoxLayout(parent)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(16)

        # Semaphore display
        sem_row = QHBoxLayout()
        sem_lbl = QLabel("◈  SEMAPHORE VALUE:")
        sem_lbl.setStyleSheet(f"color:{ACCENT_PURPLE};font-size:13px;font-weight:bold;font-family:'Consolas',monospace;")
        sem_row.addWidget(sem_lbl)
        self._sem_display = SemaphoreDisplay()
        sem_row.addWidget(self._sem_display)
        sem_row.addStretch()
        layout.addLayout(sem_row)

        # Threads
        t_lbl = QLabel("◈  THREADS")
        t_lbl.setStyleSheet(f"color:{TEXT_SECONDARY};font-size:11px;font-weight:bold;font-family:'Consolas',monospace;")
        layout.addWidget(t_lbl)

        self._threads_row = QWidget()
        self._threads_row_layout = QHBoxLayout(self._threads_row)
        self._threads_row_layout.setContentsMargins(0, 0, 0, 0)
        self._threads_row_layout.setSpacing(14)
        self._threads_row_layout.addStretch()
        layout.addWidget(self._threads_row)
        layout.addStretch()

        self._rebuild_threads(5)

    def _rebuild_threads(self, n):
        for b in self._thread_blocks:
            b.setParent(None); b.deleteLater()
        self._thread_blocks.clear()
        while self._threads_row_layout.count() > 1:
            item = self._threads_row_layout.takeAt(0)
            if item.widget(): item.widget().deleteLater()
        for i in range(n):
            b = ThreadBlock(i, THREAD_COLORS[i % len(THREAD_COLORS)])
            self._thread_blocks.append(b)
            self._threads_row_layout.insertWidget(i, b)

    def _setup_controls(self, card, layout):
        lbl1 = QLabel("Total Threads:")
        lbl1.setStyleSheet(f"color:{TEXT_SECONDARY};font-size:12px;font-family:'Consolas',monospace;")
        layout.addWidget(lbl1)
        self._n_spin = QSpinBox()
        self._n_spin.setRange(2, 7)
        self._n_spin.setValue(5)
        layout.addWidget(self._n_spin)

        lbl2 = QLabel("Max Concurrent (Semaphore):")
        lbl2.setStyleSheet(f"color:{TEXT_SECONDARY};font-size:12px;font-family:'Consolas',monospace;")
        layout.addWidget(lbl2)
        self._max_spin = QSpinBox()
        self._max_spin.setRange(1, 5)
        self._max_spin.setValue(2)
        layout.addWidget(self._max_spin)

        lbl3 = QLabel("Speed:")
        lbl3.setStyleSheet(f"color:{TEXT_SECONDARY};font-size:12px;font-family:'Consolas',monospace;")
        layout.addWidget(lbl3)
        self._speed_slider = QSlider(Qt.Orientation.Horizontal)
        self._speed_slider.setRange(1, 5)
        self._speed_slider.setValue(2)
        layout.addWidget(self._speed_slider)

    def _setup_stats(self, card, layout):
        self._stat_permits = StatBadge("PERMITS", "0", ACCENT_PURPLE)
        self._stat_active = StatBadge("ACTIVE", "0", ACCENT_GREEN)
        self._stat_waiting = StatBadge("WAITING", "0", ACCENT_YELLOW)
        layout.addWidget(self._stat_permits)
        layout.addWidget(self._stat_active)
        layout.addWidget(self._stat_waiting)

    def start(self):
        if self._running: return
        n = self._n_spin.value()
        max_c = self._max_spin.value()
        self._rebuild_threads(n)
        self._sem_display.set_max(max_c)
        self._sem_display.set_value(max_c)
        self._set_running(True)

        self._worker = SemaphoreWorker(n, max_c, self._speed_slider.value())
        self._worker.update_signal.connect(self._on_update)
        self._worker.log_signal.connect(self.event_log.add_event)
        self._worker.finished.connect(lambda: self._set_running(False))
        self._worker.start()

    def _on_update(self, data, sem_val):
        active = waiting = 0
        for tid, state in data:
            if tid < len(self._thread_blocks):
                self._thread_blocks[tid].set_state(state)
            if state == "RUNNING": active += 1
            elif state == "WAITING": waiting += 1
        self._sem_display.set_value(max(0, sem_val))
        self._stat_permits.set_value(max(0, sem_val))
        self._stat_active.set_value(active)
        self._stat_waiting.set_value(waiting)

    def stop(self):
        if self._worker: self._worker.stop()
        self._set_running(False)

    def reset(self):
        self.stop()
        if self._worker: self._worker.wait(500)
        n = self._n_spin.value()
        m = self._max_spin.value()
        self._rebuild_threads(n)
        self._sem_display.set_max(m)
        self._sem_display.set_value(m)
        self._stat_permits.set_value(m)
        self._stat_active.set_value(0)
        self._stat_waiting.set_value(0)
        self.event_log.clear_log()
        self.log("Reset", "SYSTEM")


class SemaphoreDisplay(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._value = 2
        self._max = 2
        self.setFixedSize(200, 60)

    def set_value(self, v):
        self._value = v
        self.update()

    def set_max(self, m):
        self._max = m
        self.update()

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        w, h = self.width(), self.height()

        for i in range(self._max):
            x = i * 45 + 5
            y = 10
            if i < self._value:
                p.setBrush(QBrush(QColor(ACCENT_PURPLE)))
                p.setPen(QPen(QColor(ACCENT_PURPLE), 2))
            else:
                p.setBrush(QBrush(QColor(50, 50, 80)))
                p.setPen(QPen(QColor(BORDER_COLOR), 1))
            p.drawRoundedRect(x, y, 36, 36, 6, 6)
            p.setPen(QPen(QColor(TEXT_PRIMARY)))
            p.setFont(QFont("Consolas", 11, QFont.Weight.Bold))
            p.drawText(QRect(x, y, 36, 36), Qt.AlignmentFlag.AlignCenter, str(i < self._value and "✓" or ""))

        p.setPen(QPen(QColor(TEXT_SECONDARY)))
        p.setFont(QFont("Consolas", 9))
        p.drawText(QRect(0, 50, w, 15), Qt.AlignmentFlag.AlignCenter, f"{self._value}/{self._max} permits")
        p.end()


# ─────────────────────────────────────────────────────────────────────────────
#  7. MONITOR / MUTEX SIMULATION
# ─────────────────────────────────────────────────────────────────────────────

class MutexMonitorWorker(QThread):
    update_signal = pyqtSignal(list, int, bool)  # states, cs_thread, mutex_locked
    log_signal = pyqtSignal(str, str)
    finished = pyqtSignal()

    def __init__(self, n, speed, use_monitor):
        super().__init__()
        self.n = n
        self.speed = speed
        self.use_monitor = use_monitor
        self._stop = threading.Event()
        self._lock = threading.Lock()
        self._counter = 0

    def stop(self): self._stop.set()

    def run(self):
        states = ["IDLE"] * self.n
        in_cs = [-1]
        lock_held = [False]

        def worker(tid):
            for _ in range(8):
                if self._stop.is_set(): return
                states[tid] = "RUNNING"
                self.log_signal.emit(f"T-{tid} wants to enter critical section", "INFO")
                self.update_signal.emit(list(states), in_cs[0], lock_held[0])

                if self.use_monitor:
                    self.log_signal.emit(f"T-{tid} acquiring mutex...", "LOCK")
                    with self._lock:
                        lock_held[0] = True
                        in_cs[0] = tid
                        self.log_signal.emit(f"T-{tid} entered CS (mutex held)", "SUCCESS")
                        self.update_signal.emit(list(states), tid, True)
                        time.sleep(0.4 / self.speed)
                        self._counter += 1
                        in_cs[0] = -1
                        lock_held[0] = False
                    self.log_signal.emit(f"T-{tid} exited CS, counter={self._counter}", "INFO")
                else:
                    # No mutex
                    in_cs[0] = tid
                    self.update_signal.emit(list(states), tid, False)
                    time.sleep(0.4 / self.speed)
                    self._counter += 1
                    in_cs[0] = -1
                    self.log_signal.emit(f"T-{tid} exited CS (no protection!), counter={self._counter}", "WARNING")

                states[tid] = "WAITING"
                self.update_signal.emit(list(states), in_cs[0], lock_held[0])
                time.sleep(0.2 / self.speed)

            states[tid] = "DONE"
            self.update_signal.emit(list(states), in_cs[0], lock_held[0])

        threads = [threading.Thread(target=worker, args=(i,), daemon=True) for i in range(self.n)]
        for t in threads: t.start()
        for t in threads: t.join()
        self.finished.emit()


class MutexMonitorSimulation(BaseSimulation):
    def __init__(self, parent=None):
        super().__init__("MUTEX / MONITOR",
                         "Mutual exclusion · Critical section · Lock ownership",
                         ACCENT_PURPLE, parent)
        self._worker = None
        self._thread_blocks = []

    def _setup_visualization(self, parent):
        layout = QVBoxLayout(parent)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(16)

        # Critical section display
        cs_lbl = QLabel("◈  CRITICAL SECTION")
        cs_lbl.setStyleSheet(f"color:{ACCENT_PURPLE};font-size:12px;font-weight:bold;font-family:'Consolas',monospace;")
        layout.addWidget(cs_lbl)

        self._cs_widget = CriticalSectionWidget()
        self._cs_widget.setFixedHeight(100)
        layout.addWidget(self._cs_widget)

        # Threads
        t_lbl = QLabel("◈  THREADS")
        t_lbl.setStyleSheet(f"color:{TEXT_SECONDARY};font-size:11px;font-weight:bold;font-family:'Consolas',monospace;")
        layout.addWidget(t_lbl)

        self._threads_row = QWidget()
        self._threads_row_layout = QHBoxLayout(self._threads_row)
        self._threads_row_layout.setContentsMargins(0, 0, 0, 0)
        self._threads_row_layout.setSpacing(14)
        self._threads_row_layout.addStretch()
        layout.addWidget(self._threads_row)
        layout.addStretch()

        self._rebuild_threads(4)

    def _rebuild_threads(self, n):
        for b in self._thread_blocks:
            b.setParent(None); b.deleteLater()
        self._thread_blocks.clear()
        while self._threads_row_layout.count() > 1:
            item = self._threads_row_layout.takeAt(0)
            if item.widget(): item.widget().deleteLater()
        for i in range(n):
            b = ThreadBlock(i, THREAD_COLORS[i % len(THREAD_COLORS)])
            self._thread_blocks.append(b)
            self._threads_row_layout.insertWidget(i, b)

    def _setup_controls(self, card, layout):
        lbl = QLabel("Threads:")
        lbl.setStyleSheet(f"color:{TEXT_SECONDARY};font-size:12px;font-family:'Consolas',monospace;")
        layout.addWidget(lbl)
        self._n_spin = QSpinBox()
        self._n_spin.setRange(2, 6)
        self._n_spin.setValue(4)
        layout.addWidget(self._n_spin)

        self._mutex_cb = QCheckBox("  Enable Mutex/Monitor")
        self._mutex_cb.setChecked(True)
        self._mutex_cb.setStyleSheet(f"color:{TEXT_PRIMARY};font-size:13px;font-family:'Consolas',monospace;")
        layout.addWidget(self._mutex_cb)

        lbl2 = QLabel("Speed:")
        lbl2.setStyleSheet(f"color:{TEXT_SECONDARY};font-size:12px;font-family:'Consolas',monospace;")
        layout.addWidget(lbl2)
        self._speed_slider = QSlider(Qt.Orientation.Horizontal)
        self._speed_slider.setRange(1, 5)
        self._speed_slider.setValue(2)
        layout.addWidget(self._speed_slider)

    def _setup_stats(self, card, layout):
        self._stat_cs = StatBadge("IN CS", "none", ACCENT_PURPLE)
        self._stat_mutex = StatBadge("MUTEX", "FREE", ACCENT_GREEN)
        layout.addWidget(self._stat_cs)
        layout.addWidget(self._stat_mutex)

    def start(self):
        if self._running: return
        n = self._n_spin.value()
        self._rebuild_threads(n)
        self._set_running(True)

        self._worker = MutexMonitorWorker(n, self._speed_slider.value(), self._mutex_cb.isChecked())
        self._worker.update_signal.connect(self._on_update)
        self._worker.log_signal.connect(self.event_log.add_event)
        self._worker.finished.connect(lambda: self._set_running(False))
        self._worker.start()

    def _on_update(self, states, cs_thread, mutex_locked):
        for i, state in enumerate(states):
            if i < len(self._thread_blocks):
                self._thread_blocks[i].set_state(state)
        self._cs_widget.set_state(cs_thread, mutex_locked)
        self._stat_cs.set_value(f"T-{cs_thread}" if cs_thread >= 0 else "none")
        self._stat_mutex.set_value("LOCKED" if mutex_locked else "FREE")
        if mutex_locked:
            self._stat_mutex.set_value("LOCKED")
            self._stat_mutex._color = ACCENT_RED
        else:
            self._stat_mutex.set_value("FREE")
            self._stat_mutex._color = ACCENT_GREEN
        self._stat_mutex.set_value("LOCKED" if mutex_locked else "FREE")

    def stop(self):
        if self._worker: self._worker.stop()
        self._set_running(False)

    def reset(self):
        self.stop()
        if self._worker: self._worker.wait(500)
        n = self._n_spin.value()
        self._rebuild_threads(n)
        self._cs_widget.set_state(-1, False)
        self.event_log.clear_log()
        self.log("Reset", "SYSTEM")


class CriticalSectionWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._cs_thread = -1
        self._locked = False
        self._flash = 0.0
        self._timer = QTimer()
        self._timer.timeout.connect(self._tick)
        self._timer.start(50)

    def set_state(self, cs_thread, locked):
        old = self._cs_thread
        self._cs_thread = cs_thread
        self._locked = locked
        if cs_thread != old:
            self._flash = 1.0
        self.update()

    def _tick(self):
        if self._flash > 0:
            self._flash = max(0, self._flash - 0.08)
            self.update()

    def paintEvent(self, event):
        import math
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        w, h = self.width(), self.height()

        bw, bh = 300, 70
        bx, by = (w - bw) // 2, (h - bh) // 2

        if self._locked:
            c = ACCENT_PURPLE
        else:
            c = QColor(BORDER_COLOR).name()

        r = int(c[1:3], 16) if c.startswith('#') else 100
        g = int(c[3:5], 16) if c.startswith('#') else 100
        b = int(c[5:7], 16) if c.startswith('#') else 100

        flash_a = int(self._flash * 60)
        bg = QColor(r, g, b, 30 + flash_a)
        p.setBrush(QBrush(bg))
        p.setPen(QPen(QColor(r, g, b, 180), 2))

        if self._locked:
            dash_pen = QPen(QColor(r, g, b, 180), 2)
            p.setPen(dash_pen)

        p.drawRoundedRect(bx, by, bw, bh, 10, 10)

        # Lock icon
        lock_x, lock_y = bx + 14, by + 20
        lock_c = QColor(ACCENT_GREEN) if not self._locked else QColor(ACCENT_RED)
        p.setBrush(QBrush(lock_c))
        p.setPen(QPen(lock_c, 2))
        p.drawRoundedRect(lock_x, lock_y + 8, 18, 14, 3, 3)
        p.setBrush(Qt.BrushStyle.NoBrush)
        if self._locked:
            p.drawArc(lock_x + 2, lock_y, 14, 14, 0, 180 * 16)

        p.setPen(QPen(QColor(TEXT_PRIMARY)))
        p.setFont(QFont("Consolas", 11, QFont.Weight.Bold))
        status = f"CRITICAL SECTION  [{'LOCKED — T-' + str(self._cs_thread) if self._cs_thread >= 0 else 'FREE'}]"
        p.drawText(QRect(bx + 40, by, bw - 50, bh), Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft, status)

        p.end()


# ─────────────────────────────────────────────────────────────────────────────
#  8. PROCESSES & PARALLELISM
# ─────────────────────────────────────────────────────────────────────────────

class ProcessSimulation(BaseSimulation):
    def __init__(self, parent=None):
        super().__init__("PROCESSES & PARALLELISM",
                         "Independent processes · Multi-core · Memory isolation",
                         ACCENT_BLUE, parent)
        self._timers = []
        self._process_widgets = []
        self._ticks = [0, 0]

    def _setup_visualization(self, parent):
        layout = QVBoxLayout(parent)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(16)

        top_lbl = QLabel("◈  MULTI-CORE EXECUTION  (True Parallelism)")
        top_lbl.setStyleSheet(f"color:{ACCENT_BLUE};font-size:12px;font-weight:bold;font-family:'Consolas',monospace;")
        layout.addWidget(top_lbl)

        cores_row = QHBoxLayout()
        self._core_widgets = []
        self._process_widgets = []
        for i in range(2):
            col = QVBoxLayout()
            core_lbl = QLabel(f"◈  CPU CORE {i}")
            core_lbl.setStyleSheet(f"color:{THREAD_COLORS[i]};font-size:11px;font-weight:bold;font-family:'Consolas',monospace;")
            col.addWidget(core_lbl)

            cw = CoreWidget(i, THREAD_COLORS[i])
            self._core_widgets.append(cw)
            col.addWidget(cw)

            proc_lbl = QLabel(f"Process P-{i}")
            proc_lbl.setStyleSheet(f"color:{THREAD_COLORS[i]};font-size:11px;font-family:'Consolas',monospace;")
            col.addWidget(proc_lbl)
            col.addStretch()
            cores_row.addLayout(col)

        layout.addLayout(cores_row)

        mem_lbl = QLabel("◈  MEMORY ISOLATION  (Each process has its own address space)")
        mem_lbl.setStyleSheet(f"color:{ACCENT_YELLOW};font-size:11px;font-weight:bold;font-family:'Consolas',monospace;")
        layout.addWidget(mem_lbl)

        self._mem_widget = MemoryIsolationWidget()
        self._mem_widget.setFixedHeight(80)
        layout.addWidget(self._mem_widget)
        layout.addStretch()

    def _setup_controls(self, card, layout):
        lbl = QLabel("Speed:")
        lbl.setStyleSheet(f"color:{TEXT_SECONDARY};font-size:12px;font-family:'Consolas',monospace;")
        layout.addWidget(lbl)
        self._speed_slider = QSlider(Qt.Orientation.Horizontal)
        self._speed_slider.setRange(1, 5)
        self._speed_slider.setValue(2)
        layout.addWidget(self._speed_slider)

        note = QLabel("ⓘ  Both processes run\nsimultaneously on\ndifferent CPU cores.\n\nEach has its OWN\nmemory space.")
        note.setStyleSheet(f"color:{TEXT_SECONDARY};font-size:11px;font-family:'Consolas',monospace;padding:6px;border:1px solid {BORDER_COLOR};border-radius:6px;")
        layout.addWidget(note)

    def _setup_stats(self, card, layout):
        self._stat_p0 = StatBadge("P-0 TICKS", "0", THREAD_COLORS[0])
        self._stat_p1 = StatBadge("P-1 TICKS", "0", THREAD_COLORS[1])
        layout.addWidget(self._stat_p0)
        layout.addWidget(self._stat_p1)

    def start(self):
        if self._running: return
        self._set_running(True)
        self._ticks = [0, 0]
        speed = self._speed_slider.value()

        for i, cw in enumerate(self._core_widgets):
            cw.set_active(True)

        for i in range(2):
            timer = QTimer()
            delay = int(200 / speed)
            timer.timeout.connect(lambda idx=i: self._tick_process(idx))
            timer.start(delay + i * 30)  # slight offset to show true parallelism
            self._timers.append(timer)

        self.log("Process P-0 started on Core 0", "SUCCESS")
        self.log("Process P-1 started on Core 1", "SUCCESS")
        self.log("Both running in PARALLEL (simultaneously)", "INFO")

    def _tick_process(self, i):
        if not self._running: return
        self._ticks[i] += 1
        if i == 0:
            self._stat_p0.set_value(self._ticks[i])
        else:
            self._stat_p1.set_value(self._ticks[i])
        self._core_widgets[i].add_tick()
        self._mem_widget.pulse(i)
        if self._ticks[i] % 10 == 0:
            self.log(f"P-{i} executing on Core {i} (tick {self._ticks[i]})", "INFO")

    def stop(self):
        for t in self._timers: t.stop()
        self._timers.clear()
        for cw in self._core_widgets: cw.set_active(False)
        self._set_running(False)

    def reset(self):
        self.stop()
        self._ticks = [0, 0]
        self._stat_p0.set_value(0)
        self._stat_p1.set_value(0)
        for cw in self._core_widgets: cw.reset()
        self.event_log.clear_log()
        self.log("Reset", "SYSTEM")


class CoreWidget(QWidget):
    def __init__(self, core_id, color, parent=None):
        super().__init__(parent)
        self._id = core_id
        self._color = color
        self._active = False
        self._activity = deque(maxlen=30)
        self._pulse = 0.0
        self.setFixedSize(200, 120)
        self._timer = QTimer()
        self._timer.timeout.connect(self._tick)
        self._timer.start(50)

    def set_active(self, a):
        self._active = a
        self.update()

    def add_tick(self):
        self._activity.append(random.randint(40, 100))
        self._pulse = 1.0
        self.update()

    def reset(self):
        self._activity.clear()
        self._active = False
        self._pulse = 0.0
        self.update()

    def _tick(self):
        import math
        if self._active:
            self._pulse = max(0, self._pulse - 0.05)
            self.update()

    def paintEvent(self, event):
        import math
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        w, h = self.width(), self.height()

        c = self._color
        r = int(c[1:3], 16); g = int(c[3:5], 16); b = int(c[5:7], 16)

        # Background
        bg_a = int(30 + self._pulse * 30)
        p.setBrush(QBrush(QColor(r, g, b, bg_a)))
        p.setPen(QPen(QColor(r, g, b, 150), 1.5))
        p.drawRoundedRect(2, 2, w-4, h-4, 8, 8)

        # Title
        p.setPen(QPen(QColor(c)))
        p.setFont(QFont("Consolas", 9, QFont.Weight.Bold))
        status = "RUNNING" if self._active else "IDLE"
        p.drawText(QRect(8, 6, w-16, 18), Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter,
                   f"Core {self._id}  [{status}]")

        # Activity graph
        if self._activity:
            graph_x, graph_y = 8, 30
            graph_w, graph_h = w - 16, h - 45

            p.setBrush(QBrush(QColor(0, 0, 0, 40)))
            p.setPen(Qt.PenStyle.NoPen)
            p.drawRoundedRect(graph_x, graph_y, graph_w, graph_h, 4, 4)

            bar_w = max(2, graph_w // len(self._activity))
            for j, val in enumerate(self._activity):
                bh = int(val / 100 * graph_h)
                bx = graph_x + j * bar_w
                by = graph_y + graph_h - bh
                alpha = int(100 + (j / len(self._activity)) * 155)
                p.setBrush(QBrush(QColor(r, g, b, alpha)))
                p.setPen(Qt.PenStyle.NoPen)
                p.drawRect(bx, by, bar_w - 1, bh)

        # Usage label
        if self._activity:
            avg = sum(self._activity) / len(self._activity)
            p.setPen(QPen(QColor(TEXT_SECONDARY)))
            p.setFont(QFont("Consolas", 8))
            p.drawText(QRect(8, h - 18, w - 16, 16), Qt.AlignmentFlag.AlignCenter, f"CPU: {avg:.0f}%")

        p.end()


class MemoryIsolationWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._pulses = [0.0, 0.0]
        self._timer = QTimer()
        self._timer.timeout.connect(self._tick)
        self._timer.start(50)

    def pulse(self, i):
        self._pulses[i] = 1.0

    def _tick(self):
        for i in range(2):
            self._pulses[i] = max(0, self._pulses[i] - 0.1)
        self.update()

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        w, h = self.width(), self.height()

        for i in range(2):
            bw = (w - 40) // 2
            x = 10 + i * (bw + 20)
            c = THREAD_COLORS[i]
            r = int(c[1:3], 16); g = int(c[3:5], 16); b = int(c[5:7], 16)
            pulse_a = int(self._pulses[i] * 60)
            p.setBrush(QBrush(QColor(r, g, b, 20 + pulse_a)))
            p.setPen(QPen(QColor(r, g, b, 150), 1.5))
            p.drawRoundedRect(x, 5, bw, h - 10, 8, 8)

            p.setPen(QPen(QColor(c)))
            p.setFont(QFont("Consolas", 9, QFont.Weight.Bold))
            p.drawText(QRect(x, 5, bw, h - 10), Qt.AlignmentFlag.AlignCenter, f"P-{i} Memory\n(Isolated)")

        # Barrier
        cx = w // 2
        p.setPen(QPen(QColor(ACCENT_RED), 2, Qt.PenStyle.DashLine))
        p.drawLine(cx, 5, cx, h - 5)
        p.setPen(QPen(QColor(ACCENT_RED)))
        p.setFont(QFont("Consolas", 8))
        p.drawText(QRect(cx - 20, h // 2 - 8, 40, 16), Qt.AlignmentFlag.AlignCenter, "wall")

        p.end()


# ─────────────────────────────────────────────────────────────────────────────
#  MAIN WINDOW
# ─────────────────────────────────────────────────────────────────────────────

SIMULATIONS = [
    ("THREADS", "Threads & Concurrency",  "◎", ACCENT_CYAN),
    ("PROCESSES", "Processes & Parallelism", "⬡", ACCENT_BLUE),
    ("RACE", "Race Condition",  "⚡", ACCENT_RED),
    ("MUTEX", "Mutex / Monitor",  "⚿", ACCENT_PURPLE),
    ("SEMAPHORE", "Semaphore", "◉", ACCENT_PURPLE),
    ("PRODCONS", "Producer — Consumer", "⇄", ACCENT_GREEN),
    ("DEADLOCK", "Deadlock", "⛔", ACCENT_RED),
    ("STARVATION", "Starvation",  "☁", ACCENT_ORANGE),
]


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("OS Concepts Visual Simulator — Professional Edition")
        self.setMinimumSize(1280, 800)
        self.resize(1440, 900)
        self._sim_widgets = {}
        self._nav_buttons = {}
        self._active_sim = None
        self._build_ui()
        self._switch_sim("THREADS")

    def _build_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        root = QHBoxLayout(central)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        # ── LEFT SIDEBAR ──
        sidebar = QWidget()
        sidebar.setFixedWidth(240)
        sidebar.setStyleSheet(f"""
            background: {BG_PANEL};
            border-right: 1px solid {BORDER_COLOR};
        """)
        sidebar_layout = QVBoxLayout(sidebar)
        sidebar_layout.setContentsMargins(0, 0, 0, 0)
        sidebar_layout.setSpacing(0)

        # Logo area
        logo = QWidget()
        logo.setFixedHeight(72)
        logo.setStyleSheet(f"""
            background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                stop:0 rgba(0,102,255,0.25), stop:1 rgba(0,212,255,0.1));
            border-bottom: 1px solid {BORDER_COLOR};
        """)
        logo_layout = QVBoxLayout(logo)
        logo_layout.setContentsMargins(16, 12, 16, 12)
        title1 = QLabel("OS SIMULATOR")
        title1.setStyleSheet(f"color:{ACCENT_CYAN};font-size:15px;font-weight:bold;letter-spacing:2px;font-family:'Consolas',monospace;")
        title2 = QLabel("Visual Learning Platform")
        title2.setStyleSheet(f"color:{TEXT_SECONDARY};font-size:10px;letter-spacing:1px;font-family:'Consolas',monospace;")
        logo_layout.addWidget(title1)
        logo_layout.addWidget(title2)
        sidebar_layout.addWidget(logo)

        # Nav sections
        SectionLabel("SIMULATIONS").setParent(sidebar)
        sec = SectionLabel("SIMULATIONS")
        sidebar_layout.addWidget(sec)

        for key, name, icon, color in SIMULATIONS:
            btn = NavButton(icon, name, color)
            btn.clicked.connect(lambda checked, k=key: self._switch_sim(k))
            self._nav_buttons[key] = btn
            sidebar_layout.addWidget(btn)

        sidebar_layout.addSpacing(16)

        # Status bar at bottom
        status_area = QWidget()
        status_area.setStyleSheet(f"border-top: 1px solid {BORDER_COLOR};")
        status_layout = QVBoxLayout(status_area)
        status_layout.setContentsMargins(14, 10, 14, 10)

        ver_lbl = QLabel("v2.0  •  Python 3 + PyQt6")
        ver_lbl.setStyleSheet(f"color:{TEXT_DIM};font-size:10px;font-family:'Consolas',monospace;")
        status_layout.addWidget(ver_lbl)

        sidebar_layout.addStretch()
        sidebar_layout.addWidget(status_area)
        root.addWidget(sidebar)

        # ── MAIN CONTENT ──
        self._stack = QStackedWidget()
        self._stack.setStyleSheet(f"background:{BG_DEEP};")

        # Create all simulation widgets
        sim_map = {
            "THREADS": ThreadConcurrencySimulation,
            "PROCESSES": ProcessSimulation,
            "RACE": RaceConditionSimulation,
            "MUTEX": MutexMonitorSimulation,
            "SEMAPHORE": SemaphoreSimulation,
            "PRODCONS": ProducerConsumerSimulation,
            "DEADLOCK": DeadlockSimulation,
            "STARVATION": StarvationSimulation,
        }

        for key, cls in sim_map.items():
            widget = cls()
            self._sim_widgets[key] = widget
            self._stack.addWidget(widget)

        root.addWidget(self._stack, 1)

    def _switch_sim(self, key):
        if self._active_sim == key:
            return
        self._active_sim = key

        for k, btn in self._nav_buttons.items():
            btn.set_active(k == key)

        if key in self._sim_widgets:
            self._stack.setCurrentWidget(self._sim_widgets[key])


# ─────────────────────────────────────────────────────────────────────────────
#  ENTRY POINT
# ─────────────────────────────────────────────────────────────────────────────

def main():
    app = QApplication(sys.argv)
    app.setStyleSheet(STYLESHEET)

    # Dark palette
    palette = QPalette()
    palette.setColor(QPalette.ColorRole.Window, QColor(BG_DEEP))
    palette.setColor(QPalette.ColorRole.WindowText, QColor(TEXT_PRIMARY))
    palette.setColor(QPalette.ColorRole.Base, QColor(BG_CARD))
    palette.setColor(QPalette.ColorRole.AlternateBase, QColor(BG_ELEVATED))
    palette.setColor(QPalette.ColorRole.Text, QColor(TEXT_PRIMARY))
    palette.setColor(QPalette.ColorRole.Button, QColor(BG_ELEVATED))
    palette.setColor(QPalette.ColorRole.ButtonText, QColor(TEXT_PRIMARY))
    palette.setColor(QPalette.ColorRole.Highlight, QColor(ACCENT_BLUE))
    palette.setColor(QPalette.ColorRole.HighlightedText, QColor(TEXT_PRIMARY))
    app.setPalette(palette)

    window = MainWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
