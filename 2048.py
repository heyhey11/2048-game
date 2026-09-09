import random
import streamlit as st
import streamlit.components.v1 as components

SIZE = 4

TILE_COLORS = {
    2: "#E0F2FE",
    4: "#BAE6FD",
    8: "#7DD3FC",
    16: "#38BDF8",
    32: "#0EA5E9",
    64: "#0284C7",
    128: "#0369A1",
    256: "#075985",
    512: "#0C4A6E",
    1024: "#F58C4C",
    2048: "#F5C242",
    4096: "#FFE066",
}

TILE_TEXT_COLORS = {
    2: "#0369A1",
    4: "#0369A1",
    8: "#0C4A6E",
    16: "#FFFFFF",
    32: "#FFFFFF",
    64: "#FFFFFF",
    128: "#FFFFFF",
    256: "#FFFFFF",
    512: "#FFFFFF",
    1024: "#FFFFFF",
    2048: "#1A1206",
    4096: "#1A1206",
}


def empty_board():
  return [[0] * SIZE for _ in range(SIZE)]


def clone_board(board):
  return [row[:] for row in board]


def get_empty_cells(board):
  cells = []
  for r in range(SIZE):
    for c in range(SIZE):
      if board[r][c] == 0:
        cells.append((r, c))
  return cells


def add_random_tile(board):
  empty = get_empty_cells(board)
  if not empty:
    return board
  r, c = random.choice(empty)
  next_board = clone_board(board)
  next_board[r][c] = 2 if random.random() < 0.9 else 4
  return next_board


def slide_row_left(row):
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


def transpose(board):
  return [[board[r][c] for r in range(SIZE)] for c in range(SIZE)]


def reverse_rows(board):
  return [row[::-1] for row in board]


def move(board, direction):
  working = clone_board(board)
  transformed = False
  reversed_flag = False

  if direction in ("up", "down"):
    working = transpose(working)
    transformed = True
  if direction in ("right", "down"):
    working = reverse_rows(working)
    reversed_flag = True

  total_gained = 0
  any_moved = False
  result = []
  for row in working:
    new_row, gained, moved = slide_row_left(row)
    total_gained += gained
    if moved:
      any_moved = True
    result.append(new_row)

  if reversed_flag:
    result = reverse_rows(result)
  if transformed:
    result = transpose(result)

  return result, total_gained, any_moved


def can_move(board):
  if get_empty_cells(board):
    return True
  for dir_str in ("left", "right", "up", "down"):
    _, _, moved = move(board, dir_str)
    if moved:
      return True
  return False


def has_won(board):
  return any(any(v >= 2048 for v in row) for row in board)


# Streamlit 세션 상태 초기화
if "board" not in st.session_state:
  st.session_state.board = empty_board()
if "score" not in st.session_state:
  st.session_state.score = 0
if "best" not in st.session_state:
  st.session_state.best = 0
if "status" not in st.session_state:
  st.session_state.status = "ready"
if "continued" not in st.session_state:
  st.session_state.continued = False


def start_game():
  b = empty_board()
  b = add_random_tile(b)
  b = add_random_tile(b)
  st.session_state.board = b
  st.session_state.score = 0
  st.session_state.status = "playing"
  st.session_state.continued = False


def handle_action(direction):
  if st.session_state.status != "playing":
    return
  new_board, gained, moved = move(st.session_state.board, direction)
  if not moved:
    return

  with_tile = add_random_tile(new_board)
  st.session_state.board = with_tile
  st.session_state.score += gained
  if st.session_state.score > st.session_state.best:
    st.session_state.best = st.session_state.score

  if not st.session_state.continued and has_won(with_tile):
    st.session_state.status = "won"
  elif not can_move(with_tile):
    st.session_state.status = "over"


# URL 쿼리 파라미터 기반 키 입력 처리
if "move" in st.query_params and st.session_state.status == "playing":
  direction = st.query_params["move"]
  st.query_params.clear()
  handle_action(direction)

