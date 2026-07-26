import QtQuick
import QtQuick.Controls
import QtQuick.Controls.Material
import QtQuick.Layouts

import ThemeTokens 1.0

Rectangle {
    id: root

    readonly property var result: simulationViewModel.result
    readonly property bool hasDeficit: result !== null
                                     && result !== undefined
                                     && result.first_deficit_date !== null
                                     && result.first_deficit_date !== undefined
    readonly property bool isDark: Material.theme === Material.Dark
    readonly property string uiLanguage: settingsViewModel ? settingsViewModel.language : "en"

    property bool userDismissed: false

    visible: root.hasDeficit && !root.userDismissed
    opacity: visible ? 1.0 : 0.0
    radius: ThemeTokens.radiusLg
    color: root.isDark ? ThemeTokens.deficitAmberBgDark : ThemeTokens.deficitAmberBg
    clip: true

    implicitHeight: visible ? bannerRow.implicitHeight + ThemeTokens.spaceMd * 2 : 0
    Layout.preferredHeight: implicitHeight

    Behavior on opacity {
        NumberAnimation {
            duration: 200
        }
    }

    Accessible.role: Accessible.AlertMessage
    Accessible.name: headlineLabel.text + ". " + subtitleLabel.text

    function formatDeficitDate(isoDate) {
        if (!isoDate) {
            return ""
        }
        var parsed = new Date(isoDate)
        if (isNaN(parsed.getTime())) {
            return isoDate
        }
        var monthSources = [
            "Jan", "Feb", "Mar", "Apr", "May", "Jun",
            "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"
        ]
        var monthIndex = parsed.getMonth()
        var monthName = qsTranslate("MonthlyTableView", monthSources[monthIndex])
        return parsed.getDate() + " " + monthName + " " + parsed.getFullYear()
    }

    Rectangle {
        width: 4
        anchors.top: parent.top
        anchors.bottom: parent.bottom
        anchors.left: parent.left
        color: ThemeTokens.accent
    }

    RowLayout {
        id: bannerRow
        anchors.fill: parent
        anchors.leftMargin: ThemeTokens.spaceMd
        anchors.rightMargin: ThemeTokens.spaceMd
        anchors.topMargin: ThemeTokens.spaceMd
        anchors.bottomMargin: ThemeTokens.spaceMd
        spacing: ThemeTokens.spaceSm

        Image {
            source: "qrc:/icons/warning.svg"
            Layout.preferredWidth: 20
            Layout.preferredHeight: 20
            Layout.alignment: Qt.AlignTop
            fillMode: Image.PreserveAspectFit
            Accessible.name: qsTr("Cash shortfall warning")
        }

        ColumnLayout {
            Layout.fillWidth: true
            spacing: 2

            Label {
                id: headlineLabel
                Layout.fillWidth: true
                readonly property string _uiLanguage: root.uiLanguage
                text: qsTr("Cash shortfall detected")
                font.pixelSize: ThemeTokens.fontMd
                font.weight: ThemeTokens.weightSemiBold
                color: Material.foreground
                wrapMode: Text.WordWrap
            }

            Label {
                id: subtitleLabel
                Layout.fillWidth: true
                readonly property string _uiLanguage: root.uiLanguage
                text: qsTr("First shortfall on %1")
                        .arg(root.formatDeficitDate(result ? result.first_deficit_date : ""))
                font.pixelSize: ThemeTokens.fontSm
                color: Material.secondaryTextColor
                wrapMode: Text.WordWrap
            }
        }

        ToolButton {
            flat: true
            icon.name: "window-close"
            Material.foreground: ThemeTokens.accent
            Accessible.name: qsTr("Dismiss cash shortfall alert")
            onClicked: root.userDismissed = true
        }
    }

    Connections {
        target: simulationViewModel
        function onResultChanged() {
            root.userDismissed = false
        }
    }
}
