import QtQuick
import QtQuick.Controls
import QtQuick.Controls.Material
import QtQuick.Layouts
import Qt5Compat.GraphicalEffects

import ThemeTokens 1.0

ColumnLayout {
    id: root

    property string caption: ""
    property string placeholderText: ""
    property string text: ""
    property bool required: false
    property var suggestionModel: null

    signal searchRequested(string prefix)
    signal suggestionSelected(string labelId, string label)

    property bool _syncing: false

    readonly property bool isDark: Material.theme === Material.Dark
    readonly property color cardColor: isDark ? ThemeTokens.cardDark : ThemeTokens.cardLight

    Layout.fillWidth: true
    spacing: ThemeTokens.spaceXs

    function popupX() {
        if (!suggestionPopup.parent) {
            return 0
        }
        return textField.mapToItem(suggestionPopup.parent, 0, 0).x
    }

    function popupY() {
        if (!suggestionPopup.parent) {
            return 0
        }
        var mapped = textField.mapToItem(suggestionPopup.parent, 0, textField.height)
        return mapped.y + 4
    }

    function setTextSilently(value) {
        _syncing = true
        textField.text = value
        root.text = value
        _syncing = false
    }

    Label {
        Layout.fillWidth: true
        Layout.minimumWidth: 0
        text: root.caption + (root.required ? "" : " (" + qsTr("optional") + ")")
        font.pixelSize: ThemeTokens.fontSm
        font.weight: ThemeTokens.weightMedium
        color: ThemeTokens.primary
    }

    TextField {
        id: textField
        Layout.fillWidth: true
        Layout.minimumWidth: 0
        placeholderText: root.placeholderText
        Accessible.name: root.caption
        selectByMouse: true

        onTextChanged: {
            if (root._syncing) {
                return
            }
            root.text = text
            root.searchRequested(text)
            if (textField.activeFocus && root.suggestionModel && root.suggestionModel.count > 0) {
                suggestionPopup.open()
            } else if (root.suggestionModel && root.suggestionModel.count === 0) {
                suggestionPopup.close()
            }
        }

        onActiveFocusChanged: {
            if (!activeFocus) {
                return
            }
            root.searchRequested(text)
            if (root.suggestionModel && root.suggestionModel.count > 0) {
                suggestionPopup.open()
            }
        }
    }

    Popup {
        id: suggestionPopup
        parent: Overlay.overlay
        modal: false
        focus: false
        closePolicy: Popup.CloseOnEscape | Popup.CloseOnPressOutside
        padding: ThemeTokens.spaceXs
        width: Math.max(textField.width, 220)
        implicitHeight: suggestionList.contentHeight + 2 * padding
        x: root.popupX()
        y: root.popupY()

        background: Rectangle {
            color: root.cardColor
            radius: ThemeTokens.radiusMd
            layer.enabled: true
            layer.effect: DropShadow {
                radius: 8
                samples: 17
                color: "#18000000"
                verticalOffset: 2
            }
        }

        contentItem: ListView {
            id: suggestionList
            clip: true
            implicitHeight: Math.min(contentHeight, 240)
            boundsBehavior: Flickable.StopAtBounds
            model: root.suggestionModel

            delegate: ItemDelegate {
                required property int index
                required property string labelId
                required property string label

                width: suggestionList.width
                text: label
                padding: ThemeTokens.spaceSm

                onClicked: {
                    root.setTextSilently(label)
                    root.suggestionSelected(labelId, label)
                    suggestionPopup.close()
                }
            }
        }
    }

    Connections {
        target: root.suggestionModel
        ignoreUnknownSignals: true

        function onCountChanged() {
            if (!textField.activeFocus) {
                return
            }
            if (root.suggestionModel && root.suggestionModel.count > 0) {
                suggestionPopup.open()
            } else {
                suggestionPopup.close()
            }
        }
    }
}
