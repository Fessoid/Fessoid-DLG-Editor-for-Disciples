# DLG Editor for Disciples - Новое в версии 1.3

## Русский

**Главное: кнопки в диалогах теперь можно двигать и растягивать.**

- **Кнопки BUTTON стали доступны для правки.** Раньше редактор видел только кнопки типа BUTTONSD, а обычные не показывал вовсе — в Interf.dlg это 440 кнопок, до которых нельзя было добраться. Теперь они рисуются на схеме окна и меняются мышью или вводом координат, как остальные элементы.
- **В строке над схемой виден полный путь к файлу.** Раньше было только имя. Длинный путь сокращается по папкам, но диск и имя файла остаются на виду, а окно от этого не растягивается.
- **Программа проверяет обновления при запуске.** Если вышла новая версия, она предложит обновиться. Проверка идёт в фоне: нет интернета или сайт не ответил — программа просто запускается дальше и ничего не сообщает.
- **Отказ от обновления запоминается.** Ответили «нет» — про эту версию больше не спросят. Выйдет следующая — предложение появится снова.
- **Обновление скачивается в папку с программой.** После загрузки она предложит запустить новую версию и закрыть текущую. Несохранённые изменения при этом не пропадут: их предложат сохранить, как при обычном выходе.
- **Кнопка «Открыть папку файла»** рядом с «Открыть файл в блокноте» — открывает проводник на нужной папке и сразу выделяет в ней текущий файл.
- **Кнопка «Перечитать файл»** над списком элементов — перечитывает файл с диска, если его изменили в другой программе. Подтверждения не спрашивает, но при наведении предупреждает, что несохранённые изменения пропадут.
- **У всех кнопок появились подсказки при наведении** — и в главном окне, и во всех остальных окнах, на всех четырёх языках.
- **В меню языков появились флаги стран,** а сам пункт подписан «Язык (RU/EN/PL/中文)». Даже если программа запустилась на незнакомом языке, переключатель находится с одного взгляда.
- **Текущий язык отмечен галочкой.**
- **Подсказки и окна больше не уезжают за край экрана.** Подсказка у нижних кнопок пряталась под панелью задач; теперь, если снизу нет места, она открывается сверху. Окна «История изменений», «О программе», параметров слоя и подтверждения удаления тоже всегда открываются целиком.
- **Правая панель прокручивается.** На невысоких экранах нижние кнопки не помещались, и до них было не добраться. Полоса прокрутки появляется только когда содержимое не влезает; на большом окне список элементов по-прежнему занимает всё свободное место.
- **В меню «Правка»** пункты стали называться «Отменить изменение» и «Вернуть изменение» — раньше было «действие», и это сбивало с толку.
- **В окне «О программе»** исправлена ссылка на репозиторий, а ссылка на Boosty подписана «Поддержать разработку».
- **Файл по-прежнему сохраняется в точности как был:** при правке кнопки меняются только её координаты, всё остальное в строке остаётся нетронутым.

---

## English

**Highlight: buttons in dialogs can now be moved and resized.**

