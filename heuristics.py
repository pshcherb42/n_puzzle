"""
Эвристические функции h(x) для A*.

Все три должны быть допустимыми (admissible) - никогда не переоценивать
реальную стоимость до цели. Иначе A* перестаёт гарантировать оптимальность.

Обязательная: manhattan.
Ещё две - на твой выбор, ниже два кандидата-заготовки:
    - misplaced_tiles (сколько плиток не на своём месте)
    - euclidean (сумма евклидовых расстояний)
Обе тоже допустимы и проще Манхэттена - для сравнения на защите это хорошо
("вот эвристика послабее, вот посильнее - смотрите разницу по opened set").
"""
import math
from typing import Dict, Tuple

Board = Tuple[Tuple[int, ...], ...]
Positions = Dict[int, Tuple[int, int]]


def board_to_positions(board: Board) -> Positions:
    """Вспомогательное: {значение: (row, col)} для быстрого доступа."""
    positions = {}
    for r, row in enumerate(board):
        for c, val in enumerate(row):
            positions[val] = (r, c)
    return positions


def manhattan(board: Board, goal_positions: Positions) -> int:
    """
    Сумма |dx| + |dy| для каждой плитки (кроме 0) между её позицией
    в board и позицией в goal.
    """
    h_val = 0
    for r, row in enumerate(board):
        for c, val in enumerate(row):
            if val != 0:
                goal_r, goal_c = goal_positions[val]
                h_val += abs(r - goal_r) + abs(c - goal_c)
    return h_val


def misplaced_tiles(board: Board, goal_positions: Positions) -> int:
    """Количество плиток (кроме 0), стоящих не там, где нужно."""
    h_val = 0
    for r, row in enumerate(board):
        for c, val in enumerate(row):
            if val != 0:
                goal_r, goal_c = goal_positions[val]
                if (r, c) != (goal_r, goal_c):
                    h_val += 1
    return h_val

def linear_conflict(board: Board, goal_positions: Positions) -> int:
    """
    Эвристика Линейного конфликта: manhattan(board, goal) + 2 * conflicts.
    """
    # 1. Считаем базовое Манхэттенское расстояние
    # (Вызываем написанную ранее функцию manhattan)
    from heuristics import manhattan
    base_manhattan = manhattan(board, goal_positions)
    
    n = len(board)
    conflicts = 0

    # 2. Проверка конфликтов по СТРОКАМ
    for r in range(n):
        # Собираем плитки текущей строки, которые в ЦЕЛИ должны быть НА ЭТОЙ ЖЕ СТРОКЕ
        row_tiles = []
        for c in range(n):
            val = board[r][c]
            if val != 0:
                goal_r, goal_c = goal_positions[val]
                if goal_r == r:
                    # Сохраняем текущую координату столбца и целевую координату столбца
                    row_tiles.append((c, goal_c))
                    
        # Ищем конфликты среди пар (i, j), где плитка i стоит левее плитки j
        for i in range(len(row_tiles)):
            for j in range(i + 1, len(row_tiles)):
                curr_c_i, goal_c_i = row_tiles[i]
                curr_c_j, goal_c_j = row_tiles[j]
                
                # Если в текущей доске i левее j (curr_c_i < curr_c_j),
                # но в целевой доске i должна быть правее j (goal_c_i > goal_c_j) -> конфликт
                if goal_c_i > goal_c_j:
                    conflicts += 1

    # 3. Проверка конфликтов по СТОЛБЦАМ (симметрично)
    for c in range(n):
        # Собираем плитки текущего столбца, которые в ЦЕЛИ должны быть НА ЭТОМ ЖЕ СТОЛБЦЕ
        col_tiles = []
        for r in range(n):
            val = board[r][c]
            if val != 0:
                goal_r, goal_c = goal_positions[val]
                if goal_c == c:
                    # Сохраняем текущую координату строки и целевую координату строки
                    col_tiles.append((r, goal_r))
                    
        # Ищем конфликты среди пар (i, j), где плитка i стоит выше плитки j
        for i in range(len(col_tiles)):
            for j in range(i + 1, len(col_tiles)):
                curr_r_i, goal_r_i = col_tiles[i]
                curr_r_j, goal_r_j = col_tiles[j]
                
                # Если в текущей доске i выше j (curr_r_i < curr_r_j),
                # но в целевой доске i должна быть ниже j (goal_r_i > goal_r_j) -> конфликт
                if goal_r_i > goal_r_j:
                    conflicts += 1

    # 4. Возвращаем итоговую оценку
    return base_manhattan + 2 * conflicts


HEURISTICS = {
    "manhattan": manhattan,
    "misplaced": misplaced_tiles,
    "linear_conflict": linear_conflict,
}

