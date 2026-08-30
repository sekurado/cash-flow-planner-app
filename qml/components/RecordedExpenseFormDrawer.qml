import QtQuick
import QtQuick.Controls
import QtQuick.Controls.Material
import QtQuick.Dialogs
import QtQuick.Layouts

import ThemeTokens 1.0
import "."

Drawer {
    id: root

    edge: Qt.RightEdge
    width: parent ? Math.min(400, parent.width * 0.9) : 400
    modal: true
    interactive: true

    readonly property bool isDark: Material.theme === Material.Dark
    readonly property color drawerColor: isDark ? ThemeTokens.cardDark : ThemeTokens.cardLight

    property string expenseId: ""

    function todayParts() {
        var d = new Date()
        return {
            year: d.getFullYear(),
            month: d.getMonth() + 1,
            day: d.getDate()
        }
    }

    function parseIsoDate(iso) {
        if (!iso || iso === "") {
            return todayParts()
        }
        var parts = iso.split("-")
        if (parts.length !== 3) {
            return todayParts()
        }
        return {
            year: parseInt(parts[0], 10),
            month: parseInt(parts[1], 10),
            day: parseInt(parts[2], 10)
        }
    }

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

    function receiptImageUrl(path) {
        if (!path || path === "") {
            return ""
        }
        if (path.startsWith("file:")) {
            return path
        }
        if (Qt.platform.os === "windows") {
            return "file:///" + path.replace(/\\/g, "/")
        }
        return "file://" + path
    }

    function openForCreate() {
        recordedExpensesViewModel.clearError()
        recordedExpensesViewModel.clearReceiptOcr()
        root.expenseId = ""
        expenseForm.resetForm()
        open()
    }

    function openForEdit(expense) {
        recordedExpensesViewModel.clearError()
        recordedExpensesViewModel.clearReceiptOcr()
        root.expenseId = expense.expenseId || expense.id || ""
        expenseForm.loadExpense(expense)
        open()
    }

    background: Rectangle {
        color: root.drawerColor
        topLeftRadius: ThemeTokens.radiusLg
        topRightRadius: ThemeTokens.radiusLg
    }

    ColumnLayout {
        anchors.fill: parent
        spacing: 0

        Item {
            Layout.fillWidth: true
            Layout.preferredHeight: ThemeTokens.spaceMd

            Rectangle {
                anchors.horizontalCenter: parent.horizontalCenter
                anchors.verticalCenter: parent.verticalCenter
                width: 40
                height: 4
                radius: 2
                color: "#CBD5E1"
            }
        }

        RowLayout {
            Layout.fillWidth: true
            Layout.leftMargin: ThemeTokens.spaceMd
            Layout.rightMargin: ThemeTokens.spaceMd
            Layout.bottomMargin: ThemeTokens.spaceSm
            spacing: ThemeTokens.spaceSm

            Label {
                Layout.fillWidth: true
                Layout.minimumWidth: 0
                text: root.expenseId === ""
                        ? qsTr("Add recorded expense")
                        : qsTr("Edit recorded expense")
                font.pixelSize: ThemeTokens.fontLg
                font.weight: ThemeTokens.weightBold
                elide: Text.ElideRight
            }

            ToolButton {
                visible: root.expenseId === ""
                text: qsTr("Scan")
                font.pixelSize: ThemeTokens.fontSm
                enabled: !recordedExpensesViewModel.isOcrRunning
                Accessible.name: qsTr("Scan receipt")
                onClicked: receiptFileDialog.open()
            }

            ToolButton {
                text: "✕"
                font.pixelSize: ThemeTokens.fontMd
                Accessible.name: qsTr("Close")
                onClicked: root.close()
            }
        }

        ScrollView {
            id: formScroll
            Layout.fillWidth: true
            Layout.fillHeight: true
            Layout.leftMargin: ThemeTokens.spaceMd
            Layout.rightMargin: ThemeTokens.spaceMd
            clip: true
            contentWidth: availableWidth
            ScrollBar.horizontal.policy: ScrollBar.AlwaysOff

            ColumnLayout {
                id: expenseForm
                width: formScroll.availableWidth
                spacing: ThemeTokens.spaceMd

                property bool _syncing: false

                readonly property bool canSave: nameField.text.trim() !== ""
                    && amountField.text.trim() !== ""
                    && !isNaN(parseFloat(amountField.text))
                    && parseFloat(amountField.text) > 0

                function resetForm() {
                    _syncing = true
                    var today = root.todayParts()
                    amountField.text = ""
                    currencyCombo.currentIndex = Math.max(0, currencyCombo.model.indexOf("USD"))
                    datePicker.year = today.year
                    datePicker.month = today.month
                    datePicker.day = today.day
                    nameField.setTextSilently("")
                    categoryField.setTextSilently("")
                    placeField.setTextSilently("")
                    noteField.text = ""
                    _syncing = false
                }

                function loadExpense(expense) {
                    _syncing = true
                    var parsedDate = root.parseIsoDate(expense.occurredOn || expense.occurred_on || "")
                    amountField.text = expense.amount === 0 ? "" : String(expense.amount)
                    var currency = expense.currency || "USD"
                    var currencyIndex = currencyCombo.model.indexOf(currency)
                    currencyCombo.currentIndex = currencyIndex >= 0 ? currencyIndex : 0
                    datePicker.year = parsedDate.year
                    datePicker.month = parsedDate.month
                    datePicker.day = parsedDate.day
                    nameField.setTextSilently(expense.nameLabel || expense.name || "")
                    categoryField.setTextSilently(expense.categoryLabel || expense.category || "")
                    placeField.setTextSilently(expense.placeLabel || expense.place || "")
                    noteField.text = expense.note || ""
                    _syncing = false
                }

                function save() {
                    if (!canSave || recordedExpensesViewModel.isOcrRunning) {
                        return
                    }

                    var categoryValue = categoryField.text.trim()
                    var placeValue = placeField.text.trim()
                    var noteValue = noteField.text.trim()
                    var dto = {
                        amount: parseFloat(amountField.text),
                        currency: currencyCombo.model[currencyCombo.currentIndex],
                        name: nameField.text.trim(),
                        category: categoryValue === "" ? null : categoryValue,
                        place: placeValue === "" ? null : placeValue,
                        occurred_on: datePicker.formattedDate,
                        note: noteValue === "" ? null : noteValue
                    }

                    if (root.expenseId === "") {
                        recordedExpensesViewModel.createExpense(dto)
                    } else {
                        recordedExpensesViewModel.updateExpense(root.expenseId, dto)
                    }
                }

                function applyReceiptSuggestions() {
                    if (root.expenseId !== "" || !recordedExpensesViewModel.hasReceiptSuggestions) {
                        return
                    }
                    _syncing = true
                    if (recordedExpensesViewModel.suggestedAmount !== "") {
                        amountField.text = recordedExpensesViewModel.suggestedAmount
                    }
                    if (recordedExpensesViewModel.suggestedOccurredOn !== "") {
                        var parsedDate = root.parseIsoDate(recordedExpensesViewModel.suggestedOccurredOn)
                        datePicker.year = parsedDate.year
                        datePicker.month = parsedDate.month
                        datePicker.day = parsedDate.day
                    }
                    if (recordedExpensesViewModel.suggestedMerchant !== "") {
                        nameField.setTextSilently(recordedExpensesViewModel.suggestedMerchant)
                    }
                    _syncing = false
                }

                RowLayout {
                    visible: root.expenseId === ""
                             && (recordedExpensesViewModel.isOcrRunning
                                 || recordedExpensesViewModel.pendingReceiptPath !== "")
                    Layout.fillWidth: true
                    spacing: ThemeTokens.spaceSm

                    Rectangle {
                        Layout.preferredWidth: 64
                        Layout.preferredHeight: 64
                        radius: ThemeTokens.radiusSm
                        color: root.isDark ? "#1E293B" : "#E2E8F0"
                        clip: true

                        Image {
                            anchors.fill: parent
                            visible: recordedExpensesViewModel.pendingReceiptPath !== ""
                            source: root.receiptImageUrl(recordedExpensesViewModel.pendingReceiptPath)
                            fillMode: Image.PreserveAspectCrop
                            asynchronous: true
                        }

                        BusyIndicator {
                            anchors.centerIn: parent
                            width: 28
                            height: 28
                            running: recordedExpensesViewModel.isOcrRunning
                            visible: recordedExpensesViewModel.isOcrRunning
                        }
                    }

                    ColumnLayout {
                        Layout.fillWidth: true
                        Layout.minimumWidth: 0
                        spacing: 2

                        Label {
                            Layout.fillWidth: true
                            text: recordedExpensesViewModel.isOcrRunning
                                    ? qsTr("Reading receipt…")
                                    : qsTr("Review suggested fields, then save.")
                            font.pixelSize: ThemeTokens.fontSm
                            wrapMode: Text.WordWrap
                        }

                        Label {
                            Layout.fillWidth: true
                            visible: !recordedExpensesViewModel.isOcrRunning
                            text: qsTr("You can edit any field or enter the expense manually.")
                            font.pixelSize: ThemeTokens.fontXs
                            color: Material.secondaryTextColor
                            wrapMode: Text.WordWrap
                        }
                    }

                    Button {
                        flat: true
                        text: qsTr("Enter manually")
                        enabled: !recordedExpensesViewModel.isOcrRunning
                        Material.foreground: ThemeTokens.primary
                        Accessible.name: qsTr("Enter manually")
                        onClicked: recordedExpensesViewModel.clearReceiptOcr()
                    }
                }

                RowLayout {
                    Layout.fillWidth: true
                    Layout.minimumWidth: 0
                    spacing: ThemeTokens.spaceSm

                    ColumnLayout {
                        Layout.fillWidth: true
                        Layout.minimumWidth: 0
                        spacing: ThemeTokens.spaceXs

                        RowLayout {
                            Layout.fillWidth: true
                            spacing: ThemeTokens.spaceSm

                            Label {
                                Layout.fillWidth: true
                                text: qsTr("Amount")
                                font.pixelSize: ThemeTokens.fontSm
                                font.weight: ThemeTokens.weightMedium
                                color: ThemeTokens.primary
                            }

                            Rectangle {
                                visible: recordedExpensesViewModel.hasReceiptSuggestions
                                         && recordedExpensesViewModel.amountIsLowConfidence
                                implicitHeight: amountConfidenceLabel.implicitHeight + 4
                                implicitWidth: amountConfidenceLabel.implicitWidth + 10
                                radius: ThemeTokens.radiusFull
                                color: root.isDark ? ThemeTokens.deficitAmberBgDark : ThemeTokens.deficitAmberBg

                                Label {
                                    id: amountConfidenceLabel
                                    anchors.centerIn: parent
                                    text: qsTr("Low confidence")
                                    font.pixelSize: ThemeTokens.fontXs
                                    color: root.isDark ? ThemeTokens.accentDark : "#92400E"
                                }
                            }
                        }

                        TextField {
                            id: amountField
                            Layout.fillWidth: true
                            placeholderText: qsTr("0.00")
                            inputMethodHints: Qt.ImhFormattedNumbersOnly
                            Accessible.name: qsTr("Amount")
                            selectByMouse: true
                        }
                    }

                    ColumnLayout {
                        Layout.minimumWidth: 72
                        Layout.preferredWidth: 88
                        Layout.maximumWidth: 112
                        spacing: ThemeTokens.spaceXs

                        Label {
                            Layout.fillWidth: true
                            text: qsTr("Currency")
                            font.pixelSize: ThemeTokens.fontSm
                            font.weight: ThemeTokens.weightMedium
                            color: ThemeTokens.primary
                        }

                        ComboBox {
                            id: currencyCombo
                            Layout.fillWidth: true
                            model: appViewModel.commonCurrencies
                            Accessible.name: qsTr("Currency")
                        }
                    }
                }

                ColumnLayout {
                    Layout.fillWidth: true
                    spacing: ThemeTokens.spaceXs

                    RowLayout {
                        Layout.fillWidth: true
                        spacing: ThemeTokens.spaceSm

                        Label {
                            Layout.fillWidth: true
                            text: qsTr("Date")
                            font.pixelSize: ThemeTokens.fontSm
                            font.weight: ThemeTokens.weightMedium
                            color: ThemeTokens.primary
                        }

                        Rectangle {
                            visible: recordedExpensesViewModel.hasReceiptSuggestions
                                     && recordedExpensesViewModel.dateIsLowConfidence
                            implicitHeight: dateConfidenceLabel.implicitHeight + 4
                            implicitWidth: dateConfidenceLabel.implicitWidth + 10
                            radius: ThemeTokens.radiusFull
                            color: root.isDark ? ThemeTokens.deficitAmberBgDark : ThemeTokens.deficitAmberBg

                            Label {
                                id: dateConfidenceLabel
                                anchors.centerIn: parent
                                text: qsTr("Low confidence")
                                font.pixelSize: ThemeTokens.fontXs
                                color: root.isDark ? ThemeTokens.accentDark : "#92400E"
                            }
                        }
                    }

                    DatePicker {
                        id: datePicker
                        Layout.fillWidth: true
                        Layout.preferredHeight: implicitHeight
                        stacked: true
                    }
                }

                LabelAutocompleteField {
                    id: nameField
                    caption: qsTr("Name")
                    placeholderText: qsTr("e.g. Groceries")
                    required: true
                    lowConfidence: recordedExpensesViewModel.hasReceiptSuggestions
                                   && recordedExpensesViewModel.merchantIsLowConfidence
                    suggestionModel: recordedExpensesViewModel.nameSuggestionModel
                    onSearchRequested: function (prefix) {
                        recordedExpensesViewModel.searchExpenseNames(prefix)
                    }
                }

                LabelAutocompleteField {
                    id: categoryField
                    caption: qsTr("Category")
                    placeholderText: qsTr("e.g. Food")
                    suggestionModel: recordedExpensesViewModel.categorySuggestionModel
                    onSearchRequested: function (prefix) {
                        recordedExpensesViewModel.searchCategories(prefix)
                    }
                }

                LabelAutocompleteField {
                    id: placeField
                    caption: qsTr("Place")
                    placeholderText: qsTr("e.g. Whole Foods")
                    suggestionModel: recordedExpensesViewModel.placeSuggestionModel
                    onSearchRequested: function (prefix) {
                        recordedExpensesViewModel.searchPlaces(prefix)
                    }
                }

                ColumnLayout {
                    Layout.fillWidth: true
                    spacing: ThemeTokens.spaceXs

                    Label {
                        text: qsTr("Note") + " (" + qsTr("optional") + ")"
                        font.pixelSize: ThemeTokens.fontSm
                        font.weight: ThemeTokens.weightMedium
                        color: ThemeTokens.primary
                    }

                    TextField {
                        id: noteField
                        Layout.fillWidth: true
                        placeholderText: qsTr("Add a note")
                        Accessible.name: qsTr("Note")
                        selectByMouse: true
                    }
                }
            }
        }

        Button {
            Layout.fillWidth: true
            Layout.margins: ThemeTokens.spaceMd
            text: qsTr("Save")
            enabled: expenseForm.canSave && !recordedExpensesViewModel.isOcrRunning
            Material.background: ThemeTokens.primary
            Material.foreground: "white"
            Accessible.name: qsTr("Save recorded expense")

            background: Rectangle {
                radius: ThemeTokens.radiusMd
                color: parent.enabled ? parent.Material.background : Material.color(Material.Grey, Material.Shade400)
            }

            onClicked: expenseForm.save()
        }
    }

    FileDialog {
        id: receiptFileDialog
        title: qsTr("Choose a receipt image")
        nameFilters: [qsTr("Images (*.jpg *.jpeg *.png *.webp *.heic)")]
        onAccepted: recordedExpensesViewModel.startReceiptOcr(root.localFilePath(selectedFile))
    }

    Connections {
        target: recordedExpensesViewModel

        function onExpenseCreated(createdId) {
            if (root.visible && root.expenseId === "") {
                root.close()
            }
        }

        function onExpenseUpdated(updatedId) {
            if (root.visible && updatedId === root.expenseId) {
                root.close()
            }
        }

        function onReceiptOcrChanged() {
            expenseForm.applyReceiptSuggestions()
        }
    }

    onClosed: {
        if (root.expenseId === "") {
            recordedExpensesViewModel.clearReceiptOcr()
        }
    }
}
