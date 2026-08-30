#!/usr/bin/env python3
"""Apply receipt-OCR QML and AppErrors translations to .ts files."""

from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
I18N_DIR = ROOT / "i18n"

_PRIVACY = (
    "Off by default. Receipt photos stay on this device. Enabling this "
    "does not upload images; a cloud provider is not connected yet."
)
_MACOS_PYOBJC = (
    "Receipt OCR on macOS requires PyObjC Vision bindings. "
    "Install on-device scanning from Settings, or enter the expense manually."
)
_PLATFORM_UNAVAILABLE = (
    "Receipt scanning is not available on this platform (%1). Enter the expense manually."
)

TRANSLATIONS: dict[str, dict[str, str]] = {
    "en": {
        "Scan": "Scan",
        "Scan receipt": "Scan receipt",
        "Reading receipt…": "Reading receipt…",
        "Review suggested fields, then save.": "Review suggested fields, then save.",
        "You can edit any field or enter the expense manually.": (
            "You can edit any field or enter the expense manually."
        ),
        "Enter manually": "Enter manually",
        "Choose a receipt image": "Choose a receipt image",
        "Images (*.jpg *.jpeg *.png *.webp *.heic)": "Images (*.jpg *.jpeg *.png *.webp *.heic)",
        "Low confidence": "Low confidence",
        "Receipts": "Receipts",
        "Cloud receipt scanning": "Cloud receipt scanning",
        _PRIVACY: _PRIVACY,
        "Receipt image storage is not configured": "Receipt image storage is not configured",
        _MACOS_PYOBJC: _MACOS_PYOBJC,
        _PLATFORM_UNAVAILABLE: _PLATFORM_UNAVAILABLE,
        "Receipt image not found: %1": "Receipt image not found: %1",
        "Could not read text from receipt image: %1": "Could not read text from receipt image: %1",
    },
    "fr": {
        "Scan": "Numériser",
        "Scan receipt": "Numériser un ticket",
        "Reading receipt…": "Lecture du ticket…",
        "Review suggested fields, then save.": "Vérifiez les champs proposés, puis enregistrez.",
        "You can edit any field or enter the expense manually.": (
            "Vous pouvez modifier chaque champ ou saisir la dépense manuellement."
        ),
        "Enter manually": "Saisie manuelle",
        "Choose a receipt image": "Choisir une image de ticket",
        "Images (*.jpg *.jpeg *.png *.webp *.heic)": "Images (*.jpg *.jpeg *.png *.webp *.heic)",
        "Low confidence": "Confiance faible",
        "Receipts": "Tickets",
        "Cloud receipt scanning": "Numérisation cloud des tickets",
        _PRIVACY: (
            "Désactivé par défaut. Les photos de tickets restent sur cet appareil. "
            "Activer cette option n'envoie aucune image ; aucun fournisseur cloud "
            "n'est encore connecté."
        ),
        "Receipt image storage is not configured": (
            "Le stockage des images de tickets n'est pas configuré"
        ),
        _MACOS_PYOBJC: (
            "La reconnaissance de tickets sur macOS nécessite les liaisons PyObjC Vision. "
            "Installez la numérisation sur l'appareil depuis Réglages, "
            "ou saisissez la dépense manuellement."
        ),
        _PLATFORM_UNAVAILABLE: (
            "La numérisation de tickets n'est pas disponible sur cette plateforme (%1). "
            "Saisissez la dépense manuellement."
        ),
        "Receipt image not found: %1": "Image de ticket introuvable : %1",
        "Could not read text from receipt image: %1": (
            "Impossible de lire le texte de l'image du ticket : %1"
        ),
    },
    "ru": {
        "Scan": "Сканировать",
        "Scan receipt": "Сканировать чек",
        "Reading receipt…": "Чтение чека…",
        "Review suggested fields, then save.": "Проверьте предложенные поля и сохраните.",
        "You can edit any field or enter the expense manually.": (
            "Можно изменить любое поле или ввести расход вручную."
        ),
        "Enter manually": "Ввести вручную",
        "Choose a receipt image": "Выберите изображение чека",
        "Images (*.jpg *.jpeg *.png *.webp *.heic)": (
            "Изображения (*.jpg *.jpeg *.png *.webp *.heic)"
        ),
        "Low confidence": "Низкая уверенность",
        "Receipts": "Чеки",
        "Cloud receipt scanning": "Облачное распознавание чеков",
        _PRIVACY: (
            "Выключено по умолчанию. Фото чеков остаются на этом устройстве. "
            "Включение не отправляет изображения: облачный сервис ещё не подключён."
        ),
        "Receipt image storage is not configured": "Хранилище изображений чеков не настроено",
        _MACOS_PYOBJC: (
            "Распознавание чеков на macOS требует привязок PyObjC Vision. "
            "Установите распознавание на устройстве в Настройках "
            "или введите расход вручную."
        ),
        _PLATFORM_UNAVAILABLE: (
            "Сканирование чеков недоступно на этой платформе (%1). Введите расход вручную."
        ),
        "Receipt image not found: %1": "Изображение чека не найдено: %1",
        "Could not read text from receipt image: %1": (
            "Не удалось прочитать текст с изображения чека: %1"
        ),
    },
    "es": {
        "Scan": "Escanear",
        "Scan receipt": "Escanear recibo",
        "Reading receipt…": "Leyendo el recibo…",
        "Review suggested fields, then save.": "Revise los campos sugeridos y luego guarde.",
        "You can edit any field or enter the expense manually.": (
            "Puede editar cualquier campo o introducir el gasto manualmente."
        ),
        "Enter manually": "Introducir manualmente",
        "Choose a receipt image": "Elegir una imagen del recibo",
        "Images (*.jpg *.jpeg *.png *.webp *.heic)": "Imágenes (*.jpg *.jpeg *.png *.webp *.heic)",
        "Low confidence": "Baja confianza",
        "Receipts": "Recibos",
        "Cloud receipt scanning": "Escaneo de recibos en la nube",
        _PRIVACY: (
            "Desactivado de forma predeterminada. Las fotos de recibos permanecen en este "
            "dispositivo. Activar esto no sube imágenes; aún no hay un proveedor en la nube."
        ),
        "Receipt image storage is not configured": (
            "El almacenamiento de imágenes de recibos no está configurado"
        ),
        _MACOS_PYOBJC: (
            "El OCR de recibos en macOS requiere los enlaces PyObjC de Vision. "
            "Instale el escaneo en el dispositivo desde Ajustes, "
            "o introduzca el gasto manualmente."
        ),
        _PLATFORM_UNAVAILABLE: (
            "El escaneo de recibos no está disponible en esta plataforma (%1). "
            "Introduzca el gasto manualmente."
        ),
        "Receipt image not found: %1": "No se encontró la imagen del recibo: %1",
        "Could not read text from receipt image: %1": (
            "No se pudo leer el texto de la imagen del recibo: %1"
        ),
    },
    "de": {
        "Scan": "Scannen",
        "Scan receipt": "Beleg scannen",
        "Reading receipt…": "Beleg wird gelesen…",
        "Review suggested fields, then save.": "Vorgeschlagene Felder prüfen und speichern.",
        "You can edit any field or enter the expense manually.": (
            "Sie können jedes Feld bearbeiten oder die Ausgabe manuell eingeben."
        ),
        "Enter manually": "Manuell eingeben",
        "Choose a receipt image": "Belegbild auswählen",
        "Images (*.jpg *.jpeg *.png *.webp *.heic)": "Bilder (*.jpg *.jpeg *.png *.webp *.heic)",
        "Low confidence": "Geringe Sicherheit",
        "Receipts": "Belege",
        "Cloud receipt scanning": "Cloud-Belegerkennung",
        _PRIVACY: (
            "Standardmäßig aus. Belegfotos bleiben auf diesem Gerät. Das Aktivieren lädt "
            "keine Bilder hoch; ein Cloud-Anbieter ist noch nicht verbunden."
        ),
        "Receipt image storage is not configured": "Belegbildspeicher ist nicht konfiguriert",
        _MACOS_PYOBJC: (
            "Beleg-OCR unter macOS benötigt PyObjC-Vision-Bindungen. "
            "Installieren Sie die Erkennung auf dem Gerät unter Einstellungen, "
            "oder geben Sie die Ausgabe manuell ein."
        ),
        _PLATFORM_UNAVAILABLE: (
            "Belegscan ist auf dieser Plattform nicht verfügbar (%1). "
            "Geben Sie die Ausgabe manuell ein."
        ),
        "Receipt image not found: %1": "Belegbild nicht gefunden: %1",
        "Could not read text from receipt image: %1": (
            "Text konnte nicht aus dem Belegbild gelesen werden: %1"
        ),
    },
}

