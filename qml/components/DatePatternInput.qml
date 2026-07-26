import QtQuick
import QtQuick.Controls
import QtQuick.Controls.Material

import ThemeTokens 1.0

Column {
    id: root

    spacing: 4

    property alias text: patternField.text
    property bool valid: text.length > 0 && entriesViewModel.validatePattern(text)
    readonly property string uiLanguage: settingsViewModel ? settingsViewModel.language : "en"

    width: parent ? parent.width : implicitWidth

    TextField {
        id: patternField
        width: parent.width
        placeholderText: qsTr("e.g. 10.. for monthly, ... for daily")
        Accessible.name: qsTr("Date pattern")
        selectByMouse: true

        ToolTip.visible: activeFocus
        ToolTip.text: qsTr(
            "Pattern formats:\n"
                + "• ... — every day\n"
                + "• 10.. — monthly on the 10th\n"
                + "• 15.03. — yearly on 15 March\n"
                + "• 2026-06-15 — one-time on a date")
        ToolTip.delay: 500
    }

    Label {
        width: parent.width
        visible: root.valid
        readonly property string _uiLanguage: root.uiLanguage
        text: entriesViewModel.describePattern(patternField.text)
        color: ThemeTokens.incomeGreen
        font.pixelSize: ThemeTokens.fontSm
        wrapMode: Text.WordWrap
    }

    Label {
        width: parent.width
        visible: patternField.text.length > 0 && !root.valid
        text: qsTr("Invalid date pattern")
        color: ThemeTokens.expenseRed
        font.pixelSize: ThemeTokens.fontSm
        wrapMode: Text.WordWrap
    }
}