- **BUTTON controls became editable.** The editor used to see only BUTTONSD buttons and did not show ordinary ones at all — that is 440 buttons in Interf.dlg you simply could not reach. They are now drawn on the window layout and can be changed with the mouse or by typing coordinates, like every other element.
- **The line above the layout shows the full path to the file.** It used to show only the name. A long path is shortened by folders, but the drive and the file name always stay visible, and the window does not stretch because of it.
- **The program checks for updates on startup.** If a new version is out, it offers to update. The check runs in the background: no internet or no answer from the site, and the program simply starts as usual without saying anything.
- **A declined update is remembered.** Answer "no" and you will not be asked about that version again. When the next one comes out, the offer returns.
- **The update is downloaded into the program's folder.** Once it is there, the program offers to launch the new version and close the current one. Unsaved changes are not lost: you are asked to save them, exactly as on a normal exit.
- **The "Open file folder" button** next to "Open file in Notepad" opens the file manager at the right folder and selects the current file in it.
- **The "Reload file" button** above the element list re-reads the file from disk if it was changed in another program. It asks for no confirmation, but the hover tooltip warns that unsaved changes will be lost.
- **Every button now has a hover tooltip** — in the main window and in all the other windows, in all four languages.
- **The language menu now shows country flags,** and the menu itself is labelled "Language (RU/EN/PL/中文)". Even when the program starts in an unfamiliar language, the switch is found at a glance.
- **The current language is marked with a tick.**
- **Tooltips and windows no longer slide off the screen.** The tooltip of the bottom buttons used to hide under the taskbar; now it opens above the button when there is no room below. The change history, About, layer parameters and delete confirmation windows also always open fully on screen.
- **The right panel scrolls.** On short screens the bottom buttons did not fit and could not be reached. The scrollbar appears only when the content does not fit; on a large window the element list still takes all the free space.
- **In the Edit menu** the items are now "Undo change" and "Redo change" — they used to say "action", which was confusing.
- **In the About window** the repository link is fixed, and the Boosty link is labelled "Support the development".
- **The file is still saved exactly as it was:** editing a button changes only its coordinates, everything else in the line stays untouched.

---

## Polski

**Najważniejsze: przyciski w oknach dialogowych można teraz przesuwać i skalować.**

- **Przyciski BUTTON stały się edytowalne.** Edytor widział wcześniej tylko przyciski typu BUTTONSD, a zwykłych nie pokazywał wcale — w Interf.dlg to 440 przycisków, do których nie dało się dotrzeć. Teraz są rysowane na schemacie okna i zmieniają się myszą albo przez wpisanie współrzędnych, jak pozostałe elementy.
- **W linii nad schematem widać pełną ścieżkę do pliku.** Wcześniej była tylko nazwa. Długa ścieżka jest skracana po folderach, ale dysk i nazwa pliku zawsze pozostają widoczne, a okno się przez to nie rozciąga.
- **Program sprawdza aktualizacje przy starcie.** Jeśli ukazała się nowa wersja, zaproponuje aktualizację. Sprawdzanie działa w tle: brak internetu albo brak odpowiedzi — program po prostu uruchamia się dalej i nic nie komunikuje.
- **Odrzucona aktualizacja jest zapamiętywana.** Odpowiedź „nie" i o tej wersji program już nie zapyta. Gdy ukaże się następna, propozycja wróci.
- **Aktualizacja pobierana jest do folderu z programem.** Po pobraniu program proponuje uruchomić nową wersję i zamknąć bieżącą. Niezapisane zmiany nie przepadną: zostanie zaproponowane ich zapisanie, jak przy zwykłym wyjściu.
- **Przycisk „Otwórz folder pliku"** obok „Otwórz plik w notatniku" otwiera menedżer plików na właściwym folderze i od razu zaznacza w nim bieżący plik.
- **Przycisk „Wczytaj ponownie"** nad listą elementów wczytuje plik z dysku na nowo, jeśli zmieniono go w innym programie. Nie pyta o potwierdzenie, ale podpowiedź ostrzega, że niezapisane zmiany przepadną.
- **Wszystkie przyciski mają teraz podpowiedzi po najechaniu** — w oknie głównym i we wszystkich pozostałych, we wszystkich czterech językach.
- **W menu języków pojawiły się flagi krajów,** a sama pozycja opisana jest „Język (RU/EN/PL/中文)". Nawet gdy program uruchomi się w nieznanym języku, przełącznik znajduje się od razu.
- **Bieżący język jest oznaczony ptaszkiem.**
- **Podpowiedzi i okna nie uciekają już poza ekran.** Podpowiedź dolnych przycisków chowała się pod paskiem zadań; teraz otwiera się nad przyciskiem, gdy pod spodem nie ma miejsca. Okna historii zmian, „O programie", parametrów warstwy i potwierdzenia usunięcia również zawsze otwierają się w całości.
- **Prawy panel się przewija.** Na niskich ekranach dolne przyciski nie mieściły się i nie dało się do nich dotrzeć. Suwak pojawia się tylko wtedy, gdy treść się nie mieści; przy dużym oknie lista elementów nadal zajmuje całe wolne miejsce.
- **W menu „Edycja"** pozycje nazywają się teraz „Cofnij zmianę" i „Ponów zmianę" — wcześniej było „działanie", co wprowadzało w błąd.
- **W oknie „O programie"** poprawiono link do repozytorium, a link do Boosty jest podpisany „Wesprzyj rozwój".
- **Plik nadal zapisywany jest dokładnie tak, jak był:** edycja przycisku zmienia wyłącznie jego współrzędne, reszta linii pozostaje nietknięta.

