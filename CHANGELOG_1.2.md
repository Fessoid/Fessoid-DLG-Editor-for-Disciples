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
