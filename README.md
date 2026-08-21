# Fessoid Interface DLG Editor for Disciples [![Скачать](https://img.shields.io/github/v/release/Fessoid/Fessoid-DLG-Editor-for-Disciples?color=orange)](https://github.com/Fessoid/Fessoid-DLG-Editor-for-Disciples/releases)  [RU/ENG/PL/CN]
**Редактор интерфейса для Disciples 1 and 2 by Fessoid**  
**Interface editor for Disciples 1 and 2**
  
[Патчноут/Changelog/Dziennik zmian/更新日志](https://github.com/Fessoid/Fessoid-DLG-Editor-for-Disciples/blob/main/CHANGELOG.md)
<br>  
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
 
▸ **ВАРИАНТ А — ЗАПУСК ГОТОВОГО EXE (без установки Python)**

  Если у вас есть готовый exe-файл программы, просто запустите его двойным
  кликом. Никаких дополнительных действий не требуется.
<br>
<br>
▸ **ВАРИАНТ Б — ЗАПУСК СКРИПТА НА PYTHON**

  1. Скачайте Python с официального сайта:
     https://www.python.org/downloads/

  2. При установке ОБЯЗАТЕЛЬНО поставьте галочку:
     ☑ «Add Python to PATH»
     Затем нажмите «Install Now».

  3. Откройте папку, где лежит файл fessoid_dlg_editor_for_disciples.py.
     Зажмите Shift и кликните правой кнопкой мыши по пустому месту в папке.
     Выберите «Открыть окно PowerShell здесь» (или «Открыть командную строку»).

  4. Введите команду:
     python fessoid_dlg_editor_for_disciples.py
<br>
<br>

▸ **ВАРИАНТ В — СБОРКА В EXE**

  1. Установите Python (см. выше).

  2. Откройте командную строку (Win+R → cmd → Enter).

  3. Установите PyInstaller:
     pip install pyinstaller

  4. Перейдите в папку со скриптом:
     cd C:\путь\к\папке\со\скриптом

  5. Запустите сборку:
     pyinstaller --onefile --windowed --name "Fessoid DLG Editor for Disciples" fessoid_dlg_editor_for_disciples.py


  6. Готовый Fessoid DLG Editor for Disciples.exe будет в папке dist\.
     Папку build\ и файл Fessoid DLG Editor for Disciples.spec можно удалить.
<br>
<br>  
</details>  
<details>  
 <summary>ENGLISH</summary>

▸ **OPTION A — RUNNING THE READY-MADE EXE (no Python needed)**

  If you have the program's exe file, just double-click it to run.
  No additional installation is required.
<br>
<br>

▸ **OPTION B — RUNNING THE PYTHON SCRIPT**

  1. Download Python from the official website:
     https://www.python.org/downloads/

  2. During installation, make sure to check:
     ☑ "Add Python to PATH"
     Then click "Install Now".

  3. Open the folder containing fessoid_dlg_editor_for_disciples.py.
     Hold Shift and right-click on an empty area in the folder.
     Select "Open PowerShell window here" (or "Open command window here").

  4. Type the command:
     python fessoid_dlg_editor_for_disciples.py
<br>
<br>

▸ **OPTION C — BUILDING AN EXE**

  1. Install Python (see above).

  2. Open Command Prompt (Win+R → cmd → Enter).

  3. Install PyInstaller:
     pip install pyinstaller

  4. Navigate to the script folder:
     cd C:\path\to\script\folder

  5. Build the executable:
     pyinstaller --onefile --windowed --name "Fessoid DLG Editor for Disciples" fessoid_dlg_editor_for_disciples.py

  6. The resulting Fessoid DLG Editor for Disciples.exe will be in the dist\ folder.
     The build\ folder and the Fessoid DLG Editor for Disciples.spec file can be deleted.
<br>
<br>  
</details>    
<details>
<summary>POLSKI</summary>


▸ **OPCJA A — URUCHOMIENIE GOTOWEGO PLIKU EXE (bez instalacji Pythona)**

  Jeśli posiadasz plik exe programu, po prostu kliknij go dwukrotnie.
  Nie jest wymagana żadna dodatkowa instalacja.
<br>
<br>

▸ **OPCJA B — URUCHOMIENIE SKRYPTU PYTHON**

  1. Pobierz Pythona z oficjalnej strony:
     https://www.python.org/downloads/

  2. Podczas instalacji KONIECZNIE zaznacz opcję:
     ☑ „Add Python to PATH"
     Następnie kliknij „Install Now".

  3. Otwórz folder zawierający plik fessoid_dlg_editor_for_disciples.py.
     Przytrzymaj Shift i kliknij prawym przyciskiem myszy na pustym obszarze.
     Wybierz „Otwórz okno programu PowerShell tutaj"
     (lub „Otwórz okno polecenia tutaj").

  4. Wpisz polecenie:
     python fessoid_dlg_editor_for_disciples.py
<br>
<br>

▸ **OPCJA C — KOMPILACJA DO EXE**

  1. Zainstaluj Pythona (patrz wyżej).

  2. Otwórz Wiersz polecenia (Win+R → cmd → Enter).

  3. Zainstaluj PyInstaller:
     pip install pyinstaller

  4. Przejdź do folderu ze skryptem:
     cd C:\ścieżka\do\folderu\ze\skryptem

  5. Uruchom kompilację:
     pyinstaller --onefile --windowed --name "Fessoid DLG Editor for Disciples" fessoid_dlg_editor_for_disciples.py


  6. Gotowy plik Fessoid DLG Editor for Disciples.exe znajdziesz w folderze dist\.
     Folder build\ oraz plik Fessoid DLG Editor for Disciples.spec można usunąć.
<br>
<br> 

</details>  
<details>  
<summary>简体中文</summary>


▸ **方案 A — 运行现成的 EXE 文件（无需安装 Python）**

  如果您已有本程序的 exe 文件，双击即可运行。
  无需任何额外安装。
<br>
<br>

▸ **方案 B — 运行 Python 脚本**

  1. 从官方网站下载 Python：
     https://www.python.org/downloads/

  2. 安装时务必勾选：
     ☑「Add Python to PATH」
     然后点击「Install Now」。

  3. 打开 fessoid_dlg_editor_for_disciples.py 所在的文件夹。
     按住 Shift 键，在文件夹空白处右键单击。
     选择「在此处打开 PowerShell 窗口」（或「在此处打开命令窗口」）。

  4. 输入命令：
     python fessoid_dlg_editor_for_disciples.py
<br>
<br>

▸ **方案 C — 编译为 EXE**

  1. 安装 Python（参见上文）。

  2. 打开命令提示符（Win+R → cmd → 回车）。

  3. 安装 PyInstaller：
     pip install pyinstaller

  4. 切换到脚本所在文件夹：
     cd C:\脚本文件夹路径

  5. 运行编译命令：
     pyinstaller --onefile --windowed --name "Fessoid DLG Editor for Disciples" fessoid_dlg_editor_for_disciples.py


  6. 生成的 Fessoid DLG Editor for Disciples.exe 将位于 dist\ 文件夹中。
     build\ 文件夹和 Fessoid DLG Editor for Disciples.spec 文件可以删除。
</details> 
<br>
    
**Interf.dlg**  
<img width="1365" height="729" alt="image" src="https://github.com/user-attachments/assets/a1f7359b-9fb3-4280-b3d0-8558d104e5a5" />


**ScenEdit.dlg**  
<img width="1365" height="729" alt="image" src="https://github.com/user-attachments/assets/47e13553-c541-481d-a19f-a22110969b39" />



**CustomLobby.dlg**  
<img width="1365" height="729" alt="image" src="https://github.com/user-attachments/assets/73408844-ebc9-46a6-9f55-a10b9db6bcc0" />



**Interf.dlg** 
<img width="1365" height="728" alt="image" src="https://github.com/user-attachments/assets/1b30b8f6-72c5-4d02-b535-2536e79ded05" />
  


**Capital.dat**
<img width="1365" height="729" alt="image" src="https://github.com/user-attachments/assets/609c309f-e35a-43e9-b9ab-16cc83056cfd" />

<br>

**О программе**  <br>
<img width="413" height="495" alt="image" src="https://github.com/user-attachments/assets/7180c7bd-48e8-4561-97dd-72e159f711da" />

