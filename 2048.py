import random
import sys
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor, QFont, QKeyEvent
from PyQt6.QtWidgets import (
    QApplication,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QPushButton,
    QSizePolicy,
    QStackedWidget,
    QVBoxLayout,
    QWidget,
)

SIZE = 4

TILE_STYLES = {
    2: {"bg": "#E0F2FE", "text": "#0369A1"},
    4: {"bg": "#BAE6FD", "text": "#0369A1"},
    8: {"bg": "#7DD3FC", "text": "#0C4A6E"},
    16: {"bg": "#38BDF8", "text": "#FFFFFF"},
    32: {"bg": "#0EA5E9", "text": "#FFFFFF"},
    64: {"bg": "#0284C7", "text": "#FFFFFF"},
    128: {"bg": "#0369A1", "text": "#FFFFFF"},
    256: {"bg": "#075985", "text": "#FFFFFF"},
    512: {"bg": "#0C4A6E", "text": "#FFFFFF"},
    1024: {"bg": "#F58C4C", "text": "#FFFFFF"},
    2048: {"bg": "#F5C242", "text": "#1A1206"},
    4096: {"bg": "#FFE066", "text": "#1A1206"},
}


class ScoreBox(QWidget):

    def __init__(self, label_text):
        super().__init__()
        layout = QVBoxLayout()
        layout.setContentsMargins(10, 6, 10, 6)
        layout.setSpacing(2)

        self.title_label = QLabel(label_text)
        self.title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.title_label.setFont(FontFam.get(11))
        self.title_label.setStyleSheet("color: #4B5563;")

        self.value_label = QLabel("0")
        self.value_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.value_label.setFont(FontFam.get(16, bold=True))
        self.value_label.setStyleSheet("color: #1F2937;")

        layout.addWidget(self.title_label)
        layout.addWidget(self.value_label)
        self.setLayout(layout)

        self.setStyleSheet(
            "background-color: #F3F4F6; border: 1px solid #E5E7EB; border-radius: 10px;"
        )
        self.setMinimumWidth(72)

    def set_value(self, val):
        self.value_label.setText(str(val))


class FontFam:

    @staticmethod
    def get(size, bold=False):
        font = QFont("Segoe UI", size)
        if bold:
            font.setWeight(QFont.Weight.Bold)
        return font