---

## 简体中文

**重点：对话框中的按钮现在可以移动和缩放。**

- **BUTTON 按钮变得可以编辑。** 此前编辑器只能识别 BUTTONSD 类型的按钮，普通按钮完全不显示——仅 Interf.dlg 中就有 440 个无法触及的按钮。现在它们会绘制在窗口示意图上，可以用鼠标拖动，也可以输入坐标修改，和其他元素一样。
- **示意图上方一行显示文件的完整路径。** 以前只显示文件名。路径过长时会按文件夹缩略，但盘符和文件名始终可见，窗口也不会因此被撑大。
- **程序在启动时检查更新。** 若有新版本发布，会提示更新。检查在后台进行：没有网络或网站没有响应时，程序照常启动，不作任何提示。
- **拒绝过的更新会被记住。** 选择「否」之后，就不会再就该版本询问。下一个版本发布时，提示会重新出现。
- **更新会下载到程序所在的文件夹。** 下载完成后，程序会询问是否启动新版本并关闭当前程序。未保存的更改不会丢失：会像正常退出那样提示保存。
- **「打开文件所在文件夹」按钮**位于「用记事本打开文件」旁边，可在文件管理器中打开对应文件夹并选中当前文件。
- **「重新读取文件」按钮**位于元素列表上方，用于在文件被其他程序修改后重新读取。它不询问确认，但鼠标悬停时会提示未保存的更改将会丢失。
- **所有按钮都新增了悬停提示**——主窗口和其他窗口都有，四种语言齐备。
- **语言菜单中新增了国旗，**菜单项本身标注为「语言 (RU/EN/PL/中文)」。即使程序以陌生的语言启动，也能一眼找到切换入口。
- **当前语言以对勾标出。**
- **提示和窗口不会再跑到屏幕之外。** 底部按钮的提示原本会藏到任务栏下方；现在下方空间不足时会显示在按钮上方。修改历史、「关于」、图层参数和删除确认窗口也总是完整显示。
- **右侧面板可以滚动。** 屏幕较矮时底部按钮放不下，也无法点到。滚动条仅在内容放不下时才出现；窗口较大时，元素列表仍会占满空余空间。
- **「编辑」菜单**中的项目改为「撤销修改」和「恢复修改」——此前写作「操作」，容易让人误解。
- **「关于」窗口**中修正了仓库链接，Boosty 链接标注为「支持开发」。
- **文件依然会原样保存：** 编辑按钮只改动它的坐标，行内其余内容保持不变。

---

# DLG Editor for Disciples - Новое в версии 1.2

## Русский

**Главное: добавлена поддержка Capital.dat.**

