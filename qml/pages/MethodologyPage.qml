import QtQuick
import QtQuick.Controls
import QtQuick.Controls.Material
import QtQuick.Layouts
import Qt5Compat.GraphicalEffects

import ThemeTokens 1.0

Page {
    id: root

    objectName: "methodologyPage"
    title: qsTr("Methodology")

    readonly property bool isDark: Material.theme === Material.Dark
    readonly property color cardColor: isDark ? ThemeTokens.cardDark : ThemeTokens.cardLight

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
                text: qsTr("Methodology")
                font.pixelSize: ThemeTokens.fontLg
                elide: Text.ElideRight
            }
        }
    }

    component SectionTitle: Label {
        required property string titleText

        text: titleText.toUpperCase()
        font.pixelSize: ThemeTokens.fontXs
        font.weight: ThemeTokens.weightSemiBold
        color: ThemeTokens.primary
    }

    component ContentCard: Rectangle {
        id: contentCard

        property string sectionHeading: ""
        property string bodyText: ""

        Layout.fillWidth: true
        Layout.minimumWidth: 0
        implicitHeight: cardColumn.implicitHeight + ThemeTokens.spaceMd * 2
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
            anchors.left: parent.left
            anchors.right: parent.right
            anchors.top: parent.top
            anchors.margins: ThemeTokens.spaceMd
            spacing: ThemeTokens.spaceSm

            Label {
                width: parent.width
                wrapMode: Text.WordWrap
                font.pixelSize: ThemeTokens.fontMd
                font.weight: ThemeTokens.weightSemiBold
                text: contentCard.sectionHeading
            }

            Label {
                width: parent.width
                wrapMode: Text.WordWrap
                font.pixelSize: ThemeTokens.fontSm
                color: Material.foreground
                text: contentCard.bodyText
            }
        }
    }

    component PatternExample: RowLayout {
        required property string pattern
        required property string description

        Layout.fillWidth: true
        spacing: ThemeTokens.spaceSm

        Rectangle {
            Layout.preferredWidth: patternLabel.implicitWidth + ThemeTokens.spaceSm * 2
            Layout.minimumWidth: 72
            implicitHeight: patternLabel.implicitHeight + ThemeTokens.spaceXs * 2
            radius: ThemeTokens.radiusSm
            color: root.isDark ? ThemeTokens.surfaceDark : ThemeTokens.surfaceLight

            Label {
                id: patternLabel
                anchors.centerIn: parent
                text: pattern
                font.family: ThemeTokens.fontMono
                font.pixelSize: ThemeTokens.fontSm
            }
        }

        Label {
            Layout.fillWidth: true
            text: description
            font.pixelSize: ThemeTokens.fontSm
            color: Material.secondaryTextColor
            wrapMode: Text.WordWrap
        }
    }

    Flickable {
        id: methodologyScroll
        anchors.fill: parent
        clip: true
        boundsBehavior: Flickable.StopAtBounds
        contentWidth: methodologyContent.width
        contentHeight: methodologyContent.implicitHeight

        readonly property int verticalScrollBarOverlap: contentHeight > height
            ? verticalScrollBar.implicitWidth
            : 0

        ScrollBar.vertical: ScrollBar {
            id: verticalScrollBar
            policy: ScrollBar.AsNeeded
        }

        ColumnLayout {
            id: methodologyContent
            width: methodologyScroll.width - methodologyScroll.verticalScrollBarOverlap
            spacing: ThemeTokens.spaceLg

            Label {
                Layout.fillWidth: true
                Layout.leftMargin: ThemeTokens.spaceMd
                Layout.rightMargin: ThemeTokens.spaceMd
                Layout.topMargin: ThemeTokens.spaceMd
                wrapMode: Text.WordWrap
                font.pixelSize: ThemeTokens.fontSm
                color: Material.secondaryTextColor
                text: methodologyViewModel.intro
            }

            Repeater {
                model: methodologyViewModel.groups

                delegate: ColumnLayout {
                    required property int index
                    required property string title
                    required property var sections
                    required property bool hasPatternExamples

                    Layout.fillWidth: true
                    Layout.minimumWidth: 0
                    Layout.leftMargin: ThemeTokens.spaceMd
                    Layout.rightMargin: ThemeTokens.spaceMd
                    Layout.bottomMargin: index === methodologyViewModel.groups.length - 1
                        ? ThemeTokens.spaceLg
                        : 0
                    spacing: ThemeTokens.spaceSm

                    SectionTitle {
                        titleText: title
                    }

                    Repeater {
                        model: sections

                        delegate: ContentCard {
                            required property string heading
                            required property string body

                            sectionHeading: heading
                            bodyText: body
                        }
                    }

                    Rectangle {
                        visible: hasPatternExamples
                        Layout.fillWidth: true
                        implicitHeight: patternExamplesColumn.implicitHeight + ThemeTokens.spaceMd * 2
                        radius: ThemeTokens.radiusLg
                        color: root.cardColor
                        layer.enabled: true
                        layer.effect: DropShadow {
                            radius: 8
                            samples: 17
                            color: "#18000000"
                            verticalOffset: 2
                        }

                        ColumnLayout {
                            id: patternExamplesColumn
                            anchors.left: parent.left
                            anchors.right: parent.right
                            anchors.top: parent.top
                            anchors.margins: ThemeTokens.spaceMd
                            spacing: ThemeTokens.spaceSm

                            Label {
                                Layout.fillWidth: true
                                text: methodologyViewModel.patternExamplesHeading
                                font.pixelSize: ThemeTokens.fontMd
                                font.weight: ThemeTokens.weightSemiBold
                            }

                            Repeater {
                                model: methodologyViewModel.patternExamples

                                delegate: PatternExample {}
                            }
                        }
                    }
                }
            }
        }
    }
}
