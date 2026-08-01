import QtQuick
import QtQuick.Controls
import QtQuick.Controls.Material
import QtQuick.Layouts

import ThemeTokens 1.0
import "pages"

ApplicationWindow {
    id: root

    visible: true
    width: 960
    height: 640
    title: qsTr("Cash Flow Planner")
    Material.theme: settingsViewModel ? (settingsViewModel.darkMode ? Material.Dark : Material.Light) : Material.Light
    Material.primary: ThemeTokens.primary
    Material.accent: ThemeTokens.accent
    Material.roundedScale: Material.FullScale

    readonly property bool isDark: Material.theme === Material.Dark
    readonly property color toolbarColor: isDark ? ThemeTokens.primaryDark : ThemeTokens.primary

    property int mainSection: 0

    function openSettings() {
        if (mainSection !== 0) {
            mainSection = 0
            sectionTabBar.currentIndex = 0
        }
        var existing = stackView.find(function (item) {
            return item.objectName === "settingsPage"
        })
        if (existing) {
            stackView.pop(existing)
        } else {
            stackView.push(settingsPageComponent)
        }
    }

    readonly property string activeError: {
        if (planViewModel && planViewModel.error !== "") {
            return planViewModel.error
        }
        if (entriesViewModel && entriesViewModel.error !== "") {
            return entriesViewModel.error
        }
        if (ratesViewModel && ratesViewModel.error !== "") {
            return ratesViewModel.error
        }
        if (simulationViewModel && simulationViewModel.error !== "") {
            return simulationViewModel.error
        }
        if (auditLogViewModel && auditLogViewModel.error !== "") {
            return auditLogViewModel.error
        }
        if (settingsViewModel && settingsViewModel.error !== "") {
            return settingsViewModel.error
        }
        if (recordedExpensesViewModel && recordedExpensesViewModel.error !== "") {
            return recordedExpensesViewModel.error
        }
        return ""
    }

    header: ToolBar {
        height: 56
        Material.background: root.toolbarColor
        Material.elevation: 4

        RowLayout {
            anchors.fill: parent
            anchors.leftMargin: ThemeTokens.spaceMd
            anchors.rightMargin: ThemeTokens.spaceSm
            spacing: ThemeTokens.spaceMd

            Label {
                Layout.fillWidth: true
                text: qsTr("Cash Flow Planner")
                font.pixelSize: ThemeTokens.fontLg
                font.weight: ThemeTokens.weightSemiBold
                color: "white"
                elide: Text.ElideRight
            }

            ToolButton {
                icon.source: "qrc:/icons/settings.svg"
                icon.color: "white"
                Accessible.name: qsTr("Settings")
                onClicked: root.openSettings()
            }
        }
    }

    Item {
        anchors.fill: parent
        anchors.bottomMargin: sectionTabBar.visible ? sectionTabBar.height : 0

        StackView {
            id: stackView
            anchors.fill: parent
            visible: root.mainSection === 0
            initialItem: planListPageComponent
        }

        RecordedExpensesPage {
            anchors.fill: parent
            visible: root.mainSection === 1
        }
    }

    footer: TabBar {
        id: sectionTabBar
        currentIndex: root.mainSection

        onCurrentIndexChanged: {
            if (currentIndex !== root.mainSection) {
                root.mainSection = currentIndex
            }
        }

        TabButton {
            text: qsTr("Forecasts")
            Accessible.name: qsTr("Forecasts")
        }

        TabButton {
            text: qsTr("Spending")
            Accessible.name: qsTr("Spending")
        }
    }

    Component {
        id: planListPageComponent
        PlanListPage {}
    }

    Component {
        id: settingsPageComponent
        SettingsPage {}
    }

    Rectangle {
        id: errorBar
        visible: root.activeError !== "" || opacity > 0
        anchors.horizontalCenter: parent.horizontalCenter
        anchors.bottom: parent.bottom
        anchors.bottomMargin: ThemeTokens.spaceLg
        width: Math.min(parent.width - ThemeTokens.spaceLg * 2, 520)
        radius: ThemeTokens.radiusMd
        color: ThemeTokens.cardDark
        z: 100

        implicitHeight: errorRow.implicitHeight + ThemeTokens.spaceMd

        states: [
            State {
                name: "shown"
                when: root.activeError !== ""
                PropertyChanges {
                    target: errorBar
                    opacity: 1
                    anchors.bottomMargin: ThemeTokens.spaceLg
                }
            },
            State {
                name: "hidden"
                when: root.activeError === ""
                PropertyChanges {
                    target: errorBar
                    opacity: 0
                    anchors.bottomMargin: ThemeTokens.spaceLg - 16
                }
            }
        ]

        transitions: Transition {
            NumberAnimation {
                properties: "opacity,anchors.bottomMargin"
                duration: 200
                easing.type: Easing.OutCubic
            }
        }

        RowLayout {
            id: errorRow
            anchors.fill: parent
            anchors.margins: ThemeTokens.spaceSm
            spacing: ThemeTokens.spaceSm

            Label {
                Layout.fillWidth: true
                text: root.activeError
                color: "white"
                font.pixelSize: ThemeTokens.fontSm
                wrapMode: Text.WordWrap
            }

            ToolButton {
                icon.name: "window-close"
                icon.color: "white"
                Accessible.name: qsTr("Dismiss error")
                onClicked: {
                    if (planViewModel && planViewModel.error !== "") {
                        planViewModel.clearError()
                    } else if (entriesViewModel && entriesViewModel.error !== "") {
                        entriesViewModel.clearError()
                    } else if (ratesViewModel && ratesViewModel.error !== "") {
                        ratesViewModel.clearError()
                    } else if (simulationViewModel && simulationViewModel.error !== "") {
                        simulationViewModel.clearError()
                    } else if (auditLogViewModel && auditLogViewModel.error !== "") {
                        auditLogViewModel.clearError()
                    } else if (settingsViewModel && settingsViewModel.error !== "") {
                        settingsViewModel.clearError()
                    } else if (recordedExpensesViewModel && recordedExpensesViewModel.error !== "") {
                        recordedExpensesViewModel.clearError()
                    }
                }
            }
        }
    }
}
