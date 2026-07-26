import QtQuick
import QtQuick.Controls
import QtQuick.Controls.Material
import QtQuick.Layouts
import QtCharts
import Qt5Compat.GraphicalEffects

import ThemeTokens 1.0

Item {
    id: root

    readonly property var result: simulationViewModel.result
    readonly property string displayCurrency: simulationViewModel.displayCurrency
    readonly property bool hasChartData: result !== null
                                       && result !== undefined
                                       && result.daily_balances
                                       && result.daily_balances.length > 0
    readonly property bool isDark: Material.theme === Material.Dark
    readonly property color cardColor: isDark ? ThemeTokens.cardDark : ThemeTokens.cardLight

    property int hoverIndex: -1
    readonly property bool hoverActive: hoverIndex >= 0 && root.hasChartData
    readonly property real hoverGuideX: {
        if (!root.hoverActive) {
            return 0
        }
        var point = result.daily_balances[hoverIndex]
        return root.timestampToPlotX(new Date(point.date).getTime())
    }
    readonly property string hoverDateText: {
        if (!root.hoverActive) {
            return ""
        }
        return root.formatHoverDate(result.daily_balances[hoverIndex].date)
    }
    readonly property string hoverBalanceText: {
        if (!root.hoverActive) {
            return ""
        }
        var balance = simulationViewModel.convertToDisplayAmount(
            Number(result.daily_balances[hoverIndex].closing_balance)
        )
        return root.formatHoverBalance(balance)
    }

    implicitHeight: 250

    Gradient {
        id: positiveGradient
        orientation: Gradient.Vertical
        GradientStop {
            position: 0.0
            color: "#336366F1"
        }
        GradientStop {
            position: 1.0
            color: "#006366F1"
        }
    }

    Gradient {
        id: deficitGradient
        orientation: Gradient.Vertical
        GradientStop {
            position: 0.0
            color: ThemeTokens.chartNegTop
        }
        GradientStop {
            position: 1.0
            color: ThemeTokens.chartNegBot
        }
    }

    function clearHoverState() {
        hoverIndex = -1
    }

    function formatHoverDate(dateStr) {
        return Qt.formatDate(new Date(dateStr), "dd MMM yy")
    }

    function formatHoverBalance(balance) {
        return qsTr("%1 %2").arg(
            Number(balance).toLocaleString(Qt.locale(), "f", 2)
        ).arg(root.displayCurrency)
    }

    function timestampToPlotX(timestamp) {
        var minT = axisX.min.getTime()
        var maxT = axisX.max.getTime()
        if (maxT === minT || plotHoverOverlay.width <= 0) {
            return 0
        }
        return (timestamp - minT) / (maxT - minT) * plotHoverOverlay.width
    }

    function plotXToTimestamp(plotX) {
        var minT = axisX.min.getTime()
        var maxT = axisX.max.getTime()
        var ratio = plotX / plotHoverOverlay.width
        return minT + ratio * (maxT - minT)
    }

    function findNearestPointIndex(targetTimestamp) {
        var points = result.daily_balances
        var count = points.length
        if (count === 0) {
            return -1
        }
        if (count === 1) {
            return 0
        }

        var lo = 0
        var hi = count - 1
        while (lo < hi) {
            var mid = Math.floor((lo + hi) / 2)
            var midT = new Date(points[mid].date).getTime()
            if (midT < targetTimestamp) {
                lo = mid + 1
            } else {
                hi = mid
            }
        }

        if (lo > 0) {
            var prevT = new Date(points[lo - 1].date).getTime()
            var currT = new Date(points[lo].date).getTime()
            if (Math.abs(targetTimestamp - prevT) < Math.abs(currT - targetTimestamp)) {
                return lo - 1
            }
        }
        return lo
    }

    function updateHoverFromMouseX(mouseX) {
        if (!root.hasChartData || plotHoverOverlay.width <= 0) {
            clearHoverState()
            return
        }
        var clampedX = Math.max(0, Math.min(mouseX, plotHoverOverlay.width))
        hoverIndex = findNearestPointIndex(plotXToTimestamp(clampedX))
    }

    function rebuildChart() {
        clearHoverState()
        chartView.removeAllSeries()

        if (!root.hasChartData) {
            return
        }

        var points = result.daily_balances
        var minBalance = Number.POSITIVE_INFINITY
        var maxBalance = Number.NEGATIVE_INFINITY

        var balanceLine = chartView.createSeries(
            ChartView.SeriesTypeLine,
            "balance",
            axisX,
            axisY
        )
        balanceLine.color = ThemeTokens.primary
        balanceLine.width = 2

        var positiveUpper = chartView.createSeries(
            ChartView.SeriesTypeLine,
            "positive-upper",
            axisX,
            axisY
        )
        var positiveLower = chartView.createSeries(
            ChartView.SeriesTypeLine,
            "positive-lower",
            axisX,
            axisY
        )
        var positiveArea = chartView.createSeries(
            ChartView.SeriesTypeArea,
            "positive-area",
            axisX,
            axisY
        )
        positiveArea.upperSeries = positiveUpper
        positiveArea.lowerSeries = positiveLower
        positiveArea.color = "transparent"
        positiveArea.gradient = positiveGradient
        positiveArea.borderWidth = 0

        var negativeUpper = chartView.createSeries(
            ChartView.SeriesTypeLine,
            "negative-upper",
            axisX,
            axisY
        )
        var negativeLower = chartView.createSeries(
            ChartView.SeriesTypeLine,
            "negative-lower",
            axisX,
            axisY
        )
        var negativeArea = chartView.createSeries(
            ChartView.SeriesTypeArea,
            "negative-area",
            axisX,
            axisY
        )
        negativeArea.upperSeries = negativeUpper
        negativeArea.lowerSeries = negativeLower
        negativeArea.borderWidth = 0
        negativeArea.color = "transparent"
        negativeArea.gradient = deficitGradient

        var zeroReference = chartView.createSeries(
            ChartView.SeriesTypeLine,
            "zero-reference",
            axisX,
            axisY
        )
        zeroReference.color = Material.dividerColor
        zeroReference.width = 1
        zeroReference.style = Qt.DashLine

        for (var i = 0; i < points.length; i++) {
            var point = points[i]
            var timestamp = new Date(point.date).getTime()
            var balance = simulationViewModel.convertToDisplayAmount(Number(point.closing_balance))

            minBalance = Math.min(minBalance, balance)
            maxBalance = Math.max(maxBalance, balance)

            balanceLine.append(timestamp, balance)
            positiveUpper.append(timestamp, Math.max(0, balance))
            positiveLower.append(timestamp, 0)
            negativeUpper.append(timestamp, 0)
            negativeLower.append(timestamp, Math.min(0, balance))
            zeroReference.append(timestamp, 0)
        }

        var axisMin = Math.min(minBalance, 0)
        var axisMax = Math.max(maxBalance, 0)
        var span = axisMax - axisMin
        if (span === 0) {
            span = Math.abs(axisMax) || 1
        }
        var padding = span * 0.1
        axisY.min = axisMin - padding
        axisY.max = axisMax + padding

        axisX.min = new Date(new Date(points[0].date).getTime())
        axisX.max = new Date(new Date(points[points.length - 1].date).getTime())
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
        anchors.fill: parent
        anchors.margins: ThemeTokens.spaceMd
        spacing: ThemeTokens.spaceSm

        Label {
            Layout.fillWidth: true
            text: root.hasChartData
                  ? qsTr("Balance chart (%1)").arg(root.displayCurrency)
                  : qsTr("Balance chart")
            font.pixelSize: ThemeTokens.fontMd
            font.weight: ThemeTokens.weightSemiBold
        }

        Label {
            Layout.fillWidth: true
            Layout.fillHeight: true
            visible: !root.hasChartData
            text: qsTr("Run a forecast to see the balance chart.")
            color: Material.secondaryTextColor
            horizontalAlignment: Text.AlignHCenter
            verticalAlignment: Text.AlignVCenter
            wrapMode: Text.WordWrap
        }

        ChartView {
            id: chartView
            Layout.fillWidth: true
            Layout.preferredHeight: root.hasChartData ? 170 : 0
            Layout.minimumHeight: root.hasChartData ? 120 : 0
            visible: root.hasChartData
            antialiasing: true
            legend.visible: false
            backgroundColor: root.cardColor
            plotAreaColor: "transparent"
            margins {
                top: 4
                bottom: 4
                left: 0
                right: 8
            }

            DateTimeAxis {
                id: axisX
                tickCount: 5
                format: "dd MMM yy"
            }

            ValueAxis {
                id: axisY
                labelFormat: "%.0f"
            }

            Item {
                id: plotHoverOverlay
                x: chartView.plotArea.x
                y: chartView.plotArea.y
                width: chartView.plotArea.width
                height: chartView.plotArea.height
                z: 10

                MouseArea {
                    id: plotMouseArea
                    anchors.fill: parent
                    hoverEnabled: true
                    acceptedButtons: Qt.NoButton

                    onPositionChanged: function(mouse) {
                        root.updateHoverFromMouseX(mouse.x)
                    }

                    onExited: root.clearHoverState()
                }

                Rectangle {
                    id: hoverGuide
                    visible: plotMouseArea.containsMouse && root.hasChartData && root.hoverActive
                    x: root.hoverGuideX
                    y: 0
                    width: 1
                    height: parent.height
                    color: ThemeTokens.primary
                    opacity: 0.5
                }

                Rectangle {
                    id: hoverTooltip
                    visible: hoverGuide.visible
                    x: Math.min(
                        Math.max(root.hoverGuideX - width / 2, 0),
                        Math.max(0, parent.width - width)
                    )
                    y: ThemeTokens.spaceXs
                    radius: ThemeTokens.radiusSm
                    color: root.cardColor
                    border.color: Material.dividerColor
                    border.width: 1
                    width: tooltipColumn.implicitWidth + ThemeTokens.spaceSm * 2
                    height: tooltipColumn.implicitHeight + ThemeTokens.spaceXs * 2

                    Column {
                        id: tooltipColumn
                        anchors.centerIn: parent
                        spacing: 2

                        Label {
                            text: root.hoverDateText
                            font.pixelSize: ThemeTokens.fontXs
                            color: Material.foreground
                        }

                        Label {
                            text: root.hoverBalanceText
                            font.pixelSize: ThemeTokens.fontXs
                            font.weight: ThemeTokens.weightSemiBold
                            color: Material.foreground
                        }
                    }
                }
            }
        }

        RowLayout {
            Layout.fillWidth: true
            visible: root.hasChartData
            spacing: ThemeTokens.spaceMd
            Layout.alignment: Qt.AlignHCenter

            RowLayout {
                spacing: 4

                Rectangle {
                    width: 16
                    height: 2
                    radius: 1
                    color: ThemeTokens.primary
                }

                Label {
                    text: qsTr("Balance")
                    font.pixelSize: ThemeTokens.fontXs
                    color: Material.secondaryTextColor
                }
            }

            RowLayout {
                spacing: 4

                Rectangle {
                    width: 16
                    height: 10
                    radius: 1
                    color: ThemeTokens.primary
                    opacity: 0.35
                }

                Label {
                    text: qsTr("Surplus")
                    font.pixelSize: ThemeTokens.fontXs
                    color: Material.secondaryTextColor
                }
            }

            RowLayout {
                spacing: 4

                Rectangle {
                    width: 16
                    height: 10
                    radius: 1
                    color: ThemeTokens.expenseRed
                    opacity: 0.6
                }

                Label {
                    text: qsTr("Shortfall")
                    font.pixelSize: ThemeTokens.fontXs
                    color: Material.secondaryTextColor
                }
            }

            RowLayout {
                spacing: 4

                Rectangle {
                    width: 16
                    height: 2
                    radius: 1
                    color: Material.dividerColor
                }

                Label {
                    text: qsTr("Break-even")
                    font.pixelSize: ThemeTokens.fontXs
                    color: Material.secondaryTextColor
                }
            }
        }
    }

    Connections {
        target: simulationViewModel
        function onResultChanged() {
            root.rebuildChart()
        }
        function onDisplayCurrencyChanged() {
            root.rebuildChart()
        }
    }

    Component.onCompleted: rebuildChart()
}
