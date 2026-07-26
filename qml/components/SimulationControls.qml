import QtQuick
import QtQuick.Controls
import QtQuick.Controls.Material
import QtQuick.Layouts
import Qt5Compat.GraphicalEffects

import ThemeTokens 1.0
import "."

Item {
    id: root

    signal exportCsvClicked()
    signal exportPdfClicked()

    readonly property var plan: planViewModel.selectedPlan
    readonly property string planId: plan ? plan.id : ""
    readonly property bool canExport: simulationViewModel.result !== null
                                    && !simulationViewModel.isRunning
    readonly property bool isDark: Material.theme === Material.Dark
    readonly property color cardColor: isDark ? ThemeTokens.cardDark : ThemeTokens.cardLight

    readonly property var today: {
        var d = new Date()
        d.setHours(0, 0, 0, 0)
        return d
    }

    readonly property var maxEndDate: {
        var d = new Date(root.today.getTime())
        d.setFullYear(d.getFullYear() + 10)
        return d
    }

    readonly property var startDate: root.pickerDate(startDatePicker)
    readonly property var endDate: root.pickerDate(endDatePicker)
    readonly property bool datesValid: root.endDate.getTime() >= root.startDate.getTime()

    implicitHeight: controlsCard.implicitHeight
                    + (datesErrorLabel.visible ? datesErrorLabel.implicitHeight + ThemeTokens.spaceSm : 0)

    function pad2(value) {
        return value < 10 ? "0" + value : "" + value
    }

    function pickerDate(picker) {
        return new Date(picker.year, picker.month - 1, picker.day)
    }

    function formatIsoDate(picker) {
        return picker.year + "-" + root.pad2(picker.month) + "-" + root.pad2(picker.day)
    }

    function setPickerToDate(picker, jsDate) {
        picker.year = jsDate.getFullYear()
        picker.month = jsDate.getMonth() + 1
        picker.day = jsDate.getDate()
    }

    function clampEndPicker() {
        if (root.endDate.getTime() > root.maxEndDate.getTime()) {
            root.setPickerToDate(endDatePicker, root.maxEndDate)
        }
        if (root.endDate.getTime() < root.startDate.getTime()) {
            root.setPickerToDate(endDatePicker, root.startDate)
        }
    }

    function syncEndDateWithStart() {
        if (root.endDate.getTime() < root.startDate.getTime()) {
            root.setPickerToDate(endDatePicker, root.startDate)
        }
    }

    function runSimulation() {
        if (root.planId === "" || !root.datesValid || simulationViewModel.isRunning) {
            return
        }
        var params = root.buildSimulationParams()
        if (!params) {
            return
        }
        simulationViewModel.runSimulation(root.planId, params)
    }

    function buildSimulationParams() {
        if (root.planId === "" || !root.datesValid) {
            return null
        }
        var balance = parseFloat(initialBalanceField.text)
        if (isNaN(balance)) {
            return null
        }
        return {
            start_date: root.formatIsoDate(startDatePicker),
            end_date: root.formatIsoDate(endDatePicker),
            initial_balance: balance,
            base_currency: plan.base_currency
        }
    }

    Rectangle {
        id: controlsCard
        width: parent.width
        implicitHeight: controlsRow.implicitHeight + ThemeTokens.spaceMd * 2
        radius: ThemeTokens.radiusLg
        color: root.cardColor
        clip: true
        layer.enabled: true
        layer.effect: DropShadow {
            radius: 8
            samples: 17
            color: "#18000000"
            verticalOffset: 2
        }

        ColumnLayout {
            id: controlsRow
            anchors.fill: parent
            anchors.margins: ThemeTokens.spaceMd
            spacing: ThemeTokens.spaceMd

            RowLayout {
                Layout.fillWidth: true
                spacing: ThemeTokens.spaceMd

                ColumnLayout {
                    spacing: ThemeTokens.spaceXs

                    Text {
                        text: qsTr("Start date")
                        font.pixelSize: ThemeTokens.fontXs
                        color: Material.secondaryTextColor
                    }

                    DatePicker {
                        id: startDatePicker

                        onDayChanged: root.syncEndDateWithStart()
                        onMonthChanged: root.syncEndDateWithStart()
                        onYearChanged: root.syncEndDateWithStart()
                    }
                }

                ColumnLayout {
                    spacing: ThemeTokens.spaceXs

                    Text {
                        text: qsTr("End date")
                        font.pixelSize: ThemeTokens.fontXs
                        color: Material.secondaryTextColor
                    }

                    DatePicker {
                        id: endDatePicker

                        onDayChanged: root.clampEndPicker()
                        onMonthChanged: root.clampEndPicker()
                        onYearChanged: root.clampEndPicker()
                    }
                }

                ColumnLayout {
                    spacing: ThemeTokens.spaceXs

                    Text {
                        text: qsTr("Initial balance")
                        font.pixelSize: ThemeTokens.fontXs
                        color: Material.secondaryTextColor
                    }

                    Item {
                        id: initialBalanceField
                        Layout.preferredWidth: 120
                        Layout.preferredHeight: startDatePicker.implicitHeight

                        property alias text: balanceInput.text

                        Rectangle {
                            anchors.fill: parent
                            radius: ThemeTokens.radiusSm
                            color: "transparent"
                            border.color: ThemeTokens.primary
                            border.width: 1
                        }

                        TextInput {
                            id: balanceInput
                            anchors.fill: parent
                            anchors.leftMargin: ThemeTokens.spaceSm
                            anchors.rightMargin: ThemeTokens.spaceSm
                            verticalAlignment: Text.AlignVCenter
                            inputMethodHints: Qt.ImhFormattedNumbersOnly
                            selectByMouse: true
                            font.pixelSize: ThemeTokens.fontSm
                            color: Material.foreground
                            Accessible.name: qsTr("Initial balance")
                        }

                        Text {
                            anchors.left: parent.left
                            anchors.right: parent.right
                            anchors.verticalCenter: parent.verticalCenter
                            anchors.leftMargin: ThemeTokens.spaceSm
                            anchors.rightMargin: ThemeTokens.spaceSm
                            text: qsTr("0.00")
                            font.pixelSize: ThemeTokens.fontSm
                            color: Material.secondaryTextColor
                            visible: balanceInput.text.length === 0 && !balanceInput.activeFocus
                        }
                    }
                }

                ColumnLayout {
                    spacing: ThemeTokens.spaceXs

                    Text {
                        text: qsTr("Display currency")
                        font.pixelSize: ThemeTokens.fontXs
                        color: Material.secondaryTextColor
                    }

                    ComboBox {
                        id: displayCurrencyCombo
                        Layout.preferredWidth: 108
                        model: simulationViewModel.displayCurrencies
                        enabled: model.length > 0
                        Accessible.name: qsTr("Display currency")

                        function syncIndex() {
                            var idx = model.indexOf(simulationViewModel.displayCurrency)
                            if (idx >= 0) {
                                currentIndex = idx
                            }
                        }

                        Component.onCompleted: syncIndex()

                        Connections {
                            target: simulationViewModel
                            function onDisplayCurrenciesChanged() {
                                displayCurrencyCombo.syncIndex()
                            }
                            function onDisplayCurrencyChanged() {
                                displayCurrencyCombo.syncIndex()
                            }
                        }

                        onActivated: {
                            simulationViewModel.setDisplayCurrency(
                                model[currentIndex])
                        }
                    }
                }

                Item {
                    Layout.fillWidth: true
                    Layout.minimumWidth: 0
                }
            }

            RowLayout {
                Layout.fillWidth: true
                spacing: ThemeTokens.spaceSm

                Item {
                    Layout.fillWidth: true
                    Layout.minimumWidth: 0
                }

                Item {
                    id: runButtonContainer
                    Layout.preferredHeight: 36
                    Layout.preferredWidth: runButton.implicitWidth

                    Button {
                        id: runButton
                        anchors.fill: parent
                        text: qsTr("Run forecast")
                        enabled: root.planId !== ""
                                 && root.datesValid
                                 && !simulationViewModel.isRunning
                        Accessible.name: qsTr("Run forecast")
                        Material.background: ThemeTokens.primary
                        Material.foreground: "white"
                        Material.elevation: 0
                        topInset: 0
                        bottomInset: 0
                        leftInset: 0
                        rightInset: 0
                        topPadding: 0
                        bottomPadding: 0
                        leftPadding: ThemeTokens.spaceMd
                        rightPadding: ThemeTokens.spaceMd
                        font.pixelSize: ThemeTokens.fontSm
                        font.weight: ThemeTokens.weightSemiBold
                        onClicked: root.runSimulation()

                        background: Rectangle {
                            anchors.fill: parent
                            radius: ThemeTokens.radiusFull
                            color: runButton.Material.background
                            opacity: runButton.enabled ? 1.0 : 0.45
                        }
                    }

                    BusyIndicator {
                        anchors.centerIn: parent
                        width: 18
                        height: 18
                        running: simulationViewModel.isRunning
                        visible: simulationViewModel.isRunning
                        Material.foreground: "white"
                    }
                }

                Button {
                    padding: ThemeTokens.spaceXs
                    leftPadding: ThemeTokens.spaceSm
                    rightPadding: ThemeTokens.spaceSm
                    font.pixelSize: ThemeTokens.fontSm
                    text: qsTr("Export CSV")
                    flat: true
                    enabled: root.canExport
                    Material.foreground: ThemeTokens.primary
                    Accessible.name: qsTr("Export CSV")
                    onClicked: root.exportCsvClicked()

                    background: Rectangle {
                        anchors.fill: parent
                        radius: ThemeTokens.radiusSm
                        color: "transparent"
                        border.color: ThemeTokens.primary
                        border.width: 1
                        opacity: parent.enabled ? 1.0 : 0.45
                    }
                }

                Button {
                    padding: ThemeTokens.spaceXs
                    leftPadding: ThemeTokens.spaceSm
                    rightPadding: ThemeTokens.spaceSm
                    font.pixelSize: ThemeTokens.fontSm
                    text: qsTr("Export executive report")
                    flat: true
                    enabled: root.canExport
                    Material.foreground: ThemeTokens.primary
                    Accessible.name: qsTr("Export executive report")
                    onClicked: root.exportPdfClicked()

                    background: Rectangle {
                        anchors.fill: parent
                        radius: ThemeTokens.radiusSm
                        color: "transparent"
                        border.color: ThemeTokens.primary
                        border.width: 1
                        opacity: parent.enabled ? 1.0 : 0.45
                    }
                }
            }
        }
    }

    Label {
        id: datesErrorLabel
        anchors.top: controlsCard.bottom
        anchors.topMargin: ThemeTokens.spaceSm
        width: parent.width
        visible: !root.datesValid
        text: qsTr("End date must be on or after the start date.")
        color: Material.color(Material.Red)
        font.pixelSize: ThemeTokens.fontXs
        wrapMode: Text.WordWrap
    }

    Connections {
        target: planViewModel
        function onSelectedPlanChanged() {
            if (root.plan) {
                initialBalanceField.text = String(root.plan.initial_balance)
            }
        }
    }

    Component.onCompleted: {
        root.setPickerToDate(startDatePicker, root.today)
        var defaultEnd = new Date(root.today.getTime())
        defaultEnd.setFullYear(defaultEnd.getFullYear() + 1)
        if (defaultEnd.getTime() > root.maxEndDate.getTime()) {
            defaultEnd = root.maxEndDate
        }
        root.setPickerToDate(endDatePicker, defaultEnd)
        if (root.plan) {
            initialBalanceField.text = String(root.plan.initial_balance)
        }
    }
}
