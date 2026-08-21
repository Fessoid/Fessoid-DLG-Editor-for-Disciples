"""
Fessoid DLG Editor for Disciples — визуальный редактор .dlg и Capital.dat.

Запуск:
    python fessoid_dlg_editor_for_disciples.py [путь_к_файлу.dlg|.dat]

Сборка (версия в имени exe подставляется из APP_VERSION, PowerShell):
    $v = (Select-String -Path fessoid_dlg_editor_for_disciples.py `
          -Pattern '^APP_VERSION = "(.+)"').Matches.Groups[1].Value
    pyinstaller --onefile --windowed `
        --name "Fessoid DLG Editor for Disciples v$v" `
        fessoid_dlg_editor_for_disciples.py
"""

import configparser
import json
import os
import re
import subprocess
import sys
import threading
import urllib.error
import urllib.request
import webbrowser
import tkinter as tk
from tkinter import filedialog, font as tkfont, messagebox, ttk

# Название и версия программы — единственное место, где они задаются.
APP_T = "Fessoid DLG Editor for Disciples v"
APP_VERSION = "1.3"
APP_TITLE = APP_T + APP_VERSION

# Папка программы — рядом с exe / скриптом. Туда же кладётся файл настроек
# и скачивается новая версия при обновлении.
APP_DIR = os.path.dirname(os.path.abspath(sys.argv[0]))
SETTINGS_PATH = os.path.join(APP_DIR, "Fessoid_DLG_Editor_settings.ini")
# До версии 1.3 файл настроек назывался иначе. Переносим его один раз, чтобы
# у тех, кто уже пользуется программой, не пропали язык, последний открытый
# файл и отметка об отказе от обновления.
OLD_SETTINGS_PATH = os.path.join(APP_DIR, "DLG_Editor_settings.ini")


def migrate_settings():
    if os.path.exists(SETTINGS_PATH) or not os.path.exists(OLD_SETTINGS_PATH):
        return
    try:
        os.replace(OLD_SETTINGS_PATH, SETTINGS_PATH)
    except OSError:
        pass    # не вышло — программа просто начнёт с настроек по умолчанию

# --- Проверка обновлений -----------------------------------------------------
# Репозиторий публичный, поэтому запрос к API GitHub идёт без авторизации:
# токен не нужен. Лимит анонимных запросов — 60 в час на IP-адрес, а проверка
# выполняется один раз за запуск, так что упереться в него нельзя.
UPDATE_REPO = "Fessoid/Fessoid-DLG-Editor-for-Disciples"
UPDATE_API_URL = f"https://api.github.com/repos/{UPDATE_REPO}/releases/latest"
UPDATE_PAGE_URL = f"https://github.com/{UPDATE_REPO}/releases/latest"
UPDATE_TIMEOUT = 4      # секунд на сетевой запрос
UPDATE_DELAY_MS = 1200  # пауза после старта, чтобы окно успело отрисоваться

# Режимы работы редактора.
MODE_DLG = "dlg"
MODE_DAT = "dat"

# --- Горячие клавиши независимо от раскладки ---------------------------------
# При русской раскладке event.keysym приходит кириллическим ("Cyrillic_ya" и
# т.п.), поэтому привязки вида <Control-z> не срабатывают. Физическую клавишу
# определяем по event.keycode: на Windows это виртуальный код клавиши (VK),
# он от раскладки не зависит. Для Linux/X11 держим отдельную таблицу.
VK_KEYCODES = {67: "c", 72: "h", 79: "o", 83: "s", 89: "y", 90: "z"}
X11_KEYCODES = {54: "c", 43: "h", 32: "o", 39: "s", 29: "y", 52: "z"}


def key_letter(event):
    """Латинская буква нажатой клавиши независимо от раскладки (или None)."""
    ks = event.keysym
    if len(ks) == 1 and ks.isascii() and ks.isalpha():
        return ks.lower()
    if sys.platform.startswith("win"):
        return VK_KEYCODES.get(event.keycode)
    return X11_KEYCODES.get(event.keycode)

# =============================================================================
# ЛОКАЛИЗАЦИЯ — все строки программы.
# Чтобы добавить или изменить текст, отредактируйте словари ниже.
# Ключ — внутренний идентификатор, значение — текст для пользователя.
# =============================================================================

# Контакты для окна «О программе». Формат: (название, URL, жирный шрифт).
# Название, начинающееся с «@», — ключ перевода: текст берётся из STRINGS для
# текущего языка. Для email используйте mailto: — программа автоматически
# откроет почтовый клиент. Адрес репозитория собирается из UPDATE_REPO, чтобы
# ссылка в окне и адрес проверки обновлений не разъехались.
ABOUT_LINKS = [
    ("@about_support", "https://boosty.to/fessoid",              True),
    ("YouTube",        "https://www.youtube.com/@Fessoid",       False),
    ("Steam",          "https://steamcommunity.com/id/fessoid/", False),
    ("",               "",                                       False),
    ("Github",         f"https://github.com/{UPDATE_REPO}",      False),
    ("Email",          "mailto:fessoid@gmail.com",               False),
]

