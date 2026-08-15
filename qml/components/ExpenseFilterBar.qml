import QtQuick
import QtQuick.Controls
import QtQuick.Controls.Material
import QtQuick.Layouts

import ThemeTokens 1.0
import "."

ColumnLayout {
    id: root

    readonly property bool isDark: Material.theme === Material.Dark
    readonly property color cardColor: isDark ? ThemeTokens.cardDark : ThemeTokens.cardLight

    property bool customRangeActive: false
    property bool _syncingSearch: false

    spacing: ThemeTokens.spaceSm

    function setSearchFieldSilently(value) {
        _syncingSearch = true
        searchField.text = value
        _syncingSearch = false
    }

    function pad2(value) {
        return value < 10 ? "0" + value : "" + value
    }

    function pickerDate(picker) {
        return picker.year + "-" + pad2(picker.month) + "-" + pad2(picker.day)
    }

    function setPickerToIso(picker, isoDate) {
        if (!isoDate || isoDate === "") {
            return
        }
        var parts = isoDate.split("-")
        if (parts.length !== 3) {
            return
        }
        picker.year = parseInt(parts[0], 10)
        picker.month = parseInt(parts[1], 10)
        picker.day = parseInt(parts[2], 10)
    }

    function syncAnalyticsDateRange() {
        if (recordedExpensesViewModel.filterStartDate === ""
                || recordedExpensesViewModel.filterEndDate === "") {
            return
        }
        expenseAnalyticsViewModel.setDateRange(
            recordedExpensesViewModel.filterStartDate,
            recordedExpensesViewModel.filterEndDate
        )
    }

    function applyPreset(preset) {
        if (preset === "custom") {
            customRangeActive = true
            return
        }
        customRangeActive = false
        recordedExpensesViewModel.applyDatePreset(preset)
        syncAnalyticsDateRange()
    }

    function applyCustomDateRange() {
        recordedExpensesViewModel.setFilterDateRange(
            pickerDate(startDatePicker),
            pickerDate(endDatePicker)
        )
        syncAnalyticsDateRange()
    }

    Rectangle {
        Layout.fillWidth: true
        Layout.preferredHeight: filterColumn.implicitHeight + ThemeTokens.spaceMd * 2
        radius: ThemeTokens.radiusLg
        color: root.cardColor
        border.color: Material.dividerColor
        border.width: 1

        ColumnLayout {
            id: filterColumn
            anchors.fill: parent
            anchors.margins: ThemeTokens.spaceMd
            spacing: ThemeTokens.spaceSm

            TextField {
                id: searchField
                Layout.fillWidth: true
                placeholderText: qsTr("Search name, category, place, or note")
                Accessible.name: qsTr("Search expenses")
                selectByMouse: true

                onTextChanged: {
                    if (root._syncingSearch) {
                        return
                    }
                    recordedExpensesViewModel.setSearchText(text)
                }
            }

            Flow {
                Layout.fillWidth: true
                spacing: ThemeTokens.spaceXs

                Repeater {
                    model: [
                        { id: "this_month", label: qsTr("This month") },
                        { id: "last_30_days", label: qsTr("Last 30 days") },
                        { id: "ytd", label: qsTr("Year to date") },
                        { id: "custom", label: qsTr("Custom") }
                    ]

                    delegate: Button {
                        required property var modelData

                        text: modelData.label
                        flat: true
                        Material.background: root.customRangeActive && modelData.id === "custom"
                            ? Qt.rgba(
                                ThemeTokens.primary.r,
                                ThemeTokens.primary.g,
                                ThemeTokens.primary.b,
                                0.12)
                            : "transparent"
                        onClicked: root.applyPreset(modelData.id)
                    }
                }
            }

            RowLayout {
                Layout.fillWidth: true
                visible: root.customRangeActive
                spacing: ThemeTokens.spaceSm

                ColumnLayout {
                    Layout.fillWidth: true
                    spacing: ThemeTokens.spaceXs

                    Label {
                        text: qsTr("From")
                        font.pixelSize: ThemeTokens.fontSm
                        color: Material.secondaryTextColor
                    }

                    DatePicker {
                        id: startDatePicker
                        Layout.fillWidth: true
                        Layout.preferredHeight: implicitHeight
                        stacked: true
                    }
                }

                ColumnLayout {
                    Layout.fillWidth: true
                    spacing: ThemeTokens.spaceXs

                    Label {
                        text: qsTr("To")
                        font.pixelSize: ThemeTokens.fontSm
                        color: Material.secondaryTextColor
                    }

                    DatePicker {
                        id: endDatePicker
                        Layout.fillWidth: true
                        Layout.preferredHeight: implicitHeight
                        stacked: true
                    }
                }

                Button {
                    text: qsTr("Apply")
                    onClicked: root.applyCustomDateRange()
                }
            }

            Button {
                Layout.alignment: Qt.AlignLeft
                visible: recordedExpensesViewModel.hasActiveFilters
                text: qsTr("Clear filters")
                flat: true
                onClicked: {
                    customRangeActive = false
                    recordedExpensesViewModel.clearFilters()
                }
            }
        }
    }

    Connections {
        target: recordedExpensesViewModel
        function onFilterDateRangeChanged() {
            root.setPickerToIso(startDatePicker, recordedExpensesViewModel.filterStartDate)
            root.setPickerToIso(endDatePicker, recordedExpensesViewModel.filterEndDate)
        }

        function onSearchTextChanged() {
            if (searchField.text !== recordedExpensesViewModel.searchText) {
                root.setSearchFieldSilently(recordedExpensesViewModel.searchText)
            }
        }
    }

    Component.onCompleted: {
        root.setSearchFieldSilently(recordedExpensesViewModel.searchText)
    }
}
