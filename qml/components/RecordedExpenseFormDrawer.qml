import QtQuick
import QtQuick.Controls
import QtQuick.Controls.Material
import QtQuick.Layouts

import ThemeTokens 1.0

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

    function openForCreate() {
        recordedExpensesViewModel.clearError()
        root.expenseId = ""
        expenseForm.resetForm()
        open()
    }

    function openForEdit(expense) {
        recordedExpensesViewModel.clearError()
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
                    if (!canSave) {
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

                RowLayout {
                    Layout.fillWidth: true
                    Layout.minimumWidth: 0
                    spacing: ThemeTokens.spaceSm

                    ColumnLayout {
                        Layout.fillWidth: true
                        Layout.minimumWidth: 0
                        spacing: ThemeTokens.spaceXs

                        Label {
                            Layout.fillWidth: true
                            text: qsTr("Amount")
                            font.pixelSize: ThemeTokens.fontSm
                            font.weight: ThemeTokens.weightMedium
                            color: ThemeTokens.primary
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

                    Label {
                        text: qsTr("Date")
                        font.pixelSize: ThemeTokens.fontSm
                        font.weight: ThemeTokens.weightMedium
                        color: ThemeTokens.primary
                    }

                    DatePicker {
                        id: datePicker
                        stacked: true
                    }
                }

                LabelAutocompleteField {
                    id: nameField
                    caption: qsTr("Name")
                    placeholderText: qsTr("e.g. Groceries")
                    required: true
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
            enabled: expenseForm.canSave
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
    }
}