STRINGS = {
    "ru": {
        # --- Меню ---
        "menu_file":             "Файл",
        "menu_open":             "Открыть...",
        "menu_save":             "Сохранить",
        "menu_save_as":          "Сохранить как...",
        "menu_exit":             "Выход",
        "menu_edit":             "Правка",
        "menu_undo":             "Отменить изменение",
        "menu_redo":             "Вернуть изменение",
        "menu_history":          "История изменений...",
        "menu_settings":         "Настройки",
        "menu_dat_secondary":    "Изменять вторичные координаты в .dat",
        "menu_language":         "Язык",
        "menu_lang_ru":          "Русский",
        "menu_lang_en":          "English",
        "menu_lang_pl":          "Polski",
        "menu_lang_zh":          "简体中文",
        "menu_about":            "О программе",

        # --- Левая панель ---
        "sections_label":        "Секции DIALOG:",
        "sections_label_dat":    "Секции (расы):",

        # --- Статус ---
        "status_open_hint":      "Откройте .dlg или Capital.dat (Ctrl+O)",
        "status_loaded":         "Загружено: {path} — секций: {count}",
        "status_loaded_dat":     "Загружено: {path} — рас: {count}, слоёв: {layers}",
        "status_saved":          "Сохранено: {path}",

        # --- Правая панель ---
        "elements_label":        "Элементы:",
        "elements_label_dat":    "Слои (здания):",
        "dialog_size_label":     "Размер окна DIALOG",
        "coord_label":           "Координаты выбранного элемента",
        "hints_label":           "Подсказки",
        "hint_text": (
            "• Клик по элементу — выделить\n"
            "• Тянуть за центр — переместить\n"
            "• Тянуть за край/угол — изменить размер\n"
            "• Тянуть правый/нижний край окна —\n"
            "  менять размер DIALOG\n"
            "• Ctrl+S — сохранить, Ctrl+Z — отменить\n"
            "• Ctrl+H — история изменений\n"
            "• Двойной клик в «Истории изменений» —\n"
            "  вернуться к выбранной правке\n"
            "• Ctrl+C — копировать имя секции"
        ),
        "hint_text_dat": (
            "• Клик по слою — выделить\n"
            "• Тянуть за центр — переместить\n"
            "• Тянуть за край/угол — изменить размер\n"
            "• Добавить / Изменить / Удалить —\n"
            "  работа со слоями зданий\n"
            "• Ctrl+S — сохранить, Ctrl+Z — отменить\n"
            "• Ctrl+H — история изменений\n"
            "• Двойной клик в «Истории изменений» —\n"
            "  вернуться к выбранной правке\n"
            "• Ctrl+C — копировать имя секции"
        ),
        "dlg_size_fixed":        "X1, Y1 = 0 (фиксировано)",
        "dlg_size_warn":         "Внимание: вторая пара = {w}×{h}, "
                                 "при сохранении будет синхронизирована.",

        # --- Кнопки ---
        "btn_save":              "Сохранить",
        "btn_revert":            "Отменить",
        "btn_history":           "История",
        "btn_open_external":     "Открыть файл в блокноте",
        "btn_open_external_tip": "Открыть текущий файл текстовым редактором",
        "btn_reload":            "Перечитать файл",
        "btn_reload_tip":        "Прочитать файл с диска заново — подхватить\n"
                                 "правки, сделанные в другой программе.\n"
                                 "Несохранённые изменения пропадут.",
        "btn_open_folder":       "Открыть папку файла",
        "btn_add":               "Добавить",
        "btn_edit":              "Изменить",
        "btn_delete":            "Удалить",
        "btn_ok":                "ОК",
        "btn_cancel":            "Отмена",
        "btn_close":             "Закрыть",
        "btn_copy":              "Копировать",

        # --- Подсказки к кнопкам (всплывают при наведении) ---
        "btn_save_tip":          "Записать изменения в текущий файл (Ctrl+S)",
        "btn_revert_tip":        "Отменить все несохранённые изменения\n"
                                 "и вернуть файл к состоянию на диске",
        "btn_history_tip":       "Открыть список всех правок и вернуться\n"
                                 "к любой из них (Ctrl+H)",
        "btn_open_folder_tip":   "Открыть папку с текущим файлом\n"
                                 "и выделить его в ней",
        "btn_add_tip":           "Добавить новый слой здания в выбранную расу",
        "btn_edit_tip":          "Изменить параметры выделенного слоя",
        "btn_delete_tip":        "Удалить выделенный слой.\n"
                                 "Действие можно отменить через Ctrl+Z.",
        "hist_revert_to_tip":    "Вернуть файл к выделенной строке истории",
        "btn_close_tip":         "Закрыть окно",
        "btn_ok_tip":            "Применить изменения и закрыть окно",
        "btn_cancel_tip":        "Закрыть окно, ничего не меняя",
        "btn_delete_ok_tip":     "Удалить слой.\n"
                                 "Действие можно отменить через Ctrl+Z.",

        # --- Диалоги ---
        "err_read_title":        "Ошибка чтения",
        "err_read_msg":          "Не удалось прочитать файл:\n{err}",
        "err_write_title":       "Ошибка записи",
        "err_write_msg":         "Не удалось сохранить:\n{err}",
        "err_open_title":        "Ошибка открытия",
        "err_open_msg":          "Не удалось открыть файл во внешней программе:\n{err}",
        "unsaved_title":         "Несохранённые изменения",
        "unsaved_msg":           "В файле есть несохранённые изменения.\n"
                                 "Сохранить перед продолжением?",

        # --- История ---
        "hist_title":            "История изменений",
        "hist_initial":          "— исходное состояние файла —",
        "hist_revert_to":        "Откатиться к выбранному состоянию",
        "hist_current_mark":     "►",
        "hist_col_sec":          "Секция",
        "hist_col_param":        "Параметр",
        "hist_col_before":       "Было",
        "hist_col_after":        "Стало",
        "hist_param_dlgsize":    "Размер окна DIALOG",
        "hist_none":             "—",

        # --- Редактор слоя Capital.dat ---
        "layer_add_title":       "Новый слой",
        "layer_edit_title":      "Изменение слоя",
        "fld_z":                 "Z-order (номер LAYER)",
        "fld_build":             "ID здания (Gbuild)",
        "fld_image":             "Имя изображения (Capital.ff)",
        "fld_coords":            "Координаты X1, Y1, X2, Y2",
        "fld_extra":             "Прочие поля (через запятую)",
        "fld_layerinfo":         "Создать запись LAYERINFO для этого здания",
        "err_layer_title":       "Некорректные данные",
        "err_layer_z":           "Z-order должен быть целым числом.",
        "err_layer_dup":         "Слой с номером {z} уже существует в этой секции.",
        "err_layer_coords":      "Координаты должны быть целыми числами.",
        "del_title":             "Удаление слоя",
        "del_msg":               "Удалить слой {name} ({image})?\n"
                                 "Действие можно отменить через Ctrl+Z.",
        "del_layerinfo":         "Также удалить запись LAYERINFO для {build}",
        "no_selection":          "Слой не выбран.",

        # --- Обновление ---
        "update_title":          "Доступно обновление",
        "update_msg":            "Вышла новая версия {new}.\n"
                                 "Установлена версия {cur}.\n\n"
                                 "Скачать новую версию сейчас?",
        "update_downloading":    "Загрузка обновления...",
        "update_done_title":     "Обновление скачано",
        "update_done_msg":       "Новая версия сохранена рядом с программой:\n"
                                 "{path}\n\n"
                                 "Запустить её и закрыть текущую?",
        "update_fail_title":     "Не удалось скачать",
        "update_fail_msg":       "Скачать обновление не получилось.\n{err}\n\n"
                                 "Открыть страницу релиза в браузере?",

        # --- О программе ---
        "about_title":           "О программе",
        "about_support":         "Поддержать разработку",
        "about_name":            APP_TITLE,
        "about_version":         "версия " + APP_VERSION,
        "about_text": (
            "Визуальный редактор файлов интерфейса Disciples.\n\n"
            "Режим .dlg: изменение размеров и положения элементов\n"
            "интерфейса мышью или вводом координат вручную.\n\n"
            "Режим Capital.dat: добавление, изменение и удаление\n"
            "слоёв зданий на главном экране столицы (общий вид\n"
            "города, а не ветки развития юнитов) с визуальным\n"
            "размещением.\n\n"
            "Изменения сохраняются обратно в файл с сохранением\n"
            "исходного синтаксиса."
        ),
    },
    "en": {
        # --- Menu ---
        "menu_file":             "File",
        "menu_open":             "Open...",
        "menu_save":             "Save",
        "menu_save_as":          "Save As...",
        "menu_exit":             "Exit",
        "menu_edit":             "Edit",
        "menu_undo":             "Undo change",
        "menu_redo":             "Redo change",
        "menu_history":          "Change History...",
        "menu_settings":         "Settings",
        "menu_dat_secondary":    "Update secondary coordinates in .dat",
        "menu_language":         "Language",
        "menu_lang_ru":          "Русский",
        "menu_lang_en":          "English",
        "menu_lang_pl":          "Polski",
        "menu_lang_zh":          "简体中文",
        "menu_about":            "About",

        # --- Left panel ---
        "sections_label":        "DIALOG Sections:",
        "sections_label_dat":    "Sections (races):",

        # --- Status ---
        "status_open_hint":      "Open a .dlg file or Capital.dat (Ctrl+O)",
        "status_loaded":         "Loaded: {path} — sections: {count}",
        "status_loaded_dat":     "Loaded: {path} — races: {count}, layers: {layers}",
        "status_saved":          "Saved: {path}",

        # --- Right panel ---
        "elements_label":        "Elements:",
        "elements_label_dat":    "Layers (buildings):",
        "dialog_size_label":     "DIALOG Window Size",
        "coord_label":           "Selected Element Coordinates",
        "hints_label":           "Tips",
        "hint_text": (
            "• Click an element to select it\n"
            "• Drag from center to move\n"
            "• Drag edge/corner to resize\n"
            "• Drag right/bottom edge of window\n"
            "  to resize DIALOG\n"
            "• Ctrl+S to save, Ctrl+Z to undo\n"
            "• Ctrl+H opens the change history\n"
            "• Double-click in the Change History —\n"
            "  revert to the selected edit\n"
            "• Ctrl+C copies the section name"
        ),
        "hint_text_dat": (
            "• Click a layer to select it\n"
            "• Drag from center to move\n"
            "• Drag edge/corner to resize\n"
            "• Add / Edit / Delete —\n"
            "  manage building layers\n"
            "• Ctrl+S to save, Ctrl+Z to undo\n"
            "• Ctrl+H opens the change history\n"
            "• Double-click in the Change History —\n"
            "  revert to the selected edit\n"
            "• Ctrl+C copies the section name"
        ),
        "dlg_size_fixed":        "X1, Y1 = 0 (fixed)",
        "dlg_size_warn":         "Warning: second pair = {w}×{h}, "
                                 "will be synced on save.",

        # --- Buttons ---
        "btn_save":              "Save",
        "btn_revert":            "Revert",
        "btn_history":           "History",
        "btn_open_external":     "Open file in Notepad",
        "btn_open_external_tip": "Open the current file in a text editor",
        "btn_reload":            "Reload file",
        "btn_reload_tip":        "Read the file from disk again to pick up\n"
                                 "edits made in another program.\n"
                                 "Unsaved changes will be lost.",
        "btn_open_folder":       "Open file folder",
        "btn_add":               "Add",
        "btn_edit":              "Edit",
        "btn_delete":            "Delete",
        "btn_ok":                "OK",
        "btn_cancel":            "Cancel",
        "btn_close":             "Close",
        "btn_copy":              "Copy",

        # --- Button tooltips (shown on hover) ---
        "btn_save_tip":          "Write the changes to the current file (Ctrl+S)",
        "btn_revert_tip":        "Discard all unsaved changes and restore\n"
                                 "the file to its state on disk",
        "btn_history_tip":       "Open the list of all edits and jump back\n"
                                 "to any of them (Ctrl+H)",
        "btn_open_folder_tip":   "Open the folder of the current file\n"
                                 "and select the file in it",
        "btn_add_tip":           "Add a new building layer to the selected race",
        "btn_edit_tip":          "Change the parameters of the selected layer",
        "btn_delete_tip":        "Delete the selected layer.\n"
                                 "The action can be undone with Ctrl+Z.",
        "hist_revert_to_tip":    "Restore the file to the selected history row",
        "btn_close_tip":         "Close the window",
        "btn_ok_tip":            "Apply the changes and close the window",
        "btn_cancel_tip":        "Close the window without changing anything",
        "btn_delete_ok_tip":     "Delete the layer.\n"
                                 "The action can be undone with Ctrl+Z.",

        # --- Dialogs ---
        "err_read_title":        "Read Error",
        "err_read_msg":          "Could not read file:\n{err}",
        "err_write_title":       "Write Error",
        "err_write_msg":         "Could not save file:\n{err}",
        "err_open_title":        "Open Error",
        "err_open_msg":          "Could not open the file externally:\n{err}",
        "unsaved_title":         "Unsaved Changes",
        "unsaved_msg":           "There are unsaved changes.\n"
                                 "Save before continuing?",

        # --- History ---
        "hist_title":            "Change History",
        "hist_initial":          "— initial file state —",
        "hist_revert_to":        "Revert to selected state",
        "hist_current_mark":     "►",
        "hist_col_sec":          "Section",
        "hist_col_param":        "Parameter",
        "hist_col_before":       "Before",
        "hist_col_after":        "After",
        "hist_param_dlgsize":    "DIALOG window size",
        "hist_none":             "—",

        # --- Capital.dat layer editor ---
        "layer_add_title":       "New Layer",
        "layer_edit_title":      "Edit Layer",
        "fld_z":                 "Z-order (LAYER number)",
        "fld_build":             "Building ID (Gbuild)",
        "fld_image":             "Image name (Capital.ff)",
        "fld_coords":            "Coordinates X1, Y1, X2, Y2",
        "fld_extra":             "Other fields (comma separated)",
        "fld_layerinfo":         "Create a LAYERINFO entry for this building",
        "err_layer_title":       "Invalid Data",
        "err_layer_z":           "Z-order must be an integer.",
        "err_layer_dup":         "A layer numbered {z} already exists in this section.",
        "err_layer_coords":      "Coordinates must be integers.",
        "del_title":             "Delete Layer",
        "del_msg":               "Delete layer {name} ({image})?\n"
                                 "This can be undone with Ctrl+Z.",
        "del_layerinfo":         "Also delete the LAYERINFO entry for {build}",
        "no_selection":          "No layer selected.",

        # --- Update ---
        "update_title":          "Update available",
        "update_msg":            "Version {new} has been released.\n"
                                 "You have version {cur}.\n\n"
                                 "Download the new version now?",
        "update_downloading":    "Downloading update...",
        "update_done_title":     "Update downloaded",
        "update_done_msg":       "The new version was saved next to the program:\n"
                                 "{path}\n\n"
                                 "Launch it and close the current one?",
        "update_fail_title":     "Download failed",
        "update_fail_msg":       "The update could not be downloaded.\n{err}\n\n"
                                 "Open the release page in the browser?",

        # --- About ---
        "about_title":           "About",
        "about_support":         "Support the development",
        "about_name":            APP_TITLE,
        "about_version":         "version " + APP_VERSION,
        "about_text": (
            "A visual editor for Disciples interface files.\n\n"
            ".dlg mode: change sizes and positions of interface\n"
            "elements with the mouse or by typing coordinates.\n\n"
            "Capital.dat mode: add, edit and delete building\n"
            "layers on the capital's main screen (the city view,\n"
            "not the unit branch dialogs) with visual placement.\n\n"
            "Changes are written back to the file preserving\n"
            "the original syntax."
        ),
    },
    "pl": {
        # --- Menu ---
        "menu_file":             "Plik",
        "menu_open":             "Otwórz...",
        "menu_save":             "Zapisz",
        "menu_save_as":          "Zapisz jako...",
        "menu_exit":             "Wyjście",
        "menu_edit":             "Edycja",
        "menu_undo":             "Cofnij zmianę",
        "menu_redo":             "Ponów zmianę",
        "menu_history":          "Historia zmian...",
        "menu_settings":         "Ustawienia",
        "menu_dat_secondary":    "Zmieniaj wtórne współrzędne w .dat",
        "menu_language":         "Język",
        "menu_lang_ru":          "Русский",
        "menu_lang_en":          "English",
        "menu_lang_pl":          "Polski",
        "menu_lang_zh":          "简体中文",
        "menu_about":            "O programie",

        # --- Left panel ---
        "sections_label":        "Sekcje DIALOG:",
        "sections_label_dat":    "Sekcje (rasy):",

        # --- Status ---
        "status_open_hint":      "Otwórz plik .dlg lub Capital.dat (Ctrl+O)",
        "status_loaded":         "Wczytano: {path} — sekcji: {count}",
        "status_loaded_dat":     "Wczytano: {path} — ras: {count}, warstw: {layers}",
        "status_saved":          "Zapisano: {path}",

        # --- Right panel ---
        "elements_label":        "Elementy:",
        "elements_label_dat":    "Warstwy (budynki):",
        "dialog_size_label":     "Rozmiar okna DIALOG",
        "coord_label":           "Współrzędne wybranego elementu",
        "hints_label":           "Wskazówki",
        "hint_text": (
            "• Kliknij element, aby go wybrać\n"
            "• Przeciągnij ze środka, aby przesunąć\n"
            "• Przeciągnij krawędź/róg, aby zmienić rozmiar\n"
            "• Przeciągnij prawą/dolną krawędź okna,\n"
            "  aby zmienić rozmiar DIALOG\n"
            "• Ctrl+S — zapisz, Ctrl+Z — cofnij\n"
            "• Ctrl+H — historia zmian\n"
            "• Podwójne kliknięcie w „Historii zmian” —\n"
            "  powrót do wybranej zmiany\n"
            "• Ctrl+C — kopiuj nazwę sekcji"
        ),
        "hint_text_dat": (
            "• Kliknij warstwę, aby ją wybrać\n"
            "• Przeciągnij ze środka, aby przesunąć\n"
            "• Przeciągnij krawędź/róg, aby zmienić rozmiar\n"
            "• Dodaj / Zmień / Usuń —\n"
            "  zarządzanie warstwami budynków\n"
            "• Ctrl+S — zapisz, Ctrl+Z — cofnij\n"
            "• Ctrl+H — historia zmian\n"
            "• Podwójne kliknięcie w „Historii zmian” —\n"
            "  powrót do wybranej zmiany\n"
            "• Ctrl+C — kopiuj nazwę sekcji"
        ),
        "dlg_size_fixed":        "X1, Y1 = 0 (stałe)",
        "dlg_size_warn":         "Uwaga: druga para = {w}×{h}, "
                                 "zostanie zsynchronizowana przy zapisie.",

        # --- Buttons ---
        "btn_save":              "Zapisz",
        "btn_revert":            "Cofnij",
        "btn_history":           "Historia",
        "btn_open_external":     "Otwórz plik w Notatniku",
        "btn_open_external_tip": "Otwórz bieżący plik w edytorze tekstu",
        "btn_reload":            "Wczytaj ponownie",
        "btn_reload_tip":        "Wczytaj plik z dysku ponownie, aby podchwycić\n"
                                 "zmiany z innego programu.\n"
                                 "Niezapisane zmiany przepadną.",
        "btn_open_folder":       "Otwórz folder pliku",
        "btn_add":               "Dodaj",
        "btn_edit":              "Zmień",
        "btn_delete":            "Usuń",
        "btn_ok":                "OK",
        "btn_cancel":            "Anuluj",
        "btn_close":             "Zamknij",
        "btn_copy":              "Kopiuj",

        # --- Podpowiedzi przycisków (po najechaniu myszą) ---
        "btn_save_tip":          "Zapisz zmiany w bieżącym pliku (Ctrl+S)",
        "btn_revert_tip":        "Odrzuć wszystkie niezapisane zmiany\n"
                                 "i przywróć plik do stanu z dysku",
        "btn_history_tip":       "Otwórz listę wszystkich zmian i wróć\n"
                                 "do dowolnej z nich (Ctrl+H)",
        "btn_open_folder_tip":   "Otwórz folder bieżącego pliku\n"
                                 "i zaznacz w nim ten plik",
        "btn_add_tip":           "Dodaj nową warstwę budynku do wybranej rasy",
        "btn_edit_tip":          "Zmień parametry zaznaczonej warstwy",
        "btn_delete_tip":        "Usuń zaznaczoną warstwę.\n"
                                 "Operację można cofnąć przez Ctrl+Z.",
        "hist_revert_to_tip":    "Przywróć plik do zaznaczonego wiersza historii",
        "btn_close_tip":         "Zamknij okno",
        "btn_ok_tip":            "Zastosuj zmiany i zamknij okno",
        "btn_cancel_tip":        "Zamknij okno bez żadnych zmian",
        "btn_delete_ok_tip":     "Usuń warstwę.\n"
                                 "Operację można cofnąć przez Ctrl+Z.",

        # --- Dialogs ---
        "err_read_title":        "Błąd odczytu",
        "err_read_msg":          "Nie udało się odczytać pliku:\n{err}",
        "err_write_title":       "Błąd zapisu",
        "err_write_msg":         "Nie udało się zapisać pliku:\n{err}",
        "err_open_title":        "Błąd otwarcia",
        "err_open_msg":          "Nie udało się otworzyć pliku zewnętrznie:\n{err}",
        "unsaved_title":         "Niezapisane zmiany",
        "unsaved_msg":           "Plik zawiera niezapisane zmiany.\n"
                                 "Zapisać przed kontynuacją?",

        # --- History ---
        "hist_title":            "Historia zmian",
        "hist_initial":          "— stan początkowy pliku —",
        "hist_revert_to":        "Przywróć wybrany stan",
        "hist_current_mark":     "►",
        "hist_col_sec":          "Sekcja",
        "hist_col_param":        "Parametr",
        "hist_col_before":       "Było",
        "hist_col_after":        "Jest",
        "hist_param_dlgsize":    "Rozmiar okna DIALOG",
        "hist_none":             "—",

        # --- Capital.dat ---
        "layer_add_title":       "Nowa warstwa",
        "layer_edit_title":      "Edycja warstwy",
        "fld_z":                 "Z-order (numer LAYER)",
        "fld_build":             "ID budynku (Gbuild)",
        "fld_image":             "Nazwa obrazu (Capital.ff)",
        "fld_coords":            "Współrzędne X1, Y1, X2, Y2",
        "fld_extra":             "Pozostałe pola (po przecinku)",
        "fld_layerinfo":         "Utwórz wpis LAYERINFO dla tego budynku",
        "err_layer_title":       "Nieprawidłowe dane",
        "err_layer_z":           "Z-order musi być liczbą całkowitą.",
        "err_layer_dup":         "Warstwa o numerze {z} już istnieje w tej sekcji.",
        "err_layer_coords":      "Współrzędne muszą być liczbami całkowitymi.",
        "del_title":             "Usuwanie warstwy",
        "del_msg":               "Usunąć warstwę {name} ({image})?\n"
                                 "Można to cofnąć przez Ctrl+Z.",
        "del_layerinfo":         "Usuń także wpis LAYERINFO dla {build}",
        "no_selection":          "Nie wybrano warstwy.",

        # --- Aktualizacja ---
        "update_title":          "Dostępna aktualizacja",
        "update_msg":            "Ukazała się nowa wersja {new}.\n"
                                 "Zainstalowana jest wersja {cur}.\n\n"
                                 "Pobrać nową wersję teraz?",
        "update_downloading":    "Pobieranie aktualizacji...",
        "update_done_title":     "Aktualizacja pobrana",
        "update_done_msg":       "Nowa wersja została zapisana obok programu:\n"
                                 "{path}\n\n"
                                 "Uruchomić ją i zamknąć bieżącą?",
        "update_fail_title":     "Nie udało się pobrać",
        "update_fail_msg":       "Nie udało się pobrać aktualizacji.\n{err}\n\n"
                                 "Otworzyć stronę wydania w przeglądarce?",

        # --- About ---
        "about_title":           "O programie",
        "about_support":         "Wesprzyj rozwój",
        "about_name":            APP_TITLE,
        "about_version":         "wersja " + APP_VERSION,
        "about_text": (
            "Edytor wizualny plików interfejsu Disciples.\n\n"
            "Tryb .dlg: zmiana rozmiarów i pozycji elementów\n"
            "interfejsu myszą lub przez wpisanie współrzędnych.\n\n"
            "Tryb Capital.dat: dodawanie, zmiana i usuwanie warstw\n"
            "budynków na głównym ekranie stolicy (widok miasta,\n"
            "a nie gałęzie rozwoju jednostek) z wizualnym\n"
            "rozmieszczeniem.\n\n"
            "Zmiany są zapisywane z zachowaniem oryginalnej składni."
        ),
    },
    "zh": {
        # --- 菜单 ---
        "menu_file":             "文件",
        "menu_open":             "打开...",
        "menu_save":             "保存",
        "menu_save_as":          "另存为...",
        "menu_exit":             "退出",
        "menu_edit":             "编辑",
        "menu_undo":             "撤销修改",
        "menu_redo":             "恢复修改",
        "menu_history":          "修改历史...",
        "menu_settings":         "设置",
        "menu_dat_secondary":    "修改 .dat 中的次要坐标",
        "menu_language":         "语言",
        "menu_lang_ru":          "Русский",
        "menu_lang_en":          "English",
        "menu_lang_pl":          "Polski",
        "menu_lang_zh":          "简体中文",
        "menu_about":            "关于",

        # --- 左面板 ---
        "sections_label":        "DIALOG 区段：",
        "sections_label_dat":    "区段（种族）：",

        # --- 状态 ---
        "status_open_hint":      "请打开 .dlg 或 Capital.dat（Ctrl+O）",
        "status_loaded":         "已加载：{path} — 区段数：{count}",
        "status_loaded_dat":     "已加载：{path} — 种族：{count}，图层：{layers}",
        "status_saved":          "已保存：{path}",

        # --- 右面板 ---
        "elements_label":        "元素：",
        "elements_label_dat":    "图层（建筑）：",
        "dialog_size_label":     "DIALOG 窗口尺寸",
        "coord_label":           "所选元素坐标",
        "hints_label":           "提示",
        "hint_text": (
            "• 单击元素以选中\n"
            "• 从中心拖动以移动\n"
            "• 拖动边缘/角以调整大小\n"
            "• 拖动窗口的右/下边缘\n"
            "  以调整 DIALOG 大小\n"
            "• Ctrl+S 保存，Ctrl+Z 撤销\n"
            "• Ctrl+H 修改历史\n"
            "• 在「修改历史」中双击 —\n"
            "  回到所选的修改\n"
            "• Ctrl+C 复制区段名称"
        ),
        "hint_text_dat": (
            "• 单击图层以选中\n"
            "• 从中心拖动以移动\n"
            "• 拖动边缘/角以调整大小\n"
            "• 添加 / 修改 / 删除 —\n"
            "  管理建筑图层\n"
            "• Ctrl+S 保存，Ctrl+Z 撤销\n"
            "• Ctrl+H 修改历史\n"
            "• 在「修改历史」中双击 —\n"
            "  回到所选的修改\n"
            "• Ctrl+C 复制区段名称"
        ),
        "dlg_size_fixed":        "X1、Y1 = 0（固定）",
        "dlg_size_warn":         "注意：第二组值 = {w}×{h}，"
                                 "保存时将自动同步。",

        # --- 按钮 ---
        "btn_save":              "保存",
        "btn_revert":            "撤销",
        "btn_history":           "历史",
        "btn_open_external":     "用记事本打开文件",
        "btn_open_external_tip": "用文本编辑器打开当前文件",
        "btn_reload":            "重新读取文件",
        "btn_reload_tip":        "重新从磁盘读取文件，以获取\n"
                                 "在其他程序中所做的修改。\n"
                                 "未保存的更改将会丢失。",
        "btn_open_folder":       "打开文件所在文件夹",
        "btn_add":               "添加",
        "btn_edit":              "修改",
        "btn_delete":            "删除",
        "btn_ok":                "确定",
        "btn_cancel":            "取消",
        "btn_close":             "关闭",
        "btn_copy":              "复制",

        # --- 按钮提示（鼠标悬停时显示）---
        "btn_save_tip":          "将更改写入当前文件（Ctrl+S）",
        "btn_revert_tip":        "放弃所有未保存的更改，\n"
                                 "将文件恢复到磁盘上的状态",
        "btn_history_tip":       "打开全部修改的列表，\n"
                                 "可回退到其中任意一步（Ctrl+H）",
        "btn_open_folder_tip":   "打开当前文件所在的文件夹\n"
                                 "并在其中选中该文件",
        "btn_add_tip":           "为选中的种族添加新的建筑图层",
        "btn_edit_tip":          "修改选中图层的参数",
        "btn_delete_tip":        "删除选中的图层。\n"
                                 "该操作可通过 Ctrl+Z 撤销。",
        "hist_revert_to_tip":    "将文件恢复到选中的历史记录行",
        "btn_close_tip":         "关闭窗口",
        "btn_ok_tip":            "应用更改并关闭窗口",
        "btn_cancel_tip":        "关闭窗口且不做任何更改",
        "btn_delete_ok_tip":     "删除该图层。\n"
                                 "该操作可通过 Ctrl+Z 撤销。",

        # --- 对话框 ---
        "err_read_title":        "读取错误",
        "err_read_msg":          "无法读取文件：\n{err}",
        "err_write_title":       "写入错误",
        "err_write_msg":         "无法保存文件：\n{err}",
        "err_open_title":        "打开错误",
        "err_open_msg":          "无法用外部程序打开文件：\n{err}",
        "unsaved_title":         "未保存的更改",
        "unsaved_msg":           "文件中有未保存的更改。\n"
                                 "是否在继续之前保存？",

        # --- 历史 ---
        "hist_title":            "修改历史",
        "hist_initial":          "— 文件初始状态 —",
        "hist_revert_to":        "回退到所选状态",
        "hist_current_mark":     "►",
        "hist_col_sec":          "区段",
        "hist_col_param":        "参数",
        "hist_col_before":       "修改前",
        "hist_col_after":        "修改后",
        "hist_param_dlgsize":    "DIALOG 窗口尺寸",
        "hist_none":             "—",

        # --- Capital.dat ---
        "layer_add_title":       "新建图层",
        "layer_edit_title":      "编辑图层",
        "fld_z":                 "Z 顺序（LAYER 编号）",
        "fld_build":             "建筑 ID（Gbuild）",
        "fld_image":             "图像名称（Capital.ff）",
        "fld_coords":            "坐标 X1、Y1、X2、Y2",
        "fld_extra":             "其他字段（逗号分隔）",
        "fld_layerinfo":         "为该建筑创建 LAYERINFO 记录",
        "err_layer_title":       "数据无效",
        "err_layer_z":           "Z 顺序必须是整数。",
        "err_layer_dup":         "该区段中已存在编号为 {z} 的图层。",
        "err_layer_coords":      "坐标必须是整数。",
        "del_title":             "删除图层",
        "del_msg":               "删除图层 {name}（{image}）？\n"
                                 "可通过 Ctrl+Z 撤销。",
        "del_layerinfo":         "同时删除 {build} 的 LAYERINFO 记录",
        "no_selection":          "未选中图层。",

        # --- 更新 ---
        "update_title":          "有可用更新",
        "update_msg":            "已发布新版本 {new}。\n"
                                 "当前版本为 {cur}。\n\n"
                                 "现在下载新版本吗？",
        "update_downloading":    "正在下载更新……",
        "update_done_title":     "更新已下载",
        "update_done_msg":       "新版本已保存在程序所在的文件夹中：\n"
                                 "{path}\n\n"
                                 "要启动它并关闭当前程序吗？",
        "update_fail_title":     "下载失败",
        "update_fail_msg":       "无法下载更新。\n{err}\n\n"
                                 "要在浏览器中打开发布页面吗？",

        # --- 关于 ---
        "about_title":           "关于",
        "about_support":         "支持开发",
        "about_name":            APP_TITLE,
        "about_version":         "版本 " + APP_VERSION,
        "about_text": (
            "Disciples 界面文件的可视化编辑器。\n\n"
            ".dlg 模式：用鼠标拖拽或手动输入坐标来\n"
            "更改界面元素的大小和位置。\n\n"
            "Capital.dat 模式：可视化地添加、修改和删除\n"
            "都城主界面（城市全景，而非单位发展分支）中的\n"
            "建筑图层。\n\n"
            "修改将写回文件并保留原始语法。"
        ),
    },
}

# =============================================================================
# ПАРСИНГ .DLG
# =============================================================================

ELEMENT_TYPES = {
    "BUTTON", "BUTTONSD", "EDIT", "IMAGE", "LBOX", "RADIO", "SCROLL",
    "SPIN", "TEXT", "TLBOX", "TOGGLE", "TOGGLESD",
}

COLOR_BG_WINDOW    = "#c8c0b0"
COLOR_BG_APP       = "#d4d0c8"
COLOR_BORDER_DARK  = "#404040"
COLOR_BORDER_MED   = "#808080"
COLOR_BORDER_LIGHT = "#ffffff"
COLOR_INPUT_BG     = "#ffffff"
COLOR_BUTTON_BG    = "#d4d0c8"
COLOR_TEXT         = "#000000"
COLOR_TEXT_MUTED   = "#606060"
COLOR_SELECTION    = "#0a64a4"
COLOR_DIALOG_FRAME = "#000000"
COLOR_WARN         = "#a04020"