_INSTALL_STRINGS: dict[str, dict[str, str]] = {
    "en": {
        "On-device receipt scanning": "On-device receipt scanning",
        "Ready. Uses Apple Vision on this Mac. Photos stay on this device.": (
            "Ready. Uses Apple Vision on this Mac. Photos stay on this device."
        ),
        "Required for Scan. Installs Apple Vision bindings for this app. Network access is required.": (
            "Required for Scan. Installs Apple Vision bindings for this app. "
            "Network access is required."
        ),
        "This app build does not include on-device scanning.": (
            "This app build does not include on-device scanning."
        ),
        "Install": "Install",
        "Installing…": "Installing…",
        "Install on-device receipt scanning": "Install on-device receipt scanning",
        "On-device receipt scanning can only be installed on macOS.": (
            "On-device receipt scanning can only be installed on macOS."
        ),
        "On-device receipt scanning cannot be installed in this app build.": (
            "On-device receipt scanning cannot be installed in this app build."
        ),
        "Could not install on-device receipt scanning. Check your network connection and try again.": (
            "Could not install on-device receipt scanning. "
            "Check your network connection and try again."
        ),
        "Installing on-device receipt scanning timed out. Check your network and try again.": (
            "Installing on-device receipt scanning timed out. Check your network and try again."
        ),
        "Installed OCR packages but Vision is still unavailable. Restart the app and try Scan again.": (
            "Installed OCR packages but Vision is still unavailable. "
            "Restart the app and try Scan again."
        ),
        "Could not install on-device receipt scanning: %1": (
            "Could not install on-device receipt scanning: %1"
        ),
    },
    "fr": {
        "On-device receipt scanning": "Numérisation de tickets sur l'appareil",
        "Ready. Uses Apple Vision on this Mac. Photos stay on this device.": (
            "Prêt. Utilise Apple Vision sur ce Mac. Les photos restent sur cet appareil."
        ),
        "Required for Scan. Installs Apple Vision bindings for this app. Network access is required.": (
            "Requis pour Numériser. Installe les liaisons Apple Vision pour cette application. "
            "Une connexion réseau est nécessaire."
        ),
        "This app build does not include on-device scanning.": (
            "Cette version de l'application n'inclut pas la numérisation sur l'appareil."
        ),
        "Install": "Installer",
        "Installing…": "Installation…",
        "Install on-device receipt scanning": "Installer la numérisation de tickets sur l'appareil",
        "On-device receipt scanning can only be installed on macOS.": (
            "La numérisation de tickets sur l'appareil ne peut être installée que sous macOS."
        ),
        "On-device receipt scanning cannot be installed in this app build.": (
            "La numérisation de tickets sur l'appareil ne peut pas être installée "
            "dans cette version de l'application."
        ),
        "Could not install on-device receipt scanning. Check your network connection and try again.": (
            "Impossible d'installer la numérisation de tickets sur l'appareil. "
            "Vérifiez votre connexion réseau et réessayez."
        ),
        "Installing on-device receipt scanning timed out. Check your network and try again.": (
            "L'installation de la numérisation de tickets sur l'appareil a expiré. "
            "Vérifiez votre réseau et réessayez."
        ),
        "Installed OCR packages but Vision is still unavailable. Restart the app and try Scan again.": (
            "Les paquets OCR sont installés, mais Vision est toujours indisponible. "
            "Redémarrez l'application et réessayez Numériser."
        ),
        "Could not install on-device receipt scanning: %1": (
            "Impossible d'installer la numérisation de tickets sur l'appareil : %1"
        ),
    },
    "ru": {
        "On-device receipt scanning": "Распознавание чеков на устройстве",
        "Ready. Uses Apple Vision on this Mac. Photos stay on this device.": (
            "Готово. Используется Apple Vision на этом Mac. Фото остаются на этом устройстве."
        ),
        "Required for Scan. Installs Apple Vision bindings for this app. Network access is required.": (
            "Нужно для сканирования. Устанавливает привязки Apple Vision для этого приложения. "
            "Требуется доступ к сети."
        ),
        "This app build does not include on-device scanning.": (
            "Эта сборка приложения не включает распознавание на устройстве."
        ),
        "Install": "Установить",
        "Installing…": "Установка…",
        "Install on-device receipt scanning": "Установить распознавание чеков на устройстве",
        "On-device receipt scanning can only be installed on macOS.": (
            "Распознавание чеков на устройстве можно установить только на macOS."
        ),
        "On-device receipt scanning cannot be installed in this app build.": (
            "Распознавание чеков на устройстве нельзя установить в этой сборке приложения."
        ),
        "Could not install on-device receipt scanning. Check your network connection and try again.": (
            "Не удалось установить распознавание чеков на устройстве. "
            "Проверьте подключение к сети и повторите попытку."
        ),
        "Installing on-device receipt scanning timed out. Check your network and try again.": (
            "Установка распознавания чеков на устройстве превысила время ожидания. "
            "Проверьте сеть и повторите попытку."
        ),
        "Installed OCR packages but Vision is still unavailable. Restart the app and try Scan again.": (
            "Пакеты OCR установлены, но Vision по-прежнему недоступен. "
            "Перезапустите приложение и снова нажмите «Сканировать»."
        ),
        "Could not install on-device receipt scanning: %1": (
            "Не удалось установить распознавание чеков на устройстве: %1"
        ),
    },
    "es": {
        "On-device receipt scanning": "Escaneo de recibos en el dispositivo",
        "Ready. Uses Apple Vision on this Mac. Photos stay on this device.": (
            "Listo. Usa Apple Vision en este Mac. Las fotos permanecen en este dispositivo."
        ),
        "Required for Scan. Installs Apple Vision bindings for this app. Network access is required.": (
            "Obligatorio para Escanear. Instala los enlaces de Apple Vision para esta aplicación. "
            "Se requiere acceso a la red."
        ),
        "This app build does not include on-device scanning.": (
            "Esta versión de la aplicación no incluye el escaneo en el dispositivo."
        ),
        "Install": "Instalar",
        "Installing…": "Instalando…",
        "Install on-device receipt scanning": "Instalar el escaneo de recibos en el dispositivo",
        "On-device receipt scanning can only be installed on macOS.": (
            "El escaneo de recibos en el dispositivo solo se puede instalar en macOS."
        ),
        "On-device receipt scanning cannot be installed in this app build.": (
            "El escaneo de recibos en el dispositivo no se puede instalar "
            "en esta versión de la aplicación."
        ),
        "Could not install on-device receipt scanning. Check your network connection and try again.": (
            "No se pudo instalar el escaneo de recibos en el dispositivo. "
            "Compruebe la conexión de red e inténtelo de nuevo."
        ),
        "Installing on-device receipt scanning timed out. Check your network and try again.": (
            "La instalación del escaneo de recibos en el dispositivo agotó el tiempo de espera. "
            "Compruebe la red e inténtelo de nuevo."
        ),
        "Installed OCR packages but Vision is still unavailable. Restart the app and try Scan again.": (
            "Se instalaron los paquetes de OCR, pero Vision sigue no disponible. "
            "Reinicie la aplicación e intente Escanear de nuevo."
        ),
        "Could not install on-device receipt scanning: %1": (
            "No se pudo instalar el escaneo de recibos en el dispositivo: %1"
        ),
    },
    "de": {
        "On-device receipt scanning": "Belegerkennung auf dem Gerät",
        "Ready. Uses Apple Vision on this Mac. Photos stay on this device.": (
            "Bereit. Verwendet Apple Vision auf diesem Mac. Fotos bleiben auf diesem Gerät."
        ),
        "Required for Scan. Installs Apple Vision bindings for this app. Network access is required.": (
            "Erforderlich für Scannen. Installiert Apple-Vision-Bindungen für diese App. "
            "Netzwerkzugriff ist erforderlich."
        ),
        "This app build does not include on-device scanning.": (
            "Diese App-Version enthält keine Belegerkennung auf dem Gerät."
        ),
        "Install": "Installieren",
        "Installing…": "Wird installiert…",
        "Install on-device receipt scanning": "Belegerkennung auf dem Gerät installieren",
        "On-device receipt scanning can only be installed on macOS.": (
            "Die Belegerkennung auf dem Gerät kann nur unter macOS installiert werden."
        ),
        "On-device receipt scanning cannot be installed in this app build.": (
            "Die Belegerkennung auf dem Gerät kann in dieser App-Version nicht installiert werden."
        ),
        "Could not install on-device receipt scanning. Check your network connection and try again.": (
            "Die Belegerkennung auf dem Gerät konnte nicht installiert werden. "
            "Prüfen Sie die Netzwerkverbindung und versuchen Sie es erneut."
        ),
        "Installing on-device receipt scanning timed out. Check your network and try again.": (
            "Die Installation der Belegerkennung auf dem Gerät ist abgelaufen. "
            "Prüfen Sie das Netzwerk und versuchen Sie es erneut."
        ),
        "Installed OCR packages but Vision is still unavailable. Restart the app and try Scan again.": (
            "OCR-Pakete wurden installiert, aber Vision ist weiterhin nicht verfügbar. "
            "Starten Sie die App neu und versuchen Sie Scannen erneut."
        ),
        "Could not install on-device receipt scanning: %1": (
            "Die Belegerkennung auf dem Gerät konnte nicht installiert werden: %1"
        ),
    },
}


def _escape_xml(text: str) -> str:
    return (
        text.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
        .replace("'", "&apos;")
    )


def apply_translations(locale: str) -> None:
    path = I18N_DIR / f"app_{locale}.ts"
    content = path.read_text(encoding="utf-8")
    mapping = {**TRANSLATIONS[locale], **_INSTALL_STRINGS[locale]}

    for source, translation in mapping.items():
        escaped_source = re.escape(_escape_xml(source))
        escaped_translation = _escape_xml(translation)
        pattern = (
            rf"(<source>{escaped_source}</source>\s*)"
            rf"<translation(?: type=\"unfinished\")?>(?:[^<]*)</translation>"
        )
        replacement = rf"\1<translation>{escaped_translation}</translation>"
        content, count = re.subn(pattern, replacement, content)
        if count == 0:
            msg = f"Missing translation entry for {locale!r}: {source!r}"
            raise RuntimeError(msg)

    path.write_text(content, encoding="utf-8")


def main() -> None:
    for locale in TRANSLATIONS:
        apply_translations(locale)
        print(f"Updated app_{locale}.ts")


if __name__ == "__main__":
    main()
