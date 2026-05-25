import sys

# Кодировки фиксируем ДО любых других импортов
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
sys.stderr.reconfigure(encoding='utf-8', errors='replace')

import os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "lib"))

import json
import subprocess
import threading
from flowlauncher import FlowLauncher
from urllib.parse import urlparse, urlunparse

# === НАСТРОЙКИ ===
DOWNLOAD_DIR     = os.path.join(os.path.expanduser("~"), "Music", "YandexMusic")
QUALITY          = "2"  # 0 - AAC 64kbps, 1 - AAC 192kbps, 2 - FLAC
COVER_RESOLUTION = "original"
CONFIG_PATH      = os.path.join(os.path.dirname(os.path.abspath(__file__)), "config.json")
LIB_PATH         = os.path.join(os.path.dirname(os.path.abspath(__file__)), "lib")
# =================

YANDEX_MUSIC_HOST = "music.yandex.ru"

# === ЛОКАЛИЗАЦИЯ ===
STRINGS = {
    "ru": {
        "enter_token":        "⚙️ Введите токен Яндекс Музыки",
        "enter_token_sub":    "Вставьте токен начинающийся с y0_...",
        "save_token_title":   "Сохранить токен: {token}...",
        "save_token_sub":     "Нажмите Enter чтобы сохранить токен",
        "reset_token_title":  "🔄 Сбросить токен",
        "reset_token_sub":    "Нажмите Enter чтобы удалить сохранённый токен",
        "paste_link":         "Вставьте ссылку на трек, альбом или плейлист",
        "paste_link_sub":     "Пример: yad https://music.yandex.ru/album/123/track/456",
        "bad_url":            "Некорректная ссылка",
        "bad_url_sub":        "Ожидается ссылка на music.yandex.ru",
        "download_title":     "⬇ Скачать {type}",
        "download_sub":       "{url}  →  {dir}",
        "notif_token_saved":  "Токен сохранён! Теперь вставляйте ссылки.",
        "notif_token_reset":  "Токен сброшен. Введите новый.",
        "notif_downloading":  "Скачивание: {type}...",
        "notif_done":         "{type} скачан успешно!",
        "notif_error":        "Ошибка: {error}",
        "notif_launch_error": "Ошибка запуска: {error}",
        "notif_no_token":     "Токен не задан! Напишите yad y0_...",
        "type_track":         "трек",
        "type_album":         "альбом",
        "type_playlist":      "плейлист",
        "type_artist":        "артист",
        "type_unknown":       "объект",
    },
    "en": {
        "enter_token":        "⚙️ Enter your Yandex Music token",
        "enter_token_sub":    "Paste the token starting with y0_...",
        "save_token_title":   "Save token: {token}...",
        "save_token_sub":     "Press Enter to save the token",
        "reset_token_title":  "🔄 Reset token",
        "reset_token_sub":    "Press Enter to delete the saved token",
        "paste_link":         "Paste a link to a track, album or playlist",
        "paste_link_sub":     "Example: yad https://music.yandex.ru/album/123/track/456",
        "bad_url":            "Invalid link",
        "bad_url_sub":        "Expected a link to music.yandex.ru",
        "download_title":     "⬇ Download {type}",
        "download_sub":       "{url}  →  {dir}",
        "notif_token_saved":  "Token saved! Now paste your links.",
        "notif_token_reset":  "Token cleared. Enter a new one.",
        "notif_downloading":  "Downloading: {type}...",
        "notif_done":         "{type} downloaded successfully!",
        "notif_error":        "Error: {error}",
        "notif_launch_error": "Launch error: {error}",
        "notif_no_token":     "Token not set! Type yad y0_...",
        "type_track":         "track",
        "type_album":         "album",
        "type_playlist":      "playlist",
        "type_artist":        "artist",
        "type_unknown":       "item",
    },
}
# ===================