- **Новый режим Capital.dat.** Редактор автоматически переключается по расширению открытого файла. Читаются 5 расовых секций ([HUMAN], [UNDEAD], [HERETIC], [DWARF], [ELF]), строки `LAYER_zzz` и `LAYERINFO_xx`. Слои рисуются на холсте 800×600, их можно двигать и растягивать мышью.
- **Работа со слоями:** добавление, изменение и удаление слоя (с подтверждением и опцией удаления связанной записи LAYERINFO). Счётчики `LayerCount` / `LayerInfoCount` изменяются на дельту, чтобы не ломать оригинальные файлы, где они не совпадают с фактическим числом строк.
- **Вторичные координаты картинки** (DAT_IMG_X_INDEX / DAT_IMG_Y_INDEX) сдвигаются вместе с рамкой при перемещении слоя и не трогаются при изменении её размера. Поведение отключается: меню «Настройки» → «Изменять вторичные координаты в .dat».
- **История изменений.** Отмена и повтор (Ctrl+Z / Ctrl+Y), отдельное окно «История изменений» (Ctrl+H): таблица со столбцами ►, Секция, Параметр, Было, Стало и первой строкой — исходным состоянием файла. Двойной клик или кнопка «Откатиться к выбранному состоянию» возвращают файл к любому шагу. История своя на каждый файл.
- **Копирование имён.** Ctrl+C и правый клик копируют имя секции или элемента/слоя.
- **Горячие клавиши работают при любой раскладке клавиатуры** — клавиша определяется по физическому коду, а не по символу.
- **Кнопка «Открыть файл в блокноте»** в заголовке блока «Подсказки» — открывает текущий файл системным редактором по умолчанию.
- Блок «Подсказки» получил вертикальную прокрутку, тексты подсказок отдельные для .dlg и .dat.
- В диалоге открытия появился общий фильтр «Disciples files (*.dlg *.dat)».
- Новые пункты меню «Правка» и «Настройки», номер версии теперь задаётся в коде и виден в окне «О программе».
- Настройка «Изменять вторичные координаты» сохраняется в DLG_Editor_settings.ini.
- Побайтовый round-trip нетронутого файла гарантирован для обоих форматов.

---

## English

**Highlight: Capital.dat support added.**

- **New Capital.dat mode.** The editor switches automatically based on the file extension. It reads the 5 race sections ([HUMAN], [UNDEAD], [HERETIC], [DWARF], [ELF]) and the `LAYER_zzz` / `LAYERINFO_xx` lines. Layers are drawn on an 800×600 canvas and can be moved and resized with the mouse.
- **Layer editing:** add, edit and delete layers (with confirmation and an option to also remove the linked LAYERINFO entry). `LayerCount` / `LayerInfoCount` are adjusted by delta, so original files where these counters do not match the actual number of lines stay intact.
- **Secondary image coordinates** (DAT_IMG_X_INDEX / DAT_IMG_Y_INDEX) shift together with the frame when a layer is moved, and stay untouched when the frame is resized. This can be turned off in Settings → "Update secondary coordinates in .dat".
- **Change history.** Undo/redo (Ctrl+Z / Ctrl+Y) and a dedicated "Change history" window (Ctrl+H): a table with ►, Section, Parameter, Before, After columns, the first row being the file's initial state. A double click or the "Revert to selected state" button restores any step. History is kept per file.
- **Copying names.** Ctrl+C and right click copy the name of a section or an element/layer.
- **Shortcuts now work with any keyboard layout** — the key is detected by its physical code, not by the produced character.
- **"Open file in Notepad" button** in the header of the Tips panel — opens the current file in the OS default editor.
- The Tips panel is now scrollable, with separate tip texts for .dlg and .dat.
- The Open dialog got a combined "Disciples files (*.dlg *.dat)" filter.
- New "Edit" and "Settings" menus; the version number is now defined in code and shown in the About window.
- The "Update secondary coordinates" option is stored in DLG_Editor_settings.ini.
- Byte-for-byte round-trip of an untouched file is guaranteed for both formats.

---

## Polski

**Najważniejsze: dodano obsługę Capital.dat.**