class Game2048Window(QMainWindow):

    def __init__(self):
        super().__init__()
        self.board = self.empty_board()
        self.score = 0
        self.best = 0
        self.status = "ready"  # ready, playing, won, over
        self.continued = False

        self.init_ui()

    def empty_board(self):
        return [[0] * SIZE for _ in range(SIZE)]

    def clone_board(self, board):
        return [row[:] for row in board]

    def get_empty_cells(self, board):
        cells = []
        for r in range(SIZE):
            for c in range(SIZE):
                if board[r][c] == 0:
                    cells.append((r, c))
        return cells

    def add_random_tile(self, board):
        empty = self.get_empty_cells(board)
        if not empty:
            return board
        r, c = random.choice(empty)
        next_board = self.clone_board(board)
        next_board[r][c] = 2 if random.random() < 0.9 else 4
        return next_board

    def slide_row_left(self, row):
        filtered = [v for v in row if v != 0]
        gained = 0
        merged = []
        i = 0
        while i < len(filtered):
            if i + 1 < len(filtered) and filtered[i] == filtered[i + 1]:
                val = filtered[i] * 2
                merged.append(val)
                gained += val
                i += 2
            else:
                merged.append(filtered[i])
                i += 1
        while len(merged) < SIZE:
            merged.append(0)
        moved = merged != row
        return merged, gained, moved

    def transpose(self, board):
        return [[board[r][c] for r in range(SIZE)] for c in range(SIZE)]

    def reverse_rows(self, board):
        return [row[::-1] for row in board]

    def move(self, board, direction):
        working = self.clone_board(board)
        transformed = False
        reversed_flag = False

        if direction in ("up", "down"):
            working = self.transpose(working)
            transformed = True
        if direction in ("right", "down"):
            working = self.reverse_rows(working)
            reversed_flag = True

        total_gained = 0
        any_moved = False
        result = []
        for row in working:
            new_row, gained, moved = self.slide_row_left(row)
            total_gained += gained
            if moved:
                any_moved = True
            result.append(new_row)

        if reversed_flag:
            result = self.reverse_rows(result)
        if transformed:
            result = self.transpose(result)

        return result, total_gained, any_moved

    def can_move(self, board):
        if self.get_empty_cells(board):
            return True
        for dir_str in ("left", "right", "up", "down"):
            _, _, moved = self.move(board, dir_str)
            if moved:
                return True
        return False

    def has_won(self, board):
        return any(any(v >= 2048 for v in row) for row in board)

    def init_ui(self):
        self.setWindowTitle("2048")
        self.setFixedSize(420, 620)
        self.setStyleSheet("background-color: #FFFFFF;")

        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(16, 32, 16, 32)
        central_widget.setLayout(main_layout)

        # 상단 헤더 영역
        header_layout = QHBoxLayout()

        title_layout = QVBoxLayout()
        title_layout.setSpacing(6)
        title_label = QLabel("2048")
        title_label.setFont(FontFam.get(32, bold=True))
        title_label.setStyleSheet("color: #1F2937;")

        subtitle_label = QLabel("같은 숫자를 합쳐 2048을 만드세요")
        subtitle_label.setFont(FontFam.get(13))
        subtitle_label.setStyleSheet("color: #4B5563;")

        title_layout.addWidget(title_label)
        title_layout.addWidget(subtitle_label)
        header_layout.addLayout(title_layout)

        score_layout = QHBoxLayout()
        score_layout.setSpacing(8)
        self.score_box = ScoreBox("점수")
        self.best_box = ScoreBox("최고")
        score_layout.addWidget(self.score_box)
        score_layout.addWidget(self.best_box)
        header_layout.addLayout(score_layout)

        main_layout.addLayout(header_layout)
        main_layout.addSpacing(20)

        # 게임 보드 및 오버레이 스택
        self.board_container = QWidget()
        self.board_container.setStyleSheet(
            "background-color: #F3F4F6; border: 1px solid #E5E7EB; border-radius: 16px;"
        )
        board_outer_layout = QVBoxLayout()
        board_outer_layout.setContentsMargins(10, 10, 10, 10)

        self.grid_widget = QWidget()
        self.grid_layout = QGridLayout()
        self.grid_layout.setSpacing(10)
        self.grid_widget.setLayout(self.grid_layout)

        self.tile_labels = []
        for r in range(SIZE):
            row_labels = []
            for c in range(SIZE):
                lbl = QLabel("")
                lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
                lbl.setSizePolicy(
                    QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding
                )
                self.grid_layout.addWidget(lbl, r, c)
                row_labels.append(lbl)
            self.tile_labels.append(row_labels)

        board_outer_layout.addWidget(self.grid_widget)
        self.board_container.setLayout(board_outer_layout)

        # 오버레이 페이지 (Ready, Win/Over)
        self.stacked_widget = QStackedWidget(self.board_container)
        self.stacked_widget.setGeometry(10, 10, 378, 378)
        self.stacked_widget.setStyleSheet(
            "background: transparent;"
        )  # 투명 처리용

        # 1. Ready 오버레이
        self.ready_page = QWidget()
        ready_layout = QVBoxLayout()
        ready_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        ready_layout.setSpacing(14)
        ready_bg = QLabel(self.ready_page)
        ready_bg.setStyleSheet(
            "background-color: rgba(255, 255, 255, 0.9); border-radius: 16px;"
        )
        ready_bg.setGeometry(0, 0, 378, 378)

        r_title = QLabel("준비되셨나요?", self.ready_page)
        r_title.setFont(FontFam.get(22, bold=True))
        r_title.setStyleSheet("color: #1F2937; background: transparent;")
        r_title.setAlignment(Qt.AlignmentFlag.AlignCenter)

        r_btn = QPushButton("게임 시작", self.ready_page)
        r_btn.setFont(FontFam.get(13, bold=True))
        r_btn.setStyleSheet(
            "background-color: #0284C7; color: #FFFFFF; border: none; border-radius: 8px; padding: 9px 16px;"
        )
        r_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        r_btn.clicked.connect(self.start_game)

        ready_content_layout = QVBoxLayout()
        ready_content_layout.addWidget(r_title)
        ready_content_layout.addWidget(r_btn, alignment=Qt.AlignmentFlag.AlignCenter)
        self.ready_page.setLayout(ready_content_layout)

        # 2. Game Over / Win 오버레이
        self.end_page = QWidget()
        end_bg = QLabel(self.end_page)
        end_bg.setStyleSheet(
            "background-color: rgba(255, 255, 255, 0.95); border-radius: 16px;"
        )
        end_bg.setGeometry(0, 0, 378, 378)

        self.end_title = QLabel("게임 오버", self.end_page)
        self.end_title.setFont(FontFam.get(20, bold=True))
        self.end_title.setStyleSheet("color: #1F2937; background: transparent;")
        self.end_title.setAlignment(Qt.AlignmentFlag.AlignCenter)

        btn_layout = QHBoxLayout()
        self.btn_continue = QPushButton("계속하기")
        self.btn_continue.setFont(FontFam.get(13, bold=True))
        self.btn_continue.setStyleSheet(
            "background-color: #0284C7; color: #FFFFFF; border: none; border-radius: 8px; padding: 9px 16px;"
        )
        self.btn_continue.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_continue.clicked.connect(self.keep_going)

        self.btn_new = QPushButton("새 게임")
        self.btn_new.setFont(FontFam.get(13, bold=True))
        self.btn_new.setStyleSheet(
            "background-color: #F5C242; color: #1A1206; border: none; border-radius: 8px; padding: 9px 16px;"
        )
        self.btn_new.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_new.clicked.connect(self.restart_game)

        btn_layout.addWidget(self.btn_continue)
        btn_layout.addWidget(self.btn_new)

        end_content_layout = QVBoxLayout()
        end_content_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        end_content_layout.setSpacing(10)
        end_content_layout.addWidget(self.end_title)
        end_content_layout.addLayout(btn_layout)
        self.end_page.setLayout(end_content_layout)

        self.stacked_widget.addWidget(self.ready_page)  # Index 0
        self.stacked_widget.addWidget(self.end_page)  # Index 1

        main_layout.addWidget(self.board_container)
        main_layout.addSpacing(18)

        # 하단 안내 및 리스타트 버튼
        footer_layout = QHBoxLayout()
        guide_label = QLabel("방향키(←, →, ↑, ↓)로 이동")
        guide_label.setFont(FontFam.get(12))
        guide_label.setStyleSheet("color: #4B5563;")

        restart_btn = QPushButton("다시 시작")
        restart_btn.setFont(FontFam.get(13, bold=True))
        restart_btn.setStyleSheet(
            "background-color: transparent; color: #374151; border: 1px solid #D1D5DB; border-radius: 8px; padding: 9px 16px;"
        )
        restart_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        restart_btn.clicked.connect(self.restart_game)

        footer_layout.addWidget(guide_label)
        footer_layout.addWidget(restart_btn)
        main_layout.addLayout(footer_layout)

        self.update_view()

    def resizeEvent(self, event):
        super().resizeEvent(event)
        # 보드 컨테이너 크기에 맞춰 오버레이 크기 동적 조절
        w = self.board_container.width() - 20
        h = self.board_container.height() - 20
        self.stacked_widget.setGeometry(10, 10, w, h)
        for i in range(self.stacked_widget.count()):
            page = self.stacked_widget.widget(i)
            for child in page.findChildren(QLabel):
                if child.styleSheet().startswith("background-color: rgba"):
                    child.setGeometry(0, 0, w, h)

    def start_game(self):
        self.board = self.empty_board()
        self.board = self.add_random_tile(self.board)
        self.board = self.add_random_tile(self.board)
        self.score = 0
        self.status = "playing"
        self.continued = False
        self.stacked_widget.hide()
        self.update_view()

    def restart_game(self):
        self.start_game()

    def keep_going(self):
        self.continued = True
        self.status = "playing"
        self.stacked_widget.hide()
        self.update_view()

    def handle_move(self, direction):
        if self.status != "playing":
            return

        new_board, gained, moved = self.move(self.board, direction)
        if not moved:
            return

        with_tile = self.add_random_tile(new_board)
        self.board = with_tile

        self.score += gained
        if self.score > self.best:
            self.best = self.score

        if not self.continued and self.has_won(with_tile):
            self.status = "won"
            self.show_overlay(won=True)
        elif not self.can_move(with_tile):
            self.status = "over"
            self.show_overlay(won=False)

        self.update_view()

    def show_overlay(self, won):
        if won:
            self.end_title.setText("2048 달성!")
            self.btn_continue.show()
        else:
            self.end_title.setText("게임 오버")
            self.btn_continue.hide()

        self.stacked_widget.setCurrentWidget(self.end_page)
        self.stacked_widget.show()

    def update_view(self):
        self.score_box.set_value(self.score)
        self.best_box.set_value(self.best)

        for r in range(SIZE):
            for c in range(SIZE):
                val = self.board[r][c]
                lbl = self.tile_labels[r][c]
                if val == 0:
                    lbl.setText("")
                    lbl.setStyleSheet(
                        "background-color: #E5E7EB; border-radius: 10px;"
                    )
                else:
                    style = TILE_STYLES.get(
                        val, {"bg": "#FFE066", "text": "#1A1206"}
                    )
                    font_size = 20 if val >= 1000 else (24 if val >= 100 else 28)
                    lbl.setText(str(val))
                    lbl.setFont(FontFam.get(font_size, bold=True))
                    lbl.setStyleSheet(
                        f"background-color: {style['bg']}; color: {style['text']}; border-radius: 10px;"
                    )

    def keyPressEvent(self, event: QKeyEvent):
        key = event.key()
        if key in (Qt.Key.Key_Left, Qt.Key.Key_A):
            self.handle_move("left")
        elif key in (Qt.Key.Key_Right, Qt.Key.Key_D):
            self.handle_move("right")
        elif key in (Qt.Key.Key_Up, Qt.Key.Key_W):
            self.handle_move("up")
        elif key in (Qt.Key.Key_Down, Qt.Key.Key_S):
            self.handle_move("down")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = Game2048Window()
    window.show()
    sys.exit(app.exec())