def get_flow_language() -> str:
    """
    Определяет язык Flow Launcher.
    Порядок поиска:
      1. Переменная окружения FLOW_LAUNCHER_LANGUAGE (есть в некоторых сборках)
      2. %APPDATA%/FlowLauncher/Settings/Settings.json → поле Language
      3. Системная локаль Windows
      4. Фоллбэк: 'en'
    """
    # 1. Переменная окружения
    env_lang = os.environ.get("FLOW_LAUNCHER_LANGUAGE", "")
    if env_lang:
        return _normalize_lang(env_lang)

    # 2. Settings.json Flow Launcher
    settings_path = os.path.join(
        os.environ.get("APPDATA", ""),
        "FlowLauncher", "Settings", "Settings.json"
    )
    if os.path.exists(settings_path):
        try:
            with open(settings_path, "r", encoding="utf-8") as f:
                settings = json.load(f)
            lang = settings.get("Language", "")
            if lang:
                return _normalize_lang(lang)
        except Exception:
            pass

    # 3. Системная локаль через PowerShell (не тянет лишних зависимостей)
    try:
        result = subprocess.run(
            ["powershell", "-NoProfile", "-Command",
             "[System.Globalization.CultureInfo]::CurrentUICulture.TwoLetterISOLanguageName"],
            capture_output=True, text=True,
            encoding="utf-8", errors="replace",
            creationflags=subprocess.CREATE_NO_WINDOW,
            timeout=3,
        )
        lang = result.stdout.strip()
        if lang:
            return _normalize_lang(lang)
    except Exception:
        pass

    return "en"


def _normalize_lang(lang: str) -> str:
    """Приводит любой тег языка к 'ru' или 'en'."""
    lang = lang.lower().strip()
    # Flow Launcher хранит как 'ru-RU', 'en-US', иногда просто 'ru'
    if lang.startswith("ru"):
        return "ru"
    return "en"


def t(key: str, lang: str, **kwargs) -> str:
    """Возвращает переведённую строку с подстановкой переменных."""
    template = STRINGS.get(lang, STRINGS["en"]).get(key, key)
    return template.format(**kwargs) if kwargs else template


# =====================

