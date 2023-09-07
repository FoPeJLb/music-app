import os
from os import environ
environ['PYGAME_HIDE_SUPPORT_PROMPT'] = '1'
import pygame
import sys
import questionary
import yt_dlp
import curses
import subprocess
import time

def install_ffmpeg():
    # Выполняем команды в PowerShell для установки ffmpeg
    powershell_commands = [
        'Set-ExecutionPolicy RemoteSigned -Scope CurrentUser -Force',
        'Import-Module PowerShellGet',
        'Install-PackageProvider -Name NuGet -Force',
        'Install-Module -Name PowerShellGet -Force -AllowClobber',
        'Install-Module -Name Microsoft.PowerShell.Archive -Force',
        'Invoke-Expression (New-Object System.Net.WebClient).DownloadString(\'https://get.scoop.sh\')',
        'scoop install ffmpeg'
    ]
    
    # Запускаем PowerShell и выполняем команды
    powershell_process = subprocess.Popen(['powershell', '-Command', '; '.join(powershell_commands)], shell=True)
    powershell_process.communicate()  # Дожидаемся завершения процесса PowerShell

    clear_screen()
    # После завершения PowerShell продолжаем выполнение Python-скрипта
    print('Утилита ffmpeg успешно установлена. Запустите приложение заново.')
    time.sleep(5)
    
    powershell_close = [
        '$host.UI.RawUI.WindowTitle = "Restarting PowerShell"',
        'Stop-Process -Id $PID'
    ]
    
    print('Приложение завершает свою работу...')
    powershell_process_close = subprocess.Popen(['powershell', '-Command', '; '.join(powershell_close)], shell=True)
    powershell_process_close.communicate()
    sys.exit()

def check_ffmpeg_availability():
    # Выполняем команду `ffmpeg -v` в PowerShell
    command = 'ffmpeg -version'
    result = subprocess.run(['powershell', '-Command', command], capture_output=True, text=True)

    if 'ffmpeg version' in result.stdout:
        # Если вывод содержит строку "ffmpeg version", значит команда ffmpeg доступна
        print("Команда ffmpeg доступна.")
    else:
        # Если вывод не содержит строку "ffmpeg version", значит команда ffmpeg не найдена
        print(f"Утилита ffmpeg не найдена. Выполняем скрипт. Ожидайте...\nЭто одноразовая операция.\nПри следующем запуске приложения после успешной установки ffmpeg данная операция производиться не будет.\n\n")
        install_ffmpeg()

# Функция для очистки экрана
def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

