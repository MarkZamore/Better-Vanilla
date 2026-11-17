# Better Vanilla

Better Vanilla для библиотеки LANMinecraft. Minecraft 26.3, Fabric Loader 0.20.1, Java 25. Карточка предназначена для группы «Мало модов», сразу после Better Than Wolves.

## Состав

В `upstream-lock.json` закреплены SHA-256 входного архива, точные версии 76 авторских JAR и их источники. [Слой правок](tools/mod-overlay-lock.json) фиксирует пять добавленных JAR и исключает Shoulder Surfing Reloaded, камера которого перекрывает сцены Cinematic Interactions. Добавлены Entity Texture Features 7.2.7, Entity Model Features 3.3.12, RightClickHarvest 4.7.1, его зависимость JamLib 2.3.3 и Cinematic Interactions 0.18.28 beta. RightClickHarvest собирает созревший урожай по ПКМ и пересаживает его. Cinematic Interactions добавляет сцены от первого лица у верстака, печи и других рабочих блоков.

JAR выпускаются в исходных байтах. Соответствующие исходники добавлений указаны в слое правок, лицензии и атрибуция сохранены в [tools/mod-licenses](tools/mod-licenses). Шейдеры поставляются в оригинальных ZIP и выбираются вручную в Iris. Поставка сохраняет выбор игрока, настройки дальности и графического бэкенда.

- [Bliss 2.1.2](https://modrinth.com/shader/bliss-shader/version/kC2Y8q1P), X0nk, редакция шейдеров Chocapic13.
- [Complementary Reimagined r5.9.3](https://modrinth.com/shader/complementary-reimagined/version/Bqen1mJX), Complementary Development.
- [MakeUp — Ultra Fast 9.6](https://modrinth.com/shader/makeup-ultra-fast-shaders/version/t4YRxQug), Javier G. C. (XavierFST) и участники проекта. LGPL-3.0-or-later, текст и соответствующие исходники указаны в NOTICE.

Владелец выпуска подтвердил разрешение на размещение точного состава в GitHub Releases. Оригинальные лицензии сохранены в файлах авторов.

## Подготовка поставки

Используйте неизменённый исходный ZIP и актуальные инструменты LANMinecraft. Материализация скачивает пять добавлений из официальных источников и сверяет их размеры и SHA-256 перед записью.

```powershell
python -B tools/materialize.py --original <Better-Vanilla.zip> --out <novel-pack-path>
python -B tools/generate_manifest.py --pack <pack-path> --out <new-dist-path> --launcher <LANMinecraft-source>
python -B tools/generate_manifest.py --pack <pack-path> --out <dist-path> --launcher <LANMinecraft-source> --verify-only
```

При обновлении автора сохраните пресет, три исходных ZIP шейдеров, лицензионные материалы, настройку предупреждения и слой логирования. После согласованной замены входов переснимите фактический список Fabric и обновите lock, страницы модов и проверку управления. Команды восстановления настроек выполняются в независимых исходниках.

```powershell
python -B tools/multiplayer_warning_policy.py prepare --pack .
python -B tools/network_logging_policy.py prepare --pack .
```

## Изменения состава

Inventory Profiles Next и его отдельная библиотека libIPN исключены по запросу пользователя. Также исключён Shoulder Surfing Reloaded для работы камеры Cinematic Interactions. Точные исключённые SHA-256 закреплены в tools/mod-overlay-lock.json. Исходный архив и upstream-lock.json сохраняют авторский состав. Материализация и генератор выпуска проверяют слой исключений. Поставка содержит 73 исходных JAR и пять добавлений, всего 78 JAR и 204 фактически загружаемых компонента Fabric.
