"""
CLI:
    python main.py --file puzzle.txt --heuristic manhattan
    python main.py --size 4 --heuristic misplaced
    python main.py --file puzzle.txt --heuristic manhattan --search greedy

Вывод в конце (обязательно по сабжекту):
    - total states in opened set
    - max states in memory
    - number of moves
    - ordered sequence of states (путь решения)
    - если нерешаемо - явно сообщить и выйти
"""

import argparse
import sys
from functools import partial

# Импорты ваших модулей (убедитесь, что файлы лежат в той же директории)
from parser import parse_file
from generator import random_board, snail_goal, is_solvable
from heuristics import HEURISTICS, board_to_positions
from solver import a_star


def print_board(board) -> None:
    """Красивый вывод доски в виде понятной текстовой матрицы."""
    n = len(board)
    # Находим максимальную длину числа, чтобы сетка была ровной
    max_len = max(len(str(num)) for row in board for num in row)
    
    # Горизонтальный разделитель строк
    divider = "+" + ("-" * (max_len + 2) + "+") * n
    
    print(divider)
    for row in board:
        row_str = " | ".join(
            f"\033[91m·\033[0m" if num == 0 else f"{num}" 
            for num in row
        )
        # Если не нужны цветные спецсимволы в терминале, замените строку выше на:
        # row_str = " | ".join("." if num == 0 else str(num) for num in row)
        print(f"| {row_str} |")
        print(divider)


def build_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="N-puzzle A* solver")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--file", help="путь к файлу с пазлом")
    group.add_argument("--size", type=int, help="сгенерировать случайный пазл размера N")
    parser.add_argument(
        "--heuristic", choices=HEURISTICS.keys(), default="manhattan",
        help="выбор эвристической функции"
    )
    parser.add_argument(
        "--search", choices=["astar", "uniform", "greedy"], default="astar",
        help="бонус: uniform-cost / greedy как частные случаи A*",
    )
    return parser.parse_args()


def main() -> None:
    args = build_args()

    # 1. Получаем стартовую доску (board) и целевую (goal)
    try:
        if args.file:
            print(f"Reading puzzle from file: {args.file}...")
            start_board = parse_file(args.file)
            n = len(start_board)
        else:
            if args.size < 3:
                print("Error: Минимальный размер доски — 3.", file=sys.stderr)
                sys.exit(1)
            print(f"Generating random solvable board of size {args.size}x{args.size}...")
            start_board = random_board(args.size)
            n = args.size
    except Exception as e:
        print(f"Ошибка при инициализации доски: {e}", file=sys.stderr)
        sys.exit(1)

    # Строим целевую доску-улитку для данного размера N
    goal_board = snail_goal(n)

    print("\n--- СТАРТОВАЯ ДОСКА ---")
    print_board(start_board)
    print("\n--- ЦЕЛЕВАЯ ДОСКА (SNAIL GOAL) ---")
    print_board(goal_board)

    # 2. Проверяем доску на решаемость
    if not is_solvable(start_board, goal_board):
        print("\n\033[91m❌ КРИТИЧЕСКАЯ ОШИБКА: Данная доска не имеет решения!\033[0m", file=sys.stderr)
        sys.exit(1)
    
    print("\n\033[92m✓ Доска решаема. Запуск алгоритма поиска...\033[0m")

    # 3. Настраиваем эвристику (передаем goal_positions с помощью partial)
    goal_positions = board_to_positions(goal_board)
    base_heuristic_func = HEURISTICS[args.heuristic]
    
    # Оборачиваем функцию, чтобы solver принимал только один аргумент h(board)
    heuristic_closure = partial(base_heuristic_func, goal_positions=goal_positions)

    # 4. Выбираем флаги use_g / use_h в зависимости от режима поиска
    use_g, use_h = True, True
    if args.search == "uniform":
        use_g, use_h = True, False
    elif args.search == "greedy":
        use_g, use_h = False, True

    # 5. Вызываем алгоритм поиска решения A*
    print(f"Параметры поиска: алгоритм={args.search.upper()}, эвристика={args.heuristic}\n")
    result = a_star(start_board, goal_board, heuristic_closure, use_g=use_g, use_h=use_h)

    if not result:
        print("Ошибка: Очередь пуста, решение не найдено (хотя проверка на валидность пройдена).")
        sys.exit(1)

    # 6. Выводим результаты в соответствии с сабжектом проекта
    print("=================== РЕЗУЛЬТАТЫ ПОИСКА ===================")
    print(f"- Total states in opened set : {result.total_opened}")
    print(f"- Max states in memory       : {result.max_in_memory}")
    print(f"- Number of moves            : {result.moves}")
    print("=========================================================\n")

    print("Хотите увидеть последовательность шагов решения? (y/n): ", end="")
    choice = input().strip().lower()
    
    if choice == 'y' or choice == 'yes':
        print("\n--- ПОСЛЕДОВАТЕЛЬНОСТЬ ШАГОВ (ПУТЬ РЕШЕНИЯ) ---")
        for step, board in enumerate(result.path):
            print(f"\nШаг #{step} {('(СТАРТ)' if step == 0 else '(ЦЕЛЬ)' if step == result.moves else '')}")
            print_board(board)
    else:
        print("Вывод шагов пропущен.")


if __name__ == "__main__":
    main()