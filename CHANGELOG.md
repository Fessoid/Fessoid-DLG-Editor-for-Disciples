# DLG Editor for Disciples - Новое в версии 1.3

## Русский

**Главное: кнопки BUTTON в .dlg теперь редактируются.**

- **Поддержка элементов BUTTON.** Раньше редактор знал только `BUTTONSD` и кнопки обычного типа не показывал вовсе. Теперь `BUTTON` разбирается, рисуется на холсте, двигается и растягивается мышью наравне с остальными элементами — в `Interf.dlg` это 440 кнопок, которые до сих пор были недоступны. Строки, где после имени кнопки координат нет, пропускаются как и прежде.
- **Полный путь к файлу в строке над холстом.** Вместо одного имени файла показывается весь путь. Если он не помещается по ширине, путь сжимается по границе папок (`D:\…\references\Interf.dlg`), так что диск и имя файла видны всегда, а окно от длинного пути не растягивается.
- **Проверка обновлений при запуске.** Программа сверяет свою версию с последним релизом на GitHub и предлагает обновиться. Запрос идёт в фоновом потоке с таймаутом: нет сети, нет ответа или сбой проверки — программа просто запускается дальше, ничего не показывая.
- **Отказ от обновления запоминается.** Если ответить «нет», номер версии пишется в `DLG_Editor_settings.ini` (секция `[Update]`, ключ `skipped_version`) и про эту версию больше не спрашивают. Как только выйдет более новый релиз, запрос появится снова.
- **Обновление скачивается рядом с программой.** После согласия новая версия загружается в папку с exe, после чего предлагается запустить её и закрыть текущую. Несохранённые изменения при этом проверяются как при обычном выходе. Если запущен .py, а не exe, или в релизе нет .exe-файла — открывается страница релиза в браузере.
- **Новая кнопка «Открыть папку файла»** в заголовке блока «Подсказки», рядом с «Открыть файл в блокноте» — открывает проводник на папке с текущим файлом и выделяет в ней сам файл.
- **Кнопка «Перечитать файл»** в заголовке списка элементов, в цвете кнопки «Отменить» — заново читает файл с диска. Подтверждения не спрашивает; при наведении показывает подсказку о том, что несохранённые изменения пропадут.
- **Подсказки при наведении у всех кнопок.** Раньше их не было вовсе: тексты лежали в словарях с версии 1.2, но ни к одной кнопке подключены не были. Теперь подсказка есть у каждой кнопки — в главном окне, в истории изменений, в окне параметров слоя и в подтверждении удаления — на всех четырёх языках.
- **Флаги языков в меню.** В выпадающем списке каждый язык помечен флагом страны, а сам пункт меню подписан кодами языков — «Язык (RU/EN/PL/中文)». Так переключатель находится взглядом, даже если программа запустилась на незнакомом языке. Флаги нарисованы кодом: эмодзи-флаги Tk под Windows не отображает, а картинки в самой строке меню Windows не поддерживает вовсе.
- **Текущий язык отмечен галочкой** в списке языков.
- **Всплывающие окна всегда видны целиком.** Подсказка у нижних кнопок уходила под панель задач Windows; теперь положение считается от рабочей области экрана, а не от координат кнопки: если снизу места нет, подсказка открывается над кнопкой. То же правило применено к окнам «История изменений», «О программе», параметров слоя и подтверждения удаления — они больше не открываются частично за границей экрана.
- **Прокрутка правой панели.** При небольшой высоте экрана список элементов, поля координат и нижние кнопки в панель целиком не помещались, и кнопки становились недоступны. Теперь панель прокручивается колесом мыши и полосой, а сама полоса появляется только когда содержимое не влезло. При высоком окне список по-прежнему растягивается на всё свободное место.
- **Шрифт меню задан явно.** В стандартном Segoe UI китайских глифов нет: Windows подставляла их при отрисовке, а ширину пункта Tk считал по исходному шрифту — от «简体中文» в списке языков был виден один иероглиф. Теперь берётся первый доступный шрифт с собственными CJK-глифами (Microsoft YaHei UI на Windows, PingFang SC на macOS, Noto Sans CJK на Linux).
- **В меню «Правка»** пункты «Отменить действие» и «Вернуть действие» переименованы в «Отменить изменение» и «Вернуть изменение» — понятнее, о чём речь.
- **Окно «О программе»:** исправлен адрес репозитория — он собирается из того же значения, что и адрес проверки обновлений, поэтому разъехаться больше не может. Ссылка на Boosty подписана «Поддержать разработку» и выделена жирным.
- Побайтовый round-trip нетронутого файла по-прежнему гарантирован: правка кнопки меняет только четыре числа координат, остальная часть строки не трогается.

