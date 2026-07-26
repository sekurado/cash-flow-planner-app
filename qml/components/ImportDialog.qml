import QtQuick
import QtQuick.Controls
import QtQuick.Controls.Material
import QtQuick.Dialogs
import QtQuick.Layouts

import ThemeTokens 1.0

CenteredDialog {
    id: root

    standardButtons: Dialog.NoButton
    width: Math.min(parent ? parent.width - 48 : 360, 640)

    readonly property bool isDark: Material.theme === Material.Dark
    readonly property color panelColor: isDark ? "#334155" : "#F1F5F9"

    property string planId: ""
    property string selectedPath: ""
    property int currentStep: 0
    property var columnHeaders: []
    property bool isImporting: false
    property bool importFinished: false
    property var fieldMappings: ({})

    readonly property var requiredFields: [
        { key: "name", label: qsTr("Name") },
        { key: "date_pattern", label: qsTr("Date pattern") },
        { key: "amount", label: qsTr("Amount") },
        { key: "currency", label: qsTr("Currency") },
        { key: "type", label: qsTr("Type") }
    ]

    readonly property var optionalFields: [
        { key: "category", label: qsTr("Category") }
    ]

    readonly property var previewColumns: [
        { key: "name", label: qsTr("Name") },
        { key: "date_pattern", label: qsTr("Date pattern") },
        { key: "amount", label: qsTr("Amount") },
        { key: "currency", label: qsTr("Currency") },
        { key: "type", label: qsTr("Type") },
        { key: "category", label: qsTr("Category") }
    ]

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
        columnHeaders = []
        isImporting = false
        importFinished = false
        fieldMappings = {}
        importViewModel.clearError()
    }

    function guessHeaderIndex(fieldKey) {
        var aliases = [fieldKey]
        if (fieldKey === "type") {
            aliases.push("entry_type")
        }
        for (var a = 0; a < aliases.length; a++) {
            var alias = aliases[a].toLowerCase()
            for (var i = 0; i < columnHeaders.length; i++) {
                if (columnHeaders[i].toLowerCase() === alias) {
                    return i
                }
            }
        }
        return -1
    }

    function initializeMappings() {
        var mappings = {}
        for (var i = 0; i < requiredFields.length; i++) {
            var field = requiredFields[i]
            var index = guessHeaderIndex(field.key)
            mappings[field.key] = index >= 0 ? columnHeaders[index] : ""
        }
        for (var j = 0; j < optionalFields.length; j++) {
            var optionalField = optionalFields[j]
            var optionalIndex = guessHeaderIndex(optionalField.key)
            mappings[optionalField.key] = optionalIndex >= 0 ? columnHeaders[optionalIndex] : ""
        }
        fieldMappings = mappings
    }

    function buildMappingObject() {
        var mapping = {}
        for (var key in fieldMappings) {
            if (fieldMappings[key] !== "") {
                mapping[key] = fieldMappings[key]
            }
        }
        return mapping
    }

    function mappingIsComplete() {
        for (var i = 0; i < requiredFields.length; i++) {
            var fieldKey = requiredFields[i].key
            if (!fieldMappings[fieldKey] || fieldMappings[fieldKey] === "") {
                return false
            }
        }
        return true
    }

    function headerModelForField(fieldKey) {
        var options = [""]
        for (var i = 0; i < columnHeaders.length; i++) {
            options.push(columnHeaders[i])
        }
        return options
    }

    function selectedIndexForField(fieldKey) {
        var selected = fieldMappings[fieldKey] || ""
        if (selected === "") {
            return 0
        }
        for (var i = 0; i < columnHeaders.length; i++) {
            if (columnHeaders[i] === selected) {
                return i + 1
            }
        }
        return 0
    }

    function setFieldMapping(fieldKey, comboIndex) {
        var next = {}
        for (var existingKey in fieldMappings) {
            next[existingKey] = fieldMappings[existingKey]
        }
        if (comboIndex <= 0) {
            next[fieldKey] = ""
        } else {
            next[fieldKey] = columnHeaders[comboIndex - 1]
        }
        fieldMappings = next
    }

    function refreshPreview() {
        if (selectedPath === "") {
            return
        }
        importViewModel.updatePreview(selectedPath, buildMappingObject())
    }

    function startImport() {
        if (selectedPath === "" || planId === "" || !mappingIsComplete()) {
            return
        }
        isImporting = true
        importFinished = false
        importViewModel.importFile(selectedPath, planId, buildMappingObject())
    }

    function showSummary(importedCount, errorCount) {
        summarySnackbar.message = qsTr("Imported %1 cash flows with %2 errors.")
                                      .arg(importedCount)
                                      .arg(errorCount)
        summarySnackbar.open()
    }

    onAboutToShow: resetState()
    onClosed: resetState()

    background: Rectangle {
        radius: ThemeTokens.radiusLg
        color: Material.dialogColor
    }

    header: Label {
        text: qsTr("Import cash flows")
        font.pixelSize: ThemeTokens.fontLg
        font.weight: ThemeTokens.weightSemiBold
        topPadding: ThemeTokens.spaceMd
        leftPadding: ThemeTokens.spaceMd
        rightPadding: ThemeTokens.spaceMd
        bottomPadding: ThemeTokens.spaceSm
    }

    FileDialog {
        id: fileDialog
        title: qsTr("Select file to import")
        nameFilters: [qsTr("Spreadsheets (*.csv *.xlsx)")]
        onAccepted: {
            root.selectedPath = root.localFilePath(selectedFile)
            importViewModel.inspectFile(root.selectedPath)
        }
    }

    Connections {
        target: importViewModel

        function onHeadersReady(headers) {
            root.columnHeaders = headers
            root.initializeMappings()
            root.currentStep = 1
        }

        function onImportCompleted(importedCount, errorCount) {
            root.isImporting = false
            root.importFinished = true
            if (root.planId !== "") {
                entriesViewModel.loadEntries(root.planId)
            }
            root.showSummary(importedCount, errorCount)
            if (errorCount === 0) {
                root.close()
            }
        }
    }

    contentItem: ColumnLayout {
        spacing: ThemeTokens.spaceMd
        Layout.leftMargin: ThemeTokens.spaceMd
        Layout.rightMargin: ThemeTokens.spaceMd
        Layout.topMargin: ThemeTokens.spaceSm
        Layout.bottomMargin: ThemeTokens.spaceSm
        Layout.fillHeight: false

        StackLayout {
            id: stepStack
            Layout.fillWidth: true
            Layout.fillHeight: false
            Layout.preferredHeight: Math.max(implicitHeight, 280)
            currentIndex: root.currentStep

            // Step 1 — file selection
            ColumnLayout {
                spacing: 12

                Label {
                    Layout.fillWidth: true
                    text: qsTr("Choose a CSV or Excel file to import.")
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
                    font.pixelSize: 13
                }
            }

            // Step 2 — column mapping
            ColumnLayout {
                spacing: 8

                Label {
                    Layout.fillWidth: true
                    text: qsTr("Map each required field to a column in your file.")
                    wrapMode: Text.WordWrap
                }

                Repeater {
                    model: root.requiredFields

                    RowLayout {
                        Layout.fillWidth: true
                        spacing: 12

                        required property string key
                        required property string label

                        Label {
                            Layout.preferredWidth: 120
                            text: label
                        }

                        ComboBox {
                            Layout.fillWidth: true
                            model: root.headerModelForField(key)
                            currentIndex: root.selectedIndexForField(key)
                            displayText: currentIndex <= 0 ? qsTr("Select column…") : currentText
                            onActivated: root.setFieldMapping(key, currentIndex)
                        }
                    }
                }

                Label {
                    Layout.fillWidth: true
                    Layout.topMargin: 8
                    text: qsTr("Optional fields")
                    font.bold: true
                }

                Repeater {
                    model: root.optionalFields

                    RowLayout {
                        Layout.fillWidth: true
                        spacing: 12

                        required property string key
                        required property string label

                        Label {
                            Layout.preferredWidth: 120
                            text: label
                        }

                        ComboBox {
                            Layout.fillWidth: true
                            model: root.headerModelForField(key)
                            currentIndex: root.selectedIndexForField(key)
                            displayText: currentIndex <= 0 ? qsTr("Not mapped") : currentText
                            onActivated: root.setFieldMapping(key, currentIndex)
                        }
                    }
                }
            }

            // Step 3 — preview
            ColumnLayout {
                spacing: 8

                Label {
                    Layout.fillWidth: true
                    text: qsTr("Preview of the first 5 rows with your column mapping applied.")
                    wrapMode: Text.WordWrap
                }

                Rectangle {
                    Layout.fillWidth: true
                    Layout.fillHeight: true
                    color: root.panelColor
                    border.color: Material.dividerColor
                    radius: ThemeTokens.radiusSm

                    ColumnLayout {
                        anchors.fill: parent
                        anchors.margins: 8
                        spacing: 4

                        RowLayout {
                            Layout.fillWidth: true
                            spacing: 8

                            Repeater {
                                model: root.previewColumns

                                Label {
                                    required property string label
                                    Layout.preferredWidth: 88
                                    text: label
                                    font.bold: true
                                    font.pixelSize: 12
                                    elide: Text.ElideRight
                                }
                            }
                        }

                        Rectangle {
                            Layout.fillWidth: true
                            height: 1
                            color: Material.dividerColor
                        }

                        ListView {
                            id: previewList
                            Layout.fillWidth: true
                            Layout.fillHeight: true
                            clip: true
                            spacing: 4
                            model: importViewModel.previewRows

                            delegate: RowLayout {
                                spacing: 8
                                width: previewList.width

                                property var rowData: modelData

                                Label {
                                    Layout.preferredWidth: 88
                                    text: rowData && rowData.name ? rowData.name : ""
                                    font.pixelSize: 12
                                    elide: Text.ElideRight
                                }
                                Label {
                                    Layout.preferredWidth: 88
                                    text: rowData && rowData.date_pattern ? rowData.date_pattern : ""
                                    font.pixelSize: 12
                                    elide: Text.ElideRight
                                }
                                Label {
                                    Layout.preferredWidth: 88
                                    text: rowData && rowData.amount ? rowData.amount : ""
                                    font.pixelSize: 12
                                    elide: Text.ElideRight
                                }
                                Label {
                                    Layout.preferredWidth: 88
                                    text: rowData && rowData.currency ? rowData.currency : ""
                                    font.pixelSize: 12
                                    elide: Text.ElideRight
                                }
                                Label {
                                    Layout.preferredWidth: 88
                                    text: rowData && rowData.type ? rowData.type : ""
                                    font.pixelSize: 12
                                    elide: Text.ElideRight
                                }
                                Label {
                                    Layout.preferredWidth: 88
                                    text: rowData && rowData.category ? rowData.category : ""
                                    font.pixelSize: 12
                                    elide: Text.ElideRight
                                }
                            }
                        }

                        Label {
                            Layout.fillWidth: true
                            visible: importViewModel.previewRows.length === 0
                            text: qsTr("No preview rows available.")
                            color: Material.secondaryTextColor
                        }
                    }
                }
            }

            // Step 4 — confirmation
            ColumnLayout {
                spacing: 12

                Label {
                    Layout.fillWidth: true
                    text: qsTr("Ready to import. Review the summary below and click Import.")
                    wrapMode: Text.WordWrap
                }

                Label {
                    Layout.fillWidth: true
                    text: root.selectedPath
                    color: Material.secondaryTextColor
                    wrapMode: Text.WordWrap
                    font.pixelSize: 13
                }

                ProgressBar {
                    Layout.fillWidth: true
                    from: 0
                    to: 1
                    value: importViewModel.progress
                    visible: root.isImporting || root.importFinished
                }

                Button {
                    Layout.alignment: Qt.AlignLeft
                    text: qsTr("Import")
                    enabled: !root.isImporting && root.mappingIsComplete() && root.planId !== ""
                    Material.background: ThemeTokens.primary
                    Material.foreground: "white"
                    onClicked: root.startImport()

                    background: Rectangle {
                        radius: ThemeTokens.radiusFull
                        color: parent.Material.background
                        opacity: parent.enabled ? 1.0 : 0.45
                    }
                }

                ImportErrorsSection {
                    id: importErrorsSection
                    Layout.fillWidth: true
                    visible: root.importFinished && importViewModel.errorCount > 0
                    errors: importViewModel.errors
                }
            }
        }

        Label {
            Layout.fillWidth: true
            visible: importViewModel.error !== ""
            text: importViewModel.error
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
                visible: root.currentStep > 0 && !root.isImporting
                enabled: root.currentStep > 0
                onClicked: root.currentStep = Math.max(0, root.currentStep - 1)
            }

            Button {
                text: qsTr("Next")
                visible: root.currentStep < 3 && !root.isImporting
                enabled: {
                    if (root.currentStep === 0) {
                        return root.selectedPath !== ""
                    }
                    if (root.currentStep === 1) {
                        return root.mappingIsComplete()
                    }
                    if (root.currentStep === 2) {
                        return importViewModel.previewRows.length > 0 || importViewModel.error === ""
                    }
                    return false
                }
                Material.background: Material.accent
                Material.foreground: "white"
                onClicked: {
                    if (root.currentStep === 1) {
                        root.refreshPreview()
                    }
                    root.currentStep = Math.min(3, root.currentStep + 1)
                }
            }

            Button {
                text: qsTr("Done")
                visible: root.importFinished && importViewModel.errorCount > 0
                Material.background: Material.accent
                Material.foreground: "white"
                onClicked: root.close()
            }
        }
    }

    Popup {
        id: summarySnackbar
        property string message: ""
        parent: Overlay.overlay
        modal: false
        focus: false
        closePolicy: Popup.CloseOnEscape | Popup.CloseOnPressOutside
        x: parent ? (parent.width - width) / 2 : 0
        y: parent ? parent.height - height - 24 : 0
        width: Math.min(parent ? parent.width - 48 : 360, 420)
        padding: 12

        background: Rectangle {
            radius: 4
            color: Material.color(Material.Green, Material.Shade700)
        }

        contentItem: Label {
            text: summarySnackbar.message
            color: "white"
            wrapMode: Text.WordWrap
        }

        Timer {
            interval: 2500
            running: summarySnackbar.opened
            onTriggered: summarySnackbar.close()
        }
    }

    component ImportErrorsSection: ColumnLayout {
        id: errorsSection
        property var errors: []

        spacing: 4
        property bool expanded: true

        Button {
            Layout.fillWidth: true
            flat: true
            text: errorsSection.expanded
                  ? qsTr("Hide import errors")
                  : qsTr("Show import errors (%1)").arg(errorsSection.errors.length)
            onClicked: errorsSection.expanded = !errorsSection.expanded
        }

        Repeater {
            model: errorsSection.expanded ? errorsSection.errors : []

            Label {
                required property int row
                required property string message
                Layout.fillWidth: true
                text: qsTr("Row %1: %2").arg(row).arg(message)
                color: Material.color(Material.Red)
                wrapMode: Text.WordWrap
                font.pixelSize: 12
            }
        }
    }
}