# Цвета для режима Capital.dat.
COLOR_CAPITAL_BG   = "#3a4a34"   # «трава» — фон карты столицы
COLOR_LAYER_FILL   = "#b8a882"   # обычное здание
COLOR_LAYER_SYS    = "#8fa3b8"   # системный слой (без ID здания)
COLOR_LAYER_EDGE   = "#2a2a2a"


class DlgElement:
    def __init__(self, line_index, raw_line, kind, name, x1, y1, x2, y2,
                 prefix, suffix):
        self.line_index = line_index
        self.raw_line = raw_line
        self.kind = kind
        self.name = name
        self.x1 = x1
        self.y1 = y1
        self.x2 = x2
        self.y2 = y2
        self.prefix = prefix
        self.suffix = suffix


class DlgSection:
    def __init__(self, name, header_line_index, header_raw,
                 x1, y1, x2, y2, w2, h2,
                 prefix, middle, tail,
                 begin_line_index, end_line_index):
        self.name = name
        self.header_line_index = header_line_index
        self.header_raw = header_raw
        self.x1 = x1
        self.y1 = y1
        self.x2 = x2
        self.y2 = y2
        self.w2 = w2
        self.h2 = h2
        self.header_prefix = prefix
        self.header_middle = middle
        self.header_tail = tail
        self.begin_line_index = begin_line_index
        self.end_line_index = end_line_index
        self.elements = []


_ELEMENT_RE = re.compile(
    r"^(?P<prefix>\s+(?P<kind>[A-Z]+)\s+(?P<n>[A-Za-z0-9_]+),)"
    r"(?P<x1>-?\d+),(?P<y1>-?\d+),(?P<x2>-?\d+),(?P<y2>-?\d+)"
    r"(?P<suffix>.*)$"
)

_DIALOG_RE = re.compile(
    r"^(?P<prefix>DIALOG\s+(?P<n>[A-Za-z0-9_]+),)"
    r"(?P<x1>-?\d+),(?P<y1>-?\d+),(?P<x2>-?\d+),(?P<y2>-?\d+)"
    r"(?P<middle>,[^,]*,[^,]*,[^,]*,[^,]*,[^,]*,[^,]*,)"
    r"(?P<w2>-?\d+),(?P<h2>-?\d+)"
    r"(?P<tail>.*)$"
)


def parse_dlg_file(path):
    with open(path, "rb") as f:
        raw = f.read()
    line_ending = "\r\n" if b"\r\n" in raw else "\n"
    text = raw.decode("cp1252", errors="replace")
    lines = text.split(line_ending)
    sections = []
    current = None
    in_body = False
    for i, line in enumerate(lines):
        if not in_body:
            m = _DIALOG_RE.match(line)
            if m:
                current = DlgSection(
                    name=m.group("n"), header_line_index=i, header_raw=line,
                    x1=int(m.group("x1")), y1=int(m.group("y1")),
                    x2=int(m.group("x2")), y2=int(m.group("y2")),
                    w2=int(m.group("w2")), h2=int(m.group("h2")),
                    prefix=m.group("prefix"), middle=m.group("middle"),
                    tail=m.group("tail"),
                    begin_line_index=-1, end_line_index=-1,
                )
                continue
            if current is not None and line.strip().upper() == "BEGIN":
                current.begin_line_index = i
                in_body = True
                continue
        else:
            if line.strip().upper() == "END":
                current.end_line_index = i
                sections.append(current)
                current = None
                in_body = False
                continue
            m = _ELEMENT_RE.match(line)
            if m and m.group("kind") in ELEMENT_TYPES:
                el = DlgElement(
                    line_index=i, raw_line=line,
                    kind=m.group("kind"), name=m.group("n"),
                    x1=int(m.group("x1")), y1=int(m.group("y1")),
                    x2=int(m.group("x2")), y2=int(m.group("y2")),
                    prefix=m.group("prefix"), suffix=m.group("suffix"),
                )
                current.elements.append(el)
    return lines, sections, line_ending


def write_dlg_file(path, lines, sections, line_ending):
    out_lines = list(lines)
    for section in sections:
        out_lines[section.header_line_index] = (
            f"{section.header_prefix}"
            f"{section.x1},{section.y1},{section.x2},{section.y2}"
            f"{section.header_middle}"
            f"{section.w2},{section.h2}"
            f"{section.header_tail}"
        )
        for el in section.elements:
            out_lines[el.line_index] = (
                f"{el.prefix}{el.x1},{el.y1},{el.x2},{el.y2}{el.suffix}"
            )
    text = line_ending.join(out_lines)
    with open(path, "wb") as f:
        f.write(text.encode("cp1252", errors="replace"))


# =============================================================================
# ПАРСИНГ CAPITAL.DAT
#
# Формат (см. https://d2ext.sklabs.ru/ru/articles/modding-buildings-in-the-capital):
#
#   [HUMAN]
#   LayerInfoCount=26
#   LAYERINFO_00=1,,                        флаг, ID здания, (пусто)
#   LAYERINFO_01=0,G000BB0001,
#   ...
#   LayerCount=31
#   LAYER_160=G000BB0001,EMP_STABLE,0,0,0,,0,0,0,520,524,640,600
#   ^^^^^^^^^ ^^^^^^^^^^ ^^^^^^^^^^ ^^^^^^^^^^^^ ^^^^^^^^^^^^^^^
#   Z-order   ID здания  имя картинки  доп. поля   X1,Y1,X2,Y2
#
# Объявленные счётчики (LayerCount / LayerInfoCount) в оригинальных файлах
# не всегда совпадают с фактическим количеством строк, поэтому мы храним
# исходное значение и меняем его только на дельту при добавлении/удалении.
# Так гарантируется побайтовый round-trip нетронутого файла.
# =============================================================================

_DAT_SECTION_RE   = re.compile(r"^\s*\[([^\]]+)\]\s*$")
_DAT_LAYERINFO_RE = re.compile(r"^(LAYERINFO_\w+)=(.*)$", re.IGNORECASE)
_DAT_LAYER_RE     = re.compile(r"^(LAYER_\w+)=(.*)$", re.IGNORECASE)
_DAT_LICOUNT_RE   = re.compile(r"^LayerInfoCount=(-?\d+)\s*$", re.IGNORECASE)
_DAT_LCOUNT_RE    = re.compile(r"^LayerCount=(-?\d+)\s*$", re.IGNORECASE)

# Индексы координат внутри списка полей строки LAYER_*.
DAT_COORD_OFFSET = 9
DAT_FIELD_COUNT = 13

# Вторичные («картиночные») координаты слоя — поля 3 и 4:
#   LAYER_99=G000BB0100,EL_CENTORHOLE,0,274,475,,0,0,0,309,497,383,564
#                                       ^^^ ^^^                (X, Y картинки)
# Первые четыре координаты (поля 9..12) — программная рамка здания, а поля
# 3 и 4 задают положение самой картинки на экране. Смещение картинки
# относительно рамки у каждого слоя своё, поэтому при перемещении слоя мы
# сдвигаем вторичные координаты на ту же дельту, сохраняя это смещение.
DAT_IMG_X_INDEX = 3
DAT_IMG_Y_INDEX = 4


def _to_int(value, default=0):
    try:
        return int(str(value).strip())
    except (TypeError, ValueError):
        return default


class DatLayerInfo:
    """Строка LAYERINFO_xx=флаг,ID_здания,"""

    def __init__(self, key, fields):
        self.key = key
        self.fields = list(fields)
        while len(self.fields) < 3:
            self.fields.append("")

    @property
    def build_id(self):
        return self.fields[1]

    @build_id.setter
    def build_id(self, value):
        self.fields[1] = value

    def to_line(self):
        return f"{self.key}={','.join(self.fields)}"


class DatLayer:
    """Строка LAYER_zzz=ID,IMAGE,...,X1,Y1,X2,Y2"""

    def __init__(self, key, fields):
        self.key = key
        self.fields = list(fields)
        while len(self.fields) < DAT_FIELD_COUNT:
            self.fields.append("0")

    # --- Z-order --------------------------------------------------------
    @property
    def z(self):
        return _to_int(self.key.split("_", 1)[1], 0)

    # --- Поля -----------------------------------------------------------
    @property
    def build_id(self):
        return self.fields[0]

    @build_id.setter
    def build_id(self, value):
        self.fields[0] = value

    @property
    def image(self):
        return self.fields[1]

    @image.setter
    def image(self, value):
        self.fields[1] = value

    @property
    def extra(self):
        """Поля между именем картинки и координатами."""
        return self.fields[2:DAT_COORD_OFFSET]

    @extra.setter
    def extra(self, values):
        self.fields[2:DAT_COORD_OFFSET] = list(values)

    # --- Координаты (интерфейс, совместимый с DlgElement) ----------------
    def _coord(self, i):
        return _to_int(self.fields[DAT_COORD_OFFSET + i], 0)

    def _set_coord(self, i, value):
        self.fields[DAT_COORD_OFFSET + i] = str(int(value))

    # --- Вторичные координаты (положение картинки на экране) -------------
    @property
    def img_x(self):
        return _to_int(self.fields[DAT_IMG_X_INDEX], 0)

    @img_x.setter
    def img_x(self, value):
        self.fields[DAT_IMG_X_INDEX] = str(int(value))

    @property
    def img_y(self):
        return _to_int(self.fields[DAT_IMG_Y_INDEX], 0)

    @img_y.setter
    def img_y(self, value):
        self.fields[DAT_IMG_Y_INDEX] = str(int(value))

    def shift_secondary(self, dx, dy):
        """Сдвигает вторичные координаты вслед за рамкой слоя."""
        if not dx and not dy:
            return
        self.img_x = self.img_x + int(dx)
        self.img_y = self.img_y + int(dy)

    x1 = property(lambda s: s._coord(0), lambda s, v: s._set_coord(0, v))
    y1 = property(lambda s: s._coord(1), lambda s, v: s._set_coord(1, v))
    x2 = property(lambda s: s._coord(2), lambda s, v: s._set_coord(2, v))
    y2 = property(lambda s: s._coord(3), lambda s, v: s._set_coord(3, v))

    @property
    def name(self):
        """Отображаемое имя — так же, как у DlgElement."""
        return self.image or self.build_id or self.key

    @property
    def kind(self):
        return "LAYER"

    def drawable(self):
        """Слои с -1 или нулевым размером в игре не позиционируются."""
        return self.x2 > self.x1 and self.y2 > self.y1 and \
            self.x1 >= 0 and self.y1 >= 0

    def to_line(self):
        return f"{self.key}={','.join(self.fields)}"

    @staticmethod
    def make(z, build_id, image, extra, coords):
        fields = [build_id, image] + list(extra) + [str(int(c)) for c in coords]
        return DatLayer(f"LAYER_{z:02d}", fields)


class DatSection:
    """Секция [HUMAN] / [UNDEAD] / ... файла Capital.dat."""

    def __init__(self, name):
        self.name = name
        self.layerinfos = []
        self.layers = []
        # Объявленные в файле счётчики (могут не совпадать с фактическими).
        self.li_count = 0
        self.layer_count = 0
        # Сколько пустых строк стоит перед заголовком секции — нужно для
        # побайтового round-trip (в оригинале разметка неравномерная).
        self.blank_before = 0

    # Совместимость с кодом, работающим с DlgSection.
    @property
    def elements(self):
        return self.layers

    def next_free_z(self, preferred=None):
        used = {l.z for l in self.layers}
        z = preferred if preferred is not None else 1
        while z in used:
            z += 1
        return z

    def next_layerinfo_key(self):
        idx = len(self.layerinfos)
        return f"LAYERINFO_{idx:02d}"

    def has_layerinfo(self, build_id):
        bid = (build_id or "").strip().upper()
        if not bid:
            return False
        return any((li.build_id or "").strip().upper() == bid
                   for li in self.layerinfos)


def parse_dat_file(path):
    with open(path, "rb") as f:
        raw = f.read()
    line_ending = "\r\n" if b"\r\n" in raw else "\n"
    text = raw.decode("cp1252", errors="replace")
    lines = text.split(line_ending)

    sections = []
    current = None
    pending_blanks = 0
    for line in lines:
        if not line.strip():
            pending_blanks += 1
            continue
        m = _DAT_SECTION_RE.match(line)
        if m:
            current = DatSection(m.group(1))
            current.blank_before = pending_blanks
            pending_blanks = 0
            sections.append(current)
            continue
        pending_blanks = 0
        if current is None:
            continue
        m = _DAT_LICOUNT_RE.match(line.strip())
        if m:
            current.li_count = int(m.group(1))
            continue
        m = _DAT_LCOUNT_RE.match(line.strip())
        if m:
            current.layer_count = int(m.group(1))
            continue
        m = _DAT_LAYERINFO_RE.match(line.strip())
        if m:
            current.layerinfos.append(
                DatLayerInfo(m.group(1), m.group(2).split(",")))
            continue
        m = _DAT_LAYER_RE.match(line.strip())
        if m:
            current.layers.append(
                DatLayer(m.group(1), m.group(2).split(",")))
            continue
    return sections, line_ending, pending_blanks


def write_dat_file(path, sections, line_ending, trailing_blanks=0):
    out = []
    for sec in sections:
        out.extend([""] * sec.blank_before)      # разделители между секциями
        out.append(f"[{sec.name}]")
        out.append(f"LayerInfoCount={sec.li_count}")
        out.extend(li.to_line() for li in sec.layerinfos)
        out.append(f"LayerCount={sec.layer_count}")
        out.extend(l.to_line() for l in sec.layers)
    out.extend([""] * trailing_blanks)
    text = line_ending.join(out)
    with open(path, "wb") as f:
        f.write(text.encode("cp1252", errors="replace"))


# =============================================================================
# ПРОВЕРКА ОБНОВЛЕНИЙ
#
# Сеть трогаем только в фоновом потоке и только на чтение публичного API
# GitHub. Любая ошибка — нет сети, нет релизов, изменился формат ответа —
# гасится молча: проверка обновлений не должна мешать запуску редактора.
# =============================================================================


def parse_version(text):
    """'v1.2' -> (1, 2). Нечисловой хвост отбрасывается, мусор даёт ()."""
    if not text:
        return ()
    parts = []
    for chunk in re.split(r"[._\-+]", str(text).strip().lstrip("vV")):
        m = re.match(r"^(\d+)", chunk)
        if not m:
            break
        parts.append(int(m.group(1)))
    return tuple(parts)


def is_newer(candidate, current):
    """True, если версия candidate строго новее current."""
    a = parse_version(candidate)
    return bool(a) and a > parse_version(current)


def _github_request(url):
    return urllib.request.Request(url, headers={
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
        # GitHub отклоняет запросы без User-Agent.
        "User-Agent": f"DLG-Editor-for-Disciples/{APP_VERSION}",
    })


def fetch_latest_release():
    """Последний релиз: (тег, страница, ссылка_на_exe|None, имя_exe|None)."""
    req = _github_request(UPDATE_API_URL)
    with urllib.request.urlopen(req, timeout=UPDATE_TIMEOUT) as resp:
        data = json.loads(resp.read().decode("utf-8", errors="replace"))
    tag = (data.get("tag_name") or "").strip()
    if not tag:
        return None
    page = data.get("html_url") or UPDATE_PAGE_URL
    # Имена ассетов между релизами не согласованы (в v1.1 был .zip, в v1.2 —
    # .exe), поэтому ищем первый .exe, а если его нет — отправим на страницу.
    for asset in data.get("assets") or []:
        name = (asset.get("name") or "").strip()
        if name.lower().endswith(".exe") and asset.get("browser_download_url"):
            return tag, page, asset["browser_download_url"], name
    return tag, page, None, None


def download_file(url, dest_path, timeout=120):
    """Качает во временный .part и переименовывает: обрыв связи не оставит
    рядом с программой недокачанный exe."""
    tmp_path = dest_path + ".part"
    req = _github_request(url)
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            with open(tmp_path, "wb") as f:
                while True:
                    chunk = resp.read(65536)
                    if not chunk:
                        break
                    f.write(chunk)
        os.replace(tmp_path, dest_path)
    except Exception:
        try:
            os.remove(tmp_path)
        except OSError:
            pass
        raise
    return dest_path


def running_as_exe():
    """True, если программа запущена собранным exe, а не как .py-скрипт."""
    return bool(getattr(sys, "frozen", False))


# =============================================================================
# GUI
# =============================================================================

CANVAS_W = 800
CANVAS_H = 600
HANDLE_SIZE = 6

HIT_NONE = 0
HIT_INSIDE = 1
HIT_L = 2
HIT_R = 4
HIT_T = 8
HIT_B = 16
HIT_DIALOG = "dialog"

# Ширина боковых колонок — фиксирована, центр тянется на всё остальное.
LEFT_WIDTH = 260
RIGHT_WIDTH = 400   # с запасом на полосу прокрутки панели: без него
                    # кнопки в заголовке «Подсказки» обрезаются
# Высота видимой части блока подсказок (остальное — прокруткой).
HINTS_HEIGHT = 120


# =============================================================================
# ФЛАГИ ЯЗЫКОВ В МЕНЮ
#
# Флаг — визуальная подсказка: человек, запустивший программу на чужом языке,
# находит переключатель по картинке, не читая надписей. Поэтому флаги рисуются
# кодом, а не берутся эмодзи: символы 🇷🇺 и подобные лежат за пределами BMP,
# и Tk 8.6 на Windows выводит вместо них пустые прямоугольники. Внешних файлов
# у программы тоже нет — она распространяется одним exe.
# =============================================================================

FLAG_W, FLAG_H = 16, 11

# Приписка к пункту «Язык» в строке меню — см. _build_menu.
LANG_CODES = " (RU/EN/PL/中文)"


def _make_flag(code):
    """Флаг 16×11 для кода языка. Возвращает tk.PhotoImage."""
    img = tk.PhotoImage(width=FLAG_W, height=FLAG_H)

    def band(color, y1, y2):
        img.put(color, to=(0, y1, FLAG_W, y2))

    def dot(color, x, y):
        if 0 <= x < FLAG_W and 0 <= y < FLAG_H:
            img.put(color, to=(x, y, x + 1, y + 1))

    if code == "ru":
        band("#ffffff", 0, 4)
        band("#0039a6", 4, 8)
        band("#d52b1e", 8, FLAG_H)
    elif code == "pl":
        band("#ffffff", 0, 6)
        band("#dc143c", 6, FLAG_H)
    elif code == "zh":
        band("#de2910", 0, FLAG_H)
        for x, y in ((3, 1), (2, 2), (3, 2), (4, 2), (2, 3), (4, 3), (3, 4)):
            dot("#ffde00", x, y)          # большая звезда
        for x, y in ((6, 1), (8, 2), (8, 4), (6, 5)):
            dot("#ffde00", x, y)          # четыре малые
    else:                                  # en — Union Jack, упрощённый
        band("#012169", 0, FLAG_H)
        for x in range(FLAG_W):           # белые диагонали
            y = round(x * (FLAG_H - 1) / (FLAG_W - 1))
            dot("#ffffff", x, y)
            dot("#ffffff", x, FLAG_H - 1 - y)
        img.put("#ffffff", to=(6, 0, 10, FLAG_H))     # белый крест
        band("#ffffff", 4, 7)
        img.put("#c8102e", to=(7, 0, 9, FLAG_H))      # красный крест
        band("#c8102e", 5, 6)

    for x in range(FLAG_W):               # рамка, иначе белый край сливается
        dot("#808080", x, 0)
        dot("#808080", x, FLAG_H - 1)
    for y in range(FLAG_H):
        dot("#808080", 0, y)
        dot("#808080", FLAG_W - 1, y)
    return img


