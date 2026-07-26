import QtQuick
import QtQuick.Controls
import QtQuick.Controls.Material
import QtQuick.Layouts

import ThemeTokens 1.0

Item {
    id: root

    property bool active: false

    readonly property string planId: planViewModel.selectedPlan ? planViewModel.selectedPlan.id : ""
    readonly property bool isDark: Material.theme === Material.Dark
    readonly property color cardColor: isDark ? ThemeTokens.cardDark : ThemeTokens.cardLight
    readonly property color mutedTextColor: isDark ? "#94A3B8" : "#64748B"

    function formatTimestamp(isoString) {
        var parsed = new Date(isoString)
        if (isNaN(parsed.getTime())) {
            return isoString
        }
        return parsed.toLocaleString(Qt.locale(), Locale.ShortFormat)
    }

    function reloadHistory() {
        if (root.planId !== "") {
            auditLogViewModel.loadForPlan(root.planId)
        }
    }

    Rectangle {
        anchors.fill: parent
        color: root.isDark ? ThemeTokens.surfaceDark : ThemeTokens.surfaceLight
    }

    ColumnLayout {
        anchors.fill: parent
        anchors.margins: ThemeTokens.spaceMd
        spacing: ThemeTokens.spaceMd

        Label {
            Layout.fillWidth: true
            text: qsTr("Forecast history")
            font.pixelSize: ThemeTokens.fontMd
            font.weight: ThemeTokens.weightSemiBold
            color: Material.foreground
        }

        Label {
            Layout.fillWidth: true
            visible: root.planId === ""
            text: qsTr("Select a forecast to view its change history.")
            wrapMode: Text.WordWrap
            color: root.mutedTextColor
            font.pixelSize: ThemeTokens.fontSm
        }

        Label {
            Layout.fillWidth: true
            visible: root.planId !== "" && auditLogViewModel.entries.length === 0
            text: qsTr("No changes recorded yet.")
            wrapMode: Text.WordWrap
            color: root.mutedTextColor
            font.pixelSize: ThemeTokens.fontSm
        }

        ListView {
            id: historyList
            Layout.fillWidth: true
            Layout.fillHeight: true
            visible: auditLogViewModel.entries.length > 0
            clip: true
            spacing: ThemeTokens.spaceSm
            model: auditLogViewModel.entries

            delegate: Rectangle {
                required property int index
                required property string id
                required property string summary
                required property string timestamp

                width: historyList.width
                height: historyContent.implicitHeight + ThemeTokens.spaceMd * 2
                radius: ThemeTokens.radiusLg
                color: root.cardColor

                ColumnLayout {
                    id: historyContent
                    anchors.fill: parent
                    anchors.margins: ThemeTokens.spaceMd
                    spacing: ThemeTokens.spaceXs

                    Label {
                        Layout.fillWidth: true
                        text: root.formatTimestamp(timestamp)
                        font.pixelSize: ThemeTokens.fontXs
                        color: root.mutedTextColor
                    }

                    Label {
                        Layout.fillWidth: true
                        text: summary
                        wrapMode: Text.WordWrap
                        font.pixelSize: ThemeTokens.fontSm
                        color: Material.foreground
                    }
                }
            }
        }
    }

    onActiveChanged: {
        if (root.active) {
            root.reloadHistory()
        }
    }

    Connections {
        target: planViewModel
        function onSelectedPlanChanged() {
            root.reloadHistory()
        }
    }

    Connections {
        target: entriesViewModel
        function onEntryCreated() {
            root.reloadHistory()
        }
        function onEntryUpdated() {
            root.reloadHistory()
        }
        function onEntryDeleted() {
            root.reloadHistory()
        }
    }

    Component.onCompleted: root.reloadHistory()
}
