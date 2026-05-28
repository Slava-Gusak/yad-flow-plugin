# YAD — Flow Launcher Plugin

**YAD** созвучна со словом «яд», потому решил по приколу оставить) — плагин для [Flow Launcher](https://www.flowlauncher.com/), позволяющий скачивать треки, альбомы и плейлисты с Яндекс Музыки прямо из строки поиска. Все зависимости включены — ничего дополнительно устанавливать не нужно.

Использует утилиту [yandex-music-downloader](https://github.com/llistochek/yandex-music-downloader) от [llistochek](https://github.com/llistochek).

---

**YAD** sounds like the Russian word for "poison" (яд), just kept it for fun) — a [Flow Launcher](https://www.flowlauncher.com/) plugin for downloading tracks, albums and playlists from Yandex Music directly from the search bar. All dependencies are bundled — no extra installation needed.

Built on top of [yandex-music-downloader](https://github.com/llistochek/yandex-music-downloader) by [llistochek](https://github.com/llistochek).

## Возможности / Features

- Скачивание треков, альбомов, плейлистов и всей дискографии артиста
- Качество до FLAC (при наличии подписки Яндекс Плюс)
- Обложка в оригинальном разрешении, встроенная в файл
- Автоматическая сортировка по папкам: `Артист / Альбом / Трек`
- Уведомления о начале и завершении загрузки
- Первоначальная настройка токена прямо из Flow Launcher
- Интерфейс на русском и английском языках

---

- Download tracks, albums, playlists and full artist discography
- Quality up to FLAC (requires Yandex Plus subscription)
- Original resolution cover art embedded in the file
- Automatic folder sorting: `Artist / Album / Track`
- Notifications on download start and completion
- First-time token setup directly from Flow Launcher
- Russian and English interface

---

## Требования / Requirements

- [Flow Launcher](https://www.flowlauncher.com/)
- [Python 3.10+](https://www.python.org/downloads/)
- Подписка Яндекс Плюс / Yandex Plus subscription

---

## Установка / Installation

1. Скачай последний релиз / Download the latest release
2. Распакуй папку `YAD` в / Extract the `YAD` folder to:
```
%APPDATA%\FlowLauncher\Plugins\
```
3. Перезапусти Flow Launcher / Restart Flow Launcher

---

## Настройка токена / Token setup

При первом запуске плагин попросит токен. Получить его можно так:

1. Открой [music.yandex.ru](https://music.yandex.ru) в браузере
2. Открой DevTools (`F12`) → Application → Cookies
3. Скопируй значение куки `Session_id`

On first launch the plugin will ask for a token:

1. Open [music.yandex.ru](https://music.yandex.ru) in your browser
2. Open DevTools (`F12`) → Application → Cookies
3. Copy the value of the `Session_id` cookie

```
yad y0_ВАШ_ТОКЕН
```

---

## Использование / Usage

| Команда / Command | Действие / Action |
|---|---|
| `yad` | Подсказка / Hint |
| `yad [ссылка]` | Скачать трек / альбом / плейлист / артиста |
| `yad reset token` | Сбросить токен / Reset token |

Ссылки с UTM-метками поддерживаются — плагин обрежет лишнее автоматически.
UTM links are supported — extra parameters are stripped automatically.

---

## Куда сохраняются файлы / Where files are saved

```
~/Music/YandexMusic/Артист/Альбом/Трек
```