# =============================================================================
# РАЗМЕЩЕНИЕ ОКОН В ВИДИМОЙ ОБЛАСТИ
#
# Правило: любой элемент интерфейса должен быть виден целиком при любом
# сценарии — окно развёрнуто, окно у края экрана, панель задач снизу, сбоку
# или скрыта, экран любого размера. Поэтому позицию всплывающих окон всегда
# считаем от рабочей области, а не от координат виджета.
# =============================================================================


def work_area(widget):
    """Видимая область экрана без панели задач: (ширина, высота).

    wm_maxsize на Windows возвращает именно рабочую область — экран минус
    панель задач, где бы она ни стояла. На других системах отдаёт размер
    экрана, что тоже верный ответ. На winfo_screenheight полагаться нельзя:
    он про панель задач не знает.
    """
    try:
        w, h = widget.winfo_toplevel().wm_maxsize()
    except tk.TclError:
        w = h = 0
    return (min(w or widget.winfo_screenwidth(), widget.winfo_screenwidth()),
            min(h or widget.winfo_screenheight(), widget.winfo_screenheight()))


def place_in_view(win, x, y, ref=None):
    """Ставит окно в (x, y), сдвигая его так, чтобы оно влезло целиком.

    ref — виджет, по которому меряется рабочая область. Указывать его нужно
    всегда: wm_maxsize отдаёт рабочую область только для главного окна
    программы, а у дочерних окон и окон без рамки — весь экран вместе с
    панелью задач.

    Рамка и заголовок окна в winfo_width/height не входят, но место на экране
    занимают, а портативного способа спросить их размер у системы нет —
    поэтому меряем по разнице между заданной и фактической позицией.
    """
    aw, ah = work_area(ref if ref is not None else win)
    win.wm_geometry(f"+{x}+{y}")
    win.update_idletasks()
    border = max(0, win.winfo_rootx() - x)
    title = max(0, win.winfo_rooty() - y)
    full_w = win.winfo_width() + 2 * border
    full_h = win.winfo_height() + title + border
    x = max(0, min(x, aw - full_w))
    y = max(0, min(y, ah - full_h))
    win.wm_geometry(f"+{x}+{y}")


def menu_font():
    """Шрифт меню, в котором есть собственные иероглифы.

    Стандартный TkMenuFont — Segoe UI, китайских глифов в нём нет. Windows
    подставляет их при отрисовке, а ширину пункта Tk считает по исходному
    шрифту: место выделяется под 48 пикселей, рисуется вдвое шире, и от
    «简体中文» видно один иероглиф. Со шрифтом, где глифы свои, подстановки
    не происходит и обрезать нечего.

    Начертание берём обычное, а не как у TkMenuFont: на части систем он
    объявлен жирным, и в другом семействе это выглядит тяжело.
    """
    base = tkfont.nametofont("TkMenuFont")
    families = set(tkfont.families())
    for name in ("Microsoft YaHei UI", "Microsoft YaHei",   # Windows
                 "PingFang SC", "Heiti SC",                 # macOS
                 "Noto Sans CJK SC", "WenQuanYi Micro Hei"):  # Linux
        if name in families:
            return tkfont.Font(family=name, size=base.actual("size"),
                               weight="normal")
    return base


class Tooltip:
    """Всплывающая подсказка у виджета.

    Текст берётся функцией, а не строкой: язык программы меняется на лету,
    и подсказка должна показывать текущий, а не тот, что был при создании.
    """

    def __init__(self, widget, text_func, delay=450):
        self.widget = widget
        self.text_func = text_func
        self.delay = delay
        self._after_id = None
        self._win = None
        widget.bind("<Enter>", self._schedule, add="+")
        widget.bind("<Leave>", self._hide, add="+")
        widget.bind("<ButtonPress>", self._hide, add="+")

    def _schedule(self, _event=None):
        self._cancel()
        self._after_id = self.widget.after(self.delay, self._show)

    def _cancel(self):
        if self._after_id is not None:
            self.widget.after_cancel(self._after_id)
            self._after_id = None

    def _show(self):
        text = self.text_func()
        if not text or self._win is not None:
            return
        self._win = tk.Toplevel(self.widget)
        self._win.wm_overrideredirect(True)
        tk.Label(self._win, text=text, justify="left", bg="#ffffe1",
                 fg=COLOR_TEXT, relief="solid", borderwidth=1,
                 font=("Segoe UI", 8), padx=6, pady=3).pack()
        self._win.update_idletasks()
        # Кнопки внизу панели: подсказка под ними уходит под панель задач,
        # поэтому если снизу места нет — показываем её над кнопкой. Сдвиг по
        # горизонтали и окончательную проверку делает place_in_view.
        x = self.widget.winfo_rootx()
        y = self.widget.winfo_rooty() + self.widget.winfo_height() + 4
        if y + self._win.winfo_height() > work_area(self.widget)[1]:
            y = self.widget.winfo_rooty() - self._win.winfo_height() - 4
        place_in_view(self._win, x, y, ref=self.widget)

    def _hide(self, _event=None):
        self._cancel()
        if self._win is not None:
            self._win.destroy()
            self._win = None


class HistoryEntry:
    """Одно действие в истории.

    Для таблицы истории: секция, параметр (имя элемента / картинки слоя),
    значение «было» и значение «стало». Плюс снимки данных до и после —
    по ним работают откат и повтор.
    """

    def __init__(self, section, param, old_value, new_value, before, after):
        self.section = section
        self.param = param
        self.old_value = old_value
        self.new_value = new_value
        self.before = before
        self.after = after


