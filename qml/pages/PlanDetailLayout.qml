import QtQuick
import QtQuick.Controls
import QtQuick.Controls.Material
import QtQuick.Layouts

import ThemeTokens 1.0

Page {
    id: root

    readonly property var plan: planViewModel.selectedPlan
    readonly property bool isDark: Material.theme === Material.Dark
    readonly property color toolbarColor: isDark ? ThemeTokens.primaryDark : ThemeTokens.primary

    property int currentIndex: 0

    readonly property var tabLabels: [qsTr("Cash flows"), qsTr("Projection"), qsTr("Change history")]
    readonly property int tabCount: tabLabels.length

    title: plan ? plan.name : qsTr("Forecast")

    background: Rectangle {
        color: Material.background
    }

    header: ColumnLayout {
        spacing: 0

        ToolBar {
            Layout.fillWidth: true
            height: 56
            Material.background: root.toolbarColor
            Material.elevation: 4

            RowLayout {
                anchors.fill: parent
                anchors.leftMargin: ThemeTokens.spaceXs
                anchors.rightMargin: ThemeTokens.spaceSm
                spacing: ThemeTokens.spaceXs

                ToolButton {
                    icon.name: "go-previous"
                    icon.color: "white"
                    Accessible.name: qsTr("Back to forecasts")
                    onClicked: {
                        if (root.StackView.view) {
                            root.StackView.view.pop()
                        }
                    }
                }

                Label {
                    Layout.fillWidth: true
                    text: root.title
                    font.pixelSize: ThemeTokens.fontLg
                    font.weight: ThemeTokens.weightSemiBold
                    color: "white"
                    elide: Text.ElideRight
                }
            }
        }

        Item {
            Layout.fillWidth: true
            Layout.preferredHeight: 56
            Layout.leftMargin: ThemeTokens.spaceMd
            Layout.rightMargin: ThemeTokens.spaceMd
            Layout.bottomMargin: ThemeTokens.spaceSm

            Rectangle {
                id: tabContainer
                anchors.horizontalCenter: parent.horizontalCenter
                width: Math.min(parent.width, 480)
                height: 40
                radius: ThemeTokens.radiusFull
                color: root.isDark ? ThemeTokens.cardDark : "#E0E7FF"

                readonly property real tabWidth: width / root.tabCount

                Rectangle {
                    id: pillIndicator
                    y: 4
                    height: parent.height - 8
                    width: tabContainer.tabWidth - 4
                    radius: ThemeTokens.radiusFull
                    color: root.isDark ? ThemeTokens.surfaceDark : "white"
                    x: 4 + root.currentIndex * tabContainer.tabWidth

                    Behavior on x {
                        NumberAnimation {
                            duration: 180
                            easing.type: Easing.OutCubic
                        }
                    }
                }

                Row {
                    anchors.fill: parent

                    Repeater {
                        model: root.tabLabels

                        Item {
                            required property int index
                            required property string modelData

                            width: tabContainer.tabWidth
                            height: tabContainer.height

                            Text {
                                anchors.centerIn: parent
                                text: parent.modelData
                                font.pixelSize: ThemeTokens.fontSm
                                font.weight: root.currentIndex === parent.index
                                               ? ThemeTokens.weightSemiBold
                                               : ThemeTokens.weightRegular
                                color: root.currentIndex === parent.index
                                       ? ThemeTokens.primary
                                       : (root.isDark ? "#94A3B8" : "#64748B")

                                Behavior on color {
                                    ColorAnimation {
                                        duration: 180
                                    }
                                }
                            }

                            MouseArea {
                                anchors.fill: parent
                                Accessible.name: parent.modelData + " " + qsTr("tab")
                                onClicked: root.currentIndex = parent.index
                            }
                        }
                    }
                }
            }
        }
    }

    contentItem: StackLayout {
        currentIndex: root.currentIndex

        EntriesPage {
            Layout.fillWidth: true
            Layout.fillHeight: true
        }

        SimulationPage {
            Layout.fillWidth: true
            Layout.fillHeight: true
        }

        ChangeHistoryPage {
            Layout.fillWidth: true
            Layout.fillHeight: true
            active: root.currentIndex === 2
        }
    }

    Connections {
        target: planViewModel
        function onSelectedPlanChanged() {
            if (planViewModel.selectedPlan) {
                simulationViewModel.setActivePlan(
                    planViewModel.selectedPlan.id,
                    planViewModel.selectedPlan.base_currency)
            }
        }
    }

    Component.onCompleted: {
        if (planViewModel.selectedPlan) {
            simulationViewModel.setActivePlan(
                planViewModel.selectedPlan.id,
                planViewModel.selectedPlan.base_currency)
        }
        simulationViewModel.refreshDisplayCurrencies()
    }
}
