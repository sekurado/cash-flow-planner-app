import QtQuick
import QtQuick.Controls
import QtQuick.Controls.Material
import QtQuick.Layouts

import ThemeTokens 1.0

ColumnLayout {
    id: root

    spacing: ThemeTokens.spaceMd

    property string entryId: ""
    property string planId: ""
    property string entryType: "income"
    property string name: ""
    property string datePattern: ""
    property real amount: 0
    property string currency: "USD"
    property string category: ""

    property bool _syncing: false

    readonly property bool canSave: nameField.text.trim() !== ""
        && amountField.text.trim() !== ""
        && patternInput.valid
        && !isNaN(parseFloat(amountField.text))

    ColumnLayout {
        Layout.fillWidth: true
        Layout.minimumWidth: 0
        spacing: ThemeTokens.spaceXs

        Label {
            Layout.fillWidth: true
            Layout.minimumWidth: 0
            text: qsTr("Description")
            font.pixelSize: ThemeTokens.fontSm
            font.weight: ThemeTokens.weightMedium
            color: ThemeTokens.primary
        }

        TextField {
            id: nameField
            Layout.fillWidth: true
            Layout.minimumWidth: 0
            placeholderText: qsTr("e.g. Salary")
            Accessible.name: qsTr("Cash flow name")
            selectByMouse: true
            onTextChanged: {
                if (!root._syncing) {
                    root.name = text
                }
            }
        }
    }

    ColumnLayout {
        Layout.fillWidth: true
        Layout.minimumWidth: 0
        spacing: ThemeTokens.spaceXs

        Label {
            Layout.fillWidth: true
            Layout.minimumWidth: 0
            text: qsTr("Type")
            font.pixelSize: ThemeTokens.fontSm
            font.weight: ThemeTokens.weightMedium
            color: ThemeTokens.primary
        }

        RowLayout {
            Layout.fillWidth: true
            Layout.minimumWidth: 0
            spacing: ThemeTokens.spaceSm

            ButtonGroup {
                id: typeGroup
            }

            RadioButton {
                text: qsTr("Income")
                checked: root.entryType === "income"
                ButtonGroup.group: typeGroup
                Accessible.name: qsTr("Income")
                onClicked: root.entryType = "income"
            }

            RadioButton {
                text: qsTr("Expense")
                checked: root.entryType === "expense"
                ButtonGroup.group: typeGroup
                Accessible.name: qsTr("Expense")
                onClicked: root.entryType = "expense"
            }
        }
    }

    ColumnLayout {
        Layout.fillWidth: true
        Layout.minimumWidth: 0
        spacing: ThemeTokens.spaceXs

        Label {
            Layout.fillWidth: true
            Layout.minimumWidth: 0
            text: qsTr("Date pattern")
            font.pixelSize: ThemeTokens.fontSm
            font.weight: ThemeTokens.weightMedium
            color: ThemeTokens.primary
        }

        DatePatternInput {
            id: patternInput
            Layout.fillWidth: true
            Layout.minimumWidth: 0
            onTextChanged: {
                if (!root._syncing) {
                    root.datePattern = text
                }
            }
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
                Layout.minimumWidth: 0
                text: qsTr("Amount")
                font.pixelSize: ThemeTokens.fontSm
                font.weight: ThemeTokens.weightMedium
                color: ThemeTokens.primary
            }

            TextField {
                id: amountField
                Layout.fillWidth: true
                Layout.minimumWidth: 0
                placeholderText: qsTr("0.00")
                inputMethodHints: Qt.ImhFormattedNumbersOnly
                Accessible.name: qsTr("Amount")
                selectByMouse: true
                onTextChanged: {
                    if (root._syncing) {
                        return
                    }
                    var parsed = parseFloat(text)
                    root.amount = isNaN(parsed) ? 0 : parsed
                }
            }
        }

        ColumnLayout {
            Layout.minimumWidth: 72
            Layout.preferredWidth: 88
            Layout.maximumWidth: 112
            spacing: ThemeTokens.spaceXs

            Label {
                Layout.fillWidth: true
                Layout.minimumWidth: 0
                text: qsTr("Currency")
                font.pixelSize: ThemeTokens.fontSm
                font.weight: ThemeTokens.weightMedium
                color: ThemeTokens.primary
            }

            ComboBox {
                id: currencyCombo
                Layout.fillWidth: true
                Layout.minimumWidth: 0
                model: appViewModel.commonCurrencies
                Accessible.name: qsTr("Currency")
                onActivated: root.currency = model[currentIndex]
            }
        }
    }

    ColumnLayout {
        Layout.fillWidth: true
        Layout.minimumWidth: 0
        spacing: ThemeTokens.spaceXs

        Label {
            Layout.fillWidth: true
            Layout.minimumWidth: 0
            text: qsTr("Category (optional)")
            font.pixelSize: ThemeTokens.fontSm
            font.weight: ThemeTokens.weightMedium
            color: ThemeTokens.primary
        }

        TextField {
            id: categoryField
            Layout.fillWidth: true
            Layout.minimumWidth: 0
            placeholderText: qsTr("Category")
            Accessible.name: qsTr("Category")
            selectByMouse: true
            onTextChanged: {
                if (!root._syncing) {
                    root.category = text
                }
            }
        }
    }

    Label {
        Layout.fillWidth: true
        Layout.minimumWidth: 0
        visible: entriesViewModel.error !== ""
        text: entriesViewModel.error
        color: ThemeTokens.expenseRed
        wrapMode: Text.WordWrap
        font.pixelSize: ThemeTokens.fontSm
    }

    function loadEntry(data) {
        _syncing = true
        root.entryId = data.entryId || ""
        root.planId = data.planId || ""
        root.entryType = data.entryType || "income"
        root.name = data.name || ""
        root.datePattern = data.datePattern || ""
        root.amount = data.amount || 0
        root.currency = data.currency || "USD"
        root.category = data.category || ""
        nameField.text = root.name
        patternInput.text = root.datePattern
        amountField.text = root.amount === 0 ? "" : String(root.amount)
        var idx = currencyCombo.model.indexOf(root.currency)
        currencyCombo.currentIndex = idx >= 0 ? idx : 0
        categoryField.text = root.category
        _syncing = false
    }

    function save() {
        if (!root.canSave) {
            return
        }

        var categoryValue = categoryField.text.trim()
        var dto = {
            plan_id: root.planId,
            entry_type: root.entryType,
            name: nameField.text.trim(),
            date_pattern: patternInput.text,
            amount: parseFloat(amountField.text),
            currency: currencyCombo.model[currencyCombo.currentIndex],
            category: categoryValue === "" ? null : categoryValue
        }

        if (root.entryId === "") {
            entriesViewModel.createEntry(dto)
        } else {
            entriesViewModel.updateEntry(root.entryId, dto)
        }
    }
}
