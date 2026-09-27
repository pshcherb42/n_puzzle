"""
A* (и, для бонуса, uniform-cost / greedy как частные случаи g/h).

f(x) = g(x) + h(x)
    g(x) - число ходов от старта до x (реальная стоимость, шаг = 1)
    h(x) - эвристика (0 для uniform-cost, g(x) игнорируется для greedy)
"""

import heapq
from typing import Callable, Dict, List, Optional, Tuple

Board = Tuple[Tuple[int, ...], ...]


class SearchResult:
    def __init__(self):
        self.path: List[Board] = []       # решение: список досок от старта до цели
        self.total_opened: int = 0        # сколько состояний ушло в open (выбрано из него)
        self.max_in_memory: int = 0       # пик размера open+closed одновременно
        self.moves: int = 0               # len(path) - 1


def neighbors(board: Board) -> List[Board]:
    """
    Все доски, достижимые одним ходом (сдвиг пустой клетки вверх/вниз/влево/вправо).

    Подсказка: найди позицию 0, для каждого из 4 направлений проверь границы,
    сделай копию доски с обменом (0 <-> сосед).
    """
    n = len(board)
    res = []
    
    # 1. Находим позицию нуля (строка и столбец)
    zero_r, zero_c = -1, -1
    for r in range(n):
        if 0 in board[r]:
            zero_r, zero_c = r, board[r].index(0)
            break

    # 2. Возможные направления сдвигов (вверх, вниз, влево, вправо)
    directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]
    
    for dr, dc in directions:
        nr, nc = zero_r + dr, zero_c + dc
        
        # Проверяем, не вышли ли мы за границы доски
        if 0 <= nr < n and 0 <= nc < n:
            # Чтобы поменять элементы в кортеже кортежей, временно преобразуем в list элементов
            new_board_list = [list(row) for row in board]
            
            # Меняем местами 0 и его соседа
            new_board_list[zero_r][zero_c], new_board_list[nr][nc] = (
                new_board_list[nr][nc],
                new_board_list[zero_r][zero_c]
            )
            
            # Сохраняем в виде неизменяемой структуры (tuple of tuples)
            res.append(tuple(tuple(row) for row in new_board_list))
            
    return res


def reconstruct_path(came_from: Dict[Board, Board], current: Board) -> List[Board]:
    """Пройти по came_from от цели к старту и развернуть список."""
    path = [current]
    while current in came_from:
        current = came_from[current]
        path.append(current)
    return path[::-1]


def a_star(
    start: Board,
    goal: Board,
    heuristic: Callable[[Board], int],
    use_g: bool = True,
    use_h: bool = True,
) -> Optional[SearchResult]:
    """
    Общий поиск: при use_g=use_h=True - классический A*,
    use_h=False - uniform-cost (Дейкстра), use_g=False - greedy best-first.

    Структуры:
      open_heap: heapq из (f, счётчик_для_tie-break, board)
      g_score: dict[Board, int] - лучшая известная g(x)
      came_from: dict[Board, Board] - для восстановления пути
      in_open: set[Board] - для быстрой проверки "уже в очереди"
      closed: set[Board]

    Основной цикл (псевдокод см. приложение к сабжекту):
      pop доску с минимальным f
      если это goal -> restore path, вернуть SearchResult
      добавить в closed, total_opened += 1
      для каждого соседа:
        tentative_g = g_score[current] + 1
        если сосед не в g_score или tentative_g лучше:
          обновить g_score, came_from, положить в open_heap
      после каждой итерации обновлять max_in_memory =
        max(max_in_memory, len(open) + len(closed))

    Если очередь опустела, а goal не найден - пазл нерешаем, вернуть None.
    """
    # Инициализируем объект результата
    res = SearchResult()
    
    # g_score хранит минимальную стоимость достижения вершины от старта
    g_score: Dict[Board, int] = {start: 0}
    came_from: Dict[Board, Board] = {}
    
    # Множества для быстрого контроля посещенных и находящихся в очереди вершин
    closed_set = set()
    
    # Очередь приоритетов: (f_score, tie_break_counter, board)
    open_heap = []
    
    # Счетчик для разрешения tie-break
    counter = 0
    
    # Вычисляем f_score для стартовой вершины
    h_start = heuristic(start) if use_h else 0
    g_start = 0 if use_g else 0
    f_start = (g_start if use_g else 0) + (h_start if use_h else 0)
    
    heapq.heappush(open_heap, (f_start, counter, start))
    
    while open_heap:
        # Обновляем пиковое потребление памяти
        current_memory = len(open_heap) + len(closed_set)
        if current_memory > res.max_in_memory:
            res.max_in_memory = current_memory
            
        # Извлекаем вершину с минимальным f_score
        f_curr, _, current = heapq.heappop(open_heap)
        
        # Если цель достигнута — собираем результат
        if current == goal:
            res.path = reconstruct_path(came_from, current)
            res.moves = len(res.path) - 1
            return res
            
        # Если вершина уже была раскрыта и закрыта — пропускаем ее 
        # (в куче могут быть дубликаты состояний с худшим f_score)
        if current in closed_set:
            continue
            
        # Закрываем текущую ноду
        closed_set.add(current)
        res.total_opened += 1
        
        # Перебираем соседние состояния
        for neighbor in neighbors(current):
            if neighbor in closed_set:
                continue
                
            # Стоимость пути до соседа: текущая реальная стоимость g + 1 шаг
            tentative_g = g_score[current] + 1
            
            # Если нашли более короткий путь до соседа (или он встречен впервые)
            if neighbor not in g_score or tentative_g < g_score[neighbor]:
                g_score[neighbor] = tentative_g
                came_from[neighbor] = current
                
                # Считаем f_score в зависимости от режима алгоритма
                h_val = heuristic(neighbor) if use_h else 0
                g_val = tentative_g if use_g else 0
                f_val = g_val + h_val
                
                counter += 1
                heapq.heappush(open_heap, (f_val, counter, neighbor))
                
    # Очередь пуста, цель не найдена
    return None