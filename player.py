import curses
import os
import sys

# Функция для очистки экрана
def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

# Функция для создания окна меню
def create_menu_window(stdscr, menu_items, selected_item):
    sh, sw = stdscr.getmaxyx()
    menu_width = int(sw / 5)
    menu_height = sh - 9  # Высота меню - 3 (поиск) - 6 (сообщения)
    menu_win = curses.newwin(menu_height, menu_width, 3, 0)
    menu_win.box()
    
    # Отображаем пункты меню с обрезанным текстом, если он слишком длинный
    for i, item in enumerate(menu_items):
        if i == selected_item:
            menu_text = f"→ {item}"
        else:
            menu_text = f"  {item}"
        menu_win.addstr(i + 1, 2, menu_text[:menu_width - 4])  # Обрезаем текст, чтобы он умещался в окне
    
    menu_win.refresh()

# Функция для создания окна проигрывателя
def create_player_window(stdscr):
    sh, sw = stdscr.getmaxyx()
    menu_width = int(sw / 5)
    player_win = curses.newwin(sh - 9, sw - menu_width, 3, menu_width)
    player_win.box()
    player_win.addstr(int((sh - 9) / 2), int((sw - menu_width) / 2) - 3, "Плеер")
    player_win.refresh()

# Функция для создания окна сообщений
def create_message_window(stdscr):
    sh, sw = stdscr.getmaxyx()
    message_win = curses.newwin(6, sw, sh - 6, 0)
    message_win.box()
    message_win.addstr(0, 2, " Сообщения системы и Python ")
    message_win.refresh()
    
    # Перенаправляем стандартный вывод в окно сообщений
    sys.stdout = message_win
    sys.stderr = message_win

# Функция для создания окна поиска
def create_search_window(stdscr, input_active):
    search_win = curses.newwin(3, stdscr.getmaxyx()[1], 0, 0)
    search_win.box()
    if input_active:
        search_win.addstr(0, 2, "[+] Поиск: ")
    else:
        search_win.addstr(0, 2, "[ ] Поиск: ")
    search_win.refresh()
    return search_win

