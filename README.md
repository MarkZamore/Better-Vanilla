# Better Vanilla

Better Vanilla для библиотеки LANMinecraft. Minecraft 26.3, Fabric Loader 0.20.1, Java 25. Карточка предназначена для группы «Мало модов», сразу после Better Than Wolves.

## Состав

В `upstream-lock.json` закреплены 76 исходных авторских JAR. Dark Loading Screen исключён по запросу пользователя. Остальные активны, включая Inventory Profiles Next 2.3.8, libIPN 6.9.0 и Shoulder Surfing Reloaded 5.3.1. Слой правок tools/mod-overlay-lock.json добавляет Entity Texture Features 7.2.7, Entity Model Features 3.3.12, RightClickHarvest 4.7.1 и JamLib 2.3.3. Cinematic Interactions удалён по запросу пользователя. С Player Extension, EMF Compat, Reimagined Intro, Wavey Capes, Do a Barrel Roll и CICADA состав содержит 85 JAR и 212 компонентов Fabric. First-person Model удалён по запросу пользователя.

Fresh Animations 1.11.2 от FreshLX добавляет анимации жителям и другим существам. Оригинальный ZIP для Minecraft 26.3 закреплён в tools/resourcepacks-lock.json и включён в поставку с разрешения официальных условий на использование в модпаках. launcher/resourcepacks-default.txt включает пакет при первом предложении и сохраняет последующий выбор игрока. Not Enough Animations продолжает отвечать за анимации действий игрока.

JAR выпускаются в исходных байтах. Соответствующие исходники добавлений указаны в слое правок, лицензии и атрибуция сохранены в [tools/mod-licenses](tools/mod-licenses). Шейдеры поставляются в оригинальных ZIP и выбираются вручную в Iris. Поставка сохраняет выбор игрока, настройки дальности и графического бэкенда.

- [Bliss 2.1.2](https://modrinth.com/shader/bliss-shader/version/kC2Y8q1P), X0nk, редакция шейдеров Chocapic13.
- [Complementary Reimagined r5.9.3](https://modrinth.com/shader/complementary-reimagined/version/Bqen1mJX), Complementary Development.
- [MakeUp — Ultra Fast 9.6](https://modrinth.com/shader/makeup-ultra-fast-shaders/version/t4YRxQug), Javier G. C. (XavierFST) и участники проекта. LGPL-3.0-or-later, текст и соответствующие исходники указаны в NOTICE.

Владелец выпуска подтвердил разрешение на размещение точного состава в GitHub Releases. Оригинальные лицензии сохранены в файлах авторов.

## Подготовка поставки

Используйте неизменённый исходный ZIP и актуальные инструменты LANMinecraft. Материализация скачивает закреплённые добавления из официальных источников и сверяет их размеры и SHA-256 перед записью.

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

Добавлены Fresh Animations: Player Extension 1.1.0 от FreshLX, EMF Compat: Not Enough Animations 1.2.1 и его обязательная библиотека EMF Compat Core 2.4.0 от STRadaT. Player Extension выбирается после базового Fresh Animations. Выбор пакетов включён по умолчанию с сохранением последующего решения игрока.

Pack-owned агент в tools/inventory-defaults применяет четыре обязательных значения к config/notenoughanimations.json. enableAnimationSmoothing=false, disableLegSmoothing=true, enableLadderAnimation=false, bowAnimation=VANILLA. Прочие параметры и неизвестные поля сохраняются, некорректный JSON остаётся без перезаписи. Миграция стрелочек IPN сохраняет прежнюю однократную семантику.

Reimagined Intro 3.0.0 показывает авторскую последовательность перед главным меню. Esc пропускает её. Изначальные настройки воспроизведения и громкости принадлежат моду. Исходные байты JAR закреплены в tools/mod-overlay-lock.json.

Reimagined Intro содержит CC0-1.0, текст включён в поставку. Полные соответствующие исходники обоих модулей EMF Compat приложены к выпуску, их SHA-256 и URL закреплены в overlay.

Проверка зависимостей через tools/native-qa/resolve.py --run <agent-run> --jdk <JDK-25> запускает настоящий Fabric, но QA-agent заменяет только точку входа Minecraft на немедленное завершение. Окно игры, мир, рендер и ввод пользователя не запускаются. Полученный журнал привязывается к SHA клиентского JAR и используется snapshot_fabric_inventory.py. Агент проверки не входит в игровую поставку.

Приёмка этой ревизии записана в tools/player-animations-qa.json. Отображение анимаций, внутриигровое поведение и видео интро не проверялись по указанию пользователя.

## Плащи, полёт и расширения Fresh Animations

Добавлены Wavey Capes 1.11.3, Do a Barrel Roll 3.8.5 и обязательная CICADA 0.15.3 для Fabric 26.3. Владелец сборки 17 ноября 2026 года отдельно подтвердил разрешение автора Wavey Capes на распространение точного JAR в GitHub Releases Better Vanilla. Не переносить это разрешение на другие проекты или файлы. Лицензии включены в config/better-vanilla/licenses, полный исходный код Do a Barrel Roll на закреплённом коммите приложен к выпуску.

Оригинальный FA+All_Extensions-v1.10.1.zip от FreshLX включён без изменения с официальными условиями. Порядок по умолчанию снизу вверх — Fresh Animations, All Extensions, Player Extension. Последующий выбор игрока сохраняется. Четыре обязательные настройки NEA и скрытые по умолчанию стрелочки IPN сохранены.

Wavey Capes использует исправление привязки плаща к корню анимированного игрока, введённое автором после issue #123. Fancy World Animations сохраняется. В Objects Add-on видимая крышка сундука lid2 имеет собственную анимацию, исходная lid используется для определения состояния, а не повторного применения её угла. Проверено по оригинальному chest_animations.jpm и ChestLidControllerMixin в точных входных файлах.

Do a Barrel Roll и Shoulder Surfing оставлены со штатными параметрами. У авторов есть сообщение о проблемах камеры на старых версиях и незавершённое исправление PR #206. В 3.8.5 setRoll складывает угол с исходным значением, но совместимость текущей пары в полёте без рендера не подтверждена. При проблемах камеры используйте вид от первого лица для полётов. Не считать разрешение зависимостей проверкой визуальной совместимости.

Dark Loading Screen и First-person Model исключены из активной поставки. Reimagined Intro 3.0.0 остаётся с авторскими настройками. Его LoadingOverlayMixin скрывает логотип Mojang при enableIntro=true. В ModConfig отсутствует более ранний этап запуска заставки. Удаление Dark Loading Screen не пропускает обязательную инициализацию ресурсов Minecraft и не гарантирует отсутствие паузы перед видео.

Актуальная приёмка находится в tools/flight-capes-qa.json. Рендер, анимации в мире, камера в полёте и фактическое воспроизведение интро не проверены. Computer-use не применялся. Все изменения принадлежат сборке, новых исключений в лаунчере нет.