---

## English

**Highlight: BUTTON elements in .dlg are now editable.**

- **BUTTON element support.** The editor previously knew only `BUTTONSD` and did not show plain buttons at all. `BUTTON` is now parsed, drawn on the canvas, and can be moved and resized with the mouse like any other element — that is 440 buttons in `Interf.dlg` which were unreachable until now. Lines with no coordinates after the button name are skipped, as before.
- **Full file path in the line above the canvas.** The whole path is shown instead of just the file name. If it does not fit the available width, the path is shortened at folder boundaries (`D:\…\references\Interf.dlg`), so the drive and the file name always stay visible and a long path never stretches the window.
- **Update check on startup.** The program compares its version against the latest GitHub release and offers to update. The request runs in a background thread with a timeout: no network, no answer or any failure simply lets the program start as usual, showing nothing.
- **A declined update is remembered.** Answering "no" writes the version number into `DLG_Editor_settings.ini` (section `[Update]`, key `skipped_version`) and that version is never offered again. As soon as a newer release appears, the prompt comes back.
- **The update is downloaded next to the program.** Once accepted, the new version is saved into the folder with the exe, and the program offers to launch it and close the current one. Unsaved changes are checked exactly as on a normal exit. When running from .py rather than an exe, or when the release has no .exe asset, the release page opens in the browser instead.
- **New "Open file folder" button** in the header of the Tips panel, next to "Open file in Notepad" — opens the file manager at the folder of the current file and selects the file in it.
- **"Reload file" button** in the header of the element list, in the colour of the "Revert" button — re-reads the file from disk. It asks for no confirmation and shows a hover tooltip warning that unsaved changes will be lost.
- **Hover tooltips on every button.** There were none before: the texts had been sitting in the dictionaries since 1.2 but were never attached to any button. Every button now has one — in the main window, the change history, the layer parameters window and the delete confirmation — in all four languages.
- **Language flags in the menu.** Every language in the drop-down list is marked with a country flag, and the menu entry itself is labelled with the language codes — "Language (RU/EN/PL/中文)". The switch can therefore be found at a glance even when the program starts in an unfamiliar language. The flags are drawn in code: Tk on Windows cannot render flag emoji, and the Windows menu bar does not support images at all.
- **The right panel scrolls.** On a short screen the element list, the coordinate fields and the bottom buttons did not fit into the panel and the buttons became unreachable. The panel now scrolls with the mouse wheel and a scrollbar, and the bar itself appears only when the content does not fit. On a tall window the list still stretches to fill the free space.
- **The menu font is now set explicitly.** The default Segoe UI has no Chinese glyphs: Windows substituted them while drawing, but Tk measured the entry with the original font, so only one character of "简体中文" was visible in the language list. The first available font with its own CJK glyphs is now used (Microsoft YaHei UI on Windows, PingFang SC on macOS, Noto Sans CJK on Linux).
- **The current language is marked with a tick** in the language list.
- **Pop-up windows are always fully visible.** The tooltip of the bottom buttons used to slide under the Windows taskbar; the position is now computed from the screen work area rather than from the button coordinates, and when there is no room below, the tooltip opens above the button. The same rule is applied to the change history, About, layer parameters and delete confirmation windows — they no longer open partly off-screen.
- **In the Edit menu** the "Undo" and "Redo" items are now "Undo change" and "Redo change" — it is clearer what exactly they undo.
- **About window:** the repository address is fixed — it is built from the same value as the update-check address, so the two can no longer drift apart. The Boosty link is now labelled "Support the development" and shown in bold.
- Byte-for-byte round-trip of an untouched file is still guaranteed: editing a button changes only the four coordinate numbers, the rest of the line stays untouched.

---

## Polski

**Najważniejsze: elementy BUTTON w .dlg można teraz edytować.**

