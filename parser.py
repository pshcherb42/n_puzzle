"""
Разбор входного файла пазла.

Формат (см. приложение к сабжекту):
    # комментарий
    3            <- размер N
    3 2 6        <- N строк по N чисел, 0 = пустая клетка
    1 4 0
    8 7 5

Комментарии (после #) и лишние пробелы нужно игнорировать.
"""

from typing import List, Tuple

Board = Tuple[Tuple[int, ...], ...]


def strip_comment(line: str) -> str:
    """Убрать всё начиная с '#' и обрезать пробелы по краям."""
    return line.split('#', 1)[0].strip()


def parse_file(path: str) -> Board:
    """
    Прочитать файл, вернуть доску как tuple of tuples.

    Шаги:
    1. Прочитать все строки, применить strip_comment, выкинуть пустые.
    2. Первая непустая строка -> N (int).
    3. Следующие N строк -> по N чисел каждая.
    4. Проверить: ровно N строк, в каждой ровно N чисел,
       числа - это перестановка 0..N*N-1 без повторов.
       Если что-то не так - кидать ValueError с понятным сообщением.
    """
    lines = []
    with open(path, "r") as file:
        for line in file:
            stripped = strip_comment(line)
            if stripped:
                lines.append(stripped)
    
    if not lines:
        raise ValueError("Empty file")
    
    try:
        N = int(lines[0])
    except ValueError:
        raise ValueError("First line should be a number")

    matrix_lines = lines[1:]
    if len(matrix_lines) != N:
        raise ValueError("Wrong number of lines")
    
    board_list = []
    all_numbers = []

    for idx, line in enumerate(matrix_lines, start=1):
        try:
            # Разделяем строку по пробелам и конвертируем в int
            row = [int(num) for num in line.split()]
        except ValueError:
            raise ValueError(f"Строка {idx} содержит некорректные символы (не числа)")
            
        # Проверяем, что в строке ровно N чисел
        if len(row) != N:
            raise ValueError(f"В строке {idx} ожидалось {N} чисел, получено: {len(row)}")
            
        board_list.append(tuple(row))
        all_numbers.extend(row)
        
    # ШАГ 4: Проверяем, что числа — это перестановка от 0 до N*N-1 без повторов
    expected_set = set(range(N * N))  # Набор чисел {0, 1, 2, ..., N*N-1}
    actual_set = set(all_numbers)
    
    if len(all_numbers) != len(actual_set):
        raise ValueError("В матрице обнаружены повторяющиеся числа")
        
    if actual_set != expected_set:
        raise ValueError(f"Числа не являются перестановкой от 0 до {N*N-1}")
        
    # Возвращаем финальный tuple of tuples
    return tuple(board_list)