- **Nowy tryb Capital.dat.** Edytor przełącza się automatycznie według rozszerzenia pliku. Wczytuje 5 sekcji ras ([HUMAN], [UNDEAD], [HERETIC], [DWARF], [ELF]) oraz linie `LAYER_zzz` i `LAYERINFO_xx`. Warstwy są rysowane na płótnie 800×600 i można je przesuwać oraz rozciągać myszą.
- **Edycja warstw:** dodawanie, zmiana i usuwanie warstwy (z potwierdzeniem i opcją usunięcia powiązanego wpisu LAYERINFO). Liczniki `LayerCount` / `LayerInfoCount` zmieniają się o deltę, dzięki czemu oryginalne pliki, w których nie zgadzają się one z faktyczną liczbą linii, pozostają poprawne.
- **Wtórne współrzędne obrazka** (DAT_IMG_X_INDEX / DAT_IMG_Y_INDEX) przesuwają się razem z ramką przy przenoszeniu warstwy, a przy zmianie jej rozmiaru pozostają nietknięte. Można to wyłączyć: Ustawienia → „Zmieniaj wtórne współrzędne w .dat".
- **Historia zmian.** Cofnij/ponów (Ctrl+Z / Ctrl+Y) oraz osobne okno „Historia zmian" (Ctrl+H): tabela z kolumnami ►, Sekcja, Parametr, Było, Jest, gdzie pierwszy wiersz to stan początkowy pliku. Podwójne kliknięcie lub przycisk „Przywróć wybrany stan" cofa plik do dowolnego kroku. Historia jest osobna dla każdego pliku.
- **Kopiowanie nazw.** Ctrl+C i prawy przycisk myszy kopiują nazwę sekcji lub elementu/warstwy.
- **Skróty klawiszowe działają przy każdym układzie klawiatury** — klawisz rozpoznawany jest po kodzie fizycznym, a nie po znaku.
- **Przycisk „Otwórz plik w notatniku"** w nagłówku panelu „Wskazówki" — otwiera bieżący plik domyślnym edytorem systemu.
- Panel „Wskazówki" ma teraz pionowe przewijanie, a teksty wskazówek są osobne dla .dlg i .dat.
- W oknie otwierania pojawił się wspólny filtr „Disciples files (*.dlg *.dat)".
- Nowe menu „Edycja" i „Ustawienia"; numer wersji jest definiowany w kodzie i widoczny w oknie „O programie".
- Opcja „Zmieniaj wtórne współrzędne" zapisywana jest w DLG_Editor_settings.ini.
- Zapewniony bajt w bajt round-trip nietkniętego pliku dla obu formatów.

---

## 简体中文

**重点：新增对 Capital.dat 的支持。**

- **全新 Capital.dat 模式。** 编辑器根据文件扩展名自动切换模式，可读取 5 个种族段（[HUMAN]、[UNDEAD]、[HERETIC]、[DWARF]、[ELF]）以及 `LAYER_zzz` / `LAYERINFO_xx` 行。图层绘制在 800×600 画布上，可用鼠标拖动和缩放。
- **图层编辑：** 添加、修改和删除图层（删除时需确认，并可选择同时删除关联的 LAYERINFO 记录）。`LayerCount` / `LayerInfoCount` 按增量修改，因此原始文件中计数与实际行数不一致的情况不会被破坏。
- **图片的次级坐标**（DAT_IMG_X_INDEX / DAT_IMG_Y_INDEX）在移动图层时随边框一起偏移，调整边框大小时保持不变。该行为可在「设置」→「修改 .dat 中的次级坐标」中关闭。
- **修改历史。** 撤销/重做（Ctrl+Z / Ctrl+Y）以及独立的「修改历史」窗口（Ctrl+H）：表格包含 ►、区段、参数、修改前、修改后等列，首行为文件的初始状态。双击或点击「回退到所选状态」即可恢复到任意步骤。每个文件拥有独立的历史记录。
- **复制名称。** Ctrl+C 和右键单击可复制区段或元素/图层的名称。
- **快捷键在任何键盘布局下均可使用** —— 按键通过物理键码识别，而非字符。
- 「提示」面板标题栏新增**「用记事本打开文件」按钮**，可用系统默认编辑器打开当前文件。
- 「提示」面板支持垂直滚动，.dlg 与 .dat 拥有各自的提示文本。
- 打开文件对话框新增统一过滤器「Disciples files (*.dlg *.dat)」。
- 新增「编辑」和「设置」菜单；版本号现于代码中定义，并显示在「关于」窗口中。
- 「修改次级坐标」选项保存在 DLG_Editor_settings.ini 中。
- 两种格式均保证未修改文件的逐字节一致往返读写。
