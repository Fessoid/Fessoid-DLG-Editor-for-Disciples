# Interface DLG Editor for Disciples by Fessoid v1.1 [RU/ENG/PL/CN]
**Редактор интерфейса для Disciples 1 and 2 by Fessoid**  
**Interface editor for Disciples 1 and 2**
  
  
[![Скачать](https://img.shields.io/github/v/release/Fessoid/DLG-Editor-for-Disciples?color=orange)](https://github.com/Fessoid/DLG-Editor-for-Disciples/releases)  
[Патчноут/Changelog/Dziennik zmian/更新日志](https://github.com/Fessoid/DLG-Editor-for-Disciples/blob/main/CHANGELOG.md)

Разработал программу для самостоятельного изменения интерфейса игр Disciples (1 и 2 части).  

Редактирует dlg-файлы интерфейса как для Оригинальной игры, так и любых модов (папка Interf).  
Основная фишка - акцент на редактировании текстов и размеров полей, окон и кнопок.  

Так же редактирует размещение иконок зданий на Главном экране Столицы (файл Capital.dat в папке Imgs)

VIDEO 
[YouTube](https://youtu.be/MfSSoe-kNx4)/[Boosty](https://boosty.to/fessoid/posts/a86bc6a9-8427-40c7-8787-47226955f194?share=post_link&utm_source=github)
=
  
**Installation & How to Use**  

  
  
<details>
 <summary> РУССКИЙ </summary>
 
▸ ВАРИАНТ А — ЗАПУСК ГОТОВОГО EXE (без установки Python)

  Если у вас есть готовый файл DLG Editor for Disciples.exe, просто запустите его двойным
  кликом. Никаких дополнительных действий не требуется.


▸ ВАРИАНТ Б — ЗАПУСК СКРИПТА НА PYTHON

  1. Скачайте Python с официального сайта:
     https://www.python.org/downloads/

  2. При установке ОБЯЗАТЕЛЬНО поставьте галочку:
     ☑ «Add Python to PATH»
     Затем нажмите «Install Now».

  3. Откройте папку, где лежит файл dlg_editor_for_disciples.py.
     Зажмите Shift и кликните правой кнопкой мыши по пустому месту в папке.
     Выберите «Открыть окно PowerShell здесь» (или «Открыть командную строку»).

  4. Введите команду:
     python dlg_editor_for_disciples.py


▸ ВАРИАНТ В — СБОРКА В EXE

  1. Установите Python (см. выше).

  2. Откройте командную строку (Win+R → cmd → Enter).

  3. Установите PyInstaller:
     pip install pyinstaller

  4. Перейдите в папку со скриптом:
     cd C:\путь\к\папке\со\скриптом

  5. Запустите сборку:
     pyinstaller --onefile --windowed --name "DLG Editor for Disciples" dlg_editor_for_disciples.py


  6. Готовый DLG Editor for Disciples.exe будет в папке dist\.
     Папки build\ и файл DLG Editor for Disciples.spec можно удалить.
  
</details>  
<details>  
 <summary>ENGLISH</summary>

▸ OPTION A — RUNNING THE READY-MADE EXE (no Python needed)

  If you have the DLG Editor for Disciples.exe file, just double-click it to run.
  No additional installation is required.


▸ OPTION B — RUNNING THE PYTHON SCRIPT

  1. Download Python from the official website:
     https://www.python.org/downloads/

  2. During installation, make sure to check:
     ☑ "Add Python to PATH"
     Then click "Install Now".

  3. Open the folder containing dlg_editor_for_disciples.py.
     Hold Shift and right-click on an empty area in the folder.
     Select "Open PowerShell window here" (or "Open command window here").

  4. Type the command:
     python dlg_editor_for_disciples.py


▸ OPTION C — BUILDING AN EXE

  1. Install Python (see above).

  2. Open Command Prompt (Win+R → cmd → Enter).

  3. Install PyInstaller:
     pip install pyinstaller

  4. Navigate to the script folder:
     cd C:\path\to\script\folder

  5. Build the executable:
     pyinstaller --onefile --windowed --name "DLG Editor for Disciples" dlg_editor_for_disciples.py

  6. The resulting DLG Editor for Disciples.exe will be in the dist\ folder.
     The build\ folder and DLG Editor for Disciples.spec file can be deleted.
  
</details>    
<details>
<summary>POLSKI</summary>


▸ OPCJA A — URUCHOMIENIE GOTOWEGO PLIKU EXE (bez instalacji Pythona)

  Jeśli posiadasz plik DLG Editor for Disciples.exe, po prostu kliknij go dwukrotnie.
  Nie jest wymagana żadna dodatkowa instalacja.



▸ OPCJA B — URUCHOMIENIE SKRYPTU PYTHON

  1. Pobierz Pythona z oficjalnej strony:
     https://www.python.org/downloads/

  2. Podczas instalacji KONIECZNIE zaznacz opcję:
     ☑ „Add Python to PATH"
     Następnie kliknij „Install Now".

  3. Otwórz folder zawierający plik dlg_editor_for_disciples.py.
     Przytrzymaj Shift i kliknij prawym przyciskiem myszy na pustym obszarze.
     Wybierz „Otwórz okno programu PowerShell tutaj"
     (lub „Otwórz okno polecenia tutaj").

  4. Wpisz polecenie:
     python dlg_editor_for_disciples.py


▸ OPCJA C — KOMPILACJA DO EXE

  1. Zainstaluj Pythona (patrz wyżej).

  2. Otwórz Wiersz polecenia (Win+R → cmd → Enter).

  3. Zainstaluj PyInstaller:
     pip install pyinstaller

  4. Przejdź do folderu ze skryptem:
     cd C:\ścieżka\do\folderu\ze\skryptem

  5. Uruchom kompilację:
     pyinstaller --onefile --windowed --name "DLG Editor for Disciples" dlg_editor_for_disciples.py


  6. Gotowy plik DLG Editor for Disciples.exe znajdziesz w folderze dist\.
     Foldery build\ oraz plik DLG Editor for Disciples.spec można usunąć.

  

</details>  
<details>  
<summary>简体中文</summary>


▸ 方案 A — 运行现成的 EXE 文件（无需安装 Python）

  如果您已有 DLG Editor for Disciples.exe 文件，双击即可运行。
  无需任何额外安装。


▸ 方案 B — 运行 Python 脚本

  1. 从官方网站下载 Python：
     https://www.python.org/downloads/

  2. 安装时务必勾选：
     ☑「Add Python to PATH」
     然后点击「Install Now」。

  3. 打开 dlg_editor_for_disciples.py 所在的文件夹。
     按住 Shift 键，在文件夹空白处右键单击。
     选择「在此处打开 PowerShell 窗口」（或「在此处打开命令窗口」）。

  4. 输入命令：
     python dlg_editor_for_disciples.py


▸ 方案 C — 编译为 EXE

  1. 安装 Python（参见上文）。

  2. 打开命令提示符（Win+R → cmd → 回车）。

  3. 安装 PyInstaller：
     pip install pyinstaller

  4. 切换到脚本所在文件夹：
     cd C:\脚本文件夹路径

  5. 运行编译命令：
     pyinstaller --onefile --windowed --name "DLG Editor for Disciples" dlg_editor_for_disciples.py


  6. 生成的 DLG Editor for Disciples.exe 将位于 dist\ 文件夹中。
     build\ 文件夹和 DLG Editor for Disciples.spec 文件可以删除。
</details> 


    
**ScenEdit.dlg**  
<img width="1365" height="730" alt="image" src="https://github.com/user-attachments/assets/1bd996cf-e3ea-432c-be1e-e389a2b9a4fe" />

  
**ScenEdit.dlg**  
<img width="1365" height="730" alt="image" src="https://github.com/user-attachments/assets/811848ae-734c-4ff9-acf7-c5d40acfb7e4" />

  
**CustomLobby.dlg**  
<img width="1365" height="730" alt="image" src="https://github.com/user-attachments/assets/06a54d5b-6666-4280-8c92-e84be2470881" />

  
**Interf.dlg**  
<img width="1365" height="728" alt="image" src="https://github.com/user-attachments/assets/1b94a6f6-0458-412e-9da6-01e23dae91f1" />

  
**О программе**  
<img width="395" height="497" alt="image" src="https://github.com/user-attachments/assets/b08ea5c3-0be1-42d5-b31f-e457559734cc" />
