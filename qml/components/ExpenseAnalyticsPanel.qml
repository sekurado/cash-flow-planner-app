import QtQuick
import QtQuick.Controls
import QtQuick.Controls.Material
import QtQuick.Layouts

import ThemeTokens 1.0
import "."

ColumnLayout {
    id: root

    spacing: ThemeTokens.spaceMd

    Label {
        Layout.fillWidth: true
        text: qsTr("Overview")
        font.pixelSize: ThemeTokens.fontLg
        font.weight: ThemeTokens.weightSemiBold
    }

    Label {
        Layout.fillWidth: true
        visible: expenseAnalyticsViewModel.error !== ""
        text: expenseAnalyticsViewModel.error
        color: Material.color(Material.Red)
        wrapMode: Text.WordWrap
        font.pixelSize: ThemeTokens.fontSm
    }

    ExpenseBucketBarChart {
        Layout.fillWidth: true
        title: qsTr("Top categories")
        series: expenseAnalyticsViewModel.categorySeries
        displayCurrency: expenseAnalyticsViewModel.displayCurrency
        emptyMessage: qsTr("No category spending in this period.")
    }

    ExpenseBucketBarChart {
        Layout.fillWidth: true
        title: qsTr("Top places")
        series: expenseAnalyticsViewModel.placeSeries
        displayCurrency: expenseAnalyticsViewModel.displayCurrency
        emptyMessage: qsTr("No place spending in this period.")
    }

    ExpenseBucketBarChart {
        Layout.fillWidth: true
        title: qsTr("Top names")
        series: expenseAnalyticsViewModel.nameSeries
        displayCurrency: expenseAnalyticsViewModel.displayCurrency
        emptyMessage: qsTr("No name spending in this period.")
    }
}
