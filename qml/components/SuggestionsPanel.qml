import QtQuick
import QtQuick.Controls
import QtQuick.Controls.Material
import QtQuick.Layouts
import Qt5Compat.GraphicalEffects

import ThemeTokens 1.0

Item {
    id: root

    readonly property var suggestionsModel: suggestionsViewModel.suggestions
    readonly property bool hasResult: simulationViewModel.result !== null
                                    && simulationViewModel.result !== undefined
    readonly property bool showPanel: root.hasResult
                                      && !simulationViewModel.isRunning
    readonly property bool showEmptyState: root.showPanel
                                           && !suggestionsViewModel.isAnalyzing
                                           && !suggestionsViewModel.hasSuggestions
    readonly property string currency: simulationViewModel.displayCurrency
    readonly property bool isDark: Material.theme === Material.Dark
    readonly property color cardColor: isDark ? ThemeTokens.cardDark : ThemeTokens.cardLight

    property bool expanded: false

    readonly property int collapsedItemCount: 3
    readonly property int visibleItemCount: root.expanded
        ? suggestionsModel.count
        : Math.min(suggestionsModel.count, root.collapsedItemCount)

    visible: root.showPanel
    implicitHeight: visible ? panelColumn.implicitHeight : 0
    Layout.preferredHeight: implicitHeight
    opacity: visible ? 1.0 : 0.0
    clip: true

    Behavior on opacity {
        NumberAnimation {
            duration: 200
        }
    }

    function kindAccentColor(kind) {
        switch (kind) {
        case "reduce_spend":
            return ThemeTokens.expenseRed
        case "increase_income":
            return ThemeTokens.incomeGreen
        case "avoid_deficit":
        case "extend_runway":
            return ThemeTokens.accent
        case "build_buffer":
        case "save_more":
            return ThemeTokens.primary
        default:
            return ThemeTokens.primary
        }
    }

    function formatImpact(amount) {
        if (amount === null || amount === undefined || amount === "") {
            return ""
        }
        var converted = simulationViewModel.convertToDisplayAmount(Number(amount))
        return qsTr("%1 %2")
            .arg(Number(converted).toLocaleString(Qt.locale(), "f", 2))
            .arg(root.currency)
    }

    function tryInScenario(entryId, changeJson) {
        simulationViewModel.prefillWhatIfOverride(entryId, changeJson)
    }

    ColumnLayout {
        id: panelColumn
        anchors.fill: parent
        spacing: ThemeTokens.spaceSm

        RowLayout {
            Layout.fillWidth: true
            spacing: ThemeTokens.spaceSm

            Label {
                Layout.fillWidth: true
                text: qsTr("Suggestions")
                font.pixelSize: ThemeTokens.fontMd
                font.weight: ThemeTokens.weightSemiBold
                color: Material.foreground
            }

            BusyIndicator {
                visible: suggestionsViewModel.isAnalyzing
                running: suggestionsViewModel.isAnalyzing
                implicitWidth: 20
                implicitHeight: 20
            }
        }

        Label {
            id: scenarioDisclaimerLabel
            Layout.fillWidth: true
            visible: simulationViewModel.isScenarioResult
                     && suggestionsViewModel.hasSuggestions
            text: qsTr("Based on the saved forecast — the chart above reflects your scenario.")
            color: Material.secondaryTextColor
            font.pixelSize: ThemeTokens.fontXs
            font.italic: true
            wrapMode: Text.WordWrap
            Accessible.name: scenarioDisclaimerLabel.text
        }

        Label {
            Layout.fillWidth: true
            visible: root.showEmptyState
            text: qsTr("No suggestions for this projection.")
            color: Material.secondaryTextColor
            font.pixelSize: ThemeTokens.fontSm
            wrapMode: Text.WordWrap
        }

        ListView {
            id: suggestionList
            Layout.fillWidth: true
            implicitHeight: contentHeight
            visible: suggestionsViewModel.hasSuggestions
            interactive: false
            spacing: ThemeTokens.spaceSm
            clip: true
            model: suggestionsModel

            delegate: Rectangle {
                id: suggestionCard
                required property int index
                required property string suggestionId
                required property string kind
                required property string title
                required property string detail
                required property var impactAmount
                required property string relatedEntryId
                required property bool hasSuggestedChange
                required property string suggestedChangeJson

                width: suggestionList.width
                height: suggestionCard.index < root.visibleItemCount
                        ? cardColumn.implicitHeight + ThemeTokens.spaceMd * 2
                        : 0
                visible: height > 0
                radius: ThemeTokens.radiusLg
                color: root.cardColor
                border.color: Material.dividerColor
                border.width: 1
                layer.enabled: visible
                layer.effect: DropShadow {
                    radius: 6
                    samples: 13
                    color: "#12000000"
                    verticalOffset: 1
                }

                readonly property string impactLabel: root.formatImpact(impactAmount)
                readonly property color accentColor: root.kindAccentColor(kind)
                readonly property bool canTryScenario: hasSuggestedChange && relatedEntryId !== ""

                Rectangle {
                    width: 4
                    anchors.top: parent.top
                    anchors.bottom: parent.bottom
                    anchors.left: parent.left
                    anchors.topMargin: ThemeTokens.radiusLg
                    anchors.bottomMargin: ThemeTokens.radiusLg
                    radius: 2
                    color: suggestionCard.accentColor
                }

                ColumnLayout {
                    id: cardColumn
                    anchors.fill: parent
                    anchors.leftMargin: ThemeTokens.spaceMd
                    anchors.rightMargin: ThemeTokens.spaceMd
                    anchors.topMargin: ThemeTokens.spaceMd
                    anchors.bottomMargin: ThemeTokens.spaceMd
                    spacing: ThemeTokens.spaceXs

                    RowLayout {
                        Layout.fillWidth: true
                        spacing: ThemeTokens.spaceSm

                        Label {
                            Layout.fillWidth: true
                            text: suggestionCard.title
                            font.pixelSize: ThemeTokens.fontSm
                            font.weight: ThemeTokens.weightSemiBold
                            color: Material.foreground
                            wrapMode: Text.WordWrap
                        }

                        Label {
                            visible: suggestionCard.impactLabel !== ""
                            text: suggestionCard.impactLabel
                            font.pixelSize: ThemeTokens.fontXs
                            font.weight: ThemeTokens.weightMedium
                            color: suggestionCard.accentColor
                            padding: ThemeTokens.spaceXs
                            background: Rectangle {
                                radius: ThemeTokens.radiusSm
                                color: Qt.rgba(
                                    suggestionCard.accentColor.r,
                                    suggestionCard.accentColor.g,
                                    suggestionCard.accentColor.b,
                                    root.isDark ? 0.18 : 0.12
                                )
                            }
                        }
                    }

                    Label {
                        Layout.fillWidth: true
                        text: suggestionCard.detail
                        font.pixelSize: ThemeTokens.fontSm
                        color: Material.secondaryTextColor
                        wrapMode: Text.WordWrap
                    }

                    Button {
                        visible: suggestionCard.canTryScenario
                        flat: true
                        text: qsTr("Try in scenario")
                        font.pixelSize: ThemeTokens.fontXs
                        Material.foreground: ThemeTokens.primary
                        Accessible.name: qsTr("Try in scenario: %1").arg(suggestionCard.title)
                        onClicked: root.tryInScenario(
                            suggestionCard.relatedEntryId,
                            suggestionCard.suggestedChangeJson
                        )

                        background: Rectangle {
                            radius: ThemeTokens.radiusSm
                            color: parent.hovered
                                   ? (root.isDark
                                      ? Qt.lighter(root.cardColor, 1.1)
                                      : Qt.darker(root.cardColor, 1.03))
                                   : "transparent"
                        }
                    }
                }

                Accessible.role: Accessible.Grouping
                Accessible.name: suggestionCard.title + ". " + suggestionCard.detail
            }
        }

        Button {
            Layout.fillWidth: true
            visible: suggestionsModel.count > root.collapsedItemCount
            flat: true
            text: root.expanded ? qsTr("Show less") : qsTr("Show more")
            font.pixelSize: ThemeTokens.fontSm
            Material.foreground: ThemeTokens.primary
            Accessible.name: root.expanded ? qsTr("Show less") : qsTr("Show more")
            onClicked: root.expanded = !root.expanded
        }
    }

    Connections {
        target: simulationViewModel
        function onResultChanged() {
            root.expanded = false
        }
    }
}
