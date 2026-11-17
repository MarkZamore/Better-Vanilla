# Better Vanilla

Better Vanilla для библиотеки LANMinecraft. Minecraft 26.3, Fabric Loader 0.20.1, Java 25. Карточка предназначена для группы «Мало модов», сразу после Better Than Wolves.

## Состав

В `upstream-lock.json` закреплены SHA-256 входного архива, точные версии 76 JAR и авторские адреса. JAR выпускаются в исходных байтах. Шейдеры поставляются в оригинальных ZIP и выбираются вручную в Iris. Поставка сохраняет выбор игрока, настройки дальности и графического бэкенда.

- [Bliss 2.1.2](https://modrinth.com/shader/bliss-shader/version/kC2Y8q1P), X0nk, редакция шейдеров Chocapic13.
- [Complementary Reimagined r5.9.3](https://modrinth.com/shader/complementary-reimagined/version/Bqen1mJX), Complementary Development.
- [MakeUp — Ultra Fast 9.6](https://modrinth.com/shader/makeup-ultra-fast-shaders/version/t4YRxQug), Javier G. C. (XavierFST) и участники проекта. LGPL-3.0-or-later, текст и соответствующие исходники указаны в NOTICE.

Владелец выпуска подтвердил разрешение на размещение точного состава в GitHub Releases. Оригинальные лицензии сохранены в файлах авторов.

## Подготовка поставки

Используйте неизменённый исходный ZIP и актуальные инструменты LANMinecraft. Версия совместимых инструментов для первой поставки — `5a8f986505a729f7a3749a7450e3e77c9060edb0`.

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

Inventory Profiles Next и его отдельная библиотека libIPN исключены по запросу пользователя. Точные исключённые SHA-256 закреплены в tools/mod-overlay-lock.json. Исходный архив и upstream-lock.json сохраняют авторский состав. Материализация и генератор выпуска проверяют слой исключений. Остальные 74 исходных JAR сохраняют свои байты.
