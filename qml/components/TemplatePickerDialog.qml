import QtQuick
import QtQuick.Controls
import QtQuick.Controls.Material
import QtQuick.Layouts

import ThemeTokens 1.0

CenteredDialog {
    id: root

    standardButtons: Dialog.NoButton
    width: Math.min(parent ? parent.width - ThemeTokens.spaceXl : 360, 520)

    readonly property bool isDark: Material.theme === Material.Dark
    readonly property color panelColor: isDark ? ThemeTokens.cardDark : ThemeTokens.cardLight

    property int currentStep: 0
    property string selectedTemplateId: ""
    property string selectedTemplateName: ""

    function resetState() {
        currentStep = 0
        selectedTemplateId = ""
        selectedTemplateName = ""
        forecastNameField.text = ""
    }

    function selectTemplate(templateData, index) {
        selectedTemplateId = templateData.id
        selectedTemplateName = templateData.name
        templateList.currentIndex = index
    }

    function confirmNameStep() {
        var name = forecastNameField.text.trim()
        if (name === "" || selectedTemplateId === "") {
            return
        }
        var created = planViewModel.createFromTemplate(name, selectedTemplateId)
        if (planViewModel.error === "" && created) {
            root.close()
        }
    }

    onAboutToShow: resetState()
    onClosed: resetState()

    background: Rectangle {
        radius: ThemeTokens.radiusLg
        color: Material.dialogColor
    }

    header: Label {
        text: root.currentStep === 0 ? qsTr("Choose a template") : qsTr("Name your forecast")
        font.pixelSize: ThemeTokens.fontLg
        font.weight: ThemeTokens.weightSemiBold
        topPadding: ThemeTokens.spaceMd
        leftPadding: ThemeTokens.spaceMd
        rightPadding: ThemeTokens.spaceMd
        bottomPadding: ThemeTokens.spaceSm
    }

    contentItem: StackLayout {
        currentIndex: root.currentStep
        width: 440

        ColumnLayout {
            spacing: ThemeTokens.spaceMd
            Layout.fillWidth: true
            Layout.leftMargin: ThemeTokens.spaceMd
            Layout.rightMargin: ThemeTokens.spaceMd
            Layout.topMargin: ThemeTokens.spaceSm
            Layout.bottomMargin: ThemeTokens.spaceSm

            Label {
                Layout.fillWidth: true
                text: qsTr("Start from a pre-built cash-flow template. You can edit every line item after creation.")
                wrapMode: Text.WordWrap
                font.pixelSize: ThemeTokens.fontSm
                color: Material.secondaryTextColor
            }

            ListView {
                id: templateList
                Layout.fillWidth: true
                Layout.preferredHeight: Math.min(contentHeight, 320)
                clip: true
                boundsBehavior: Flickable.StopAtBounds
                focus: true
                activeFocusOnTab: true
                model: planViewModel.availableTemplates
                spacing: ThemeTokens.spaceSm
                keyNavigationEnabled: true
                highlightRangeMode: ListView.ApplyRange
                preferredHighlightBegin: ThemeTokens.spaceSm
                preferredHighlightEnd: height - ThemeTokens.spaceSm

                Keys.onReturnPressed: {
                    if (templateList.currentIndex < 0) {
                        return
                    }
                    var data = planViewModel.availableTemplates[templateList.currentIndex]
                    root.selectTemplate(data, templateList.currentIndex)
                    root.currentStep = 1
                    forecastNameField.text = root.selectedTemplateName
                    forecastNameField.forceActiveFocus()
                }

                delegate: ItemDelegate {
                    id: templateDelegate
                    required property var modelData
                    required property int index

                    width: templateList.width
                    height: templateCard.implicitHeight + topPadding + bottomPadding
                    padding: 0
                    topPadding: ThemeTokens.spaceSm
                    bottomPadding: ThemeTokens.spaceSm
                    leftPadding: ThemeTokens.spaceMd
                    rightPadding: ThemeTokens.spaceMd

                    readonly property bool isSelected: root.selectedTemplateId === modelData.id

                    background: Rectangle {
                        radius: ThemeTokens.radiusMd
                        color: templateDelegate.isSelected
                               ? (root.isDark ? "#334155" : "#E0E7FF")
                               : root.panelColor
                        border.width: templateDelegate.isSelected || templateDelegate.activeFocus ? 2 : 1
                        border.color: templateDelegate.isSelected || templateDelegate.activeFocus
                                      ? ThemeTokens.primary
                                      : Material.dividerColor
                    }

                    contentItem: ColumnLayout {
                        id: templateCard
                        width: parent.width
                        spacing: ThemeTokens.spaceXs

                        Label {
                            Layout.fillWidth: true
                            text: templateDelegate.modelData.name
                            font.pixelSize: ThemeTokens.fontMd
                            font.weight: ThemeTokens.weightSemiBold
                            wrapMode: Text.WordWrap
                        }

                        Label {
                            Layout.fillWidth: true
                            text: templateDelegate.modelData.description
                            font.pixelSize: ThemeTokens.fontSm
                            color: Material.secondaryTextColor
                            wrapMode: Text.WordWrap
                        }
                    }

                    Accessible.name: qsTr("%1 template: %2").arg(templateDelegate.modelData.name)
                                           .arg(templateDelegate.modelData.description)
                    Accessible.role: Accessible.RadioButton
                    Accessible.checked: templateDelegate.isSelected

                    onClicked: root.selectTemplate(templateDelegate.modelData, templateDelegate.index)
                }
            }
        }

        ColumnLayout {
            spacing: ThemeTokens.spaceMd
            Layout.fillWidth: true
            Layout.leftMargin: ThemeTokens.spaceMd
            Layout.rightMargin: ThemeTokens.spaceMd
            Layout.topMargin: ThemeTokens.spaceSm
            Layout.bottomMargin: ThemeTokens.spaceSm

            Label {
                Layout.fillWidth: true
                text: qsTr("Template: %1").arg(root.selectedTemplateName)
                font.pixelSize: ThemeTokens.fontSm
                color: Material.secondaryTextColor
                wrapMode: Text.WordWrap
            }

            TextField {
                id: forecastNameField
                Layout.fillWidth: true
                placeholderText: qsTr("My budget 2026")
                Accessible.name: qsTr("Forecast name")

                Keys.onReturnPressed: root.confirmNameStep()
            }
        }
    }

    footer: DialogButtonBox {
        Button {
            text: qsTr("Cancel")
            flat: true
            DialogButtonBox.buttonRole: DialogButtonBox.RejectRole
            onClicked: root.close()
        }

        Button {
            visible: root.currentStep === 1
            text: qsTr("Back")
            flat: true
            onClicked: {
                root.currentStep = 0
                templateList.forceActiveFocus()
            }
        }

        Button {
            visible: root.currentStep === 0
            text: qsTr("Use template")
            enabled: root.selectedTemplateId !== ""
            Material.background: ThemeTokens.primary
            Material.foreground: "white"
            onClicked: {
                forecastNameField.text = root.selectedTemplateName
                root.currentStep = 1
                forecastNameField.forceActiveFocus()
            }
        }

        Button {
            visible: root.currentStep === 1
            text: qsTr("Create")
            enabled: forecastNameField.text.trim() !== ""
            Material.background: ThemeTokens.primary
            Material.foreground: "white"
            onClicked: root.confirmNameStep()
        }
    }
}
