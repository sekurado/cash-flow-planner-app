import QtQuick
import QtQuick.Controls
import QtQuick.Controls.Material
import QtQuick.Dialogs
import QtQuick.Layouts

import ThemeTokens 1.0

CenteredDialog {
    id: root

    standardButtons: Dialog.NoButton
    width: Math.min(parent ? parent.width - ThemeTokens.spaceXl : 360, 560)

    readonly property bool isDark: Material.theme === Material.Dark
    readonly property color panelColor: isDark ? ThemeTokens.cardDark : ThemeTokens.cardLight

    property string selectedPath: ""
    property int currentStep: 0

    function localFilePath(fileUrl) {
        var path = fileUrl.toString()
        if (!path.startsWith("file://")) {
            return path
        }
        path = decodeURIComponent(path.slice(7))
        if (Qt.platform.os === "windows" && path.length > 0 && path.charAt(0) === "/") {
            path = path.slice(1)
        }
        return path
    }

    function resetState() {
        currentStep = 0
        selectedPath = ""
        planImportViewModel.clearError()
    }

    function formatRate(fromCurrency, rate) {
        return qsTr("%1 → USD: %2").arg(fromCurrency).arg(Number(rate).toLocaleString(Qt.locale(), "f", 4))
    }

    function startImport() {
        if (selectedPath === "" || planImportViewModel.isImporting) {
            return
        }
        planImportViewModel.importFile(selectedPath)
    }

    onAboutToShow: resetState()
    onClosed: resetState()

    background: Rectangle {
        radius: ThemeTokens.radiusLg
        color: Material.dialogColor
    }

    header: Label {
        text: qsTr("Import forecast")
        font.pixelSize: ThemeTokens.fontLg
        font.weight: ThemeTokens.weightSemiBold
        topPadding: ThemeTokens.spaceMd
        leftPadding: ThemeTokens.spaceMd
        rightPadding: ThemeTokens.spaceMd
        bottomPadding: ThemeTokens.spaceSm
    }

    FileDialog {
        id: fileDialog
        title: qsTr("Select forecast file")
        nameFilters: [qsTr("Forecast files (*.ftplan)")]
        onAccepted: {
            root.selectedPath = root.localFilePath(selectedFile)
            planImportViewModel.inspectFile(root.selectedPath)
        }
    }

    Connections {
        target: planImportViewModel

        function onPreviewReady() {
            if (root.selectedPath !== "") {
                root.currentStep = 1
            }
        }

        function onImportCompleted(planId) {
            planViewModel.loadPlans()
            root.close()
            importSuccessSnackbar.open()
        }
    }

    contentItem: ColumnLayout {
        spacing: ThemeTokens.spaceMd
        Layout.leftMargin: ThemeTokens.spaceMd
        Layout.rightMargin: ThemeTokens.spaceMd
        Layout.topMargin: ThemeTokens.spaceSm
        Layout.bottomMargin: ThemeTokens.spaceSm

        StackLayout {
            id: stepStack
            Layout.fillWidth: true
            currentIndex: root.currentStep

            // Step 1 — file selection
            ColumnLayout {
                spacing: ThemeTokens.spaceMd

                Label {
                    Layout.fillWidth: true
                    text: qsTr("Choose a .ftplan file to import as a new forecast.")
                    wrapMode: Text.WordWrap
                }

                Button {
                    text: qsTr("Browse…")
                    onClicked: fileDialog.open()
                }

                Label {
                    Layout.fillWidth: true
                    visible: root.selectedPath !== ""
                    text: root.selectedPath
                    color: Material.secondaryTextColor
                    wrapMode: Text.WordWrap
                    font.pixelSize: ThemeTokens.fontSm
                }
            }

            // Step 2 — preview & confirm
            ColumnLayout {
                spacing: ThemeTokens.spaceMd

                Label {
                    Layout.fillWidth: true
                    text: qsTr("Review the forecast summary below, resolve any rate conflicts, then import.")
                    wrapMode: Text.WordWrap
                }

                Rectangle {
                    Layout.fillWidth: true
                    radius: ThemeTokens.radiusMd
                    color: root.panelColor
                    implicitHeight: previewColumn.implicitHeight + ThemeTokens.spaceMd * 2

                    ColumnLayout {
                        id: previewColumn
                        anchors.left: parent.left
                        anchors.right: parent.right
                        anchors.top: parent.top
                        anchors.margins: ThemeTokens.spaceMd
                        spacing: ThemeTokens.spaceSm

                        PreviewRow {
                            label: qsTr("Forecast name")
                            value: planImportViewModel.previewName
                        }

                        PreviewRow {
                            label: qsTr("Cash flows")
                            value: planImportViewModel.previewEntryCount.toString()
                        }

                        PreviewRow {
                            label: qsTr("Currencies")
                            value: planImportViewModel.previewCurrencies.join(", ")
                        }
                    }
                }

                Label {
                    Layout.fillWidth: true
                    visible: planImportViewModel.rateAdditions.length > 0
                    text: qsTr("New rates")
                    font.weight: ThemeTokens.weightSemiBold
                }

                Repeater {
                    model: planImportViewModel.rateAdditions

                    Label {
                        required property string fromCurrency
                        required property real rate

                        Layout.fillWidth: true
                        text: root.formatRate(fromCurrency, rate)
                        color: Material.secondaryTextColor
                        font.pixelSize: ThemeTokens.fontSm
                    }
                }

                ColumnLayout {
                    Layout.fillWidth: true
                    visible: planImportViewModel.hasRateConflicts
                    spacing: ThemeTokens.spaceSm

                    RowLayout {
                        Layout.fillWidth: true
                        spacing: ThemeTokens.spaceSm

                        Label {
                            Layout.fillWidth: true
                            text: qsTr("Rate conflicts")
                            font.weight: ThemeTokens.weightSemiBold
                        }

                        Button {
                            flat: true
                            text: qsTr("Keep all mine")
                            onClicked: planImportViewModel.setAllRateResolutions("keep")
                        }

                        Button {
                            flat: true
                            text: qsTr("Use all from file")
                            onClicked: planImportViewModel.setAllRateResolutions("use_file")
                        }
                    }

                    Repeater {
                        model: planImportViewModel.rateConflicts

                        RateConflictRow {
                            required property string fromCurrency
                            required property real localRate
                            required property real fileRate
                            required property string resolution

                            Layout.fillWidth: true
                            currency: fromCurrency
                            localRateValue: localRate
                            fileRateValue: fileRate
                            useFileRate: resolution === "use_file"
                            onResolutionChoiceChanged: function(useFile) {
                                planImportViewModel.setRateResolution(
                                            fromCurrency,
                                            useFile ? "use_file" : "keep")
                            }
                        }
                    }
                }

                Button {
                    Layout.alignment: Qt.AlignLeft
                    text: planImportViewModel.isImporting ? qsTr("Importing…") : qsTr("Import")
                    enabled: !planImportViewModel.isImporting && root.selectedPath !== ""
                    Material.background: ThemeTokens.primary
                    Material.foreground: "white"
                    onClicked: root.startImport()

                    background: Rectangle {
                        radius: ThemeTokens.radiusFull
                        color: parent.Material.background
                        opacity: parent.enabled ? 1.0 : 0.45
                    }
                }
            }
        }

        Label {
            Layout.fillWidth: true
            visible: planImportViewModel.error !== ""
            text: planImportViewModel.error
            color: Material.color(Material.Red)
            wrapMode: Text.WordWrap
        }
    }

    footer: Item {
        implicitHeight: footerRow.implicitHeight + ThemeTokens.spaceSm + ThemeTokens.spaceMd

        RowLayout {
            id: footerRow
            anchors.left: parent.left
            anchors.right: parent.right
            anchors.bottom: parent.bottom
            anchors.leftMargin: ThemeTokens.spaceMd
            anchors.rightMargin: ThemeTokens.spaceMd
            anchors.bottomMargin: ThemeTokens.spaceMd
            anchors.topMargin: ThemeTokens.spaceSm
            spacing: ThemeTokens.spaceSm

            Item { Layout.fillWidth: true }

            Button {
                text: qsTr("Cancel")
                flat: true
                onClicked: root.close()
            }

            Button {
                text: qsTr("Back")
                visible: root.currentStep > 0 && !planImportViewModel.isImporting
                enabled: root.currentStep > 0
                onClicked: root.currentStep = 0
            }

            Button {
                text: qsTr("Next")
                visible: root.currentStep === 0 && !planImportViewModel.isImporting
                enabled: root.selectedPath !== "" && planImportViewModel.error === ""
                Material.background: ThemeTokens.accent
                Material.foreground: "white"
                onClicked: {
                    if (root.selectedPath !== "") {
                        planImportViewModel.inspectFile(root.selectedPath)
                    }
                }
            }
        }
    }

    Popup {
        id: importSuccessSnackbar
        parent: Overlay.overlay
        modal: false
        focus: false
        closePolicy: Popup.CloseOnEscape | Popup.CloseOnPressOutside
        x: parent ? (parent.width - width) / 2 : 0
        y: parent ? parent.height - height - 24 : 0
        width: Math.min(parent ? parent.width - 48 : 360, 420)
        padding: ThemeTokens.spaceMd

        background: Rectangle {
            radius: ThemeTokens.radiusMd
            color: Material.color(Material.Grey, Material.Shade800)
        }

        contentItem: Label {
            text: qsTr("Forecast imported successfully")
            color: "white"
            wrapMode: Text.WordWrap
        }

        Timer {
            interval: 3000
            running: importSuccessSnackbar.opened
            onTriggered: importSuccessSnackbar.close()
        }
    }

    component PreviewRow: RowLayout {
        Layout.fillWidth: true
        Layout.minimumWidth: 0

        property string label: ""
        property string value: ""

        spacing: ThemeTokens.spaceSm

        Label {
            text: label
            color: Material.secondaryTextColor
            font.pixelSize: ThemeTokens.fontSm
            Layout.alignment: Qt.AlignTop
        }

        Label {
            Layout.fillWidth: true
            Layout.minimumWidth: 0
            text: value
            wrapMode: Text.WordWrap
            font.pixelSize: ThemeTokens.fontSm
            Layout.alignment: Qt.AlignTop
        }
    }

    component RateConflictRow: ColumnLayout {
        id: conflictRow

        property string currency: ""
        property real localRateValue: 0
        property real fileRateValue: 0
        property bool useFileRate: false

        signal resolutionChoiceChanged(bool useFile)

        spacing: ThemeTokens.spaceXs

        Label {
            Layout.fillWidth: true
            text: qsTr("%1 → USD").arg(conflictRow.currency)
            font.weight: ThemeTokens.weightSemiBold
            font.pixelSize: ThemeTokens.fontSm
        }

        RowLayout {
            Layout.fillWidth: true
            spacing: ThemeTokens.spaceMd

            Label {
                Layout.fillWidth: true
                text: qsTr("Local: %1").arg(
                          Number(conflictRow.localRateValue).toLocaleString(Qt.locale(), "f", 4))
                font.pixelSize: ThemeTokens.fontSm
                color: Material.secondaryTextColor
            }

            Label {
                Layout.fillWidth: true
                text: qsTr("File: %1").arg(
                          Number(conflictRow.fileRateValue).toLocaleString(Qt.locale(), "f", 4))
                font.pixelSize: ThemeTokens.fontSm
                color: Material.secondaryTextColor
            }
        }

        ButtonGroup {
            id: resolutionGroup
        }

        RowLayout {
            Layout.fillWidth: true
            spacing: ThemeTokens.spaceMd

            RadioButton {
                Layout.fillWidth: true
                text: qsTr("Keep mine")
                checked: !conflictRow.useFileRate
                ButtonGroup.group: resolutionGroup
                onClicked: conflictRow.resolutionChoiceChanged(false)
            }

            RadioButton {
                Layout.fillWidth: true
                text: qsTr("Use file's")
                checked: conflictRow.useFileRate
                ButtonGroup.group: resolutionGroup
                onClicked: conflictRow.resolutionChoiceChanged(true)
            }
        }

        Rectangle {
            Layout.fillWidth: true
            height: 1
            color: Material.dividerColor
        }
    }
}