# Функция для конвертации времени в формат минут:секунды
def format_time(time):
    minutes = int(time // 60)
    seconds = int(time % 60)
    return f"{minutes:02d}:{seconds:02d}"

ydl_opts = {
    'format': 'bestaudio/best',  # Только аудиоформат
    'noplaylist': True,      # Пропуск списков воспроизведения
    'postprocessors': [{
        'key': 'FFmpegExtractAudio',
        'preferredcodec': 'mp3',
        'preferredquality': '192',
    }],
    'extract_flat': True,    # Загружать только базовую информацию о видео
    'outtmpl': '%(title)s.%(ext)s',  # Задаем имя файла
    'external_downloader': 'aria2c',  # Используем aria2c
    'external_downloader_args': ['-j', '16', '-x', '16'],  # Количество потоков
}

ydl = yt_dlp.YoutubeDL(ydl_opts)

def download_audio(url):
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info_dict = ydl.extract_info(url, download=True)
        audio_file = ydl.prepare_filename(info_dict)

    return audio_file, info_dict.get('title', 'Unknown Title'), info_dict.get('duration', 0)

# Функция для загрузки и воспроизведения аудио
def play_audio(url):
    # Загрузка аудио и воспроизведение
    audio_file, audio_title, audio_duration = download_audio(url)
    print("Загрузка и конвертация завершены.")
    
    mp3_file = os.path.splitext(audio_file)[0] + '.mp3'

    pygame.mixer.init()
        
    player = pygame.mixer.music
    player.load(mp3_file)
    
    sound = pygame.mixer.Sound(mp3_file)
    duration = sound.get_length()# / 1000
    player.play()

    stdscr = curses.initscr()
    stdscr.nodelay(1)
    curses.noecho()
    curses.curs_set(0)

    while True:
        key = stdscr.getch()

        if key == ord('q'):
            break
        elif key == 32:  # Код символа пробела
            if player.get_busy():
                player.pause()
            else:
                player.unpause()
        elif key == ord('s'):
            player.stop()
            player.play()
            player.pause()
        elif key == ord('r'):
            player.stop()
            player.play()

        # Обновление информации о текущем статусе
        position = player.get_pos() / 1000  # Время в секундах

        # Отрисовка прогресс-бара
        progress_bar_width = 30
        filled_width = int(progress_bar_width * (position / duration))
        empty_width = progress_bar_width - filled_width
        progress_bar = "[" + "~" * filled_width + "●" + "-" * empty_width + "]"
        
        # Вывод текущего тайм-кода и прогресс-бара
        current_time = format_time(position)
        stdscr.erase()
        stdscr.addstr(0, 0, f"Текущая композиция: {audio_title}")
        stdscr.addstr(1, 0, f"Продолжительность: {format_time(audio_duration)}")
        stdscr.addstr(3, 0, f"{current_time}m", curses.A_BOLD)
        if len(progress_bar) <= curses.COLS:
            stdscr.addstr(3, 7, progress_bar)
        else:
            truncated_progress_bar = progress_bar[:curses.COLS]
            stdscr.addstr(3, 7, truncated_progress_bar)
        stdscr.addstr(3, 41, f"{format_time(audio_duration)}m", curses.A_BOLD)

        # Отображение кнопок управления
        stdscr.addstr(6, 0, "[Пробел] Воспроизвести / Пауза")
        stdscr.addstr(7, 0, "[S] Стоп")
        stdscr.addstr(8, 0, "[R] Рестарт")
        stdscr.addstr(9, 0, "[Q] Выход")

        stdscr.refresh()

    player.stop()
    curses.endwin()
    
    # Ожидание завершения воспроизведения
    while pygame.mixer.music.get_busy():
        pygame.time.delay(100)  # Подождать 100 миллисекунд
    
    # Завершение воспроизведения
    pygame.mixer.quit()
    
    # Удаление файла
    os.remove(mp3_file)   
    
# Возможные варианты количества выводимых результатов на одну страницу
results_per_page_choices = [str(i) for i in [5, 10, 15, 20, 25, 30, 35, 40]]

# Переменные для хранения состояния страниц
current_page = 1
results_per_page = 20  # Значение по умолчанию

# Переменная для хранения последнего поискового запроса и результатов поиска
last_search_query = None
search_results = None

while True:
    # Проверка доступности ffmpeg
    check_ffmpeg_availability()
    clear_screen()
    # Поисковый запрос
    if search_results is None:
        if last_search_query is None:
            search_query = input("Введите поисковый запрос: ")
        else:
            search_query = last_search_query

        # Проверка на пустой поисковый запрос
        if not search_query:
            print("Поиск по пустому запросу невозможен. Пожалуйста, введите поисковый запрос.")
            input("Нажмите Enter для продолжения...")
            continue

        # Выполнение поиска видео по запросу для текущей страницы
        start_index = (current_page - 1) * results_per_page + 1
        end_index = current_page * results_per_page
        search_results = ydl.extract_info(f"ytsearch{end_index}:{search_query}", download=False)
        last_search_query = search_query

    clear_screen()

    # Вывод списка видео на текущей странице
    video_entries = search_results.get('entries', [])[start_index - 1:end_index]

    # Предоставление выбора видео для воспроизведения
    options = [entry['title'] for entry in video_entries]
    options.append(questionary.Separator(line="-" * 40))
    
    # Проверка для доступности кнопки Previous Page
    if current_page > 1:
        options += ['Предыдущая страница']

    # Проверка для доступности кнопки First Page
    if current_page > 2:
        options += ['На начальную страницу']

    # Отображение текущего значения количества выводимых результатов
    options += [f"Изменить кол-во результатов на страницу ({results_per_page})", 'Следующая страница', 'Выход']

    selected_option = questionary.select(
        f"Страница {current_page}. Выберите композицию или опцию:",
        choices=options,
    ).ask()

    if selected_option == 'Выход':
        break
    elif selected_option == 'Следующая страница':
        if len(video_entries) == results_per_page:
            current_page += 1
            search_results = None
    elif selected_option == 'Предыдущая страница':
        if current_page > 1:
            current_page -= 1
            search_results = None
    elif selected_option == 'На начальную страницу':
        current_page = 1
        search_results = None
    elif selected_option.startswith('Изменить кол-во результатов на страницу'):
        results_per_page = int(questionary.select(
            "Выберите количество выводимых результатов на одну страницу:",
            choices=results_per_page_choices,
        ).ask())
        current_page = 1
        search_results = None
    elif selected_option != "─" * 40:  # Игнорируем разделитель
        selected_video_info = next(entry for entry in video_entries if entry['title'] == selected_option)
        play_audio(selected_video_info['url'])