# 레이아웃 스타일 설정 (800px)
st.markdown(
    """
    <style>
    .block-container {
        max-width: 800px !important;
        padding-top: 2rem;
        padding-bottom: 2rem;
    }
    .stButton>button {
        width: 100%;
        border-radius: 8px;
        font-weight: bold;
        font-size: 1rem;
        padding: 0.5rem 1rem;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# 키보드 이벤트 리스너 주입
if st.session_state.status == "playing":
  components.html(
      """
    <script>
    const parentWin = window.parent;
    if (!parentWin._keyListenerInitialized) {
        parentWin._keyListenerInitialized = true;
        parentWin.addEventListener('keydown', function(e) {
            if(["ArrowUp", "ArrowDown", "ArrowLeft", "ArrowRight", " ", "w", "a", "s", "d", "W", "A", "S", "D"].includes(e.key)) {
                e.preventDefault();
                let dir = "";
                const key = e.key.toLowerCase();
                if (e.key === "ArrowLeft" || key === "a") dir = "left";
                else if (e.key === "ArrowRight" || key === "d") dir = "right";
                else if (e.key === "ArrowUp" || key === "w") dir = "up";
                else if (e.key === "ArrowDown" || key === "s") dir = "down";

                if (dir) {
                    const url = new URL(parentWin.location);
                    url.searchParams.set('move', dir);
                    parentWin.location.href = url.toString();
                }
            }
        });
    }
    </script>
    """,
      height=0,
  )

# 헤더 영역
col_title, col_score1, col_score2 = st.columns([3, 1, 1])
with col_title:
  st.markdown(
      "<h1 style='margin:0; padding:0; font-size: 2.5rem;'>2048</h1>",
      unsafe_allow_html=True,
  )
  st.caption("키보드 방향키(←, →, ↑, ↓) 또는 WASD로 조작하세요.")
with col_score1:
  st.metric("점수", st.session_state.score)
with col_score2:
  st.metric("최고", st.session_state.best)

st.write("")

# 게임판 렌더링
for r in range(SIZE):
  cols = st.columns(SIZE)
  for c in range(SIZE):
    val = st.session_state.board[r][c]
    with cols[c]:
      if val == 0:
        bg = "#E5E7EB"
        txt = "transparent"
        display_val = ""
      else:
        bg = TILE_COLORS.get(val, "#FFE066")
        txt = TILE_TEXT_COLORS.get(val, "#1A1206")
        display_val = str(val)

      font_size = "24px" if val >= 1000 else ("28px" if val >= 100 else "32px")

      st.markdown(
          f"""
            <div style="
                background-color: {bg};
                color: {txt};
                aspect-ratio: 1 / 1;
                display: flex;
                align-items: center;
                justify-content: center;
                border-radius: 12px;
                font-size: {font_size};
                font-weight: 800;
                margin-bottom: 10px;
                box-shadow: 0 2px 4px rgba(0,0,0,0.05);
            ">{display_val}</div>
            """,
          unsafe_allow_html=True,
      )

st.write("")

# 상태 제어 및 버튼 (보조용)
if st.session_state.status == "ready":
  st.warning("게임을 시작하려면 아래 버튼을 누르세요.")
  if st.button("게임 시작", type="primary"):
    start_game()
    st.rerun()

elif st.session_state.status == "playing":
  b1, b2, b3 = st.columns(3)
  with b2:
    if st.button("⬆️ 위로 (W)"):
      handle_action("up")
      st.rerun()

  b4, b5, b6 = st.columns(3)
  with b4:
    if st.button("⬅️ 왼쪽 (A)"):
      handle_action("left")
      st.rerun()
  with b5:
    if st.button("⬇️ 아래로 (S)"):
      handle_action("down")
      st.rerun()
  with b6:
    if st.button("➡️ 오른쪽 (D)"):
      handle_action("right")
      st.rerun()

elif st.session_state.status == "won":
  st.success("🎉 2048 달성!")
  col_w1, col_w2 = st.columns(2)
  with col_w1:
    if st.button("계속하기"):
      st.session_state.continued = True
      st.session_state.status = "playing"
      st.rerun()
  with col_w2:
    if st.button("새 게임"):
      start_game()
      st.rerun()

elif st.session_state.status == "over":
  st.error("💀 게임 오버!")
  if st.button("다시 시작", type="primary"):
    start_game()
    st.rerun()

if st.session_state.status != "ready":
  st.write("")
  if st.button("초기화 (새 게임)"):
    start_game()
    st.rerun()
