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
        "Ready. On-device OCR is available. Photos stay on this device.": (
            "Ready. On-device OCR is available. Photos stay on this device."
        ),
        "Required for Scan. Installs on-device OCR for this app. Network access is required.": (
            "Required for Scan. Installs on-device OCR for this app. Network access is required."
        ),
        "Required for Scan. Installs Tesseract bindings. Also install the Tesseract engine (for example: apt install tesseract-ocr). Network access is required.": (
            "Required for Scan. Installs Tesseract bindings. Also install the Tesseract engine "
            "(for example: apt install tesseract-ocr). Network access is required."
        ),
        "This app build does not include on-device scanning.": (
            "This app build does not include on-device scanning."
        ),
        "Install": "Install",
        "Installing…": "Installing…",
        "Install on-device receipt scanning": "Install on-device receipt scanning",
        "On-device receipt scanning is not available on this platform.": (
            "On-device receipt scanning is not available on this platform."
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
        "Installed OCR packages but scanning is still unavailable. Restart the app and try Scan again.": (
            "Installed OCR packages but scanning is still unavailable. "
            "Restart the app and try Scan again."
        ),
        "Could not install on-device receipt scanning: %1": (
            "Could not install on-device receipt scanning: %1"
        ),
        "Receipt OCR on Windows requires WinRT OCR bindings. Install on-device scanning from Settings, or enter the expense manually.": (
            "Receipt OCR on Windows requires WinRT OCR bindings. "
            "Install on-device scanning from Settings, or enter the expense manually."
        ),
        "Receipt OCR on Linux requires Tesseract Python bindings. Install on-device scanning from Settings, or enter the expense manually.": (
            "Receipt OCR on Linux requires Tesseract Python bindings. "
            "Install on-device scanning from Settings, or enter the expense manually."
        ),
        "The Tesseract OCR engine was not found. Install it with your package manager (for example: apt install tesseract-ocr) and try again, or enter the expense manually.": (
            "The Tesseract OCR engine was not found. Install it with your package "
            "manager (for example: apt install tesseract-ocr) and try again, "
            "or enter the expense manually."
        ),
        "Python Tesseract bindings are installed, but the Tesseract engine was not found. Install it with your package manager (for example: apt install tesseract-ocr) and try Scan again.": (
            "Python Tesseract bindings are installed, but the Tesseract engine was not found. "
            "Install it with your package manager (for example: apt install tesseract-ocr) "
            "and try Scan again."
        ),
        "Windows OCR is not available. Install an OCR language pack in Windows Settings and try again, or enter the expense manually.": (
            "Windows OCR is not available. Install an OCR language pack in Windows "
            "Settings and try again, or enter the expense manually."
        ),
    },
    "fr": {
        "On-device receipt scanning": "Numérisation de tickets sur l'appareil",
        "Ready. On-device OCR is available. Photos stay on this device.": (
            "Prêt. La reconnaissance sur l'appareil est disponible. "
            "Les photos restent sur cet appareil."
        ),
        "Required for Scan. Installs on-device OCR for this app. Network access is required.": (
            "Requis pour Numériser. Installe la reconnaissance sur l'appareil pour cette "
            "application. Une connexion réseau est nécessaire."
        ),
        "Required for Scan. Installs Tesseract bindings. Also install the Tesseract engine (for example: apt install tesseract-ocr). Network access is required.": (
            "Requis pour Numériser. Installe les liaisons Tesseract. Installez aussi le moteur "
            "Tesseract (par exemple : apt install tesseract-ocr). Une connexion réseau "
            "est nécessaire."
        ),
        "This app build does not include on-device scanning.": (
            "Cette version de l'application n'inclut pas la numérisation sur l'appareil."
        ),
        "Install": "Installer",
        "Installing…": "Installation…",
        "Install on-device receipt scanning": "Installer la numérisation de tickets sur l'appareil",
        "On-device receipt scanning is not available on this platform.": (
            "La numérisation de tickets sur l'appareil n'est pas disponible sur cette plateforme."
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
        "Installed OCR packages but scanning is still unavailable. Restart the app and try Scan again.": (
            "Les paquets OCR sont installés, mais la numérisation est toujours indisponible. "
            "Redémarrez l'application et réessayez Numériser."
        ),
        "Could not install on-device receipt scanning: %1": (
            "Impossible d'installer la numérisation de tickets sur l'appareil : %1"
        ),
        "Receipt OCR on Windows requires WinRT OCR bindings. Install on-device scanning from Settings, or enter the expense manually.": (
            "La reconnaissance de tickets sous Windows nécessite les liaisons WinRT OCR. "
            "Installez la numérisation sur l'appareil depuis Réglages, "
            "ou saisissez la dépense manuellement."
        ),
        "Receipt OCR on Linux requires Tesseract Python bindings. Install on-device scanning from Settings, or enter the expense manually.": (
            "La reconnaissance de tickets sous Linux nécessite les liaisons Python Tesseract. "
            "Installez la numérisation sur l'appareil depuis Réglages, "
            "ou saisissez la dépense manuellement."
        ),
        "The Tesseract OCR engine was not found. Install it with your package manager (for example: apt install tesseract-ocr) and try again, or enter the expense manually.": (
            "Le moteur Tesseract est introuvable. Installez-le avec votre gestionnaire de "
            "paquets (par exemple : apt install tesseract-ocr) et réessayez, "
            "ou saisissez la dépense manuellement."
        ),
        "Python Tesseract bindings are installed, but the Tesseract engine was not found. Install it with your package manager (for example: apt install tesseract-ocr) and try Scan again.": (
            "Les liaisons Python Tesseract sont installées, mais le moteur Tesseract "
            "est introuvable. Installez-le avec votre gestionnaire de paquets "
            "(par exemple : apt install tesseract-ocr) et réessayez Numériser."
        ),
        "Windows OCR is not available. Install an OCR language pack in Windows Settings and try again, or enter the expense manually.": (
            "La reconnaissance Windows n'est pas disponible. Installez un pack de langue OCR "
            "dans les paramètres Windows et réessayez, ou saisissez la dépense manuellement."
        ),
    },
    "ru": {
        "On-device receipt scanning": "Распознавание чеков на устройстве",
        "Ready. On-device OCR is available. Photos stay on this device.": (
            "Готово. Распознавание на устройстве доступно. Фото остаются на этом устройстве."
        ),
        "Required for Scan. Installs on-device OCR for this app. Network access is required.": (
            "Нужно для сканирования. Устанавливает распознавание на устройстве для этого "
            "приложения. Требуется доступ к сети."
        ),
        "Required for Scan. Installs Tesseract bindings. Also install the Tesseract engine (for example: apt install tesseract-ocr). Network access is required.": (
            "Нужно для сканирования. Устанавливает привязки Tesseract. Также установите "
            "движок Tesseract (например: apt install tesseract-ocr). Требуется доступ к сети."
        ),
        "This app build does not include on-device scanning.": (
            "Эта сборка приложения не включает распознавание на устройстве."
        ),
        "Install": "Установить",
        "Installing…": "Установка…",
        "Install on-device receipt scanning": "Установить распознавание чеков на устройстве",
        "On-device receipt scanning is not available on this platform.": (
            "Распознавание чеков на устройстве недоступно на этой платформе."
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
        "Installed OCR packages but scanning is still unavailable. Restart the app and try Scan again.": (
            "Пакеты OCR установлены, но распознавание по-прежнему недоступно. "
            "Перезапустите приложение и снова нажмите «Сканировать»."
        ),
        "Could not install on-device receipt scanning: %1": (
            "Не удалось установить распознавание чеков на устройстве: %1"
        ),
        "Receipt OCR on Windows requires WinRT OCR bindings. Install on-device scanning from Settings, or enter the expense manually.": (
            "Распознавание чеков в Windows требует привязок WinRT OCR. "
            "Установите распознавание на устройстве в Настройках "
            "или введите расход вручную."
        ),
        "Receipt OCR on Linux requires Tesseract Python bindings. Install on-device scanning from Settings, or enter the expense manually.": (
            "Распознавание чеков в Linux требует привязок Python Tesseract. "
            "Установите распознавание на устройстве в Настройках "
            "или введите расход вручную."
        ),
        "The Tesseract OCR engine was not found. Install it with your package manager (for example: apt install tesseract-ocr) and try again, or enter the expense manually.": (
            "Движок Tesseract не найден. Установите его через пакетный менеджер "
            "(например: apt install tesseract-ocr) и повторите попытку "
            "или введите расход вручную."
        ),
        "Python Tesseract bindings are installed, but the Tesseract engine was not found. Install it with your package manager (for example: apt install tesseract-ocr) and try Scan again.": (
            "Привязки Python Tesseract установлены, но движок Tesseract не найден. "
            "Установите его через пакетный менеджер "
            "(например: apt install tesseract-ocr) и снова нажмите «Сканировать»."
        ),
        "Windows OCR is not available. Install an OCR language pack in Windows Settings and try again, or enter the expense manually.": (
            "Распознавание Windows недоступно. Установите языковой пакет OCR "
            "в параметрах Windows и повторите попытку или введите расход вручную."
        ),
    },
    "es": {
        "On-device receipt scanning": "Escaneo de recibos en el dispositivo",
        "Ready. On-device OCR is available. Photos stay on this device.": (
            "Listo. El OCR en el dispositivo está disponible. "
            "Las fotos permanecen en este dispositivo."
        ),
        "Required for Scan. Installs on-device OCR for this app. Network access is required.": (
            "Obligatorio para Escanear. Instala el OCR en el dispositivo para esta "
            "aplicación. Se requiere acceso a la red."
        ),
        "Required for Scan. Installs Tesseract bindings. Also install the Tesseract engine (for example: apt install tesseract-ocr). Network access is required.": (
            "Obligatorio para Escanear. Instala los enlaces de Tesseract. Instale también "
            "el motor Tesseract (por ejemplo: apt install tesseract-ocr). "
            "Se requiere acceso a la red."
        ),
        "This app build does not include on-device scanning.": (
            "Esta versión de la aplicación no incluye el escaneo en el dispositivo."
        ),
        "Install": "Instalar",
        "Installing…": "Instalando…",
        "Install on-device receipt scanning": "Instalar el escaneo de recibos en el dispositivo",
        "On-device receipt scanning is not available on this platform.": (
            "El escaneo de recibos en el dispositivo no está disponible en esta plataforma."
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
        "Installed OCR packages but scanning is still unavailable. Restart the app and try Scan again.": (
            "Se instalaron los paquetes de OCR, pero el escaneo sigue no disponible. "
            "Reinicie la aplicación e intente Escanear de nuevo."
        ),
        "Could not install on-device receipt scanning: %1": (
            "No se pudo instalar el escaneo de recibos en el dispositivo: %1"
        ),
        "Receipt OCR on Windows requires WinRT OCR bindings. Install on-device scanning from Settings, or enter the expense manually.": (
            "El OCR de recibos en Windows requiere los enlaces WinRT de OCR. "
            "Instale el escaneo en el dispositivo desde Ajustes, "
            "o introduzca el gasto manualmente."
        ),
        "Receipt OCR on Linux requires Tesseract Python bindings. Install on-device scanning from Settings, or enter the expense manually.": (
            "El OCR de recibos en Linux requiere los enlaces Python de Tesseract. "
            "Instale el escaneo en el dispositivo desde Ajustes, "
            "o introduzca el gasto manualmente."
        ),
        "The Tesseract OCR engine was not found. Install it with your package manager (for example: apt install tesseract-ocr) and try again, or enter the expense manually.": (
            "No se encontró el motor Tesseract. Instálelo con su gestor de paquetes "
            "(por ejemplo: apt install tesseract-ocr) e inténtelo de nuevo, "
            "o introduzca el gasto manualmente."
        ),
        "Python Tesseract bindings are installed, but the Tesseract engine was not found. Install it with your package manager (for example: apt install tesseract-ocr) and try Scan again.": (
            "Los enlaces Python de Tesseract están instalados, pero no se encontró el motor "
            "Tesseract. Instálelo con su gestor de paquetes "
            "(por ejemplo: apt install tesseract-ocr) e intente Escanear de nuevo."
        ),
        "Windows OCR is not available. Install an OCR language pack in Windows Settings and try again, or enter the expense manually.": (
            "El OCR de Windows no está disponible. Instale un paquete de idioma OCR "
            "en Configuración de Windows e inténtelo de nuevo, "
            "o introduzca el gasto manualmente."
        ),
    },
    "de": {
        "On-device receipt scanning": "Belegerkennung auf dem Gerät",
        "Ready. On-device OCR is available. Photos stay on this device.": (
            "Bereit. OCR auf dem Gerät ist verfügbar. Fotos bleiben auf diesem Gerät."
        ),
        "Required for Scan. Installs on-device OCR for this app. Network access is required.": (
            "Erforderlich für Scannen. Installiert OCR auf dem Gerät für diese App. "
            "Netzwerkzugriff ist erforderlich."
        ),
        "Required for Scan. Installs Tesseract bindings. Also install the Tesseract engine (for example: apt install tesseract-ocr). Network access is required.": (
            "Erforderlich für Scannen. Installiert Tesseract-Bindungen. Installieren Sie "
            "auch die Tesseract-Engine (z. B. apt install tesseract-ocr). "
            "Netzwerkzugriff ist erforderlich."
        ),
        "This app build does not include on-device scanning.": (
            "Diese App-Version enthält keine Belegerkennung auf dem Gerät."
        ),
        "Install": "Installieren",
        "Installing…": "Wird installiert…",
        "Install on-device receipt scanning": "Belegerkennung auf dem Gerät installieren",
        "On-device receipt scanning is not available on this platform.": (
            "Die Belegerkennung auf dem Gerät ist auf dieser Plattform nicht verfügbar."
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
        "Installed OCR packages but scanning is still unavailable. Restart the app and try Scan again.": (
            "OCR-Pakete wurden installiert, aber das Scannen ist weiterhin nicht verfügbar. "
            "Starten Sie die App neu und versuchen Sie Scannen erneut."
        ),
        "Could not install on-device receipt scanning: %1": (
            "Die Belegerkennung auf dem Gerät konnte nicht installiert werden: %1"
        ),
        "Receipt OCR on Windows requires WinRT OCR bindings. Install on-device scanning from Settings, or enter the expense manually.": (
            "Beleg-OCR unter Windows benötigt WinRT-OCR-Bindungen. "
            "Installieren Sie die Erkennung auf dem Gerät unter Einstellungen, "
            "oder geben Sie die Ausgabe manuell ein."
        ),
        "Receipt OCR on Linux requires Tesseract Python bindings. Install on-device scanning from Settings, or enter the expense manually.": (
            "Beleg-OCR unter Linux benötigt Tesseract-Python-Bindungen. "
            "Installieren Sie die Erkennung auf dem Gerät unter Einstellungen, "
            "oder geben Sie die Ausgabe manuell ein."
        ),
        "The Tesseract OCR engine was not found. Install it with your package manager (for example: apt install tesseract-ocr) and try again, or enter the expense manually.": (
            "Die Tesseract-Engine wurde nicht gefunden. Installieren Sie sie mit Ihrem "
            "Paketmanager (z. B. apt install tesseract-ocr) und versuchen Sie es erneut, "
            "oder geben Sie die Ausgabe manuell ein."
        ),
        "Python Tesseract bindings are installed, but the Tesseract engine was not found. Install it with your package manager (for example: apt install tesseract-ocr) and try Scan again.": (
            "Python-Tesseract-Bindungen sind installiert, aber die Tesseract-Engine "
            "wurde nicht gefunden. Installieren Sie sie mit Ihrem Paketmanager "
            "(z. B. apt install tesseract-ocr) und versuchen Sie Scannen erneut."
        ),
        "Windows OCR is not available. Install an OCR language pack in Windows Settings and try again, or enter the expense manually.": (
            "Windows-OCR ist nicht verfügbar. Installieren Sie ein OCR-Sprachpaket "
            "in den Windows-Einstellungen und versuchen Sie es erneut, "
            "oder geben Sie die Ausgabe manuell ein."
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
