import QtQuick
import QtQuick.Controls
import QtQuick.Controls.Material
import QtQuick.Layouts
import Qt5Compat.GraphicalEffects

import ThemeTokens 1.0

Item {
    id: root

    readonly property var snapshotModel: simulationViewModel.snapshotModel
    readonly property string currency: simulationViewModel.displayCurrency
    readonly property string displayCurrencyToken: simulationViewModel.displayCurrency
    readonly property bool isDark: Material.theme === Material.Dark
    readonly property color cardColor: isDark ? ThemeTokens.cardDark : ThemeTokens.cardLight

    readonly property int minMonthColumnWidth: 96
    readonly property int minMoneyColumnWidth: 100
    readonly property int columnGap: ThemeTokens.spaceMd
    readonly property int rowHeight: 40

    TextMetrics {
        id: monthColumnMetrics
        font.pixelSize: ThemeTokens.fontSm
    }

    property int layoutMonthColumnWidth: root.minMonthColumnWidth

    function recalculateMonthColumnWidth() {
        monthColumnMetrics.font.weight = ThemeTokens.weightSemiBold
        monthColumnMetrics.text = root.columnLabels[0]
        var contentWidth = monthColumnMetrics.advanceWidth
        monthColumnMetrics.font.weight = ThemeTokens.weightRegular
        for (var month = 1; month <= 12; month++) {
            monthColumnMetrics.text = root.monthLabel(9999, month)
            contentWidth = Math.max(contentWidth, monthColumnMetrics.advanceWidth)
        }
        var nextWidth = Math.max(
            root.minMonthColumnWidth,
            Math.ceil(contentWidth) + ThemeTokens.spaceMd * 2
        )
        if (nextWidth !== root.layoutMonthColumnWidth) {
            root.layoutMonthColumnWidth = nextWidth
        }
    }

    readonly property var columnLabels: [
        qsTr("Month"),
        qsTr("Income"),
        qsTr("Expense"),
        qsTr("Net"),
        qsTr("Balance")
    ]

    readonly property int layoutTableWidth: Math.max(
        layoutMonthColumnWidth + minMoneyColumnWidth * 4 + columnGap * 4,
        tableScroll.width
    )
    readonly property int layoutMoneyColumnWidth: Math.max(
        minMoneyColumnWidth,
        Math.floor(
            (layoutTableWidth - layoutMonthColumnWidth - columnGap * 4) / 4
        )
    )

    function columnWidthFor(column) {
        return column === 0 ? layoutMonthColumnWidth : layoutMoneyColumnWidth
    }

    implicitHeight: tableCard.implicitHeight

    function formatMoney(value) {
        var converted = simulationViewModel.convertToDisplayAmount(value)
        return qsTr("%1 %2").arg(Number(converted).toLocaleString(Qt.locale(), "f", 2)).arg(root.currency)
    }

    function monthLabel(year, month) {
        var monthNames = [
            qsTr("Jan"), qsTr("Feb"), qsTr("Mar"), qsTr("Apr"),
            qsTr("May"), qsTr("Jun"), qsTr("Jul"), qsTr("Aug"),
            qsTr("Sep"), qsTr("Oct"), qsTr("Nov"), qsTr("Dec")
        ]
        var monthIndex = month - 1
        if (monthIndex < 0 || monthIndex >= monthNames.length) {
            return year + "-" + month
        }
        return monthNames[monthIndex] + " " + year
    }

    function cellText(column, year, month, totalIncome, totalExpense, netFlow, closingBalance) {
        switch (column) {
        case 0:
            return root.monthLabel(year, month)
        case 1:
            return root.formatMoney(totalIncome)
        case 2:
            return root.formatMoney(totalExpense)
        case 3:
            return root.formatMoney(netFlow)
        case 4:
            return root.formatMoney(closingBalance)
        default:
            return ""
        }
    }

    function amountColor(column, totalIncome, totalExpense, netFlow, closingBalance) {
        switch (column) {
        case 1:
            return ThemeTokens.incomeGreen
        case 2:
            return ThemeTokens.expenseRed
        case 3:
            return netFlow > 0 ? ThemeTokens.incomeGreen : ThemeTokens.expenseRed
        case 4:
            return closingBalance > 0 ? ThemeTokens.incomeGreen : ThemeTokens.expenseRed
        default:
            return Material.foreground
        }
    }

    function rowBackgroundColor(rowIndex, deficit) {
        if (deficit) {
            return root.isDark ? ThemeTokens.deficitAmberBgDark : ThemeTokens.deficitAmberBg
        }
        if (rowIndex % 2 === 0) {
            return root.cardColor
        }
        return Qt.lighter(root.cardColor, 1.02)
    }

    function pageFlickable() {
        var current = root.parent
        while (current) {
            if (current !== tableScroll
                && current.contentY !== undefined
                && current.contentHeight !== undefined
                && typeof current.flick === "function") {
                return current
            }
            current = current.parent
        }
        return null
    }

    function wheelScrollStep(event) {
        if (event.pixelDelta.y !== 0) {
            return event.pixelDelta.y
        }
        if (event.angleDelta.y !== 0) {
            return event.angleDelta.y / 120 * root.rowHeight
        }
        return 0
    }

    Rectangle {
        id: tableCard
        width: parent.width
        implicitHeight: tableColumn.implicitHeight + ThemeTokens.spaceMd * 2
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
            id: tableColumn
            anchors.fill: parent
            anchors.margins: ThemeTokens.spaceMd
            spacing: ThemeTokens.spaceSm

            Label {
                Layout.fillWidth: true
                text: qsTr("Monthly summary")
                font.pixelSize: ThemeTokens.fontMd
                font.weight: ThemeTokens.weightSemiBold
            }

            Label {
                Layout.fillWidth: true
                visible: root.snapshotModel.count === 0
                text: qsTr("Run a forecast to see monthly snapshots.")
                color: Material.secondaryTextColor
                wrapMode: Text.WordWrap
            }

            Flickable {
                id: tableScroll
                Layout.fillWidth: true
                Layout.preferredHeight: Math.min(360, Math.max(120, root.snapshotModel.count * root.rowHeight + root.rowHeight))
                visible: root.snapshotModel.count > 0
                clip: true
                boundsBehavior: Flickable.StopAtBounds
                contentWidth: root.layoutTableWidth
                contentHeight: tableContent.height
                interactive: contentHeight > height + 1
                ScrollBar.horizontal: ScrollBar {
                    policy: ScrollBar.AsNeeded
                }
                ScrollBar.vertical: ScrollBar {
                    policy: ScrollBar.AsNeeded
                }

                onWidthChanged: tableView.forceLayout()

                WheelHandler {
                    onWheel: function(event) {
                        var page = root.pageFlickable()
                        if (!page) {
                            return
                        }

                        var step = root.wheelScrollStep(event)
                        if (step === 0) {
                            return
                        }

                        var canScrollInner = tableScroll.contentHeight > tableScroll.height + 1
                        var atTop = tableScroll.contentY <= 0
                        var atBottom = tableScroll.contentY
                            >= tableScroll.contentHeight - tableScroll.height - 1
                        var scrollingUp = step > 0
                        var scrollingDown = step < 0

                        if (!canScrollInner
                            || (scrollingUp && atTop)
                            || (scrollingDown && atBottom)) {
                            var maxY = Math.max(0, page.contentHeight - page.height)
                            page.contentY = Math.max(
                                0,
                                Math.min(maxY, page.contentY - step))
                            event.accepted = true
                        }
                    }
                }

                Column {
                    id: tableContent
                    width: root.layoutTableWidth
                    spacing: 0

                    Rectangle {
                        width: parent.width
                        height: root.rowHeight
                        color: "#1F6366F1"

                        Row {
                            anchors.fill: parent
                            spacing: root.columnGap

                            Repeater {
                                model: root.columnLabels.length

                                Label {
                                    required property int index
                                    width: root.columnWidthFor(index)
                                    height: root.rowHeight
                                    text: root.columnLabels[index]
                                    font.pixelSize: ThemeTokens.fontSm
                                    font.weight: ThemeTokens.weightSemiBold
                                    color: ThemeTokens.primary
                                    horizontalAlignment: index === 0 ? Text.AlignLeft : Text.AlignRight
                                    verticalAlignment: Text.AlignVCenter
                                    leftPadding: ThemeTokens.spaceMd
                                    rightPadding: ThemeTokens.spaceMd
                                    elide: index === 0 ? Text.ElideNone : Text.ElideRight
                                }
                            }
                        }
                    }

                    TableView {
                        id: tableView
                        width: parent.width
                        height: Math.max(root.rowHeight, root.snapshotModel.count * root.rowHeight)
                        clip: true
                        interactive: false
                        model: root.snapshotModel
                        columnSpacing: root.columnGap
                        rowSpacing: 0
                        boundsBehavior: Flickable.StopAtBounds

                        columnWidthProvider: function(column) {
                            return root.columnWidthFor(column)
                        }

                        onWidthChanged: forceLayout()

                        rowHeightProvider: function() {
                            return root.rowHeight
                        }

                        delegate: Rectangle {
                            id: cellDelegate
                            required property int row
                            required property int column
                            required property int year
                            required property int month
                            required property double totalIncome
                            required property double totalExpense
                            required property double netFlow
                            required property double closingBalance
                            required property bool deficit

                            implicitWidth: tableView.columnWidthProvider(column)
                            implicitHeight: tableView.rowHeightProvider(row)
                            color: root.rowBackgroundColor(row, deficit)

                            RowLayout {
                                anchors.fill: parent
                                anchors.leftMargin: ThemeTokens.spaceMd
                                anchors.rightMargin: ThemeTokens.spaceMd
                                spacing: ThemeTokens.spaceXs
                                visible: column === 4

                                Image {
                                    visible: deficit
                                    source: "qrc:/icons/warning.svg"
                                    Layout.preferredWidth: 16
                                    Layout.preferredHeight: 16
                                    fillMode: Image.PreserveAspectFit
                                    Accessible.name: qsTr("Cash shortfall warning")
                                }

                                Label {
                                    Layout.fillWidth: true
                                    text: {
                                        var _currency = root.displayCurrencyToken
                                        return root.formatMoney(closingBalance)
                                    }
                                    horizontalAlignment: Text.AlignRight
                                    font.pixelSize: ThemeTokens.fontSm
                                    elide: Text.ElideRight
                                    color: root.amountColor(
                                               column,
                                               totalIncome,
                                               totalExpense,
                                               netFlow,
                                               closingBalance)
                                }
                            }

                            Label {
                                anchors.fill: parent
                                anchors.leftMargin: ThemeTokens.spaceMd
                                anchors.rightMargin: ThemeTokens.spaceMd
                                visible: column !== 4
                                text: {
                                    var _currency = root.displayCurrencyToken
                                    return root.cellText(
                                        column,
                                        year,
                                        month,
                                        totalIncome,
                                        totalExpense,
                                        netFlow,
                                        closingBalance)
                                }
                                horizontalAlignment: column === 0 ? Text.AlignLeft : Text.AlignRight
                                verticalAlignment: Text.AlignVCenter
                                font.pixelSize: ThemeTokens.fontSm
                                elide: column === 0 ? Text.ElideNone : Text.ElideRight
                                color: column === 0
                                       ? Material.foreground
                                       : root.amountColor(
                                             column,
                                             totalIncome,
                                             totalExpense,
                                             netFlow,
                                             closingBalance)
                            }
                        }
                    }
                }
            }
        }
    }

    Component.onCompleted: root.recalculateMonthColumnWidth()

    Connections {
        target: settingsViewModel
        function onLanguageChanged() {
            root.recalculateMonthColumnWidth()
        }
    }
}
