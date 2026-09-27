"""
Генерация случайной доски и построение "змейкой" (snail) целевого состояния.
"""
import random
from typing import Tuple

Board = Tuple[Tuple[int, ...], ...]


def snail_goal(n: int) -> Board:
    """
    Построить целевую доску размера n x n по спирали:
    для n=3:
        1 2 3
        8 0 4
        7 6 5

    Подсказка: заведи 4 границы (top, bottom, left, right) и
    заполняй по кругу, уменьшая границы после каждой стороны.
    Значение 0 (пустая клетка) - в центре в самом конце обхода.
    """
    # 1. Создаем пустую матрицу n x n, заполненную нулями
    matrix = [[0] * n for _ in range(n)]

    # 2. Инициализируем границы
    top, bottom = 0, n - 1
    left, right = 0, n - 1

    # Текущее число для записи (начинаем с 1)
    current_val = 1

    # Крутимся в цикле, пока границы не пересекутся
    while top <= bottom and left <= right:

        # Движение влево -> вправо по верхней строке
        for col in range(left, right + 1):
            matrix[top][col] = current_val
            current_val += 1
        top += 1  # Сдвигаем верхнюю границу вниз
        
        # Движение сверху -> вниз по правому столбцу
        for row in range(top, bottom + 1):
            matrix[row][right] = current_val
            current_val += 1
        right -= 1  # Сдвигаем правую границу влево
        
        # Движение вправо -> влево по нижней строке
        if top <= bottom:
            for col in range(right, left - 1, -1):
                matrix[bottom][col] = current_val
                current_val += 1
            bottom -= 1  # Сдвигаем нижнюю границу вверх
            
        # Движение снизу -> вверх по левому столбцу
        if left <= right:
            for row in range(bottom, top - 1, -1):
                matrix[row][left] = current_val
                current_val += 1
            left += 1  # Сдвигаем левую границу вправо

    # 3. Находим последнюю заполненную клетку. 
    # Так как мы инкрементировали current_val после каждой записи, 
    # максимальное число (n * n) окажется именно в центре.
    # Заменяем его на 0 по условию задачи.
    for r in range(n):
        for c in range(n):
            if matrix[r][c] == n * n:
                matrix[r][c] = 0
                break

    # 4. Конвертируем список списков в tuple of tuples и возвращаем
    return tuple(tuple(row) for row in matrix)


def is_solvable(board: Board, goal: Board) -> bool:
    """
    Проверка решаемости через чётность перестановки.

    Подсказка:
    1. Разверни board и goal в плоские списки без нуля.
    2. Посчитай число инверсий в board относительно порядка,
       заданного goal (не относительно 1..N-1 напрямую!).
    3. Для нечётного n: решаемо, если число инверсий чётное.
       Для чётного n: учитывай ещё и на какой строке (считая снизу)
       находится пустая клетка. Почитай про доказательство -
       на защите спросят объяснить, почему это работает.
    """
    n = len(board)

    # 1. Разворачиваем board и goal в плоские списки БЕЗ нуля
    flat_board = [num for row in board for num in row if num != 0]
    flat_goal = [num for row in goal for num in row if num != 0]

    # Чтобы считать инверсии "относительно порядка goal", нам нужно знать
    # правильную позицию (индекс) каждого числа в целевом массиве.
    # Создаем словарь: число -> его индекс в flat_goal
    goal_indices = {num: idx for idx, num in enumerate(flat_goal)}

    # 2. Считаем число инверсий в board относительно goal
    inversions = 0
    for i in range(len(flat_board)):
        for j in range(i + 1, len(flat_board)):
            # Инверсия — это когда элемент, который должен идти ПОЗЖЕ в goal,
            # в текущей доске (board) стоит РАНЬШЕ.
            if goal_indices[flat_board[i]] > goal_indices[flat_board[j]]:
                inversions += 1

    # 3. Для нечётного N решаемо, если количество инверсий чётно
    if n % 2 != 0:
        return inversions % 2 == 0

    # Для чётного N нужно учесть строку пустой клетки (считая СНИЗУ, от 1)
    # Находим индекс строки с нулем в исходной доске board
    zero_row_from_top = 0
    for r in range(n):
        if 0 in board[r]:
            zero_row_from_top = r
            break

    # Номер строки снизу: последняя строка (n-1) — это 1-я снизу, и т.д.
    zero_row_from_bottom = n - zero_row_from_top

    # Условие разрешимости для чётного N:
    # (инверсии + номер строки нуля снизу) должно иметь ту же чётность, 
    # что и аналогичная сумма для целевой доски (goal).
    
    # Находим строку нуля в целевой доске (считая снизу)
    goal_zero_row_from_top = 0
    for r in range(n):
        if 0 in goal[r]:
            goal_zero_row_from_top = r
            break
    goal_zero_row_from_bottom = n - goal_zero_row_from_top
    
    # В классических пятнашках цель стандартная (ноль в конце), но так как у нас 
    # цель улитка (ноль в центре), мы проверяем совпадение чётности сумм инвариантов:
    board_parity = (inversions + zero_row_from_bottom) % 2
    goal_parity = (0 + goal_zero_row_from_bottom) % 2  # у goal относительно себя 0 инверсий
    
    return board_parity == goal_parity


def random_board(n: int) -> Board:
    """
    Сгенерировать случайную решаемую доску размера n x n.

    Подсказка: перемешай случайно числа 0..n*n-1, проверь is_solvable
    относительно snail_goal(n); если не решаемо - поменяй местами
    любые две ненулевые клетки (это меняет чётность) и снова проверь.
    """
    # 1. Генерируем плоский список чисел от 0 до n*n-1 и случайно перемешиваем его
    flat = list(range(n * n))
    random.shuffle(flat)

    # Вспомогательная функция для сборки плоского списка обратно в tuple of tuples
    def make_tuple_board(flat_list: list) -> Board:
        return tuple(tuple(flat_list[i * n : (i + 1) * n]) for i in range(n))
    
    # Собираем целевую доску-улитку для проверки решаемости
    goal = snail_goal(n)

    # Строим текущую случайную доску
    board = make_tuple_board(flat)

    # 2. Если доска нерешаема — меняем четность перестановки
    if not is_solvable(board, goal):
        # Нам нужно поменять местами любые ДВА НЕУЛЕВЫХ элемента.
        # Найдем индексы первых двух элементов в списке flat, которые не равны 0.
        idx1, idx2 = -1, -1
        for i in range(len(flat)):
            if flat[i] != 0:
                if idx1 == -1:
                    idx1 = i
                elif idx2 == -1:
                    idx2 = i
                    break # Нашли оба индекса, выходим из цикла
        
        # Меняем их местами в плоском списке (это гарантированно меняет чётность всей доски)
        flat[idx1], flat[idx2] = flat[idx2], flat[idx1]
        
        # Пересобираем доску с новой чётностью
        board = make_tuple_board(flat)
        
    return board