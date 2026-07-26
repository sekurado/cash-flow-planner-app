import QtQuick
import QtQuick.Controls.Material

import ThemeTokens 1.0

Item {
    id: root

    property var model: []
    property var accessibleNames: []
    property int currentIndex: 0

    signal activated(int index)

    readonly property bool isDark: Material.theme === Material.Dark
    readonly property int tabCount: Math.max(model.length, 1)

    implicitWidth: width
    implicitHeight: height

    width: 260
    height: 36

    Rectangle {
        id: tabContainer
        anchors.fill: parent
        radius: ThemeTokens.radiusFull
        color: root.isDark ? "#334155" : "#E0E7FF"

        Rectangle {
            id: pillIndicator
            y: 2
            height: parent.height - 4
            width: parent.width / root.tabCount - 4
            radius: ThemeTokens.radiusFull
            color: ThemeTokens.primary
            x: 2 + root.currentIndex * (parent.width / root.tabCount)

            Behavior on x {
                NumberAnimation {
                    duration: 160
                    easing.type: Easing.OutCubic
                }
            }
        }

        Row {
            anchors.fill: parent

            Repeater {
                model: root.model

                Item {
                    required property int index
                    required property var modelData

                    width: tabContainer.width / root.tabCount
                    height: tabContainer.height

                    Text {
                        anchors.centerIn: parent
                        text: parent.modelData
                        font.pixelSize: ThemeTokens.fontSm
                        font.weight: root.currentIndex === parent.index
                                       ? ThemeTokens.weightSemiBold
                                       : ThemeTokens.weightRegular
                        color: root.currentIndex === parent.index
                               ? "white"
                               : Qt.rgba(
                                     ThemeTokens.primary.r,
                                     ThemeTokens.primary.g,
                                     ThemeTokens.primary.b,
                                     0.6)
                    }

                    MouseArea {
                        anchors.fill: parent
                        Accessible.name: root.accessibleNames.length > parent.index
                                         ? root.accessibleNames[parent.index]
                                         : parent.modelData
                        onClicked: {
                            if (root.currentIndex !== parent.index) {
                                root.currentIndex = parent.index
                                root.activated(parent.index)
                            }
                        }
                    }
                }
            }
        }
    }
}
