import QtQuick
import QtQuick.Controls
import QtQuick.Controls.Material
import QtQuick.Layouts
import QtCharts
import Qt5Compat.GraphicalEffects

import ThemeTokens 1.0

Item {
    id: root

    property string title: ""
    property var series: []
    property string displayCurrency: "USD"
    property string emptyMessage: qsTr("No spending in this period.")
    property real categoryLabelMargin: 88
    property real valueAxisBottomMargin: 28
    property real categoryAxisEdgeMargin: 16
    readonly property int categoryRowHeight: 36

    readonly property bool hasData: series !== undefined && series !== null && series.length > 0
    readonly property bool isDark: Material.theme === Material.Dark
    readonly property color cardColor: isDark ? ThemeTokens.cardDark : ThemeTokens.cardLight
    readonly property string accessibleSummary: {
        if (!root.hasData) {
            return root.emptyMessage
        }
        var parts = []
        for (var i = 0; i < root.series.length; i++) {
            var item = root.series[i]
            parts.push(root.displayLabel(item.label) + ": "
                         + Number(item.totalAmount).toLocaleString(Qt.locale(), "f", 2)
                         + " " + root.displayCurrency)
        }
        return parts.join("; ")
    }

    implicitWidth: 320
    implicitHeight: chartColumn.implicitHeight + ThemeTokens.spaceMd * 2

    function displayLabel(rawLabel) {
        if (rawLabel === "Other") {
            return qsTr("Other")
        }
        return rawLabel
    }

    function formatAxisValue(value) {
        return Number(value).toLocaleString(Qt.locale(), "f", 0)
    }

    function chartContentHeight() {
        if (!root.hasData) {
            return 0
        }
        // Extra row of space keeps first/last category labels inside the plot area.
        return (root.series.length + 1) * root.categoryRowHeight
    }

    function valueAxisTickCount() {
        var chartWidth = Math.max(chartView.width, root.width) - root.categoryLabelMargin - 16
        if (chartWidth <= 0) {
            return 3
        }
        return Math.max(3, Math.min(5, Math.floor(chartWidth / 72)))
    }

    function maxCategoryLabelWidth() {
        var widest = 72
        for (var i = 0; i < root.series.length; i++) {
            labelMeasure.text = root.displayLabel(root.series[i].label)
            widest = Math.max(widest, labelMeasure.implicitWidth + ThemeTokens.spaceSm)
        }
        var maxAllowed = Math.max(120, Math.max(chartView.width, root.width) * 0.5)
        return Math.min(widest, maxAllowed)
    }

    function rebuildChart() {
        spendSet.remove(0, spendSet.count)
        categoryAxis.categories = []
        axisX.min = 0
        axisX.max = 1

        if (!root.hasData) {
            return
        }

        var categories = []
        var maxValue = 0
        for (var i = root.series.length - 1; i >= 0; i--) {
            var item = root.series[i]
            var amount = Number(item.totalAmount)
            categories.push(root.displayLabel(item.label))
            spendSet.append(amount)
            maxValue = Math.max(maxValue, amount)
        }

        categoryAxis.categories = categories
        axisX.max = maxValue > 0 ? maxValue * 1.1 : 1
        axisX.tickCount = valueAxisTickCount()
        root.categoryLabelMargin = maxCategoryLabelWidth()
        valueLabelMeasure.text = formatAxisValue(axisX.max)
        root.valueAxisBottomMargin = valueLabelMeasure.implicitHeight + ThemeTokens.spaceSm
        root.categoryAxisEdgeMargin = Math.max(
            ThemeTokens.spaceMd,
            Math.ceil(root.categoryRowHeight / 2)
        )
    }

    Text {
        id: labelMeasure
        visible: false
        font.pixelSize: ThemeTokens.fontXs
    }

    Text {
        id: valueLabelMeasure
        visible: false
        font.pixelSize: ThemeTokens.fontXs
    }

    Rectangle {
        anchors.fill: parent
        radius: ThemeTokens.radiusLg
        color: root.cardColor
        border.color: Material.dividerColor
        border.width: 1
        layer.enabled: true
        layer.effect: DropShadow {
            radius: 8
            samples: 17
            color: "#18000000"
            verticalOffset: 2
        }
    }

    ColumnLayout {
        id: chartColumn
        anchors.fill: parent
        anchors.margins: ThemeTokens.spaceMd
        spacing: ThemeTokens.spaceSm

        Label {
            Layout.fillWidth: true
            text: root.title
            font.pixelSize: ThemeTokens.fontMd
            font.weight: ThemeTokens.weightSemiBold
        }

        Label {
            Layout.fillWidth: true
            Layout.preferredHeight: root.hasData ? 0 : 72
            visible: !root.hasData
            text: root.emptyMessage
            color: Material.secondaryTextColor
            horizontalAlignment: Text.AlignHCenter
            verticalAlignment: Text.AlignVCenter
            wrapMode: Text.WordWrap
        }

        ChartView {
            id: chartView
            Layout.fillWidth: true
            Layout.preferredHeight: root.hasData
                ? root.chartContentHeight() + root.categoryAxisEdgeMargin + root.valueAxisBottomMargin
                : 0
            visible: root.hasData
            antialiasing: true
            legend.visible: false
            backgroundColor: root.cardColor
            plotAreaColor: "transparent"
            margins {
                top: root.categoryAxisEdgeMargin
                bottom: root.valueAxisBottomMargin
                left: root.categoryLabelMargin
                right: 12
            }
            Accessible.ignored: false
            Accessible.role: Accessible.Graphic
            Accessible.name: root.title
            Accessible.description: root.accessibleSummary

            ValueAxis {
                id: axisX
                min: 0
                max: 1
                tickCount: 4
                labelFormat: "%.0f"
                truncateLabels: false
                labelsFont.pixelSize: ThemeTokens.fontXs
            }

            BarCategoryAxis {
                id: categoryAxis
                categories: []
                truncateLabels: false
                labelsFont.pixelSize: ThemeTokens.fontXs
            }

            HorizontalBarSeries {
                id: barSeries
                axisX: axisX
                axisY: categoryAxis
                barWidth: 0.55

                BarSet {
                    id: spendSet
                    color: ThemeTokens.chartPositive
                }
            }
        }

        Label {
            Layout.fillWidth: true
            visible: root.hasData
            text: qsTr("Amount (%1)").arg(root.displayCurrency)
            horizontalAlignment: Text.AlignHCenter
            font.pixelSize: ThemeTokens.fontXs
            color: Material.secondaryTextColor
        }
    }

    onSeriesChanged: rebuildChart()

    onDisplayCurrencyChanged: {
        if (root.hasData) {
            rebuildChart()
        }
    }

    onWidthChanged: {
        if (root.hasData) {
            rebuildChart()
        }
    }

    Component.onCompleted: rebuildChart()
}