class DlgEditorApp:
    def __init__(self, root, initial_path=None):
        self.root = root
        self.root.configure(bg=COLOR_BG_APP)

        self.lang = "ru"
        self.mode = MODE_DLG
        self.file_path = None
        self.lines = []
        self.sections = []
        self.line_ending = "\r\n"
        self.trailing_blanks = 0
        self.current_section = None
        self.selected_element = None
        self.dirty = False
        self._filtered_sections = []

        # История изменений (своя на каждый открытый файл; хранится целиком).
        self.dat_secondary = True     # править вторичные координаты в .dat
        self.history = []
        self.hist_index = 0
        self.saved_index = 0
        self.base_snapshot = None
        self.hist_selected = 0          # выделенная строка в таблице истории
        self.hist_cells = {}            # индекс строки -> её ячейки (Label)

        self.drag_target = None
        self.drag_mode = HIT_NONE
        self.drag_start_x = 0
        self.drag_start_y = 0
        self.drag_orig = None
        self.drag_orig_img = None      # вторичные координаты слоя до перетаскивания

        self.element_to_rect = {}
        self.dialog_rect_id = None
        self._history_win = None

        # Строка «Загружено»: ключ и подстановки последней загрузки. Хранятся,
        # чтобы пересобрать её при смене языка и при изменении ширины окна.
        self._status_loaded = None
        self._status_text = ""        # текст, который выставили мы сами

        # Версия, от обновления на которую пользователь отказался.
        self.skipped_version = ""
        self._update_busy = False

        migrate_settings()
        # Загружаем настройки до построения UI, чтобы язык был сразу верным.
        (saved_lang, saved_file, saved_maximized, saved_section,
         saved_dat_secondary, saved_skipped) = self._load_settings()
        if saved_lang and saved_lang in STRINGS:
            self.lang = saved_lang
        self.dat_secondary = saved_dat_secondary
        self.skipped_version = saved_skipped or ""

        self._apply_initial_geometry()
        self._setup_styles()
        # Картинки флагов держим на себе: Tk удаляет PhotoImage, на который
        # не осталось ссылок из Python, и пункты меню становятся пустыми.
        self.flag_images = {c: _make_flag(c) for c in ("ru", "en", "pl", "zh")}
        # Отметка текущего языка в меню; меню пересоздаётся, переменная — нет.
        self.lang_var = tk.StringVar(value=self.lang)
        self.menu_font = menu_font()
        self._build_ui()
        self._bind_shortcuts()
        self._apply_language()

        if saved_maximized:
            self.root.state("zoomed")

        # Приоритет: аргумент командной строки > сохранённый файл.
        open_path = initial_path if initial_path else saved_file
        if open_path and os.path.isfile(open_path):
            self._open_file(open_path)
            if saved_section and not initial_path:
                self._select_section_by_name(saved_section)

        # Проверка обновлений — после того как окно отрисовано, в фоне.
        self.root.after(UPDATE_DELAY_MS, self._start_update_check)

    def t(self, key, **kw):
        s = STRINGS.get(self.lang, STRINGS["en"]).get(key, key)
        if kw:
            s = s.format(**kw)
        return s

    # --- Geometry ----------------------------------------------------------

    def _apply_initial_geometry(self):
        """Окно масштабируется под текущий экран (важно для 4K)."""
        sw = self.root.winfo_screenwidth()
        sh = self.root.winfo_screenheight()
        w = max(1000, min(int(sw * 0.85), sw - 80))
        h = max(680, min(int(sh * 0.85), sh - 120))
        x = max(0, (sw - w) // 2)
        y = max(0, (sh - h) // 3)
        self.root.geometry(f"{w}x{h}+{x}+{y}")
        self.root.minsize(980, 620)

    # --- Settings ----------------------------------------------------------

    def _load_settings(self):
        """Читает ini: (lang, last_file, maximized, last_section,
        dat_secondary, skipped_version)."""
        cfg = configparser.ConfigParser()
        try:
            cfg.read(SETTINGS_PATH, encoding="utf-8")
            lang = cfg.get("General", "language", fallback=None)
            last_file = cfg.get("General", "last_file", fallback=None)
            maximized = cfg.get("General", "maximized", fallback="0")
            last_section = cfg.get("General", "last_section", fallback=None)
            dat_secondary = cfg.get("General", "dat_secondary", fallback="1")
            # Версия, от обновления на которую пользователь отказался.
            skipped = cfg.get("Update", "skipped_version", fallback="")
            return (lang, last_file, maximized == "1", last_section,
                    dat_secondary != "0", skipped)
        except Exception:
            return None, None, False, None, True, ""

    def _save_settings(self):
        cfg = configparser.ConfigParser()
        cfg["General"] = {
            "language": self.lang,
            "last_file": self.file_path or "",
            "maximized": "1" if self.root.state() == "zoomed" else "0",
            "last_section": self.current_section.name if self.current_section else "",
            "dat_secondary": "1" if self.dat_secondary else "0",
        }
        cfg["Update"] = {"skipped_version": self.skipped_version or ""}
        try:
            with open(SETTINGS_PATH, "w", encoding="utf-8") as f:
                cfg.write(f)
        except Exception:
            pass  # не критично — если не получилось записать, работаем дальше

    # --- Style -------------------------------------------------------------

    def _setup_styles(self):
        style = ttk.Style()
        try:
            style.theme_use("clam")
        except tk.TclError:
            pass
        style.configure(".", background=COLOR_BG_APP, foreground=COLOR_TEXT,
                        fieldbackground=COLOR_INPUT_BG)
        style.configure("TFrame", background=COLOR_BG_APP)
        style.configure("TLabel", background=COLOR_BG_APP, foreground=COLOR_TEXT)
        style.configure("TLabelframe", background=COLOR_BG_APP,
                        foreground=COLOR_TEXT)
        style.configure("TLabelframe.Label", background=COLOR_BG_APP,
                        foreground=COLOR_TEXT)
        style.configure("TEntry", fieldbackground=COLOR_INPUT_BG,
                        foreground=COLOR_TEXT)
        style.configure("TCheckbutton", background=COLOR_BG_APP,
                        foreground=COLOR_TEXT)
        style.configure("Treeview", background=COLOR_INPUT_BG,
                        fieldbackground=COLOR_INPUT_BG, foreground=COLOR_TEXT)
        style.configure("Treeview.Heading", background=COLOR_BG_APP,
                        foreground=COLOR_TEXT)
        style.configure("TButton", background=COLOR_BG_APP,
                        foreground=COLOR_TEXT)
        # Маленькая кнопка (например «Открыть» рядом с подсказками).
        style.configure("Small.TButton", background=COLOR_BG_APP,
                        foreground=COLOR_TEXT, padding=(4, 0),
                        font=("Segoe UI", 8))
        # Цветные кнопки.
        style.configure("Save.TButton",
                        background="#64DF85", foreground=COLOR_TEXT)
        style.map("Save.TButton",
                  background=[("active", "#50C870"), ("pressed", "#40B860")])
        style.configure("Revert.TButton",
                        background="#FFDF40", foreground=COLOR_TEXT)
        style.map("Revert.TButton",
                  background=[("active", "#E8CC38"), ("pressed", "#D4BA30")])
        style.configure("History.TButton",
                        background="#9CC4E4", foreground=COLOR_TEXT)
        style.map("History.TButton",
                  background=[("active", "#88B2D4"), ("pressed", "#74A0C4")])
        # Маленькая кнопка в цвете «Отменить» — «Перечитать файл».
        style.configure("SmallRevert.TButton",
                        background="#FFDF40", foreground=COLOR_TEXT,
                        padding=(4, 0), font=("Segoe UI", 8))
        style.map("SmallRevert.TButton",
                  background=[("active", "#E8CC38"), ("pressed", "#D4BA30")])
        # Маленькая кнопка в цвете «Истории» — «Открыть в блокноте».
        style.configure("SmallHistory.TButton",
                        background="#9CC4E4", foreground=COLOR_TEXT,
                        padding=(4, 0), font=("Segoe UI", 8))
        style.map("SmallHistory.TButton",
                  background=[("active", "#88B2D4"), ("pressed", "#74A0C4")])

    # --- UI build ----------------------------------------------------------

    def _build_ui(self):
        self._build_menu()

        main = ttk.Frame(self.root)
        main.pack(fill="both", expand=True)
        # Боковые колонки фиксированы, центр забирает всё свободное место.
        main.columnconfigure(0, weight=0, minsize=LEFT_WIDTH)
        main.columnconfigure(1, weight=1)
        main.columnconfigure(2, weight=0, minsize=RIGHT_WIDTH)
        main.rowconfigure(0, weight=1)

        self._build_left(main)
        self._build_center(main)
        self._build_right(main)

    def _build_left(self, main):
        left = ttk.Frame(main, padding=4, width=LEFT_WIDTH)
        left.grid(row=0, column=0, sticky="nsew")
        left.grid_propagate(False)
        left.rowconfigure(3, weight=1)
        left.columnconfigure(0, weight=1)

        self.lbl_sections = ttk.Label(left, text="...")
        self.lbl_sections.grid(row=0, column=0, sticky="w")
        self.search_var = tk.StringVar()
        self.search_var.trace_add("write",
                                  lambda *a: self._refresh_section_list())
        ttk.Entry(left, textvariable=self.search_var).grid(
            row=1, column=0, sticky="ew", pady=(2, 4))

        # --- Фильтры по размеру (только для .dlg) ---
        self.filter_frame = ttk.Frame(left)
        self.filter_frame.grid(row=2, column=0, sticky="ew", pady=(0, 4))
        self.filter_frame.columnconfigure(1, weight=1)

        ttk.Label(self.filter_frame, text="W").grid(row=0, column=0, padx=(0, 2))
        self.filter_w_op = tk.StringVar(value="—")
        self.filter_w_val = tk.StringVar(value="")
        ttk.Combobox(self.filter_frame, textvariable=self.filter_w_op,
                     values=["—", "=", ">", ">=", "<", "<="],
                     width=3, state="readonly").grid(row=0, column=1, padx=2)
        ttk.Entry(self.filter_frame, textvariable=self.filter_w_val,
                  width=5, justify="right").grid(row=0, column=2, padx=(2, 0))

        ttk.Label(self.filter_frame, text="H").grid(row=1, column=0, padx=(0, 2),
                                                    pady=(2, 0))
        self.filter_h_op = tk.StringVar(value="—")
        self.filter_h_val = tk.StringVar(value="")
        ttk.Combobox(self.filter_frame, textvariable=self.filter_h_op,
                     values=["—", "=", ">", ">=", "<", "<="],
                     width=3, state="readonly").grid(row=1, column=1, padx=2,
                                                     pady=(2, 0))
        ttk.Entry(self.filter_frame, textvariable=self.filter_h_val,
                  width=5, justify="right").grid(row=1, column=2, padx=(2, 0),
                                                 pady=(2, 0))

        for var in (self.filter_w_op, self.filter_w_val,
                    self.filter_h_op, self.filter_h_val):
            var.trace_add("write", lambda *a: self._refresh_section_list())

        self.section_listbox = tk.Listbox(
            left, exportselection=False, activestyle="dotbox",
            bg=COLOR_INPUT_BG, fg=COLOR_TEXT,
            selectbackground=COLOR_SELECTION, selectforeground="#ffffff",
            highlightthickness=1, highlightbackground=COLOR_BORDER_DARK,
            relief="flat", borderwidth=0,
        )
        self.section_listbox.grid(row=3, column=0, sticky="nsew")
        sb = ttk.Scrollbar(left, orient="vertical",
                           command=self.section_listbox.yview)
        sb.grid(row=3, column=1, sticky="ns")
        self.section_listbox.config(yscrollcommand=sb.set)
        self.section_listbox.bind("<<ListboxSelect>>", self._on_section_select)

        # Копирование имени секции: Ctrl+C и контекстное меню.
        self.section_menu = tk.Menu(self.root, tearoff=0)
        # Ctrl+C обрабатывается общим обработчиком _on_control_key.
        self.section_listbox.bind("<Button-3>", self._on_section_right_click)

    def _build_center(self, main):
        center = ttk.Frame(main, padding=4)
        center.grid(row=0, column=1, sticky="nsew")
        center.rowconfigure(1, weight=1)
        center.columnconfigure(0, weight=1)

        self.status_var = tk.StringVar(value="...")
        # width=1 + sticky="ew": ширину метке задаёт колонка, а не её текст,
        # иначе длинный путь растянул бы окно за пределы экрана.
        self.status_font = tkfont.nametofont("TkDefaultFont")
        self.status_label = ttk.Label(
            center, textvariable=self.status_var, font=self.status_font,
            foreground=COLOR_TEXT_MUTED, width=1, anchor="w")
        self.status_label.grid(row=0, column=0, sticky="ew")
        self.status_label.bind("<Configure>", self._on_status_resize)

        canvas_frame = ttk.Frame(center)
        canvas_frame.grid(row=1, column=0, sticky="nsew", pady=(2, 0))
        canvas_frame.rowconfigure(0, weight=1)
        canvas_frame.columnconfigure(0, weight=1)

        self.canvas = tk.Canvas(
            canvas_frame, bg=COLOR_BG_APP, highlightthickness=0, bd=0,
            scrollregion=(0, 0, CANVAS_W, CANVAS_H),
        )
        self.canvas.grid(row=0, column=0, sticky="nsew")

        self.h_scroll = ttk.Scrollbar(canvas_frame, orient="horizontal",
                                      command=self.canvas.xview)
        self.h_scroll.grid(row=1, column=0, sticky="ew")
        self.v_scroll = ttk.Scrollbar(canvas_frame, orient="vertical",
                                      command=self.canvas.yview)
        self.v_scroll.grid(row=0, column=1, sticky="ns")
        self.canvas.configure(xscrollcommand=self.h_scroll.set,
                              yscrollcommand=self.v_scroll.set)

        self.canvas.bind("<Motion>", self._on_canvas_motion)
        self.canvas.bind("<ButtonPress-1>", self._on_canvas_press)
        self.canvas.bind("<B1-Motion>", self._on_canvas_drag)
        self.canvas.bind("<ButtonRelease-1>", self._on_canvas_release)
        # Размер холста меняется вместе с окном — пересчитываем область прокрутки.
        self.canvas.bind("<Configure>", lambda _e: self._update_scrollregion())

    def _build_right(self, main):
        # Правая панель лежит на холсте с прокруткой: при небольшой высоте
        # экрана список элементов, поля координат и нижние кнопки в панель
        # целиком не помещаются, и без прокрутки кнопки становятся
        # недоступны. Полоса появляется только когда содержимое не влезло.
        outer = ttk.Frame(main, width=RIGHT_WIDTH)
        outer.grid(row=0, column=2, sticky="nsew")
        outer.grid_propagate(False)
        outer.columnconfigure(0, weight=1)
        outer.rowconfigure(0, weight=1)

        self.right_canvas = tk.Canvas(outer, bg=COLOR_BG_APP,
                                      highlightthickness=0, bd=0)
        self.right_canvas.grid(row=0, column=0, sticky="nsew")
        self.right_scroll = ttk.Scrollbar(outer, orient="vertical",
                                          command=self.right_canvas.yview)
        self.right_canvas.configure(yscrollcommand=self._on_right_scroll)

        right = ttk.Frame(self.right_canvas, padding=4)
        self.right_inner = right
        self._right_window = self.right_canvas.create_window(
            (0, 0), window=right, anchor="nw")
        right.columnconfigure(0, weight=1)
        right.rowconfigure(1, weight=1)

        self.right_canvas.bind("<Configure>", self._on_right_resize)
        right.bind("<Configure>", lambda _e: self._on_right_resize())
        # Колесо мыши работает над всей панелью, а не только над холстом:
        # события уходят виджету под курсором и сами наверх не всплывают.
        outer.bind("<Enter>", lambda _e: self._bind_right_wheel(True))
        outer.bind("<Leave>", lambda _e: self._bind_right_wheel(False))

        # Заголовок списка элементов и кнопка «Перечитать файл» — одной
        # строкой: кнопка идёт сразу за подписью, пустое место забирает
        # третья колонка, поэтому обе прижаты влево.
        elements_head = ttk.Frame(right)
        elements_head.grid(row=0, column=0, sticky="ew")
        elements_head.columnconfigure(2, weight=1)
        self.lbl_elements = ttk.Label(elements_head, text="...")
        self.lbl_elements.grid(row=0, column=0, sticky="w")
        self.btn_reload = ttk.Button(elements_head, text="...",
                                     style="SmallRevert.TButton",
                                     command=self.cmd_revert)
        self.btn_reload.grid(row=0, column=1, sticky="w", padx=(3, 0))
        Tooltip(self.btn_reload, lambda: self.t("btn_reload_tip"))

        list_frame = ttk.Frame(right)
        list_frame.grid(row=1, column=0, sticky="nsew", pady=(2, 4))
        list_frame.columnconfigure(0, weight=1)
        list_frame.rowconfigure(0, weight=1)

        self.element_tree = ttk.Treeview(list_frame, show="headings", height=12)
        self.element_tree.grid(row=0, column=0, sticky="nsew")
        et_sb = ttk.Scrollbar(list_frame, orient="vertical",
                              command=self.element_tree.yview)
        et_sb.grid(row=0, column=1, sticky="ns")
        self.element_tree.config(yscrollcommand=et_sb.set)
        self.element_tree.bind("<<TreeviewSelect>>",
                               self._on_element_tree_select)
        self.element_tree.bind("<Double-1>", lambda _e: self.cmd_layer_edit())

        # Копирование имени элемента/слоя: Ctrl+C и контекстное меню.
        self.element_menu = tk.Menu(self.root, tearoff=0)
        # Ctrl+C обрабатывается общим обработчиком _on_control_key.
        self.element_tree.bind("<Button-3>", self._on_element_right_click)

        self._configure_element_columns()

        # Кнопки работы со слоями Capital.dat (видны только в режиме .dat).
        self.layer_btns = ttk.Frame(right)
        self.layer_btns.grid(row=2, column=0, sticky="ew", pady=(0, 4))
        for c in range(3):
            self.layer_btns.columnconfigure(c, weight=1)
        self.btn_add = ttk.Button(self.layer_btns, text="...",
                                  command=self.cmd_layer_add)
        self.btn_add.grid(row=0, column=0, sticky="ew", padx=(0, 2))
        self.btn_edit = ttk.Button(self.layer_btns, text="...",
                                   command=self.cmd_layer_edit)
        self.btn_edit.grid(row=0, column=1, sticky="ew", padx=2)
        self.btn_delete = ttk.Button(self.layer_btns, text="...",
                                     command=self.cmd_layer_delete)
        self.btn_delete.grid(row=0, column=2, sticky="ew", padx=(2, 0))
        Tooltip(self.btn_add, lambda: self.t("btn_add_tip"))
        Tooltip(self.btn_edit, lambda: self.t("btn_edit_tip"))
        Tooltip(self.btn_delete, lambda: self.t("btn_delete_tip"))
        self.layer_btns.grid_remove()

        # Размер DIALOG (только .dlg).
        self.win_box = ttk.LabelFrame(right, text="...")
        self.win_box.grid(row=3, column=0, sticky="ew", pady=(0, 4))
        for c in range(2):
            self.win_box.columnconfigure(c, weight=1)
        ttk.Label(self.win_box, text="Width").grid(row=0, column=0, padx=2,
                                                   pady=2)
        ttk.Label(self.win_box, text="Height").grid(row=0, column=1, padx=2,
                                                    pady=2)
        self.dlg_w_var = tk.IntVar(value=0)
        self.dlg_h_var = tk.IntVar(value=0)
        e_w = ttk.Entry(self.win_box, textvariable=self.dlg_w_var, width=8,
                        justify="right")
        e_h = ttk.Entry(self.win_box, textvariable=self.dlg_h_var, width=8,
                        justify="right")
        e_w.grid(row=1, column=0, padx=2, pady=(0, 2), sticky="ew")
        e_h.grid(row=1, column=1, padx=2, pady=(0, 2), sticky="ew")
        for e in (e_w, e_h):
            e.bind("<Return>", lambda _ev: self._apply_dialog_size())
            e.bind("<FocusOut>", lambda _ev: self._apply_dialog_size())
        self.dlg_size_hint = ttk.Label(self.win_box, text="...",
                                       foreground=COLOR_TEXT_MUTED)
        self.dlg_size_hint.grid(row=2, column=0, columnspan=2, padx=2,
                                pady=(0, 4), sticky="w")

        # Координаты элемента / слоя.
        self.coord_box = ttk.LabelFrame(right, text="...")
        self.coord_box.grid(row=4, column=0, sticky="ew", pady=(0, 4))
        for c in range(4):
            self.coord_box.columnconfigure(c, weight=1)
        self.coord_vars = {}
        for i, label in enumerate(("X1", "Y1", "X2", "Y2")):
            ttk.Label(self.coord_box, text=label).grid(row=0, column=i,
                                                       padx=2, pady=2)
            v = tk.IntVar(value=0)
            e = ttk.Entry(self.coord_box, textvariable=v, width=6,
                          justify="right")
            e.grid(row=1, column=i, padx=2, pady=(0, 4), sticky="ew")
            e.bind("<Return>", lambda _ev: self._apply_coord_entries())
            e.bind("<FocusOut>", lambda _ev: self._apply_coord_entries())
            self.coord_vars[label] = v

        # Подсказки. Заголовок рамки — отдельный виджет (labelwidget), в нём
        # же живут кнопки «Открыть в блокноте» и «Открыть папку файла», чтобы
        # они не закрывали текст. Ширина заголовка задана явно (grid_propagate
        # выключен), поэтому кнопки прижаты к правому краю — подальше от слова
        # «Подсказки», а ширину каждая берёт по своей надписи: на две кнопки с
        # фиксированной шириной места в строке уже не хватает.
        self.hints_head = ttk.Frame(right, width=RIGHT_WIDTH - 16, height=24)
        # Ширину пересчитывает _on_right_resize: появление полосы прокрутки
        # сужает панель, и кнопки в заголовке иначе обрезаются.
        self.hints_head.grid_propagate(False)
        self.hints_head.columnconfigure(1, weight=1)
        self.lbl_hints_title = ttk.Label(self.hints_head, text="...")
        self.lbl_hints_title.grid(row=0, column=0, sticky="w")
        self.btn_open_dir = ttk.Button(self.hints_head, text="...",
                                       style="SmallHistory.TButton",
                                       command=self.cmd_open_folder)
        self.btn_open_dir.grid(row=0, column=2, sticky="e")
        self.btn_open_ext = ttk.Button(self.hints_head, text="...",
                                       style="SmallHistory.TButton",
                                       command=self.cmd_open_external)
        self.btn_open_ext.grid(row=0, column=3, sticky="e", padx=(3, 0))
        Tooltip(self.btn_open_dir, lambda: self.t("btn_open_folder_tip"))
        Tooltip(self.btn_open_ext, lambda: self.t("btn_open_external_tip"))

        self.hints_box = ttk.LabelFrame(right, labelwidget=self.hints_head)
        self.hints_box.grid(row=5, column=0, sticky="nsew")
        self.hints_box.columnconfigure(0, weight=1)
        self.hints_box.rowconfigure(0, weight=1)

        # Текст подсказок лежит на холсте — так он прокручивается по вертикали.
        self.hints_canvas = tk.Canvas(self.hints_box, bg=COLOR_BG_APP,
                                      highlightthickness=0, bd=0, height=HINTS_HEIGHT)
        self.hints_canvas.grid(row=0, column=0, sticky="nsew", padx=(4, 0),
                               pady=4)
        hints_sb = ttk.Scrollbar(self.hints_box, orient="vertical",
                                 command=self.hints_canvas.yview)
        hints_sb.grid(row=0, column=1, sticky="ns", pady=4)
        self.hints_canvas.configure(yscrollcommand=hints_sb.set)
        self.lbl_hints = ttk.Label(self.hints_canvas, justify="left", text="...")
        self.hints_canvas.create_window((0, 0), window=self.lbl_hints,
                                        anchor="nw")
        self.lbl_hints.bind(
            "<Configure>",
            lambda _e: self.hints_canvas.configure(
                scrollregion=self.hints_canvas.bbox("all")))
        self.hints_canvas.bind(
            "<MouseWheel>",
            lambda e: self.hints_canvas.yview_scroll(
                -1 if e.delta > 0 else 1, "units"))

        # Кнопки.
        btn_frame = ttk.Frame(right)
        btn_frame.grid(row=6, column=0, sticky="ew", pady=(6, 0))
        for c in range(3):
            btn_frame.columnconfigure(c, weight=1)

        self.btn_save = ttk.Button(btn_frame, text="...",
                                   command=self.cmd_save,
                                   style="Save.TButton")
        self.btn_save.grid(row=0, column=0, sticky="ew", padx=(0, 2))
        self.btn_revert = ttk.Button(btn_frame, text="...",
                                     command=self.cmd_revert,
                                     style="Revert.TButton")
        self.btn_revert.grid(row=0, column=1, sticky="ew", padx=2)
        self.btn_history = ttk.Button(btn_frame, text="...",
                                      command=self.cmd_history,
                                      style="History.TButton")
        self.btn_history.grid(row=0, column=2, sticky="ew", padx=(2, 0))
        Tooltip(self.btn_save, lambda: self.t("btn_save_tip"))
        Tooltip(self.btn_revert, lambda: self.t("btn_revert_tip"))
        Tooltip(self.btn_history, lambda: self.t("btn_history_tip"))

    # --- Прокрутка правой панели -------------------------------------------

    def _on_right_scroll(self, first, last):
        """Полоса прокрутки видна, только когда содержимое не помещается."""
        self.right_scroll.set(first, last)
        if float(first) <= 0.0 and float(last) >= 1.0:
            self.right_scroll.grid_remove()
        else:
            self.right_scroll.grid(row=0, column=1, sticky="ns")

    def _on_right_resize(self, event=None):
        canvas = self.right_canvas
        width = event.width if event is not None else canvas.winfo_width()
        height = event.height if event is not None else canvas.winfo_height()
        if width <= 1 or not hasattr(self, "hints_head"):
            return
        # Высота внутренней рамки — не меньше высоты холста, иначе при
        # высоком окне список элементов не растянется на свободное место.
        need = self.right_inner.winfo_reqheight()
        size = (width, max(need, height))
        # Перенастраиваем, только если что-то изменилось: смена размера
        # снова вызывает <Configure>, и без этой проверки получится цикл.
        if size == getattr(self, "_right_size", None):
            return
        self._right_size = size
        canvas.itemconfigure(self._right_window, width=size[0], height=size[1])
        canvas.configure(scrollregion=(0, 0, size[0], size[1]))
        self.hints_head.configure(width=max(200, width - 16))

    def _bind_right_wheel(self, on):
        # Флаг нужен, чтобы обработчик не навесился дважды: <Enter> прилетает
        # и при переходе курсора на вложенный виджет панели.
        if on == getattr(self, "_right_wheel_bound", False):
            return
        self._right_wheel_bound = on
        for seq in ("<MouseWheel>", "<Button-4>", "<Button-5>"):
            if on:
                self.root.bind_all(seq, self._on_right_wheel, add="+")
            else:
                self.root.unbind_all(seq)

    def _on_right_wheel(self, event):
        # Над списком элементов и над подсказками крутится их собственная
        # прокрутка — панель в этот момент стоять должна.
        w = event.widget
        while w is not None:
            if w in (self.element_tree, self.hints_canvas):
                return
            w = getattr(w, "master", None)
        up = event.delta > 0 if event.delta else event.num == 4
        self.right_canvas.yview_scroll(-1 if up else 1, "units")

    def _configure_element_columns(self):
        """Колонки таблицы зависят от режима (.dlg или Capital.dat)."""
        if self.mode == MODE_DAT:
            cols = ("z", "build", "image", "x1", "y1", "x2", "y2")
            widths = (40, 85, 105, 36, 36, 36, 36)
        else:
            cols = ("kind", "name", "x1", "y1", "x2", "y2")
            widths = (70, 130, 38, 38, 38, 38)
        self.element_tree.config(columns=cols)
        for col, w in zip(cols, widths):
            self.element_tree.heading(col, text=col.upper())
            anchor = "w" if col in ("kind", "name", "build", "image") else "e"
            self.element_tree.column(col, width=w, minwidth=30, anchor=anchor,
                                     stretch=(col in ("name", "image")))

    # --- Language ----------------------------------------------------------

    def _set_language(self, lang):
        if lang == self.lang:
            return
        self.lang = lang
        self._apply_language()
        self._save_settings()

    def _build_menu(self):
        # Меню пересоздаётся целиком: entryconfigure -label не работает на Windows Tk.
        menubar = tk.Menu(self.root)

        filemenu = tk.Menu(menubar, tearoff=0)
        filemenu.add_command(label=self.t("menu_open"), command=self.cmd_open,
                             accelerator="Ctrl+O")
        filemenu.add_command(label=self.t("menu_save"), command=self.cmd_save,
                             accelerator="Ctrl+S")
        filemenu.add_command(label=self.t("menu_save_as"),
                             command=self.cmd_save_as)
        filemenu.add_separator()
        filemenu.add_command(label=self.t("menu_exit"), command=self.cmd_exit)
        menubar.add_cascade(label=self.t("menu_file"), menu=filemenu)

        editmenu = tk.Menu(menubar, tearoff=0)
        editmenu.add_command(label=self.t("menu_undo"), command=self.cmd_undo,
                             accelerator="Ctrl+Z")
        editmenu.add_command(label=self.t("menu_redo"), command=self.cmd_redo,
                             accelerator="Ctrl+Y")
        editmenu.add_separator()
        editmenu.add_command(label=self.t("menu_history"),
                             command=self.cmd_history,
                             accelerator="Ctrl+H")
        menubar.add_cascade(label=self.t("menu_edit"), menu=editmenu)

        setmenu = tk.Menu(menubar, tearoff=0)
        self.dat_secondary_var = tk.BooleanVar(value=self.dat_secondary)
        setmenu.add_checkbutton(label=self.t("menu_dat_secondary"),
                                variable=self.dat_secondary_var,
                                command=self._toggle_dat_secondary)
        menubar.add_cascade(label=self.t("menu_settings"), menu=setmenu)

        # Шрифт со своими иероглифами нужен только здесь: в этом списке всегда
        # есть «简体中文». Остальные меню остаются на системном шрифте.
        langmenu = tk.Menu(menubar, tearoff=0, font=self.menu_font)
        self.lang_var.set(self.lang)
        for code in ("ru", "en", "pl", "zh"):
            # Радиокнопка, а не подпись с символом: индикатор рисует сама
            # система — той же галочкой, что и в «Настройках».
            langmenu.add_radiobutton(
                label=self.t("menu_lang_" + code),
                image=self.flag_images[code], compound="left",
                variable=self.lang_var, value=code,
                command=lambda c=code: self._set_language(c))
        # В самой строке меню Windows картинки не поддерживает — вместо флага
        # Tk выводит текст «(Image)». Поэтому там перечислены коды языков:
        # человек, не читающий слова «Язык», всё равно узнает свой.
        menubar.add_cascade(label=self.t("menu_language") + LANG_CODES,
                            menu=langmenu)

        menubar.add_command(label=self.t("menu_about"), command=self.cmd_about)
        self.root.config(menu=menubar)

    def _toggle_dat_secondary(self):
        """Править ли вторичные координаты (положение картинки) в .dat."""
        self.dat_secondary = bool(self.dat_secondary_var.get())
        self._save_settings()

    def _apply_language(self):
        self._update_title()
        self._build_menu()
        is_dat = self.mode == MODE_DAT
        self.lbl_sections.config(
            text=self.t("sections_label_dat" if is_dat else "sections_label"))
        self.lbl_elements.config(
            text=self.t("elements_label_dat" if is_dat else "elements_label"))
        self.win_box.config(text=self.t("dialog_size_label"))
        self.coord_box.config(text=self.t("coord_label"))
        self.lbl_hints_title.config(text=self.t("hints_label"))
        self.lbl_hints.config(
            text=self.t("hint_text_dat" if is_dat else "hint_text"))
        self.btn_save.config(text=self.t("btn_save"))
        self.btn_revert.config(text=self.t("btn_revert"))
        self.btn_reload.config(text=self.t("btn_reload"))
        self.btn_history.config(text=self.t("btn_history"))
        self.btn_open_ext.config(text=self.t("btn_open_external"))
        self.btn_open_dir.config(text=self.t("btn_open_folder"))
        self.btn_add.config(text=self.t("btn_add"))
        self.btn_edit.config(text=self.t("btn_edit"))
        self.btn_delete.config(text=self.t("btn_delete"))
        self._refresh_status()
        self._update_dialog_size_entries()

    # --- Строка состояния --------------------------------------------------

    def _refresh_status(self):
        """Строка «Загружено» с полным путём к открытому файлу."""
        if not self.file_path or not self._status_loaded:
            text = self.t("status_open_hint")
        else:
            key, kw = self._status_loaded
            # Ширину остального текста строки меряем по шаблону без пути.
            rest = self.t(key, path="", **kw)
            fitted = self._fit_path(os.path.normpath(self.file_path),
                                    self.status_label.winfo_width(), rest)
            text = self.t(key, path=fitted, **kw)
        self._status_text = text
        self.status_var.set(text)

    def _fit_path(self, path, avail_px, rest_text):
        """Путь целиком; если в строку не влезает — с многоточием в середине,
        чтобы диск и имя файла остались видны."""
        f = self.status_font
        if avail_px <= 1:          # до первой отрисовки подгонять нечего
            return path
        budget = avail_px - f.measure(rest_text) - 4
        if budget <= 0 or f.measure(path) <= budget:
            return path
        # Диск оставляем всегда, дальше отрезаем целыми папками — от самого
        # длинного варианта к короткому, чтобы имя папки не рвалось посередине.
        head = path[:3] if path[1:3] in (":\\", ":/") else ""
        mid = path[len(head):]
        for i, ch in enumerate(mid):
            if ch in "\\/" and f.measure(head + "…" + mid[i:]) <= budget:
                return head + "…" + mid[i:]
        return head + "…" + os.sep + os.path.basename(path)

    def _on_status_resize(self, _event):
        # Пересобираем только собственную строку: сообщение о сохранении или
        # о загрузке обновления перетирать нельзя.
        if self.status_var.get() == self._status_text:
            self._refresh_status()

    # --- Обновление --------------------------------------------------------

    def _start_update_check(self):
        threading.Thread(target=self._update_worker, daemon=True).start()

    def _update_worker(self):
        try:
            info = fetch_latest_release()
        except Exception:
            return      # нет сети, лимит API, битый ответ — молча выходим
        if info:
            try:
                # Обращаться к Tk можно только из главного потока.
                self.root.after(0, lambda: self._on_update_info(*info))
            except RuntimeError:
                pass    # окно уже закрыли, пока шёл запрос

    def _on_update_info(self, tag, page_url, exe_url, exe_name):
        if not is_newer(tag, APP_VERSION):
            return
        # От этой версии уже отказались — спрашиваем только про более новые.
        if self.skipped_version and not is_newer(tag, self.skipped_version):
            return
        if not messagebox.askyesno(
                self.t("update_title"),
                self.t("update_msg", new=tag.lstrip("vV"), cur=APP_VERSION)):
            self.skipped_version = tag
            self._save_settings()
            return
        # Скачивать имеет смысл только собранный exe: при запуске из .py
        # заменять нечего, поэтому открываем страницу релиза.
        if not exe_url or not running_as_exe():
            webbrowser.open(page_url)
            return
        self._download_update(exe_url, os.path.basename(exe_name), page_url)

    def _download_update(self, exe_url, exe_name, page_url):
        if self._update_busy:
            return
        self._update_busy = True
        self.status_var.set(self.t("update_downloading"))
        dest = os.path.join(APP_DIR, exe_name)

        def work():
            try:
                download_file(exe_url, dest)
            except Exception as exc:
                self.root.after(
                    0, lambda e=exc: self._update_failed(e, page_url))
            else:
                self.root.after(0, lambda: self._update_downloaded(dest))

        threading.Thread(target=work, daemon=True).start()

    def _update_failed(self, exc, page_url):
        self._update_busy = False
        self._refresh_status()
        if messagebox.askyesno(self.t("update_fail_title"),
                               self.t("update_fail_msg", err=exc)):
            webbrowser.open(page_url)

    def _update_downloaded(self, dest):
        self._update_busy = False
        self._refresh_status()
        if not messagebox.askyesno(self.t("update_done_title"),
                                   self.t("update_done_msg", path=dest)):
            return
        if not self._confirm_discard_changes():
            return
        try:
            subprocess.Popen([dest], cwd=APP_DIR)
        except Exception as exc:
            messagebox.showerror(self.t("err_open_title"),
                                 self.t("err_open_msg", err=exc))
            return
        self._save_settings()
        self.root.destroy()

    # --- Shortcuts ---------------------------------------------------------

    def _bind_shortcuts(self):
        # Одна привязка на все сочетания с Ctrl: букву определяем по
        # физической клавише (см. key_letter), поэтому раскладка не важна.
        self.root.bind("<Control-KeyPress>", self._on_control_key)
        self.root.protocol("WM_DELETE_WINDOW", self.cmd_exit)

    def _on_control_key(self, event):
        letter = key_letter(event)
        if letter == "o":
            self.cmd_open()
        elif letter == "s":
            self.cmd_save()
        elif letter == "z":
            self.cmd_undo()
        elif letter == "y":
            self.cmd_redo()
        elif letter == "h":
            self.cmd_history()
        elif letter == "c":
            # Ctrl+C копирует имя только из списка секций и таблицы элементов;
            # в полях ввода работает штатное копирование текста.
            widget = self.root.focus_get()
            if widget is self.section_listbox:
                return self._copy_section_name()
            if widget is self.element_tree:
                return self._copy_element_name()
            return None
        else:
            return None
        return "break"

    # --- File commands -----------------------------------------------------

    def cmd_open(self):
        if not self._confirm_discard_changes():
            return
        path = filedialog.askopenfilename(
            title=self.t("menu_open"),
            filetypes=[("Disciples files", "*.dlg *.dat"),
                       ("DLG files", "*.dlg"),
                       ("Capital.dat", "*.dat"),
                       ("All files", "*.*")],
        )
        if path:
            self._open_file(path)

    def _detect_mode(self, path):
        return MODE_DAT if path.lower().endswith(".dat") else MODE_DLG

    def _open_file(self, path):
        mode = self._detect_mode(path)
        try:
            if mode == MODE_DAT:
                sections, line_ending, trailing = parse_dat_file(path)
                lines = []
            else:
                lines, sections, line_ending = parse_dlg_file(path)
                trailing = 0
        except Exception as exc:
            messagebox.showerror(self.t("err_read_title"),
                                 self.t("err_read_msg", err=exc))
            return

        mode_changed = mode != self.mode
        self.mode = mode
        self.file_path = path
        self.lines = lines
        self.sections = sections
        self.line_ending = line_ending
        self.trailing_blanks = trailing
        self.current_section = None
        self.selected_element = None
        self.dirty = False

        self._apply_mode_ui()
        if mode_changed:
            self._configure_element_columns()
        self._reset_history()

        self._update_title()
        self._refresh_section_list()
        self._clear_canvas()
        self._refresh_element_list()
        self._update_coord_entries()
        self._update_dialog_size_entries()
        self._update_scrollregion()

        if mode == MODE_DAT:
            layers = sum(len(s.layers) for s in sections)
            self._status_loaded = ("status_loaded_dat",
                                   {"count": len(sections), "layers": layers})
        else:
            self._status_loaded = ("status_loaded", {"count": len(sections)})
        self._refresh_status()
        self._save_settings()

    def _apply_mode_ui(self):
        """Показывает/прячет элементы UI, специфичные для режима."""
        is_dat = self.mode == MODE_DAT
        if is_dat:
            self.filter_frame.grid_remove()
            self.win_box.grid_remove()
            self.layer_btns.grid()
        else:
            self.filter_frame.grid()
            self.win_box.grid()
            self.layer_btns.grid_remove()
        self.lbl_sections.config(
            text=self.t("sections_label_dat" if is_dat else "sections_label"))
        self.lbl_elements.config(
            text=self.t("elements_label_dat" if is_dat else "elements_label"))
        self.lbl_hints.config(
            text=self.t("hint_text_dat" if is_dat else "hint_text"))

    def cmd_save(self):
        if not self.file_path:
            return self.cmd_save_as()
        try:
            if self.mode == MODE_DAT:
                write_dat_file(self.file_path, self.sections,
                               self.line_ending, self.trailing_blanks)
            else:
                write_dlg_file(self.file_path, self.lines, self.sections,
                               self.line_ending)
        except Exception as exc:
            messagebox.showerror(self.t("err_write_title"),
                                 self.t("err_write_msg", err=exc))
            return
        self.dirty = False
        self._on_saved()
        self._update_title()
        self.status_var.set(self.t("status_saved", path=self.file_path))

    def cmd_save_as(self):
        if not self.sections:
            return
        ext = ".dat" if self.mode == MODE_DAT else ".dlg"
        path = filedialog.asksaveasfilename(
            title=self.t("menu_save_as"), defaultextension=ext,
            filetypes=[("DLG files", "*.dlg"), ("Capital.dat", "*.dat"),
                       ("All files", "*.*")],
        )
        if not path:
            return
        self.file_path = path
        self.cmd_save()

    def cmd_revert(self):
        """Полный откат к содержимому файла на диске."""
        if not self.file_path:
            return
        old_section_name = (self.current_section.name
                            if self.current_section else None)
        self._open_file(self.file_path)
        if old_section_name:
            self._select_section_by_name(old_section_name)

    def cmd_open_external(self):
        """Открывает текущий файл текстовым редактором ОС по умолчанию.

        Если для расширения (.dat) редактор не назначен, Windows сама
        предложит выбрать программу.
        """
        if not self.file_path or not os.path.isfile(self.file_path):
            return
        try:
            if sys.platform.startswith("win"):
                os.startfile(self.file_path)          # noqa: S606 (Windows only)
            elif sys.platform == "darwin":
                subprocess.Popen(["open", self.file_path])
            else:
                subprocess.Popen(["xdg-open", self.file_path])
        except Exception as exc:
            messagebox.showerror(self.t("err_open_title"),
                                 self.t("err_open_msg", err=exc))

    def cmd_open_folder(self):
        """Открывает папку с текущим файлом и выделяет в ней сам файл."""
        if not self.file_path or not os.path.isfile(self.file_path):
            return
        path = os.path.normpath(self.file_path)
        try:
            if sys.platform.startswith("win"):
                # Explorer понимает только форму /select,"путь" — кавычки
                # строго вокруг пути, иначе он открывает «Документы». Поэтому
                # команда собирается строкой, а не списком аргументов. Код
                # возврата у него 1 даже при успехе, так что Popen, не call.
                subprocess.Popen(f'explorer /select,"{path}"')
            elif sys.platform == "darwin":
                subprocess.Popen(["open", "-R", path])
            else:
                subprocess.Popen(["xdg-open", os.path.dirname(path)])
        except Exception as exc:
            messagebox.showerror(self.t("err_open_title"),
                                 self.t("err_open_msg", err=exc))

    def cmd_exit(self):
        if not self._confirm_discard_changes():
            return
        self._save_settings()
        self.root.destroy()

    def cmd_about(self):
        win = tk.Toplevel(self.root)
        win.title(self.t("about_title"))
        win.resizable(False, False)
        win.configure(bg=COLOR_BG_APP)
        win.transient(self.root)
        win.grab_set()

        pad = ttk.Frame(win, padding=20)
        pad.pack(fill="both", expand=True)

        ttk.Label(pad, text=self.t("about_name"),
                  font=("Segoe UI", 14, "bold")).pack(anchor="w")
        ttk.Label(pad, text=self.t("about_version"),
                  foreground=COLOR_TEXT_MUTED,
                  font=("Segoe UI", 10)).pack(anchor="w", pady=(0, 10))
        ttk.Label(pad, text=self.t("about_text"),
                  justify="left").pack(anchor="w", pady=(0, 10))

        # Ссылки из ABOUT_LINKS.
        for link_name, link_url, bold in ABOUT_LINKS:
            if not link_name and not link_url:
                ttk.Label(pad, text="").pack(anchor="w")
                continue
            name = (self.t(link_name[1:]) if link_name.startswith("@")
                    else link_name)
            display = (f"{name}: {link_url[7:]}"
                       if link_url.startswith("mailto:")
                       else f"{name}: {link_url}")
            font = (("Segoe UI", 9, "underline", "bold") if bold
                    else ("Segoe UI", 9, "underline"))
            lbl = ttk.Label(pad, text=display, foreground=COLOR_SELECTION,
                            cursor="hand2", font=font)
            lbl.pack(anchor="w", pady=(0, 2))
            lbl.bind("<Button-1>",
                     lambda _e, url=link_url: webbrowser.open(url))

        btn_about_ok = ttk.Button(pad, text=self.t("btn_ok"),
                                  command=win.destroy)
        btn_about_ok.pack(pady=(14, 0))
        Tooltip(btn_about_ok, lambda: self.t("btn_close_tip"))
        place_in_view(win, self.root.winfo_rootx() + 80,
                      self.root.winfo_rooty() + 80, ref=self.root)

    def _confirm_discard_changes(self):
        if not self.dirty:
            return True
        ans = messagebox.askyesnocancel(
            self.t("unsaved_title"), self.t("unsaved_msg"))
        if ans is None:
            return False
        if ans:
            self.cmd_save()
            return not self.dirty
        return True

    def _update_title(self):
        title = APP_TITLE
        if self.file_path:
            title += f" — {os.path.basename(self.file_path)}"
        if self.dirty:
            title += " *"
        self.root.title(title)

    # --- Копирование имён (Ctrl+C / правая кнопка) -------------------------

    def _copy_to_clipboard(self, text):
        if not text:
            return
        self.root.clipboard_clear()
        self.root.clipboard_append(text)
        self.root.update_idletasks()

    def _copy_section_name(self):
        """Копирует ИМЯ секции без размеров."""
        sel = self.section_listbox.curselection()
        if not sel or sel[0] >= len(self._filtered_sections):
            return "break"
        self._copy_to_clipboard(self._filtered_sections[sel[0]].name)
        return "break"

    def _on_section_right_click(self, event):
        idx = self.section_listbox.nearest(event.y)
        if idx < 0 or idx >= len(self._filtered_sections):
            return
        self.section_listbox.selection_clear(0, tk.END)
        self.section_listbox.selection_set(idx)
        self.section_listbox.event_generate("<<ListboxSelect>>")
        self.section_menu.delete(0, tk.END)
        self.section_menu.add_command(label=self.t("btn_copy"),
                                      command=self._copy_section_name)
        self.section_menu.tk_popup(event.x_root, event.y_root)

    def _element_name_of(self, el):
        """Имя для копирования: у слоя .dat — ID здания, иначе имя картинки."""
        if isinstance(el, DatLayer):
            return el.build_id or el.image or el.key
        return getattr(el, "name", "")

    def _copy_element_name(self):
        sel = self.element_tree.selection()
        if not sel or not self.current_section:
            return "break"
        elements = self.current_section.elements
        idx = int(sel[0])
        if idx < len(elements):
            self._copy_to_clipboard(self._element_name_of(elements[idx]))
        return "break"

    def _on_element_right_click(self, event):
        row = self.element_tree.identify_row(event.y)
        if not row:
            return
        self.element_tree.selection_set(row)
        self.element_menu.delete(0, tk.END)
        self.element_menu.add_command(label=self.t("btn_copy"),
                                      command=self._copy_element_name)
        self.element_menu.tk_popup(event.x_root, event.y_root)

    # --- История изменений -------------------------------------------------

    def _hist_param(self, el):
        """Значение колонки «Параметр»: NAME для .dlg, IMAGE для .dat."""
        if isinstance(el, DatLayer):
            return el.image or el.build_id or el.key
        return getattr(el, "name", "")

    @staticmethod
    def _coords_text(coords):
        """Координаты для колонок «Было» / «Стало»."""
        return ",".join(str(int(c)) for c in coords)

    def _commit_coords(self, sec, el, old):
        """Запись в историю: изменение координат элемента / слоя."""
        self._commit(sec.name, self._hist_param(el),
                     self._coords_text(old),
                     self._coords_text((el.x1, el.y1, el.x2, el.y2)))

    def _commit_dlgsize(self, sec, old):
        """Запись в историю: изменение размера окна DIALOG (old = (w, h))."""
        self._commit(sec.name, self.t("hist_param_dlgsize"),
                     f"{old[0]}×{old[1]}", f"{sec.x2}×{sec.y2}")

    def _snapshot(self):
        """Компактный слепок редактируемых данных текущего файла."""
        if self.mode == MODE_DAT:
            return ("dat", tuple(
                (s.li_count, s.layer_count,
                 tuple((li.key, tuple(li.fields)) for li in s.layerinfos),
                 tuple((l.key, tuple(l.fields)) for l in s.layers))
                for s in self.sections))
        return ("dlg", tuple(
            (s.x2, s.y2, s.w2, s.h2,
             tuple((e.x1, e.y1, e.x2, e.y2) for e in s.elements))
            for s in self.sections))

    def _restore(self, snap):
        kind, data = snap
        if kind == "dat":
            for sec, (li_count, layer_count, lis, layers) in zip(self.sections,
                                                                 data):
                sec.li_count = li_count
                sec.layer_count = layer_count
                sec.layerinfos = [DatLayerInfo(k, f) for k, f in lis]
                sec.layers = [DatLayer(k, f) for k, f in layers]
            # Объекты слоёв пересозданы — старое выделение больше не валидно.
            self.selected_element = None
        else:
            for sec, (x2, y2, w2, h2, els) in zip(self.sections, data):
                sec.x2, sec.y2, sec.w2, sec.h2 = x2, y2, w2, h2
                for el, (a, b, c, d) in zip(sec.elements, els):
                    el.x1, el.y1, el.x2, el.y2 = a, b, c, d

        self._refresh_section_list()
        self._refresh_element_list()
        self._update_coord_entries()
        self._update_dialog_size_entries()
        self._draw_section()

    def _reset_history(self):
        self.history = []
        self.hist_index = 0
        self.saved_index = 0
        self.hist_selected = 0
        self.base_snapshot = self._snapshot()
        self._refresh_history_window()

    def _commit(self, section, param, old_value, new_value):
        """Фиксирует изменение в истории (вызывается ПОСЛЕ правки данных)."""
        after = self._snapshot()
        before = (self.history[self.hist_index - 1].after
                  if self.hist_index else self.base_snapshot)
        if after == before:
            return
        # Новая ветка истории затирает «отменённые» действия.
        del self.history[self.hist_index:]
        self.history.append(
            HistoryEntry(section, param, old_value, new_value, before, after))
        self.hist_index = len(self.history)
        self.hist_selected = self.hist_index
        self._update_dirty()
        self._refresh_history_window()

    def _update_dirty(self):
        self.dirty = self.hist_index != self.saved_index
        self._update_title()

    def _on_saved(self):
        """Вызывается после успешной записи файла: история сохраняется целиком."""
        self.saved_index = self.hist_index
        self._refresh_history_window()

    def cmd_undo(self):
        if self.hist_index <= 0:
            return
        entry = self.history[self.hist_index - 1]
        self.hist_index -= 1
        self.hist_selected = self.hist_index
        self._restore(entry.before)
        self._update_dirty()
        self._refresh_history_window()

    def cmd_redo(self):
        if self.hist_index >= len(self.history):
            return
        entry = self.history[self.hist_index]
        self.hist_index += 1
        self.hist_selected = self.hist_index
        self._restore(entry.after)
        self._update_dirty()
        self._refresh_history_window()

    def _goto_history(self, index):
        """index = 0 — базовое состояние, i — состояние после i-го действия."""
        index = max(0, min(len(self.history), index))
        if index == self.hist_index:
            return
        snap = (self.base_snapshot if index == 0
                else self.history[index - 1].after)
        self.hist_index = index
        self.hist_selected = index
        self._restore(snap)
        self._update_dirty()
        self._refresh_history_window()

    def cmd_history(self):
        if self._history_win is not None and self._history_win.winfo_exists():
            self._history_win.lift()
            self._refresh_history_window()
            return
        win = tk.Toplevel(self.root)
        self._history_win = win
        win.title(self.t("hist_title"))
        win.configure(bg=COLOR_BG_APP)
        win.geometry("680x420")
        win.transient(self.root)
        place_in_view(win, self.root.winfo_rootx() + 60,
                      self.root.winfo_rooty() + 60, ref=self.root)

        frame = ttk.Frame(win, padding=8)
        frame.pack(fill="both", expand=True)
        frame.rowconfigure(0, weight=1)
        frame.columnconfigure(0, weight=1)

        # Таблица истории собрана из ячеек-Label: только так получаются
        # настоящие линии-границы колонок (у ttk.Treeview сетки нет).
        canvas = tk.Canvas(frame, bg=COLOR_INPUT_BG, bd=0,
                           highlightthickness=1,
                           highlightbackground=COLOR_BORDER_DARK)
        canvas.grid(row=0, column=0, sticky="nsew")
        sb = ttk.Scrollbar(frame, orient="vertical", command=canvas.yview)
        sb.grid(row=0, column=1, sticky="ns")
        canvas.configure(yscrollcommand=sb.set)
        self.hist_canvas = canvas

        self.hist_table = tk.Frame(canvas, bg=COLOR_INPUT_BG)
        self.hist_table_id = canvas.create_window(
            (0, 0), window=self.hist_table, anchor="nw")
        self.hist_table.bind(
            "<Configure>",
            lambda _e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.bind(
            "<Configure>",
            lambda e: canvas.itemconfigure(self.hist_table_id, width=e.width))
        canvas.bind("<MouseWheel>",
                    lambda e: canvas.yview_scroll(-1 if e.delta > 0 else 1,
                                                  "units"))

        btns = ttk.Frame(frame)
        btns.grid(row=1, column=0, columnspan=2, sticky="ew", pady=(8, 0))
        btns.columnconfigure(0, weight=1)
        btn_hist_revert = ttk.Button(
            btns, text=self.t("hist_revert_to"),
            command=self._history_revert_clicked)
        btn_hist_revert.grid(row=0, column=0, sticky="ew", padx=(0, 4))
        btn_hist_close = ttk.Button(btns, text=self.t("btn_close"),
                                    command=win.destroy)
        btn_hist_close.grid(row=0, column=1)
        Tooltip(btn_hist_revert, lambda: self.t("hist_revert_to_tip"))
        Tooltip(btn_hist_close, lambda: self.t("btn_close_tip"))

        def _on_close():
            self._history_win = None
            win.destroy()

        win.protocol("WM_DELETE_WINDOW", _on_close)
        win.bind("<Control-KeyPress>", self._on_control_key)
        self._refresh_history_window()

    def _hist_cell(self, row, col, text, header=False, index=None):
        """Одна ячейка таблицы истории: границы + текст по центру."""
        bg = COLOR_BUTTON_BG if header else COLOR_INPUT_BG
        cell = tk.Label(self.hist_table, text=text, bg=bg, fg=COLOR_TEXT,
                        anchor="center", justify="center",
                        relief="solid", borderwidth=1, padx=4, pady=2,
                        font=("Segoe UI", 9, "bold" if header else "normal"))
        cell.grid(row=row, column=col, sticky="nsew")
        if index is not None:
            # Клик по ЛЮБОЙ колонке строки: одиночный — выделить,
            # двойной — откатиться к этому состоянию.
            cell.bind("<Button-1>", lambda _e, i=index: self._hist_select(i))
            cell.bind("<Double-1>", lambda _e, i=index: self._goto_history(i))
            self.hist_cells.setdefault(index, []).append(cell)

    def _hist_select(self, index):
        """Выделение строки: таблицу НЕ пересобираем (иначе двойной клик не
        успевает сработать по уничтоженной ячейке) — только перекрашиваем."""
        self.hist_selected = index
        self._hist_apply_selection()

    def _hist_apply_selection(self):
        for i, cells in self.hist_cells.items():
            selected = (i == self.hist_selected)
            bg = COLOR_SELECTION if selected else COLOR_INPUT_BG
            fg = "#ffffff" if selected else COLOR_TEXT
            for cell in cells:
                cell.configure(bg=bg, fg=fg)

    def _refresh_history_window(self):
        win = self._history_win
        if win is None or not win.winfo_exists():
            return
        table = self.hist_table
        for child in table.winfo_children():
            child.destroy()
        self.hist_cells = {}
        for col, weight in enumerate((0, 3, 4, 3, 3)):
            table.columnconfigure(col, weight=weight)

        if self.hist_selected is None or self.hist_selected > len(self.history):
            self.hist_selected = self.hist_index

        # Шапка таблицы.
        headers = ("", self.t("hist_col_sec"), self.t("hist_col_param"),
                   self.t("hist_col_before"), self.t("hist_col_after"))
        for col, text in enumerate(headers):
            self._hist_cell(0, col, text, header=True)

        mark = self.t("hist_current_mark")
        rows = [(self.t("hist_initial"), "", "", "")]
        rows += [(e.section, e.param, e.old_value, e.new_value)
                 for e in self.history]
        for i, values in enumerate(rows):
            self._hist_cell(i + 1, 0, mark if i == self.hist_index else "",
                            index=i)
            for col, text in enumerate(values, start=1):
                self._hist_cell(i + 1, col, text, index=i)
        self._hist_apply_selection()

        table.update_idletasks()
        self.hist_canvas.configure(scrollregion=self.hist_canvas.bbox("all"))

    def _history_revert_clicked(self):
        if self.hist_selected is None:
            return
        self._goto_history(self.hist_selected)

    # --- Section list ------------------------------------------------------

    def _check_filter(self, value, op_var, val_var):
        """Проверяет, проходит ли числовое value через фильтр op+val."""
        op = op_var.get()
        if op == "—":
            return True
        try:
            threshold = int(val_var.get())
        except (ValueError, tk.TclError):
            return True
        if op == "=":  return value == threshold
        if op == ">":  return value > threshold
        if op == ">=": return value >= threshold
        if op == "<":  return value < threshold
        if op == "<=": return value <= threshold
        return True

    def _refresh_section_list(self):
        self.section_listbox.delete(0, tk.END)
        query = self.search_var.get().strip().lower()
        self._filtered_sections = []
        for s in self.sections:
            if query and query not in s.name.lower():
                continue
            if self.mode == MODE_DLG:
                if not self._check_filter(s.x2, self.filter_w_op,
                                          self.filter_w_val):
                    continue
                if not self._check_filter(s.y2, self.filter_h_op,
                                          self.filter_h_val):
                    continue
                label = f"{s.name}   [{s.x2}×{s.y2}]"
            else:
                label = f"{s.name}   [{len(s.layers)}]"
            self._filtered_sections.append(s)
            self.section_listbox.insert(tk.END, label)
        if self.current_section in self._filtered_sections:
            idx = self._filtered_sections.index(self.current_section)
            self.section_listbox.selection_set(idx)
            self.section_listbox.see(idx)

    def _on_section_select(self, _ev):
        sel = self.section_listbox.curselection()
        if not sel or sel[0] >= len(self._filtered_sections):
            return
        section = self._filtered_sections[sel[0]]
        if section is self.current_section:
            return
        self.current_section = section
        self.selected_element = None
        self._draw_section()
        self._refresh_element_list()
        self._update_coord_entries()
        self._update_dialog_size_entries()

    def _select_section_by_name(self, name):
        for i, s in enumerate(self._filtered_sections):
            if s.name == name:
                self.section_listbox.selection_clear(0, tk.END)
                self.section_listbox.selection_set(i)
                self.section_listbox.see(i)
                self.current_section = s
                self._draw_section()
                self._refresh_element_list()
                self._update_coord_entries()
                self._update_dialog_size_entries()
                break

    # --- Element list ------------------------------------------------------

    def _element_row(self, el):
        if self.mode == MODE_DAT:
            return (el.z, el.build_id, el.image, el.x1, el.y1, el.x2, el.y2)
        return (el.kind, el.name, el.x1, el.y1, el.x2, el.y2)

    def _refresh_element_list(self):
        for item in self.element_tree.get_children():
            self.element_tree.delete(item)
        if not self.current_section:
            return
        for i, el in enumerate(self.current_section.elements):
            self.element_tree.insert("", "end", iid=str(i),
                                     values=self._element_row(el))
        if self.selected_element in self.current_section.elements:
            i = self.current_section.elements.index(self.selected_element)
            self.element_tree.selection_set(str(i))
            self.element_tree.see(str(i))

    def _on_element_tree_select(self, _ev):
        sel = self.element_tree.selection()
        if not sel or not self.current_section:
            return
        el = self.current_section.elements[int(sel[0])]
        if el is self.selected_element:
            return
        self.selected_element = el
        self._update_coord_entries()
        self._redraw_selection_highlight()

    def _refresh_selected_row(self):
        el = self.selected_element
        if el is HIT_DIALOG or el is None or not self.current_section:
            return
        if el not in self.current_section.elements:
            return
        idx = self.current_section.elements.index(el)
        self.element_tree.item(str(idx), values=self._element_row(el))

    # --- Coord panel -------------------------------------------------------

    def _selected_editable(self):
        """Выбранный элемент/слой (не сам DIALOG)."""
        el = self.selected_element
        if el is None or el is HIT_DIALOG:
            return None
        return el

    def _bounds(self):
        """Границы, в которых живут элементы текущей секции."""
        if self.mode == MODE_DAT:
            return CANVAS_W, CANVAS_H
        sec = self.current_section
        return (sec.x2, sec.y2) if sec else (CANVAS_W, CANVAS_H)

    def _update_coord_entries(self):
        el = self._selected_editable()
        for label in ("X1", "Y1", "X2", "Y2"):
            self.coord_vars[label].set(
                getattr(el, label.lower()) if el else 0)

    def _apply_coord_entries(self):
        el = self._selected_editable()
        if el is None or not self.current_section:
            return
        try:
            x1 = int(self.coord_vars["X1"].get())
            y1 = int(self.coord_vars["Y1"].get())
            x2 = int(self.coord_vars["X2"].get())
            y2 = int(self.coord_vars["Y2"].get())
        except (tk.TclError, ValueError):
            self._update_coord_entries()
            return
        if x2 < x1: x1, x2 = x2, x1
        if y2 < y1: y1, y2 = y2, y1
        bw, bh = self._bounds()
        # В Capital.dat допустимо -1 (слой без позиционирования).
        lo = -1 if self.mode == MODE_DAT else 0
        x1 = max(lo, min(bw, x1)); x2 = max(lo, min(bw, x2))
        y1 = max(lo, min(bh, y1)); y2 = max(lo, min(bh, y2))
        old = (el.x1, el.y1, el.x2, el.y2)
        if (x1, y1, x2, y2) == old:
            self._update_coord_entries()
            return
        el.x1, el.y1, el.x2, el.y2 = x1, y1, x2, y2
        self._apply_secondary_shift(el, old)
        self._commit_coords(self.current_section, el, old)
        self._update_coord_entries()
        self._refresh_selected_row()
        self._draw_section()

    def _apply_secondary_shift(self, el, old):
        """Сдвигает вторичные координаты слоя .dat вслед за рамкой.

        Работает только при включённой опции «Изменять вторичные координаты
        в .dat» и только при чистом перемещении (размер рамки не изменился):
        картинка не масштабируется, поэтому при растягивании рамки её
        положение остаётся прежним.
        """
        if not self.dat_secondary or self.mode != MODE_DAT:
            return
        if not isinstance(el, DatLayer) or not old:
            return
        ox1, oy1, ox2, oy2 = old
        if (el.x2 - el.x1, el.y2 - el.y1) != (ox2 - ox1, oy2 - oy1):
            return                      # это изменение размера, а не перенос
        el.shift_secondary(el.x1 - ox1, el.y1 - oy1)

    # --- Dialog size panel -------------------------------------------------

    def _update_dialog_size_entries(self):
        sec = self.current_section
        if sec is None or self.mode == MODE_DAT:
            self.dlg_w_var.set(0)
            self.dlg_h_var.set(0)
            self.dlg_size_hint.config(text=self.t("dlg_size_fixed"),
                                      foreground=COLOR_TEXT_MUTED)
            return
        self.dlg_w_var.set(sec.x2)
        self.dlg_h_var.set(sec.y2)
        if (sec.w2, sec.h2) != (sec.x2, sec.y2):
            self.dlg_size_hint.config(
                text=self.t("dlg_size_warn", w=sec.w2, h=sec.h2),
                foreground=COLOR_WARN)
        else:
            self.dlg_size_hint.config(text=self.t("dlg_size_fixed"),
                                      foreground=COLOR_TEXT_MUTED)

    def _apply_dialog_size(self):
        sec = self.current_section
        if sec is None or self.mode == MODE_DAT:
            return
        try:
            w = int(self.dlg_w_var.get())
            h = int(self.dlg_h_var.get())
        except (tk.TclError, ValueError):
            self._update_dialog_size_entries()
            return
        min_w, min_h = 10, 10
        for el in sec.elements:
            min_w = max(min_w, el.x2)
            min_h = max(min_h, el.y2)
        w = max(min_w, min(CANVAS_W, w))
        h = max(min_h, min(CANVAS_H, h))
        if (w, h) == (sec.x2, sec.y2) and (w, h) == (sec.w2, sec.h2):
            self._update_dialog_size_entries()
            return
        old = (sec.x2, sec.y2)
        sec.x2, sec.y2 = w, h
        sec.w2, sec.h2 = w, h
        self._commit_dlgsize(sec, old)
        self._update_dialog_size_entries()
        self._refresh_section_list()
        self._draw_section()

    # --- Canvas drawing ----------------------------------------------------

    def _clear_canvas(self):
        self.canvas.delete("all")
        self.element_to_rect = {}
        self.dialog_rect_id = None

    def _content_size(self):
        """Размер полезной области холста."""
        if self.mode == MODE_DAT:
            return CANVAS_W, CANVAS_H
        sec = self.current_section
        if not sec:
            return CANVAS_W, CANVAS_H
        return sec.x2 + 20, sec.y2 + 20

    def _update_scrollregion(self):
        """Холст занимает всё свободное место; прокрутка — только при нехватке."""
        cw = max(1, self.canvas.winfo_width())
        ch = max(1, self.canvas.winfo_height())
        content_w, content_h = self._content_size()
        self.canvas.configure(
            scrollregion=(0, 0, max(content_w, cw), max(content_h, ch)))
        if content_w > cw:
            self.h_scroll.grid()
        else:
            self.h_scroll.grid_remove()
            self.canvas.xview_moveto(0)
        if content_h > ch:
            self.v_scroll.grid()
        else:
            self.v_scroll.grid_remove()
            self.canvas.yview_moveto(0)

    def _draw_order(self):
        """Порядок отрисовки: в .dat — по возрастанию Z."""
        sec = self.current_section
        if not sec:
            return []
        if self.mode == MODE_DAT:
            return sorted(sec.layers, key=lambda l: l.z)
        return list(sec.elements)

    def _draw_section(self):
        self._clear_canvas()
        sec = self.current_section
        if not sec:
            self._update_scrollregion()
            return
        if self.mode == MODE_DAT:
            self._draw_capital(sec)
        else:
            self._draw_dialog(sec)
        self._redraw_selection_highlight()
        self._update_scrollregion()

    def _draw_dialog(self, sec):
        sw, sh = sec.x2, sec.y2
        self.dialog_rect_id = self.canvas.create_rectangle(
            0, 0, sw, sh, outline=COLOR_DIALOG_FRAME, width=1,
            fill=COLOR_BG_WINDOW)
        self.canvas.create_text(
            6, 4, text=f"{sec.name}  ({sw}×{sh})", anchor="nw",
            fill=COLOR_TEXT, font=("Segoe UI", 9, "bold"))
        for el in sec.elements:
            self._draw_element(el)

    def _draw_capital(self, sec):
        """Экран столицы: фон 800×600 и слои зданий по возрастанию Z."""
        self.dialog_rect_id = self.canvas.create_rectangle(
            0, 0, CANVAS_W, CANVAS_H, outline=COLOR_DIALOG_FRAME, width=1,
            fill=COLOR_CAPITAL_BG)
        self.canvas.create_text(
            6, 4, text=f"[{sec.name}]  ({CANVAS_W}×{CANVAS_H})", anchor="nw",
            fill="#e8e4d8", font=("Segoe UI", 9, "bold"))
        for layer in self._draw_order():
            if not layer.drawable():
                continue           # -1/0 — слой без позиционирования
            fill = COLOR_LAYER_FILL if layer.build_id else COLOR_LAYER_SYS
            rect = self.canvas.create_rectangle(
                layer.x1, layer.y1, layer.x2, layer.y2,
                outline=COLOR_LAYER_EDGE, fill=fill, width=1)
            self.element_to_rect[layer] = rect
            if layer.x2 - layer.x1 >= 34 and layer.y2 - layer.y1 >= 12:
                self.canvas.create_text(
                    (layer.x1 + layer.x2) / 2, (layer.y1 + layer.y2) / 2,
                    text=layer.image, anchor="center",
                    fill=COLOR_TEXT, font=("Segoe UI", 7))

    def _draw_element(self, el):
        x1, y1, x2, y2 = el.x1, el.y1, el.x2, el.y2
        kind = el.kind
        if kind in ("BUTTON", "BUTTONSD", "TOGGLE", "TOGGLESD"):
            rect = self.canvas.create_rectangle(
                x1, y1, x2, y2, outline=COLOR_BORDER_DARK,
                fill=COLOR_BUTTON_BG, width=1)
            self.canvas.create_line(x1, y1, x2 - 1, y1,
                                    fill=COLOR_BORDER_LIGHT)
            self.canvas.create_line(x1, y1, x1, y2 - 1,
                                    fill=COLOR_BORDER_LIGHT)
        elif kind in ("EDIT", "LBOX", "TLBOX", "SPIN"):
            rect = self.canvas.create_rectangle(
                x1, y1, x2, y2, outline=COLOR_BORDER_DARK,
                fill=COLOR_INPUT_BG, width=1)
        elif kind == "TEXT":
            rect = self.canvas.create_rectangle(
                x1, y1, x2, y2, outline=COLOR_BORDER_MED,
                fill="", width=1, dash=(2, 2))
        elif kind == "IMAGE":
            rect = self.canvas.create_rectangle(
                x1, y1, x2, y2, outline=COLOR_BORDER_DARK,
                fill=COLOR_BG_WINDOW, width=1)
            self.canvas.create_line(x1, y1, x2, y2, fill=COLOR_BORDER_MED)
            self.canvas.create_line(x1, y2, x2, y1, fill=COLOR_BORDER_MED)
        else:
            rect = self.canvas.create_rectangle(
                x1, y1, x2, y2, outline=COLOR_BORDER_DARK,
                fill=COLOR_BUTTON_BG, width=1)
        self.element_to_rect[el] = rect
        if x2 - x1 >= 30 and y2 - y1 >= 12:
            self.canvas.create_text(
                (x1 + x2) / 2, (y1 + y2) / 2, text=el.name, anchor="center",
                fill=COLOR_TEXT, font=("Segoe UI", 7))

    def _redraw_selection_highlight(self):
        self.canvas.delete("selection")
        for rect in self.element_to_rect.values():
            self.canvas.itemconfigure(rect, width=1)
        if self.dialog_rect_id is not None:
            self.canvas.itemconfigure(self.dialog_rect_id,
                                      outline=COLOR_DIALOG_FRAME, width=1)
        sel = self.selected_element
        if sel is HIT_DIALOG and self.current_section and self.mode == MODE_DLG:
            sec = self.current_section
            self.canvas.itemconfigure(self.dialog_rect_id,
                                      outline=COLOR_SELECTION, width=2)
            h = HANDLE_SIZE
            self.canvas.create_rectangle(
                sec.x2 - h, sec.y2 - h, sec.x2, sec.y2,
                fill=COLOR_SELECTION, outline=COLOR_BORDER_DARK,
                tags=("selection",))
            return
        if sel is not None and sel in self.element_to_rect:
            rect = self.element_to_rect[sel]
            self.canvas.itemconfigure(rect, outline=COLOR_SELECTION, width=2)
            self.canvas.tag_raise(rect)
            h = HANDLE_SIZE
            cx = (sel.x1 + sel.x2) / 2
            cy = (sel.y1 + sel.y2) / 2
            for hx, hy in (
                (sel.x1, sel.y1), (sel.x2, sel.y1),
                (sel.x1, sel.y2), (sel.x2, sel.y2),
                (cx, sel.y1), (cx, sel.y2),
                (sel.x1, cy), (sel.x2, cy),
            ):
                self.canvas.create_rectangle(
                    hx - h / 2, hy - h / 2, hx + h / 2, hy + h / 2,
                    fill=COLOR_SELECTION, outline=COLOR_BORDER_DARK,
                    tags=("selection",))

    # --- Canvas interaction ------------------------------------------------

    def _canvas_coords(self, event):
        return (self.canvas.canvasx(event.x), self.canvas.canvasy(event.y))

    def _hit_test_rect(self, x1, y1, x2, y2, px, py, only_right_bottom=False):
        h = HANDLE_SIZE
        if not (x1 - h <= px <= x2 + h and y1 - h <= py <= y2 + h):
            return HIT_NONE
        flags = 0
        if not only_right_bottom and abs(px - x1) <= h:
            flags |= HIT_L
        elif abs(px - x2) <= h:
            flags |= HIT_R
        if not only_right_bottom and abs(py - y1) <= h:
            flags |= HIT_T
        elif abs(py - y2) <= h:
            flags |= HIT_B
        if flags:
            return flags
        if x1 < px < x2 and y1 < py < y2:
            return HIT_NONE if only_right_bottom else HIT_INSIDE
        return HIT_NONE

    def _find_target_at(self, cx, cy):
        sec = self.current_section
        if not sec:
            return None, HIT_NONE
        sel = self._selected_editable()
        if sel is not None and sel in self.element_to_rect:
            hit = self._hit_test_rect(sel.x1, sel.y1, sel.x2, sel.y2, cx, cy)
            if hit:
                return sel, hit
        for el in reversed(self._draw_order()):
            if el not in self.element_to_rect:
                continue          # непозиционируемый слой .dat
            hit = self._hit_test_rect(el.x1, el.y1, el.x2, el.y2, cx, cy)
            if hit:
                return el, hit
        if self.mode == MODE_DLG:
            hit = self._hit_test_rect(0, 0, sec.x2, sec.y2, cx, cy,
                                      only_right_bottom=True)
            if hit and (hit & (HIT_R | HIT_B)):
                return HIT_DIALOG, hit
        return None, HIT_NONE

    def _cursor_for_hit(self, hit):
        if hit == HIT_INSIDE: return "fleur"
        if hit & HIT_L and hit & HIT_T: return "top_left_corner"
        if hit & HIT_R and hit & HIT_T: return "top_right_corner"
        if hit & HIT_L and hit & HIT_B: return "bottom_left_corner"
        if hit & HIT_R and hit & HIT_B: return "bottom_right_corner"
        if hit & HIT_L: return "left_side"
        if hit & HIT_R: return "right_side"
        if hit & HIT_T: return "top_side"
        if hit & HIT_B: return "bottom_side"
        return ""

    def _on_canvas_motion(self, event):
        if self.drag_mode != HIT_NONE:
            return
        cx, cy = self._canvas_coords(event)
        target, hit = self._find_target_at(cx, cy)
        self.canvas.config(cursor=self._cursor_for_hit(hit) if target else "")

    def _on_canvas_press(self, event):
        self.canvas.focus_set()
        cx, cy = self._canvas_coords(event)
        target, hit = self._find_target_at(cx, cy)
        if not target:
            self.selected_element = None
            self._redraw_selection_highlight()
            self._update_coord_entries()
            self.element_tree.selection_remove(self.element_tree.selection())
            return
        if target is HIT_DIALOG:
            sec = self.current_section
            self.selected_element = HIT_DIALOG
            self.element_tree.selection_remove(self.element_tree.selection())
            self._update_coord_entries()
            self._redraw_selection_highlight()
            self.drag_target = HIT_DIALOG
            self.drag_mode = hit
            self.drag_start_x = cx
            self.drag_start_y = cy
            self.drag_orig = (0, 0, sec.x2, sec.y2)
            return
        if target is not self.selected_element:
            self.selected_element = target
            idx = self.current_section.elements.index(target)
            self.element_tree.selection_set(str(idx))
            self.element_tree.see(str(idx))
            self._update_coord_entries()
            self._redraw_selection_highlight()
        self.drag_target = target
        self.drag_mode = hit
        self.drag_start_x = cx
        self.drag_start_y = cy
        self.drag_orig = (target.x1, target.y1, target.x2, target.y2)
        self.drag_orig_img = ((target.img_x, target.img_y)
                              if isinstance(target, DatLayer) else None)

    def _on_canvas_drag(self, event):
        if self.drag_mode == HIT_NONE or self.drag_target is None:
            return
        cx, cy = self._canvas_coords(event)
        sec = self.current_section
        ox1, oy1, ox2, oy2 = self.drag_orig
        dx = cx - self.drag_start_x
        dy = cy - self.drag_start_y

        if self.drag_target is HIT_DIALOG:
            new_w, new_h = ox2, oy2
            if self.drag_mode & HIT_R: new_w = ox2 + dx
            if self.drag_mode & HIT_B: new_h = oy2 + dy
            min_w, min_h = 10, 10
            for el in sec.elements:
                min_w = max(min_w, el.x2)
                min_h = max(min_h, el.y2)
            new_w = max(min_w, min(CANVAS_W, int(new_w)))
            new_h = max(min_h, min(CANVAS_H, int(new_h)))
            sec.x2, sec.y2 = new_w, new_h
            sec.w2, sec.h2 = new_w, new_h
            self.canvas.coords(self.dialog_rect_id, 0, 0, new_w, new_h)
            self._update_dialog_size_entries()
            self._redraw_selection_highlight()
            return

        el = self.drag_target
        sw, sh = self._bounds()
        if self.drag_mode == HIT_INSIDE:
            w = ox2 - ox1
            h = oy2 - oy1
            nx1 = max(0, min(sw - w, ox1 + dx))
            ny1 = max(0, min(sh - h, oy1 + dy))
            el.x1, el.y1 = int(nx1), int(ny1)
            el.x2, el.y2 = el.x1 + w, el.y1 + h
            # Вторичные координаты (картинка) едут вместе с рамкой.
            if (self.dat_secondary and self.mode == MODE_DAT
                    and isinstance(el, DatLayer) and self.drag_orig_img):
                el.img_x = self.drag_orig_img[0] + (el.x1 - ox1)
                el.img_y = self.drag_orig_img[1] + (el.y1 - oy1)
        else:
            nx1, ny1, nx2, ny2 = ox1, oy1, ox2, oy2
            if self.drag_mode & HIT_L: nx1 = max(0, min(ox2 - 1, ox1 + dx))
            if self.drag_mode & HIT_R: nx2 = max(ox1 + 1, min(sw, ox2 + dx))
            if self.drag_mode & HIT_T: ny1 = max(0, min(oy2 - 1, oy1 + dy))
            if self.drag_mode & HIT_B: ny2 = max(oy1 + 1, min(sh, oy2 + dy))
            el.x1, el.y1, el.x2, el.y2 = int(nx1), int(ny1), int(nx2), int(ny2)

        rect = self.element_to_rect.get(el)
        if rect:
            self.canvas.coords(rect, el.x1, el.y1, el.x2, el.y2)
        self._redraw_selection_highlight()
        self._update_coord_entries()
        self._refresh_selected_row()

    def _on_canvas_release(self, _event):
        if self.drag_mode == HIT_NONE or self.drag_target is None:
            self.drag_mode = HIT_NONE
            self.drag_target = None
            return
        sec = self.current_section
        if self.drag_target is HIT_DIALOG:
            _, _, ox2, oy2 = self.drag_orig
            if (sec.x2, sec.y2) != (ox2, oy2):
                self._commit_dlgsize(sec, (ox2, oy2))
                self._refresh_section_list()
        else:
            el = self.drag_target
            old = self.drag_orig
            if old != (el.x1, el.y1, el.x2, el.y2):
                self._commit_coords(sec, el, old)
        self.drag_mode = HIT_NONE
        self.drag_target = None
        self.drag_orig = None
        self.drag_orig_img = None
        self._draw_section()

    # --- Capital.dat: добавление / изменение / удаление слоёв ---------------

    def cmd_layer_add(self):
        if self.mode != MODE_DAT or not self.current_section:
            return
        sec = self.current_section
        base = self._selected_editable()      # за образец берём выбранный слой
        if isinstance(base, DatLayer):
            extra = list(base.extra)
            coords = (base.x1, base.y1, base.x2, base.y2)
        else:
            extra = ["0", "0", "0", "", "0", "0", "0"]
            coords = (0, 0, 100, 100)
        data = LayerDialog(self, sec, title=self.t("layer_add_title"),
                           z=sec.next_free_z(), build_id="", image="",
                           extra=extra, coords=coords,
                           offer_layerinfo=True).result
        if not data:
            return
        layer = DatLayer.make(data["z"], data["build_id"], data["image"],
                              data["extra"], data["coords"])
        sec.layers.append(layer)
        sec.layer_count += 1
        if data["layerinfo"] and data["build_id"] and \
                not sec.has_layerinfo(data["build_id"]):
            sec.layerinfos.append(DatLayerInfo(
                sec.next_layerinfo_key(), ["0", data["build_id"], ""]))
            sec.li_count += 1
        self.selected_element = layer
        self._commit(sec.name, self._hist_param(layer),
                     self.t("hist_none"),
                     self._coords_text((layer.x1, layer.y1,
                                        layer.x2, layer.y2)))
        self.selected_element = layer
        self._refresh_section_list()
        self._refresh_element_list()
        self._draw_section()
        self._update_coord_entries()

    def cmd_layer_edit(self):
        if self.mode != MODE_DAT or not self.current_section:
            return
        layer = self._selected_editable()
        if not isinstance(layer, DatLayer):
            messagebox.showinfo(self.t("layer_edit_title"),
                                self.t("no_selection"))
            return
        sec = self.current_section
        data = LayerDialog(self, sec, title=self.t("layer_edit_title"),
                           z=layer.z, build_id=layer.build_id,
                           image=layer.image, extra=list(layer.extra),
                           coords=(layer.x1, layer.y1, layer.x2, layer.y2),
                           offer_layerinfo=not sec.has_layerinfo(layer.build_id),
                           exclude=layer).result
        if not data:
            return
        old = (layer.x1, layer.y1, layer.x2, layer.y2)
        old_extra = list(layer.extra)
        layer.key = f"LAYER_{data['z']:02d}"
        layer.build_id = data["build_id"]
        layer.image = data["image"]
        layer.extra = data["extra"]
        layer.x1, layer.y1, layer.x2, layer.y2 = data["coords"]
        # Вторичные координаты трогаем, только если пользователь не правил
        # поле «Прочие поля» вручную — иначе его значение приоритетнее.
        if list(data["extra"]) == old_extra:
            self._apply_secondary_shift(layer, old)
        if data["layerinfo"] and data["build_id"] and \
                not sec.has_layerinfo(data["build_id"]):
            sec.layerinfos.append(DatLayerInfo(
                sec.next_layerinfo_key(), ["0", data["build_id"], ""]))
            sec.li_count += 1
        self._commit_coords(sec, layer, old)
        self.selected_element = layer
        self._refresh_element_list()
        self._draw_section()
        self._update_coord_entries()

    def cmd_layer_delete(self):
        if self.mode != MODE_DAT or not self.current_section:
            return
        layer = self._selected_editable()
        if not isinstance(layer, DatLayer):
            messagebox.showinfo(self.t("del_title"), self.t("no_selection"))
            return
        sec = self.current_section
        name = self._element_name_of(layer)
        has_li = sec.has_layerinfo(layer.build_id)
        confirm = ConfirmDeleteDialog(
            self,
            message=self.t("del_msg", name=layer.key, image=name),
            option_text=(self.t("del_layerinfo", build=layer.build_id)
                         if has_li else None),
        )
        if not confirm.ok:
            return

        sec.layers.remove(layer)
        sec.layer_count -= 1
        if has_li and confirm.option:
            bid = layer.build_id.strip().upper()
            keep = [li for li in sec.layerinfos
                    if (li.build_id or "").strip().upper() != bid]
            sec.li_count -= (len(sec.layerinfos) - len(keep))
            sec.layerinfos = keep
        old = (layer.x1, layer.y1, layer.x2, layer.y2)
        self.selected_element = None
        self._commit(sec.name, self._hist_param(layer),
                     self._coords_text(old), self.t("hist_none"))
        self._refresh_section_list()
        self._refresh_element_list()
        self._draw_section()
        self._update_coord_entries()


# =============================================================================
# Диалог редактирования слоя Capital.dat
# =============================================================================

class LayerDialog:
    def __init__(self, app, section, title, z, build_id, image, extra, coords,
                 offer_layerinfo=False, exclude=None):
        self.app = app
        self.section = section
        self.exclude = exclude
        self.result = None

        win = tk.Toplevel(app.root)
        self.win = win
        win.title(title)
        win.configure(bg=COLOR_BG_APP)
        win.resizable(False, False)
        win.transient(app.root)
        win.grab_set()

        pad = ttk.Frame(win, padding=12)
        pad.pack(fill="both", expand=True)
        pad.columnconfigure(1, weight=1)

        self.v_z = tk.StringVar(value=str(z))
        self.v_build = tk.StringVar(value=build_id)
        self.v_image = tk.StringVar(value=image)
        self.v_coords = tk.StringVar(value=", ".join(str(c) for c in coords))
        self.v_extra = tk.StringVar(value=",".join(extra))
        self.v_layerinfo = tk.BooleanVar(value=bool(offer_layerinfo))

        rows = (
            ("fld_z", self.v_z),
            ("fld_build", self.v_build),
            ("fld_image", self.v_image),
            ("fld_coords", self.v_coords),
            ("fld_extra", self.v_extra),
        )
        for r, (key, var) in enumerate(rows):
            ttk.Label(pad, text=app.t(key)).grid(row=r, column=0, sticky="w",
                                                 padx=(0, 8), pady=3)
            ttk.Entry(pad, textvariable=var, width=34).grid(
                row=r, column=1, sticky="ew", pady=3)

        chk = ttk.Checkbutton(pad, text=app.t("fld_layerinfo"),
                              variable=self.v_layerinfo)
        chk.grid(row=len(rows), column=0, columnspan=2, sticky="w", pady=(6, 0))
        if not offer_layerinfo:
            self.v_layerinfo.set(False)
            chk.state(["disabled"])

        btns = ttk.Frame(pad)
        btns.grid(row=len(rows) + 1, column=0, columnspan=2, sticky="e",
                  pady=(12, 0))
        btn_ok = ttk.Button(btns, text=app.t("btn_ok"), command=self._ok,
                            style="Save.TButton")
        btn_ok.pack(side="left", padx=(0, 6))
        btn_cancel = ttk.Button(btns, text=app.t("btn_cancel"),
                                command=win.destroy)
        btn_cancel.pack(side="left")
        Tooltip(btn_ok, lambda: app.t("btn_ok_tip"))
        Tooltip(btn_cancel, lambda: app.t("btn_cancel_tip"))

        win.bind("<Return>", lambda _e: self._ok())
        win.bind("<Escape>", lambda _e: win.destroy())
        place_in_view(win, app.root.winfo_rootx() + 120,
                      app.root.winfo_rooty() + 120, ref=app.root)
        app.root.wait_window(win)

    def _ok(self):
        app = self.app
        try:
            z = int(self.v_z.get().strip())
        except ValueError:
            messagebox.showerror(app.t("err_layer_title"),
                                 app.t("err_layer_z"), parent=self.win)
            return
        for layer in self.section.layers:
            if layer is self.exclude:
                continue
            if layer.z == z:
                messagebox.showerror(app.t("err_layer_title"),
                                     app.t("err_layer_dup", z=z),
                                     parent=self.win)
                return
        parts = [p.strip() for p in self.v_coords.get().replace(";", ",")
                 .split(",") if p.strip() != ""]
        if len(parts) != 4:
            messagebox.showerror(app.t("err_layer_title"),
                                 app.t("err_layer_coords"), parent=self.win)
            return
        try:
            coords = [int(p) for p in parts]
        except ValueError:
            messagebox.showerror(app.t("err_layer_title"),
                                 app.t("err_layer_coords"), parent=self.win)
            return

        extra = self.v_extra.get().split(",")
        while len(extra) < DAT_COORD_OFFSET - 2:
            extra.append("0")
        extra = extra[:DAT_COORD_OFFSET - 2]

        self.result = {
            "z": z,
            "build_id": self.v_build.get().strip(),
            "image": self.v_image.get().strip(),
            "extra": extra,
            "coords": coords,
            "layerinfo": bool(self.v_layerinfo.get()),
        }
        self.win.destroy()


class ConfirmDeleteDialog:
    """Подтверждение удаления слоя (+ опция удаления записи LAYERINFO)."""

    def __init__(self, app, message, option_text=None):
        self.ok = False
        self.option = False

        win = tk.Toplevel(app.root)
        win.title(app.t("del_title"))
        win.configure(bg=COLOR_BG_APP)
        win.resizable(False, False)
        win.transient(app.root)
        win.grab_set()

        pad = ttk.Frame(win, padding=14)
        pad.pack(fill="both", expand=True)
        ttk.Label(pad, text=message, justify="left").pack(anchor="w")

        var = tk.BooleanVar(value=bool(option_text))
        if option_text:
            ttk.Checkbutton(pad, text=option_text, variable=var).pack(
                anchor="w", pady=(10, 0))

        def _ok():
            self.ok = True
            self.option = bool(var.get()) if option_text else False
            win.destroy()

        btns = ttk.Frame(pad)
        btns.pack(anchor="e", pady=(14, 0))
        btn_del_ok = ttk.Button(btns, text=app.t("btn_ok"), command=_ok,
                                style="Revert.TButton")
        btn_del_ok.pack(side="left", padx=(0, 6))
        btn_del_cancel = ttk.Button(btns, text=app.t("btn_cancel"),
                                    command=win.destroy)
        btn_del_cancel.pack(side="left")
        Tooltip(btn_del_ok, lambda: app.t("btn_delete_ok_tip"))
        Tooltip(btn_del_cancel, lambda: app.t("btn_cancel_tip"))

        win.bind("<Return>", lambda _e: _ok())
        win.bind("<Escape>", lambda _e: win.destroy())
        place_in_view(win, app.root.winfo_rootx() + 160,
                      app.root.winfo_rooty() + 160, ref=app.root)
        app.root.wait_window(win)


def main():
    initial = sys.argv[1] if len(sys.argv) > 1 else None
    root = tk.Tk()
    DlgEditorApp(root, initial_path=initial)
    root.mainloop()


if __name__ == "__main__":
    main()