- **Obsługa elementów BUTTON.** Wcześniej edytor znał wyłącznie `BUTTONSD` i zwykłych przycisków w ogóle nie pokazywał. Teraz `BUTTON` jest wczytywany, rysowany na płótnie oraz przesuwany i skalowany myszą tak samo jak pozostałe elementy — w `Interf.dlg` to 440 przycisków, dotąd niedostępnych. Linie, w których po nazwie przycisku nie ma współrzędnych, są pomijane jak dotychczas.
- **Pełna ścieżka pliku w linii nad płótnem.** Zamiast samej nazwy pokazywana jest cała ścieżka. Jeśli nie mieści się na szerokość, ścieżka jest skracana na granicy folderów (`D:\…\references\Interf.dlg`), więc dysk i nazwa pliku zawsze pozostają widoczne, a długa ścieżka nie rozciąga okna.
- **Sprawdzanie aktualizacji przy starcie.** Program porównuje swoją wersję z najnowszym wydaniem na GitHubie i proponuje aktualizację. Zapytanie działa w wątku w tle z limitem czasu: brak sieci, brak odpowiedzi lub dowolny błąd po prostu pozwalają programowi uruchomić się dalej, bez żadnego komunikatu.
- **Odrzucona aktualizacja jest zapamiętywana.** Odpowiedź „nie" zapisuje numer wersji w `DLG_Editor_settings.ini` (sekcja `[Update]`, klucz `skipped_version`) i o tej wersji program już nie pyta. Gdy tylko ukaże się nowsze wydanie, pytanie pojawi się ponownie.
- **Aktualizacja pobierana jest obok programu.** Po zgodzie nowa wersja trafia do folderu z plikiem exe, a program proponuje ją uruchomić i zamknąć bieżącą. Niezapisane zmiany są sprawdzane dokładnie tak jak przy zwykłym wyjściu. Przy uruchomieniu z .py zamiast exe lub gdy wydanie nie zawiera pliku .exe, otwierana jest strona wydania w przeglądarce.
- **Nowy przycisk „Otwórz folder pliku"** w nagłówku panelu „Wskazówki", obok „Otwórz plik w notatniku" — otwiera menedżer plików na folderze bieżącego pliku i zaznacza w nim ten plik.
- **Przycisk „Wczytaj ponownie"** w nagłówku listy elementów, w kolorze przycisku „Cofnij" — ponownie wczytuje plik z dysku. Nie pyta o potwierdzenie, a po najechaniu myszą pokazuje podpowiedź, że niezapisane zmiany przepadną.
- **Prawy panel się przewija.** Przy niskim ekranie lista elementów, pola współrzędnych i dolne przyciski nie mieściły się w panelu, a przyciski stawały się nieosiągalne. Teraz panel przewija się kółkiem myszy i suwakiem, a sam suwak pojawia się tylko wtedy, gdy treść się nie mieści. Przy wysokim oknie lista nadal rozciąga się na całe wolne miejsce.
- **Czcionka menu jest ustawiana jawnie.** Domyślne Segoe UI nie ma chińskich glifów: Windows podstawiał je przy rysowaniu, a szerokość pozycji Tk liczył według pierwotnej czcionki, więc z „简体中文" widoczny był jeden znak. Teraz używana jest pierwsza dostępna czcionka z własnymi glifami CJK (Microsoft YaHei UI na Windows, PingFang SC na macOS, Noto Sans CJK na Linux).
- **Podpowiedzi po najechaniu na każdy przycisk.** Wcześniej nie było ich wcale: teksty leżały w słownikach od wersji 1.2, ale nie były podpięte do żadnego przycisku. Teraz podpowiedź ma każdy przycisk — w oknie głównym, w historii zmian, w oknie parametrów warstwy i w potwierdzeniu usunięcia — we wszystkich czterech językach.
- **Flagi języków w menu.** Na liście rozwijanej każdy język jest oznaczony flagą kraju, a sama pozycja menu opisana kodami języków — „Język (RU/EN/PL/中文)". Dzięki temu przełącznik można znaleźć wzrokiem, nawet gdy program uruchomi się w nieznanym języku. Flagi są rysowane w kodzie: Tk pod Windows nie wyświetla emoji flag, a pasek menu Windows w ogóle nie obsługuje obrazków.
- **Bieżący język jest oznaczony ptaszkiem** na liście języków.
- **Okna podręczne są zawsze widoczne w całości.** Podpowiedź dolnych przycisków chowała się pod paskiem zadań Windows; teraz pozycja liczona jest od obszaru roboczego ekranu, a nie od współrzędnych przycisku, i gdy pod spodem nie ma miejsca, podpowiedź otwiera się nad przyciskiem. Ta sama zasada objęła okna historii zmian, „O programie", parametrów warstwy i potwierdzenia usunięcia — nie otwierają się już częściowo poza ekranem.
- **W menu „Edycja"** pozycje „Cofnij działanie" i „Ponów działanie" zmieniono na „Cofnij zmianę" i „Ponów zmianę" — jaśniej widać, czego dotyczą.
- **Okno „O programie":** poprawiony adres repozytorium — jest budowany z tej samej wartości co adres sprawdzania aktualizacji, więc nie mogą się już rozjechać. Link do Boosty jest podpisany „Wesprzyj rozwój" i wyróżniony pogrubieniem.
- Round-trip bajt w bajt nietkniętego pliku jest nadal zapewniony: edycja przycisku zmienia tylko cztery liczby współrzędnych, reszta linii pozostaje nietknięta.

