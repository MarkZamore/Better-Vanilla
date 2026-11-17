# Better Vanilla

Better Vanilla для библиотеки LANMinecraft. Minecraft 26.3, Fabric Loader 0.20.1, Java 25. Карточка предназначена для группы «Мало модов», сразу после Better Than Wolves.

## Состав

В `upstream-lock.json` закреплены 76 исходных авторских JAR. Все они активны, включая Inventory Profiles Next 2.3.8, libIPN 6.9.0 и Shoulder Surfing Reloaded 5.3.1. Слой правок tools/mod-overlay-lock.json добавляет Entity Texture Features 7.2.7, Entity Model Features 3.3.12, RightClickHarvest 4.7.1 и JamLib 2.3.3. Cinematic Interactions удалён по запросу пользователя. С Player Extension, First-person Model, EMF Compat и Reimagined Intro состав содержит 84 JAR и 210 компонентов Fabric.

Fresh Animations 1.11.2 от FreshLX добавляет анимации жителям и другим существам. Оригинальный ZIP для Minecraft 26.3 закреплён в tools/resourcepacks-lock.json и включён в поставку с разрешения официальных условий на использование в модпаках. launcher/resourcepacks-default.txt включает пакет при первом предложении и сохраняет последующий выбор игрока. Not Enough Animations продолжает отвечать за анимации действий игрока.

JAR выпускаются в исходных байтах. Соответствующие исходники добавлений указаны в слое правок, лицензии и атрибуция сохранены в [tools/mod-licenses](tools/mod-licenses). Шейдеры поставляются в оригинальных ZIP и выбираются вручную в Iris. Поставка сохраняет выбор игрока, настройки дальности и графического бэкенда.

- [Bliss 2.1.2](https://modrinth.com/shader/bliss-shader/version/kC2Y8q1P), X0nk, редакция шейдеров Chocapic13.
- [Complementary Reimagined r5.9.3](https://modrinth.com/shader/complementary-reimagined/version/Bqen1mJX), Complementary Development.
- [MakeUp — Ultra Fast 9.6](https://modrinth.com/shader/makeup-ultra-fast-shaders/version/t4YRxQug), Javier G. C. (XavierFST) и участники проекта. LGPL-3.0-or-later, текст и соответствующие исходники указаны в NOTICE.

Владелец выпуска подтвердил разрешение на размещение точного состава в GitHub Releases. Оригинальные лицензии сохранены в файлах авторов.

## Подготовка поставки

Используйте неизменённый исходный ZIP и актуальные инструменты LANMinecraft. Материализация скачивает четыре добавления из официальных источников и сверяет их размеры и SHA-256 перед записью.

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

## Настройки и изменения состава

Inventory Profiles Next возвращён с отключёнными значками автопополнения в слотах и хотбаре. Небольшой pack-owned агент config/better-vanilla/inventory-defaults.jar применяет эти два значения при первом запуске этой ревизии. Сортировка, автопополнение, прочие настройки и горячие клавиши сохраняются. Личная метка config/better-vanilla/ipn-arrow-defaults-v1.applied сохраняет последующие изменения игрока. При повреждённом JSON файл сохраняется с диагностикой, а применение повторяется после его исправления.

Исходники агента и проверка без игры находятся в tools/inventory-defaults. Сборка выполняется командой build.py --jdk <JDK-25.0.2> --gson <gson-2.14.0.jar> --out <agent.jar>. Проверка verify.py использует те же --jdk и --gson, а также --agent <agent.jar> и --out <new-test-directory>.

Сетевое предупреждение удалено вместе с Cinematic Interactions. Его прежний агент больше не входит в поставку. Возвращён Shoulder Surfing Reloaded с назначением смены плеча на запятую.

Прямого пересечения Fresh Animations с оставшимися модами по моделям не найдено. Fresh Animations не содержит модели игрока, Fancy World Animations меняет блоки, Cosy Critters добавляет собственных декоративных существ. Визуальная проверка и запуск игры не выполнялись по указанию пользователя.

Полная проверка публичных файлов выполняется tools/verify_public_release.py --staged <dist>/pack-manifest.json --out <new-public-check-directory>. Приёмка этой ревизии находится в tools/animation-and-inventory-qa.json.

## Анимации игрока и интро

Добавлены Fresh Animations: Player Extension 1.1.0 от FreshLX, First-person Model 2.7.3 от tr7zw, EMF Compat: Not Enough Animations 1.2.1 и его обязательная библиотека EMF Compat Core 2.4.0 от STRadaT. Player Extension выбирается после базового Fresh Animations. Выбор пакетов включён по умолчанию с сохранением последующего решения игрока.

Pack-owned агент в tools/inventory-defaults применяет четыре обязательных значения к config/notenoughanimations.json. enableAnimationSmoothing=false, disableLegSmoothing=true, enableLadderAnimation=false, bowAnimation=VANILLA. Прочие параметры и неизвестные поля сохраняются, некорректный JSON остаётся без перезаписи. Миграция стрелочек IPN сохраняет прежнюю однократную семантику.

Reimagined Intro 3.0.0 показывает авторскую последовательность перед главным меню. Esc пропускает её. Изначальные настройки воспроизведения и громкости принадлежат моду. Исходные байты JAR закреплены в tools/mod-overlay-lock.json.

Лицензия First-person Model в метаданных называется tr7zw Protective License. Точный опубликованный JAR содержит MIT License с разрешением на распространение. Этот текст сохранён в tools/mod-licenses/firstperson.LICENSE.txt и входит в поставку. Reimagined Intro в своём JAR содержит CC0-1.0, текст также включён в поставку. Полные соответствующие исходники обоих модулей EMF Compat приложены к выпуску, их SHA-256 и URL закреплены в overlay.

Проверка зависимостей через tools/native-qa/resolve.py --run <agent-run> --jdk <JDK-25> запускает настоящий Fabric, но QA-agent заменяет только точку входа Minecraft на немедленное завершение. Окно игры, мир, рендер и ввод пользователя не запускаются. Полученный журнал привязывается к SHA клиентского JAR и используется snapshot_fabric_inventory.py. Агент проверки не входит в игровую поставку.

Приёмка этой ревизии записана в tools/player-animations-qa.json. Отображение анимаций, внутриигровое поведение и видео интро не проверялись по указанию пользователя.