def load_config() -> dict:
    if os.path.exists(CONFIG_PATH):
        try:
            with open(CONFIG_PATH, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return {}
    return {}


def save_config(data: dict):
    with open(CONFIG_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def clean_url(url: str) -> str:
    parsed = urlparse(url)
    return urlunparse((parsed.scheme, parsed.netloc, parsed.path, '', '', ''))


def is_valid_url(text: str) -> bool:
    try:
        result = urlparse(text)
        return result.scheme in ("http", "https") and YANDEX_MUSIC_HOST in result.netloc
    except Exception:
        return False


def is_album_url(url: str) -> bool:
    return "/album/" in url and "/track/" not in url


def detect_type(url: str, lang: str) -> str:
    if "/album/" in url and "/track/" in url:
        return t("type_track", lang)
    elif "/album/" in url:
        return t("type_album", lang)
    elif "/playlists/" in url or "/playlist/" in url:
        return t("type_playlist", lang)
    elif "/artist/" in url:
        return t("type_artist", lang)
    return t("type_unknown", lang)


def _escape_ps(s: str) -> str:
    """Экранирует строку для вставки в PowerShell-скрипт."""
    return s.replace("'", "''")


def notify(title: str, message: str):
    ps_script = f"""
Add-Type -AssemblyName System.Windows.Forms
$notify = New-Object System.Windows.Forms.NotifyIcon
$notify.Icon = [System.Drawing.SystemIcons]::Information
$notify.Visible = $true
$notify.ShowBalloonTip(4000, '{_escape_ps(title)}', '{_escape_ps(message)}', [System.Windows.Forms.ToolTipIcon]::Info)
Start-Sleep -Seconds 5
$notify.Dispose()
"""
    subprocess.Popen(
        ["powershell", "-NoProfile", "-WindowStyle", "Hidden", "-Command", ps_script],
        creationflags=subprocess.CREATE_NO_WINDOW if sys.platform == "win32" else 0,
    )


def download_thread(url: str, media_type: str, token: str, lang: str):
    os.makedirs(DOWNLOAD_DIR, exist_ok=True)

    cmd = [
        sys.executable,
        "-m", "ymd",
        "--token", token,
        "--quality", QUALITY,
        "--cover-resolution", COVER_RESOLUTION,
        "--path-pattern",
        "#album-artist/#album/#number - #title" if is_album_url(url) else "#album-artist/#album/#title",
        "--embed-cover",
        "--dir", DOWNLOAD_DIR,
        "-u", url,
    ]

    try:
        result = subprocess.run(
            cmd,
            creationflags=subprocess.CREATE_NO_WINDOW if sys.platform == "win32" else 0,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            env={
                **os.environ,
                "PYTHONPATH": LIB_PATH,
                "PYTHONIOENCODING": "utf-8",
                "PYTHONUTF8": "1",
            },
        )

        if result.returncode == 0:
            notify("✅ Yandex Music", t("notif_done", lang, type=media_type.capitalize()))
        else:
            lines = result.stderr.strip().splitlines()
            error = lines[-1] if lines else "Unknown error"
            notify("❌ Yandex Music", t("notif_error", lang, error=error[:60]))

    except Exception as e:
        notify("❌ Yandex Music", t("notif_launch_error", lang, error=str(e)[:60]))


class YandexMusicDownloader(FlowLauncher):

    def query(self, query: str):
        query = query.strip()
        config = load_config()
        token = config.get("token", "")
        lang  = get_flow_language()

        # — Нет токена —
        if not token:
            if query.startswith("y0_"):
                return [
                    {
                        "Title":    t("save_token_title", lang, token=query[:30]),
                        "SubTitle": t("save_token_sub", lang),
                        "IcoPath":  "icon.png",
                        "score":    100,
                        "JsonRPCAction": {
                            "method":             "save_token",
                            "parameters":         [query],
                            "dontHideAfterAction": False,
                        },
                    }
                ]
            return [
                {
                    "Title":    t("enter_token", lang),
                    "SubTitle": t("enter_token_sub", lang),
                    "IcoPath":  "icon.png",
                    "score":    0,
                }
            ]

        # — Сброс токена —
        if query == "reset token":
            return [
                {
                    "Title":    t("reset_token_title", lang),
                    "SubTitle": t("reset_token_sub", lang),
                    "IcoPath":  "icon.png",
                    "score":    100,
                    "JsonRPCAction": {
                        "method":             "reset_token",
                        "parameters":         [],
                        "dontHideAfterAction": False,
                    },
                }
            ]

        # — Пустой запрос —
        if not query:
            return [
                {
                    "Title":    t("paste_link", lang),
                    "SubTitle": t("paste_link_sub", lang),
                    "IcoPath":  "icon.png",
                    "score":    0,
                }
            ]

        # — Некорректная ссылка —
        if not is_valid_url(query):
            return [
                {
                    "Title":    t("bad_url", lang),
                    "SubTitle": t("bad_url_sub", lang),
                    "IcoPath":  "icon.png",
                    "score":    0,
                }
            ]

        # — Всё ок, показываем кнопку скачивания —
        clean       = clean_url(query)
        media_type  = detect_type(clean, lang)

        return [
            {
                "Title":    t("download_title", lang, type=media_type),
                "SubTitle": t("download_sub", lang, url=clean, dir=DOWNLOAD_DIR),
                "IcoPath":  "icon.png",
                "score":    100,
                "JsonRPCAction": {
                    "method":             "download",
                    "parameters":         [clean],
                    "dontHideAfterAction": False,
                },
            }
        ]

    def save_token(self, token: str):
        lang = get_flow_language()
        config = load_config()
        config["token"] = token
        save_config(config)
        notify("✅ Yandex Music", t("notif_token_saved", lang))

    def reset_token(self):
        lang = get_flow_language()
        config = load_config()
        config.pop("token", None)
        save_config(config)
        notify("🔄 Yandex Music", t("notif_token_reset", lang))

    def download(self, url: str):
        lang = get_flow_language()
        config = load_config()
        token = config.get("token", "")

        if not token:
            notify("❌ Yandex Music", t("notif_no_token", lang))
            return

        media_type = detect_type(url, lang)
        os.makedirs(DOWNLOAD_DIR, exist_ok=True)
        notify("⏳ Yandex Music", t("notif_downloading", lang, type=media_type))

        thread = threading.Thread(
            target=download_thread,
            args=(url, media_type, token, lang),
            daemon=False,
        )
        thread.start()
        thread.join()


if __name__ == "__main__":
    YandexMusicDownloader()