---

## 简体中文

**重点：.dlg 中的 BUTTON 元素现在可以编辑。**

- **支持 BUTTON 元素。** 此前编辑器只识别 `BUTTONSD`，普通按钮完全不显示。现在 `BUTTON` 会被解析、绘制在画布上，并可像其他元素一样用鼠标移动和缩放——仅 `Interf.dlg` 中就有 440 个此前无法编辑的按钮。按钮名称后没有坐标的行仍然照旧跳过。
- **画布上方一行显示完整文件路径。** 不再只显示文件名，而是显示整个路径。若宽度不足，路径会在文件夹边界处缩略（`D:\…\references\Interf.dlg`），因此盘符和文件名始终可见，长路径也不会撑大窗口。
- **启动时检查更新。** 程序会将自身版本与 GitHub 上的最新发布进行比较，并提示更新。请求在后台线程中执行并设有超时：无网络、无响应或检查失败时，程序照常启动，不显示任何提示。
- **拒绝过的更新会被记住。** 选择「否」后，版本号会写入 `DLG_Editor_settings.ini`（`[Update]` 段的 `skipped_version` 键），此后不再就该版本提问。一旦有更新的发布出现，提示会再次弹出。
- **更新下载到程序所在文件夹。** 确认后，新版本会保存到 exe 所在的文件夹，随后程序会询问是否启动新版本并关闭当前程序。未保存的更改会像正常退出那样进行检查。若以 .py 而非 exe 运行，或发布中没有 .exe 文件，则改为在浏览器中打开发布页面。
- **右侧面板可滚动。** 屏幕高度较小时，元素列表、坐标输入框和底部按钮无法全部放入面板，按钮因此无法点击。现在面板可用鼠标滚轮和滚动条滚动，而滚动条仅在内容放不下时才出现。窗口较高时，列表仍会拉伸填满空余空间。
- **明确指定了菜单字体。** 默认的 Segoe UI 不含中文字形：Windows 在绘制时替换字体，而 Tk 却按原字体计算菜单项宽度，因此语言列表中的「简体中文」只显示出一个字。现在会选用第一个自带 CJK 字形的字体（Windows 上为 Microsoft YaHei UI，macOS 上为 PingFang SC，Linux 上为 Noto Sans CJK）。
- **「提示」面板标题栏新增「打开文件所在文件夹」按钮**，位于「用记事本打开文件」旁边——在文件管理器中打开当前文件所在的文件夹并选中该文件。
- **元素列表标题栏新增「重新读取文件」按钮**，颜色与「撤销」按钮相同——从磁盘重新读取文件。不询问确认；鼠标悬停时会提示未保存的更改将会丢失。
- **所有按钮均新增鼠标悬停提示。** 此前完全没有：提示文本自 1.2 版起就存在于词典中，却未连接到任何按钮。现在主窗口、修改历史、图层参数窗口和删除确认中的每个按钮都有提示，四种语言齐备。
- **菜单中新增语言旗帜。** 下拉列表中的每种语言都标有国旗，菜单项本身则标注了语言代码——「语言 (RU/EN/PL/中文)」。即使程序以陌生的语言启动，也能一眼找到切换入口。旗帜由代码绘制：Windows 下的 Tk 无法显示旗帜表情符号，而 Windows 的菜单栏根本不支持图片。
- **当前语言在语言列表中以对勾标出。**
- **弹出窗口始终完整可见。** 底部按钮的提示原本会滑到 Windows 任务栏下方；现在位置以屏幕工作区为基准计算，而不是以按钮坐标为准，下方空间不足时提示会显示在按钮上方。同一规则也应用于修改历史、「关于」、图层参数和删除确认窗口——它们不会再有一部分开在屏幕之外。
- **「编辑」菜单**中的「撤销操作」和「重做操作」改为「撤销修改」和「恢复修改」，含义更明确。
- **「关于」窗口：** 修正了仓库地址——它与检查更新所用的地址取自同一处，因此不会再出现不一致。Boosty 链接现标注为「支持开发」并以粗体显示。
- 未修改文件的逐字节一致往返读写依然有保证：编辑按钮只改动四个坐标数字，行内其余部分不受影响。

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
