import QtQuick
import QtQuick.Controls
import QtQuick.Controls.Material
import QtQuick.Dialogs
import QtQuick.Layouts

import ThemeTokens 1.0
import "../components"

Item {
    id: root

    readonly property string planId: planViewModel.selectedPlan ? planViewModel.selectedPlan.id : ""
    readonly property var plan: planViewModel.selectedPlan
    readonly property bool isDark: Material.theme === Material.Dark

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

    Rectangle {
        anchors.fill: parent
        color: root.isDark ? ThemeTokens.surfaceDark : ThemeTokens.surfaceLight
    }

    RowLayout {
        anchors.fill: parent
        spacing: 0

        Flickable {
            Layout.fillWidth: true
            Layout.fillHeight: true
            clip: true
            boundsBehavior: Flickable.StopAtBounds
            contentWidth: width
            contentHeight: simulationColumn.implicitHeight

            ColumnLayout {
                id: simulationColumn
                width: parent.width
                spacing: ThemeTokens.spaceMd

                SimulationControls {
                    id: simulationControls
                    Layout.fillWidth: true
                    Layout.leftMargin: ThemeTokens.spaceMd
                    Layout.rightMargin: ThemeTokens.spaceMd
                    Layout.topMargin: ThemeTokens.spaceMd
                    onExportCsvClicked: csvSaveDialog.open()
                    onExportPdfClicked: pdfSaveDialog.open()
                }

                DeficitBanner {
                    Layout.fillWidth: true
                    Layout.leftMargin: ThemeTokens.spaceMd
                    Layout.rightMargin: ThemeTokens.spaceMd
                }

                SuggestionsPanel {
                    Layout.fillWidth: true
                    Layout.leftMargin: ThemeTokens.spaceMd
                    Layout.rightMargin: ThemeTokens.spaceMd
                }

                BalanceChart {
                    Layout.fillWidth: true
                    Layout.leftMargin: ThemeTokens.spaceMd
                    Layout.rightMargin: ThemeTokens.spaceMd
                    Layout.preferredHeight: 250
                }

                MonthlyTableView {
                    Layout.fillWidth: true
                    Layout.leftMargin: ThemeTokens.spaceMd
                    Layout.rightMargin: ThemeTokens.spaceMd
                    Layout.bottomMargin: ThemeTokens.spaceMd
                }
            }
        }

        WhatIfPanel {
            id: whatIfPanel
            Layout.fillHeight: true
            simulationControls: simulationControls
        }
    }

    FileDialog {
        id: csvSaveDialog
        title: qsTr("Export projection as CSV")
        fileMode: FileDialog.SaveFile
        nameFilters: [qsTr("CSV files (*.csv)")]
        defaultSuffix: "csv"
        onAccepted: {
            simulationViewModel.exportCsv(root.localFilePath(selectedFile))
        }
    }

    FileDialog {
        id: pdfSaveDialog
        title: qsTr("Export executive report")
        fileMode: FileDialog.SaveFile
        nameFilters: [qsTr("PDF files (*.pdf)")]
        defaultSuffix: "pdf"
        onAccepted: {
            var planName = root.plan ? root.plan.name : qsTr("Forecast")
            var overrides = whatIfPanel.hasOverrides ? whatIfPanel.collectOverrides() : null
            simulationViewModel.exportExecutivePdf(
                root.localFilePath(selectedFile),
                planName,
                overrides
            )
        }
    }

    Connections {
        target: simulationViewModel

        function onExportSucceeded() {
            exportSnackbar.open()
        }
    }

    Popup {
        id: exportSnackbar
        parent: Overlay.overlay
        modal: false
        focus: false
        closePolicy: Popup.CloseOnEscape | Popup.CloseOnPressOutside
        x: parent ? (parent.width - width) / 2 : 0
        y: parent ? parent.height - height - 24 : 0
        width: Math.min(parent ? parent.width - 48 : 360, 420)
        padding: 12

        background: Rectangle {
            radius: ThemeTokens.radiusMd
            color: Material.color(Material.Grey, Material.Shade800)
        }

        contentItem: Label {
            text: qsTr("Exported successfully")
            color: "white"
            wrapMode: Text.WordWrap
        }

        Timer {
            interval: 3000
            running: exportSnackbar.opened
            onTriggered: exportSnackbar.close()
        }
    }
}