def main(stdscr):
    # Инициализация curses
    clear_screen()
    curses.curs_set(0)
    stdscr.clear()
    stdscr.refresh()

    # Создание начальных окон
    menu_items = ["Рез. поиска", "Избранное", "------------", "Выход"]  # Пункты меню
    selected_item = 0  # Текущий выбранный пункт меню
    search_results_menu = ["Рез. поиска 1", "Рез. поиска 2", "Рез. поиска 3", "------------", "Назад"]
    search_selected_item = 0
    favorites_menu = ["Избранное 1", "Избранное 2", "Избранное 3", "------------", "Назад"]
    favorites_selected_item = 0
    

    create_menu_window(stdscr, menu_items, selected_item)
    create_player_window(stdscr)
    create_message_window(stdscr)

    input_active = False
    search_text = ""
    search_win = create_search_window(stdscr, input_active)

    while True:
        if input_active:
            curses.echo()  # Включаем отображение ввода
            search_text = search_win.getstr(1, 2, stdscr.getmaxyx()[1] - 4).decode('utf-8')  # Считываем строку
            curses.noecho()  # Выключаем отображение ввода

            # Обработка введенного текста и добавление его в массив
            if search_text:
                # Тут должен быть код для добавления текста в массив
                search_win.addstr(1, 2, " " * (stdscr.getmaxyx()[1] - 4))  # Очищаем поле ввода
                search_win.refresh()

            input_active = False  # Сразу после ввода выключаем режим ввода
            search_win = create_search_window(stdscr, input_active)
            search_win.refresh()
        else:
            search_text = ""
            
        # Обработка нажатия клавиши 'S' для активации ввода
        key = stdscr.getch()
        if (key == ord('S') or key == ord('Ы')) and selected_item == 0:
            input_active = not input_active
            search_win = create_search_window(stdscr, input_active)
            search_win.refresh()
        # Обработка нажатия клавиш вверх и вниз для перемещения по меню
        elif key == curses.KEY_UP:
            # Пропускаем разделители
            selected_item = (selected_item - 1) % len(menu_items)
            while menu_items[selected_item] == "------------":
                selected_item = (selected_item - 1) % len(menu_items)
            create_menu_window(stdscr, menu_items, selected_item)
        elif key == curses.KEY_DOWN:
            # Пропускаем разделители
            selected_item = (selected_item + 1) % len(menu_items)
            while menu_items[selected_item] == "------------":
                selected_item = (selected_item + 1) % len(menu_items)
            create_menu_window(stdscr, menu_items, selected_item)

        # Обработка нажатия клавиши 'Enter' для выбора пункта меню
        elif key == 10:  # 10 - код клавиши 'Enter'
            if selected_item == len(menu_items) - 1:  # Если выбран "Выход"
                # Восстанавливаем стандартный вывод
                sys.stdout = sys.__stdout__
                sys.stderr = sys.__stderr__
                return
            # Обработка выбора других пунктов меню
            else:
                if selected_item == 0: # Если выбрано "Рез. поиска"
                    sub_menu_active = True
                    sub_menu_selected_item = 0
                    while sub_menu_active:
                        create_menu_window(stdscr, search_results_menu, sub_menu_selected_item)
                        stdscr.refresh()
                        sub_key = stdscr.getch()
                        if sub_key == curses.KEY_UP:
                            sub_menu_selected_item = (sub_menu_selected_item - 1) % len(search_results_menu)
                            while search_results_menu[sub_menu_selected_item] == "------------":
                                sub_menu_selected_item = (sub_menu_selected_item - 1) % len(search_results_menu)
                        elif sub_key == curses.KEY_DOWN:
                            sub_menu_selected_item = (sub_menu_selected_item + 1) % len(search_results_menu)
                            while search_results_menu[sub_menu_selected_item] == "------------":
                                sub_menu_selected_item = (sub_menu_selected_item + 1) % len(search_results_menu)
                        elif sub_key == 10:  # Enter
                            if sub_menu_selected_item == len(search_results_menu) - 1:  # Если выбран "Назад"
                                sub_menu_active = False
                                create_menu_window(stdscr, menu_items, selected_item)# Выйти из подменю
                            else:
                                # Обработка выбора других пунктов подменю
                                pass
                        elif sub_key == 27:  # Esc
                            sub_menu_active = False  # Выйти из подменю
                            create_menu_window(stdscr, menu_items, selected_item)
                elif selected_item == 1: # Если выбрано "Избранное"
                    sub_menu_active = True
                    sub_menu_selected_item = 0
                    while sub_menu_active:
                        create_menu_window(stdscr, favorites_menu, sub_menu_selected_item)
                        stdscr.refresh()
                        sub_key = stdscr.getch()
                        if sub_key == curses.KEY_UP:
                            sub_menu_selected_item = (sub_menu_selected_item - 1) % len(favorites_menu)
                            while favorites_menu[sub_menu_selected_item] == "------------":
                                sub_menu_selected_item = (sub_menu_selected_item - 1) % len(favorites_menu)
                        elif sub_key == curses.KEY_DOWN:
                            sub_menu_selected_item = (sub_menu_selected_item + 1) % len(favorites_menu)
                            while favorites_menu[sub_menu_selected_item] == "------------":
                                sub_menu_selected_item = (sub_menu_selected_item + 1) % len(favorites_menu)
                        elif sub_key == 10:  # Enter
                            if sub_menu_selected_item == len(favorites_menu) - 1:  # Если выбран "Назад"
                                sub_menu_active = False
                                create_menu_window(stdscr, menu_items, selected_item)# Выйти из подменю
                            else:
                                # Обработка выбора других пунктов подменю
                                pass
                        elif sub_key == 27:  # Esc
                            sub_menu_active = False  # Выйти из подменю
                            create_menu_window(stdscr, menu_items, selected_item)

        # Обработка нажатия клавиши 'Esc' для выхода из фокуса окна поиска
        if key == 27:
            if input_active:
                input_active = False
                search_win = create_search_window(stdscr, input_active)
                search_win.refresh()
            elif sub_menu_active:
                sub_menu_active = False
            
            # Восстанавливаем стандартный вывод
            sys.stdout = sys.__stdout__
            sys.stderr = sys.__stderr__
            return

        # Обработка изменения размера консоли
        if key == curses.KEY_RESIZE:
            clear_screen()
            stdscr.clear()
            stdscr.refresh()

            # Пересоздаем окна после изменения размера
            create_menu_window(stdscr, menu_items, selected_item)
            create_player_window(stdscr)
            create_message_window(stdscr)
            search_win = create_search_window(stdscr, input_active)
            search_win.refresh()

curses.wrapper(main)
