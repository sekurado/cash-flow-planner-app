import QtQuick
import QtQuick.Controls
import QtQuick.Controls.Material
import QtQuick.Layouts
import Qt5Compat.GraphicalEffects

import ThemeTokens 1.0

Item {
    id: root

    readonly property var commonCurrencies: appViewModel.commonCurrencies

    readonly property int currencyColumnWidth: 108
    readonly property int rateColumnWidth: 108
    readonly property int updatedColumnWidth: 124
    readonly property int actionColumnWidth: 40
    readonly property int rowHeight: 48
    readonly property int tableContentWidth: currencyColumnWidth + rateColumnWidth
        + updatedColumnWidth + actionColumnWidth + ThemeTokens.spaceSm * 3

    property string baseCurrency: "USD"

    readonly property bool isDark: Material.theme === Material.Dark
    readonly property color cardColor: isDark ? ThemeTokens.cardDark : ThemeTokens.cardLight

    readonly property var rateModel: ratesViewModel ? ratesViewModel.rateListModel : null
    readonly property int rateCount: {
        if (!rateModel) {
            return 0
        }
        var modelCount = rateModel.count
        return modelCount === undefined ? 0 : modelCount
    }
    readonly property string ratesError: ratesViewModel ? ratesViewModel.error : ""
    readonly property bool canFetchLiveRates: settingsViewModel
        && settingsViewModel.liveRatesEnabled
        && settingsViewModel.liveRatesFetchAvailable
    readonly property bool isFetchingLiveRates: simulationViewModel
        && simulationViewModel.isFetchingRates

    implicitWidth: 0
    implicitHeight: editorCard.implicitHeight
    width: parent ? parent.width : 0

    Timer {
        id: fetchCooldownTimer
        interval: settingsViewModel && settingsViewModel.liveRatesDailyLimitReached ? 60000 : 1000
        running: settingsViewModel
            && settingsViewModel.liveRatesEnabled
            && !settingsViewModel.liveRatesFetchAvailable
        repeat: true
        onTriggered: settingsViewModel.refreshLiveRatesCooldown()
    }

    Connections {
        target: simulationViewModel
        function onIsFetchingRatesChanged() {
            if (simulationViewModel && !simulationViewModel.isFetchingRates) {
                if (settingsViewModel) {
                    settingsViewModel.refreshLiveRatesCooldown()
                }
            }
        }
        function onLiveRatesFetched() {
            if (ratesViewModel) {
                ratesViewModel.loadRates(root.baseCurrency)
            }
            if (settingsViewModel) {
                settingsViewModel.refreshLiveRatesCooldown()
            }
            if (simulationViewModel) {
                simulationViewModel.refreshDisplayCurrencies()
            }
        }
    }

    function formatRate(value) {
        if (isNaN(value)) {
            return ""
        }
        return Number(value).toFixed(4)
    }

    function resetAddForm() {
        addFromCombo.currentIndex = 0
        addRateField.text = ""
    }

    Rectangle {
        id: editorCard
        width: parent.width
        implicitHeight: editorColumn.implicitHeight + ThemeTokens.spaceMd * 2
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
            id: editorColumn
            anchors.left: parent.left
            anchors.right: parent.right
            anchors.top: parent.top
            anchors.margins: ThemeTokens.spaceMd
            spacing: ThemeTokens.spaceSm

            RowLayout {
                Layout.fillWidth: true
                spacing: ThemeTokens.spaceSm

                Button {
                    Layout.alignment: Qt.AlignLeft
                    flat: true
                    text: qsTr("+ Add currency")
                    Material.foreground: ThemeTokens.primary
                    Accessible.name: qsTr("Add exchange rate")
                    onClicked: {
                        resetAddForm()
                        addRateDialog.open()
                    }
                }

                Item {
                    Layout.fillWidth: true
                }

                Button {
                    visible: root.rateCount > 0
                    text: qsTr("Delete all")
                    flat: true
                    Material.foreground: Material.color(Material.Red)
                    Accessible.name: qsTr("Delete all exchange rates")
                    onClicked: deleteAllRatesDialog.open()
                }

                Button {
                    visible: settingsViewModel && settingsViewModel.liveRatesEnabled
                    text: root.isFetchingLiveRates ? qsTr("Fetching…") : qsTr("Fetch live rates")
                    enabled: root.baseCurrency !== ""
                        && root.canFetchLiveRates
                        && !root.isFetchingLiveRates
                    flat: true
                    Material.foreground: ThemeTokens.primary
                    Accessible.name: qsTr("Fetch live exchange rates")
                    onClicked: {
                        if (simulationViewModel) {
                            simulationViewModel.fetchLiveRates(root.baseCurrency)
                        }
                    }
                }
            }

            Label {
                Layout.fillWidth: true
                visible: settingsViewModel
                    && settingsViewModel.liveRatesEnabled
                    && !settingsViewModel.liveRatesFetchAvailable
                text: settingsViewModel.liveRatesDailyLimitReached
                    ? qsTr("Daily fetch limit reached (10 per day). Try again tomorrow.")
                    : (settingsViewModel.secondsUntilLiveRatesFetch < 60
                        ? qsTr("Next fetch available in %1 second(s).")
                            .arg(settingsViewModel.secondsUntilLiveRatesFetch)
                        : qsTr("Next fetch available in %1 minute(s).")
                            .arg(Math.ceil(settingsViewModel.secondsUntilLiveRatesFetch / 60)))
                color: Material.secondaryTextColor
                font.pixelSize: ThemeTokens.fontXs
                wrapMode: Text.WordWrap
            }

            Label {
                Layout.fillWidth: true
                visible: root.rateCount === 0
                text: qsTr("No exchange rates defined. Add a rate or fetch live rates.")
                color: Material.secondaryTextColor
                wrapMode: Text.WordWrap
            }

            Flickable {
                id: rateTableFlickable
                Layout.fillWidth: true
                Layout.minimumWidth: 0
                visible: root.rateCount > 0
                clip: true
                boundsBehavior: Flickable.StopAtBounds
                contentWidth: Math.max(width, root.tableContentWidth + ThemeTokens.spaceSm * 2)
                contentHeight: headerRow.height + rateList.height
                implicitHeight: contentHeight
                ScrollBar.horizontal: ScrollBar {
                    policy: ScrollBar.AsNeeded
                }

                Column {
                    width: Math.max(parent.width, root.tableContentWidth + ThemeTokens.spaceSm * 2)
                    spacing: 0

                    Row {
                        id: headerRow
                        width: parent.width
                        height: 28
                        spacing: ThemeTokens.spaceSm
                        leftPadding: ThemeTokens.spaceSm
                        rightPadding: ThemeTokens.spaceSm

                        Label {
                            width: root.currencyColumnWidth
                            height: parent.height
                            text: qsTr("Currency")
                            font.pixelSize: ThemeTokens.fontXs
                            font.weight: ThemeTokens.weightSemiBold
                            color: Material.secondaryTextColor
                            verticalAlignment: Text.AlignVCenter
                        }

                        Label {
                            width: root.rateColumnWidth
                            height: parent.height
                            text: qsTr("Rate")
                            font.pixelSize: ThemeTokens.fontXs
                            font.weight: ThemeTokens.weightSemiBold
                            color: Material.secondaryTextColor
                            verticalAlignment: Text.AlignVCenter
                        }

                        Label {
                            width: root.updatedColumnWidth
                            height: parent.height
                            text: qsTr("Updated")
                            font.pixelSize: ThemeTokens.fontXs
                            font.weight: ThemeTokens.weightSemiBold
                            color: Material.secondaryTextColor
                            verticalAlignment: Text.AlignVCenter
                        }

                        Item {
                            width: root.actionColumnWidth
                            height: parent.height
                        }
                    }

                    ListView {
                        id: rateList
                        width: parent.width
                        height: root.rateCount * root.rowHeight
                        clip: true
                        spacing: 0
                        model: root.rateModel
                        boundsBehavior: Flickable.StopAtBounds
                        interactive: false

                        delegate: Rectangle {
                        id: rateRow
                        required property string fromCurrency
                        required property string toCurrency
                        required property double rate
                        required property string updatedAt
                        required property int index

                        width: rateList.width
                        height: root.rowHeight
                        color: rateField.activeFocus
                            ? "#0D6366F1"
                            : (index % 2 === 0
                                ? root.cardColor
                                : Qt.lighter(root.cardColor, 1.02))

                        Row {
                            anchors.fill: parent
                            anchors.leftMargin: ThemeTokens.spaceSm
                            anchors.rightMargin: ThemeTokens.spaceSm
                            spacing: ThemeTokens.spaceSm

                            Label {
                                width: root.currencyColumnWidth
                                height: parent.height
                                text: rateRow.fromCurrency + " → " + rateRow.toCurrency
                                font.weight: ThemeTokens.weightSemiBold
                                color: ThemeTokens.primary
                                verticalAlignment: Text.AlignVCenter
                                elide: Text.ElideRight
                            }

                            Item {
                                width: root.rateColumnWidth
                                height: parent.height

                                TextInput {
                                    id: rateField
                                    anchors.right: parent.right
                                    anchors.verticalCenter: parent.verticalCenter
                                    width: parent.width
                                    horizontalAlignment: TextInput.AlignRight
                                    text: root.formatRate(rateRow.rate)
                                    font.pixelSize: ThemeTokens.fontMd
                                    color: Material.foreground
                                    inputMethodHints: Qt.ImhFormattedNumbersOnly
                                    selectByMouse: true
                                    Accessible.name: qsTr("Exchange rate value")
                                    onEditingFinished: {
                                        var parsed = parseFloat(text)
                                        if (isNaN(parsed) || parsed === rateRow.rate) {
                                            text = root.formatRate(rateRow.rate)
                                            return
                                        }
                                        if (ratesViewModel) {
                                            ratesViewModel.updateRate(
                                                rateRow.fromCurrency,
                                                rateRow.toCurrency,
                                                parsed
                                            )
                                        }
                                    }
                                }

                                Rectangle {
                                    anchors.bottom: rateField.bottom
                                    anchors.left: rateField.left
                                    anchors.right: rateField.right
                                    height: rateField.activeFocus ? 2 : 1
                                    color: rateField.activeFocus
                                        ? ThemeTokens.primary
                                        : Material.dividerColor
                                }
                            }

                            Label {
                                width: root.updatedColumnWidth
                                height: parent.height
                                text: rateRow.updatedAt
                                font.pixelSize: ThemeTokens.fontXs
                                color: Material.secondaryTextColor
                                verticalAlignment: Text.AlignVCenter
                                elide: Text.ElideRight
                            }

                            ToolButton {
                                width: root.actionColumnWidth
                                height: parent.height
                                icon.name: "edit-delete"
                                Accessible.name: qsTr("Delete exchange rate")
                                onClicked: {
                                    if (ratesViewModel) {
                                        ratesViewModel.deleteRate(
                                            rateRow.fromCurrency,
                                            rateRow.toCurrency
                                        )
                                    }
                                }
                            }
                        }
                    }
                }
            }
            }

            Label {
                Layout.fillWidth: true
                visible: root.ratesError !== ""
                text: root.ratesError
                color: Material.color(Material.Red)
                wrapMode: Text.WordWrap
                font.pixelSize: ThemeTokens.fontXs
            }
        }
    }

    CenteredDialog {
        id: deleteAllRatesDialog
        title: qsTr("Delete all exchange rates?")
        standardButtons: Dialog.NoButton
        width: 360

        contentItem: ColumnLayout {
            spacing: ThemeTokens.spaceSm
            width: 320

            Label {
                Layout.fillWidth: true
                text: qsTr("This removes every exchange rate from the app. Forecast runs with multi-currency cash flows may fail until you add rates again.")
                wrapMode: Text.WordWrap
            }
        }

        footer: DialogButtonBox {
            Button {
                text: qsTr("Cancel")
                flat: true
                DialogButtonBox.buttonRole: DialogButtonBox.RejectRole
                onClicked: deleteAllRatesDialog.close()
            }

            Button {
                text: qsTr("Delete all")
                Material.background: Material.color(Material.Red)
                Material.foreground: "white"
                DialogButtonBox.buttonRole: DialogButtonBox.DestructiveRole
                Accessible.name: qsTr("Confirm delete all exchange rates")
                onClicked: {
                    if (ratesViewModel) {
                        ratesViewModel.deleteAllRates()
                    }
                    deleteAllRatesDialog.close()
                    if (simulationViewModel) {
                        simulationViewModel.refreshDisplayCurrencies()
                    }
                }
            }
        }
    }

    CenteredDialog {
        id: addRateDialog
        title: qsTr("Add exchange rate")
        standardButtons: Dialog.NoButton
        width: 360

        onAboutToShow: resetAddForm()

        contentItem: ColumnLayout {
            spacing: 12
            width: 320

            Label {
                Layout.fillWidth: true
                text: qsTr("From currency")
                font.pixelSize: ThemeTokens.fontXs
                color: Material.secondaryTextColor
            }

            ComboBox {
                id: addFromCombo
                Layout.fillWidth: true
                model: root.commonCurrencies
                Accessible.name: qsTr("From currency")
            }

            Label {
                Layout.fillWidth: true
                text: qsTr("To currency")
                font.pixelSize: ThemeTokens.fontXs
                color: Material.secondaryTextColor
            }

            Label {
                Layout.fillWidth: true
                text: root.baseCurrency
                font.pixelSize: ThemeTokens.fontMd
                font.weight: ThemeTokens.weightSemiBold
                Accessible.name: qsTr("To currency")
            }

            Label {
                Layout.fillWidth: true
                text: qsTr("Rate")
                font.pixelSize: ThemeTokens.fontXs
                color: Material.secondaryTextColor
            }

            TextField {
                id: addRateField
                Layout.fillWidth: true
                placeholderText: qsTr("0.00")
                inputMethodHints: Qt.ImhFormattedNumbersOnly
                selectByMouse: true
                Accessible.name: qsTr("Exchange rate")
            }
        }

        footer: DialogButtonBox {
            Button {
                text: qsTr("Cancel")
                DialogButtonBox.buttonRole: DialogButtonBox.RejectRole
                onClicked: addRateDialog.close()
            }

            Button {
                text: qsTr("Save")
                enabled: addRateField.text.trim() !== "" && !isNaN(parseFloat(addRateField.text))
                Material.background: ThemeTokens.primary
                Material.foreground: "white"
                DialogButtonBox.buttonRole: DialogButtonBox.AcceptRole
                Accessible.name: qsTr("Save exchange rate")
                onClicked: {
                    var parsedRate = parseFloat(addRateField.text)
                    if (isNaN(parsedRate) || !ratesViewModel) {
                        return
                    }
                    ratesViewModel.createRate(
                        addFromCombo.model[addFromCombo.currentIndex],
                        root.baseCurrency,
                        parsedRate
                    )
                    addRateDialog.close()
                }

                background: Rectangle {
                    radius: ThemeTokens.radiusSm
                    color: parent.Material.background
                }
            }
        }
    }

    onBaseCurrencyChanged: {
        if (ratesViewModel && root.baseCurrency !== "") {
            ratesViewModel.loadRates(root.baseCurrency)
        }
        if (simulationViewModel) {
            simulationViewModel.refreshDisplayCurrencies()
        }
    }

    Component.onCompleted: {
        if (settingsViewModel) {
            settingsViewModel.refreshLiveRatesCooldown()
        }
        if (ratesViewModel && root.baseCurrency !== "") {
            ratesViewModel.loadRates(root.baseCurrency)
        }
        if (simulationViewModel) {
            simulationViewModel.refreshDisplayCurrencies()
        }
    }
}
