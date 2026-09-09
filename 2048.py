import streamlit as st
import streamlit.components.v1 as components

# 전체 레이아웃 너비 설정 (800px)
st.markdown(
    """
    <style>
    .block-container {
        max-width: 800px !important;
        padding-top: 1rem;
        padding-bottom: 1rem;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    "<h1 style='margin:0; padding:0; font-size: 2rem;'>2048 게임</h1>",
    unsafe_allow_html=True,
)
st.caption(
    "키보드 방향키(←, →, ↑, ↓) 또는 화면의 버튼을 눌러 게임을 즐기세요."
)

# 완벽한 키보드 조작과 반응형 처리를 위한 HTML/JS 2048 게임 컴포넌트
game_html = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <style>
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background-color: transparent;
            margin: 0;
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
        }
        .game-container {
            width: 450px;
            background: #bbada0;
            border-radius: 10px;
            padding: 15px;
            position: relative;
            box-sizing: border-box;
            box-shadow: 0 4px 10px rgba(0,0,0,0.1);
        }
        .header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 15px;
        }
        .scores {
            display: flex;
            gap: 10px;
        }
        .score-box {
            background: #bbada0;
            background: #8f7a66;
            padding: 8px 15px;
            border-radius: 5px;
            text-align: center;
            color: white;
            font-weight: bold;
            font-size: 14px;
            min-width: 60px;
        }
        .score-box span {
            display: block;
            font-size: 18px;
        }
        .grid {
            display: grid;
            grid-template-columns: repeat(4, 1fr);
            gap: 12px;
            background: #bbada0;
            background: #cdc1b4;
            padding: 12px;
            border-radius: 6px;
        }
        .tile {
            aspect-ratio: 1 / 1;
            background: #eee4da;
            border-radius: 4px;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 28px;
            font-weight: bold;
            color: #776e65;
        }
        /* Tile Colors */
        .tile-2 { background: #eee4da; color: #776e65; }
        .tile-4 { background: #ede0c8; color: #776e65; }
        .tile-8 { background: #f2b179; color: #f9f6f2; }
        .tile-16 { background: #f59563; color: #f9f6f2; }
        .tile-32 { background: #f67c5f; color: #f9f6f2; }
        .tile-64 { background: #f65e3b; color: #f9f6f2; }
        .tile-128 { background: #edcf72; color: #f9f6f2; font-size: 24px; }
        .tile-256 { background: #edcc61; color: #f9f6f2; font-size: 24px; }
        .tile-512 { background: #edc850; color: #f9f6f2; font-size: 24px; }
        .tile-1024 { background: #edc53f; color: #f9f6f2; font-size: 20px; }
        .tile-2048 { background: #edc22e; color: #f9f6f2; font-size: 20px; }

        .controls {
            margin-top: 15px;
            display: flex;
            justify-content: center;
            gap: 10px;
        }
        button {
            background: #8f7a66;
            color: white;
            border: none;
            padding: 10px 20px;
            font-weight: bold;
            border-radius: 5px;
            cursor: pointer;
            font-size: 14px;
        }
        button:hover { background: #9f8a76; }
    </style>
</head>
<body>

<div class="game-container">
    <div class="header">
        <div style="font-size: 28px; font-weight: bold; color: #776e65;">2048</div>
        <div class="scores">
            <div class="score-box">점수 <span id="score">0</span></div>
            <div class="score-box">최고 <span id="best">0</span></div>
        </div>
    </div>
    <div class="grid" id="grid"></div>
    <div class="controls">
        <button onclick="restartGame()">새 게임</button>
    </div>
</div>

<script>
    const SIZE = 4;
    let board = [];
    let score = 0;
    let best = localStorage.getItem('best_2048') || 0;

    function initGame() {
        board = Array(SIZE).fill(0).map(() => Array(SIZE).fill(0));
        score = 0;
        addRandomTile();
        addRandomTile();
        updateView();
    }

    function addRandomTile() {
        let empty = [];
        for(let r=0; r<SIZE; r++) {
            for(let c=0; c<SIZE; c++) {
                if(board[r][c] === 0) empty.push({r, c});
            }
        }
        if(empty.length > 0) {
            let cell = empty[Math.floor(Math.random() * empty.length)];
            board[cell.r][cell.c] = Math.random() < 0.9 ? 2 : 4;
        }
    }

    function updateView() {
        const gridEl = document.getElementById('grid');
        gridEl.innerHTML = '';
        for(let r=0; r<SIZE; r++) {
            for(let c=0; c<SIZE; c++) {
                let val = board[r][c];
                let tile = document.createElement('div');
                tile.className = `tile ${val ? 'tile-' + val : ''}`;
                tile.innerText = val === 0 ? '' : val;
                gridEl.appendChild(tile);
            }
        }
        document.getElementById('score').innerText = score;
        document.getElementById('best').innerText = best;
        if(score > best) {
            best = score;
            localStorage.setItem('best_2048', best);
        }
    }

    function slide(row) {
        let arr = row.filter(v => v);
        let missing = SIZE - arr.length;
        for (let i = 0; i < missing; i++) arr.push(0);
        return arr;
    }

    function combine(row) {
        for (let i = 0; i < SIZE - 1; i++) {
            if (row[i] !== 0 && row[i] === row[i + 1]) {
                row[i] *= 2;
                score += row[i];
                row[i + 1] = 0;
            }
        }
        return row;
    }

    function operate(row) {
        row = slide(row);
        row = combine(row);
        row = slide(row);
        return row;
    }

    function rotLeft(b) {
        let res = Array(SIZE).fill(0).map(() => Array(SIZE).fill(0));
        for(let r=0; r<SIZE; r++) {
            for(let c=0; c<SIZE; c++) {
                res[SIZE-1-c][r] = b[r][c];
            }
        }
        return res;
    }

    function rotRight(b) {
        let res = Array(SIZE).fill(0).map(() => Array(SIZE).fill(0));
        for(let r=0; r<SIZE; r++) {
            for(let c=0; c<SIZE; c++) {
                res[c][SIZE-1-r] = b[r][c];
            }
        }
        return res;
    }

    function moveLeft() {
        let moved = false;
        for(let r=0; r<SIZE; r++) {
            let original = [...board[r]];
            board[r] = operate(board[r]);
            if(original.toString() !== board[r].toString()) moved = true;
        }
        return moved;
    }

    function moveRight() {
        let moved = false;
        for(let r=0; r<SIZE; r++) {
            let original = [...board[r]];
            board[r].reverse();
            board[r] = operate(board[r]);
            board[r].reverse();
            if(original.toString() !== board[r].toString()) moved = true;
        }
        return moved;
    }

    function moveUp() {
        let moved = false;
        board = rotLeft(board);
        let orig = JSON.stringify(board);
        for(let r=0; r<SIZE; r++) board[r] = operate(board[r]);
        board = rotRight(board);
        if(orig !== JSON.stringify(board)) moved = true;
        return moved;
    }

    function moveDown() {
        let moved = false;
        board = rotRight(board);
        let orig = JSON.stringify(board);
        for(let r=0; r<SIZE; r++) board[r] = operate(board[r]);
        board = rotLeft(board);
        if(orig !== JSON.stringify(board)) moved = true;
        return moved;
    }

    function restartGame() {
        initGame();
    }

    window.addEventListener('keydown', e => {
        if(["ArrowUp","ArrowDown","ArrowLeft","ArrowRight"," "].includes(e.key)) {
            e.preventDefault();
        }
        let moved = false;
        if(e.key === 'ArrowLeft' || e.key.toLowerCase() === 'a') moved = moveLeft();
        else if(e.key === 'ArrowRight' || e.key.toLowerCase() === 'd') moved = moveRight();
        else if(e.key === 'ArrowUp' || e.key.toLowerCase() === 'w') moved = moveUp();
        else if(e.key === 'ArrowDown' || e.key.toLowerCase() === 's') moved = moveDown();

        if(moved) {
            addRandomTile();
            updateView();
        }
    });

    initGame();
</script>

</body>
</html>
"""

components.html(game_html, height=520)
