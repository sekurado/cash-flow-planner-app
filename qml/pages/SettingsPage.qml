import QtQuick
import QtQuick.Controls
import QtQuick.Controls.Material
import QtQuick.Layouts
import Qt5Compat.GraphicalEffects
import QtCore

import ThemeTokens 1.0
import "../components"

Page {
    id: root

    objectName: "settingsPage"
    title: qsTr("Settings")

    // Base currency used when fetching live rates into the global rate table.
    readonly property string fetchBaseCurrency: {
        if (planViewModel && planViewModel.selectedPlan
                && planViewModel.selectedPlan.base_currency) {
            return planViewModel.selectedPlan.base_currency
        }
        return "USD"
    }
    readonly property bool isDark: Material.theme === Material.Dark
    readonly property color cardColor: isDark ? ThemeTokens.cardDark : ThemeTokens.cardLight

    property bool exchangeRatesExpanded: false

    Component {
        id: methodologyPageComponent
        MethodologyPage {}
    }

    function openMethodology() {
        if (root.StackView.view) {
            root.StackView.view.push(methodologyPageComponent)
        }
    }

    background: Rectangle {
        color: isDark ? ThemeTokens.surfaceDark : ThemeTokens.surfaceLight
    }

    header: ToolBar {
        Material.elevation: 2

        RowLayout {
            anchors.fill: parent
            spacing: 4

            ToolButton {
                icon.name: "go-previous"
                Accessible.name: qsTr("Back")
                onClicked: {
                    if (root.StackView.view) {
                        root.StackView.view.pop()
                    }
                }
            }

            Label {
                Layout.fillWidth: true
                text: qsTr("Settings")
                font.pixelSize: ThemeTokens.fontLg
                elide: Text.ElideRight
            }
        }
    }

    component SettingsSectionTitle: Label {
        required property string titleText

        text: titleText.toUpperCase()
        font.pixelSize: ThemeTokens.fontXs
        font.weight: ThemeTokens.weightSemiBold
        color: ThemeTokens.primary
    }

    component SettingsCard: Rectangle {
        id: settingsCard

        property alias content: cardColumn.data
        default property alias children: cardColumn.data

        Layout.fillWidth: true
        Layout.minimumWidth: 0
        implicitHeight: cardColumn.implicitHeight
        radius: ThemeTokens.radiusLg
        color: root.cardColor
        layer.enabled: true
        layer.effect: DropShadow {
            radius: 8
            samples: 17
            color: "#18000000"
            verticalOffset: 2
        }

        Column {
            id: cardColumn
            width: parent.width
        }
    }

    component SettingsRow: Item {
        id: settingsRow

        property string label: ""
        property string sublabel: ""
        property bool showDivider: true
        default property alias controls: rowLayout.data

        width: parent ? parent.width : implicitWidth
        implicitHeight: rowLayout.implicitHeight + (settingsRow.showDivider ? 1 : 0)
        height: visible ? implicitHeight : 0
        clip: true

        Column {
            width: parent.width

            RowLayout {
                id: rowLayout
                width: parent.width
                spacing: ThemeTokens.spaceMd

                ColumnLayout {
                    Layout.fillWidth: true
                    Layout.minimumWidth: 0
                    Layout.leftMargin: ThemeTokens.spaceMd
                    Layout.topMargin: ThemeTokens.spaceMd
                    Layout.bottomMargin: ThemeTokens.spaceMd
                    spacing: 2

                    Label {
                        Layout.fillWidth: true
                        text: settingsRow.label
                        font.pixelSize: ThemeTokens.fontMd
                        wrapMode: Text.WordWrap
                    }

                    Label {
                        Layout.fillWidth: true
                        visible: settingsRow.sublabel !== ""
                        text: settingsRow.sublabel
                        font.pixelSize: ThemeTokens.fontXs
                        color: Material.secondaryTextColor
                        wrapMode: Text.WordWrap
                    }
                }
            }

            Rectangle {
                width: parent.width
                height: 1
                visible: settingsRow.showDivider
                color: Material.dividerColor
            }
        }
    }

    Flickable {
        id: settingsScroll
        anchors.fill: parent
        clip: true
        boundsBehavior: Flickable.StopAtBounds
        contentWidth: settingsContent.width
        contentHeight: settingsContent.implicitHeight

        readonly property int verticalScrollBarOverlap: contentHeight > height
            ? verticalScrollBar.implicitWidth
            : 0

        ScrollBar.vertical: ScrollBar {
            id: verticalScrollBar
            policy: ScrollBar.AsNeeded
        }

        ColumnLayout {
            id: settingsContent
            width: settingsScroll.width - settingsScroll.verticalScrollBarOverlap
            spacing: ThemeTokens.spaceLg

            ColumnLayout {
                Layout.fillWidth: true
                Layout.minimumWidth: 0
                Layout.leftMargin: ThemeTokens.spaceMd
                Layout.rightMargin: ThemeTokens.spaceMd
                Layout.topMargin: ThemeTokens.spaceMd
                spacing: ThemeTokens.spaceSm

                SettingsSectionTitle {
                    titleText: qsTr("Appearance")
                }

                SettingsCard {
                    SettingsRow {
                        label: qsTr("Dark mode")
                        sublabel: qsTr("Restart not required")

                        Switch {
                            Layout.alignment: Qt.AlignVCenter
                            Layout.rightMargin: ThemeTokens.spaceMd
                            Layout.topMargin: ThemeTokens.spaceMd
                            Layout.bottomMargin: ThemeTokens.spaceMd
                            checked: settingsViewModel.darkMode
                            onToggled: settingsViewModel.setDarkMode(checked)
                            Accessible.name: qsTr("Dark mode")
                        }
                    }

                    SettingsRow {
                        label: qsTr("Language")
                        showDivider: false

                        ComboBox {
                            Layout.alignment: Qt.AlignVCenter
                            Layout.rightMargin: ThemeTokens.spaceMd
                            Layout.topMargin: ThemeTokens.spaceMd
                            Layout.bottomMargin: ThemeTokens.spaceMd
                            Layout.preferredWidth: 160
                            Material.foreground: ThemeTokens.primary
                            model: [
                                { value: "en", label: "English" },
                                { value: "fr", label: "Français" },
                                { value: "ru", label: "Русский" },
                                { value: "es", label: "Español" },
                                { value: "de", label: "Deutsch" },
                            ]
                            textRole: "label"
                            currentIndex: {
                                const idx = model.findIndex(
                                    item => item.value === settingsViewModel.language)
                                return idx >= 0 ? idx : 0
                            }
                            onActivated: settingsViewModel.setLanguage(model[currentIndex].value)
                            Accessible.name: qsTr("Language")
                        }
                    }
                }
            }

            ColumnLayout {
                Layout.fillWidth: true
                Layout.minimumWidth: 0
                Layout.leftMargin: ThemeTokens.spaceMd
                Layout.rightMargin: ThemeTokens.spaceMd
                spacing: ThemeTokens.spaceSm

                SettingsSectionTitle {
                    titleText: qsTr("Data & Currency")
                }

                SettingsCard {
                    SettingsRow {
                        label: qsTr("Exchange rates")

                        Button {
                            Layout.alignment: Qt.AlignVCenter
                            Layout.rightMargin: ThemeTokens.spaceMd
                            Layout.topMargin: ThemeTokens.spaceMd
                            Layout.bottomMargin: ThemeTokens.spaceMd
                            flat: true
                            text: root.exchangeRatesExpanded ? qsTr("Hide") : qsTr("Manage ▶")
                            Material.foreground: ThemeTokens.primary
                            Accessible.name: qsTr("Manage exchange rates")
                            onClicked: root.exchangeRatesExpanded = !root.exchangeRatesExpanded
                        }
                    }

                    SettingsRow {
                        label: qsTr("Fetch live exchange rates")
                        sublabel: settingsViewModel.useMockExchangeRates
                            ? qsTr(
                                "When enabled, exchange rates are loaded from a built-in mock "
                                + "provider instead of the live API.")
                            : qsTr(
                                "When enabled, the app may contact an external service to download "
                                + "current exchange rates. Network access is required.")

                        Switch {
                            Layout.alignment: Qt.AlignVCenter
                            Layout.rightMargin: ThemeTokens.spaceMd
                            Layout.topMargin: ThemeTokens.spaceMd
                            Layout.bottomMargin: ThemeTokens.spaceMd
                            checked: settingsViewModel.liveRatesEnabled
                            onToggled: settingsViewModel.setLiveRatesEnabled(checked)
                            Accessible.name: qsTr("Fetch live exchange rates")
                        }
                    }

                    SettingsRow {
                        visible: settingsViewModel.devModeEnabled
                        label: qsTr("Use mock exchange rates")
                        sublabel: qsTr(
                            "Developer option: returns prepared rates without contacting "
                            + "the external API. Start the app with --dev to show this toggle.")
                        showDivider: false

                        Switch {
                            Layout.alignment: Qt.AlignVCenter
                            Layout.rightMargin: ThemeTokens.spaceMd
                            Layout.topMargin: ThemeTokens.spaceMd
                            Layout.bottomMargin: ThemeTokens.spaceMd
                            checked: settingsViewModel.useMockExchangeRates
                            onToggled: settingsViewModel.setUseMockExchangeRates(checked)
                            Accessible.name: qsTr("Use mock exchange rates")
                        }
                    }
                }

                RowLayout {
                    Layout.fillWidth: true
                    Layout.leftMargin: ThemeTokens.spaceMd
                    spacing: ThemeTokens.spaceXs
                    visible: settingsViewModel.liveRatesEnabled
                        && !settingsViewModel.useMockExchangeRates

                    Label {
                        text: qsTr("Rates by")
                        color: Material.color(Material.Grey)
                        font.pixelSize: ThemeTokens.fontXs
                    }

                    Label {
                        text: qsTr("Exchange Rate API")
                        color: ThemeTokens.primary
                        font.pixelSize: ThemeTokens.fontXs
                        font.underline: true

                        MouseArea {
                            anchors.fill: parent
                            cursorShape: Qt.PointingHandCursor
                            onClicked: Qt.openUrlExternally("https://www.exchangerate-api.com")
                            Accessible.name: qsTr("Exchange Rate API provider website")
                        }
                    }
                }
            }

            CurrencyRateEditor {
                Layout.fillWidth: true
                Layout.minimumWidth: 0
                Layout.leftMargin: ThemeTokens.spaceMd
                Layout.rightMargin: ThemeTokens.spaceMd
                Layout.bottomMargin: ThemeTokens.spaceLg
                visible: root.exchangeRatesExpanded
                baseCurrency: root.fetchBaseCurrency
            }

            ColumnLayout {
                Layout.fillWidth: true
                Layout.minimumWidth: 0
                Layout.leftMargin: ThemeTokens.spaceMd
                Layout.rightMargin: ThemeTokens.spaceMd
                spacing: ThemeTokens.spaceSm

                SettingsSectionTitle {
                    titleText: qsTr("Receipts")
                }

                SettingsCard {
                    SettingsRow {
                        visible: settingsViewModel.isMacos
                        label: qsTr("On-device receipt scanning")
                        sublabel: settingsViewModel.receiptOcrAvailable
                            ? qsTr("Ready. Uses Apple Vision on this Mac. Photos stay on this device.")
                            : (settingsViewModel.canInstallMacosOcr
                                ? qsTr("Required for Scan. Installs Apple Vision bindings for this app. Network access is required.")
                                : qsTr("This app build does not include on-device scanning."))
                        showDivider: true

                        BusyIndicator {
                            visible: settingsViewModel.macosOcrInstallBusy
                            running: visible
                            Layout.preferredWidth: 24
                            Layout.preferredHeight: 24
                            Layout.alignment: Qt.AlignVCenter
                        }

                        Button {
                            visible: settingsViewModel.canInstallMacosOcr
                            enabled: !settingsViewModel.macosOcrInstallBusy
                            Layout.alignment: Qt.AlignVCenter
                            Layout.rightMargin: ThemeTokens.spaceMd
                            Layout.topMargin: ThemeTokens.spaceMd
                            Layout.bottomMargin: ThemeTokens.spaceMd
                            flat: true
                            text: settingsViewModel.macosOcrInstallBusy
                                ? qsTr("Installing…")
                                : qsTr("Install")
                            Material.foreground: ThemeTokens.primary
                            Accessible.name: qsTr("Install on-device receipt scanning")
                            onClicked: settingsViewModel.installMacosOcr()
                        }
                    }

                    SettingsRow {
                        label: qsTr("Cloud receipt scanning")
                        sublabel: qsTr(
                            "Off by default. Receipt photos stay on this device. Enabling this "
                            + "does not upload images; a cloud provider is not connected yet.")
                        showDivider: false

                        Switch {
                            Layout.alignment: Qt.AlignVCenter
                            Layout.rightMargin: ThemeTokens.spaceMd
                            Layout.topMargin: ThemeTokens.spaceMd
                            Layout.bottomMargin: ThemeTokens.spaceMd
                            checked: settingsViewModel.cloudReceiptOcrEnabled
                            onToggled: settingsViewModel.setCloudReceiptOcrEnabled(checked)
                            Accessible.name: qsTr("Cloud receipt scanning")
                        }
                    }
                }
            }

            ColumnLayout {
                Layout.fillWidth: true
                Layout.minimumWidth: 0
                Layout.leftMargin: ThemeTokens.spaceMd
                Layout.rightMargin: ThemeTokens.spaceMd
                Layout.bottomMargin: ThemeTokens.spaceLg
                spacing: ThemeTokens.spaceSm

                SettingsSectionTitle {
                    titleText: qsTr("About")
                }

                SettingsCard {
                    SettingsRow {
                        label: qsTr("User manual")
                        sublabel: qsTr(
                            "Open the bundled PDF guide in your system's default viewer")

                        Button {
                            Layout.alignment: Qt.AlignVCenter
                            Layout.rightMargin: ThemeTokens.spaceMd
                            Layout.topMargin: ThemeTokens.spaceMd
                            Layout.bottomMargin: ThemeTokens.spaceMd
                            flat: true
                            text: qsTr("Open ▶")
                            Material.foreground: ThemeTokens.primary
                            Accessible.name: qsTr("Open user manual")
                            onClicked: settingsViewModel.openUserManual()
                        }
                    }

                    SettingsRow {
                        label: qsTr("Methodology")
                        sublabel: qsTr(
                            "How cash shortfalls, date patterns, currencies, and scenarios "
                                + "are calculated")
                        showDivider: false

                        Button {
                            Layout.alignment: Qt.AlignVCenter
                            Layout.rightMargin: ThemeTokens.spaceMd
                            Layout.topMargin: ThemeTokens.spaceMd
                            Layout.bottomMargin: ThemeTokens.spaceMd
                            flat: true
                            text: qsTr("View ▶")
                            Material.foreground: ThemeTokens.primary
                            Accessible.name: qsTr("View methodology")
                            onClicked: root.openMethodology()
                        }
                    }
                }
            }
        }
    }
}
