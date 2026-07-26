import QtQuick
import QtQuick.Controls
import QtQuick.Controls.Material
import QtQuick.Layouts
import Qt5Compat.GraphicalEffects

import ThemeTokens 1.0

Item {
    id: root

    property bool expanded: false
    property var simulationControls: null

    readonly property string planId: planViewModel.selectedPlan
        ? planViewModel.selectedPlan.id
        : ""

    property var overrideState: ({})
    property int overrideRevision: 0
    property bool forceOverrideFieldSync: false

    readonly property bool isDark: Material.theme === Material.Dark
    readonly property color cardColor: isDark ? ThemeTokens.cardDark : ThemeTokens.cardLight

    readonly property bool hasOverrides: {
        var _revision = root.overrideRevision
        return root.countOverrides() > 0
    }

    readonly property bool canRunWhatIf: root.planId !== ""
        && root.simulationControls
        && root.simulationControls.buildSimulationParams() !== null
        && root.hasOverrides
        && !simulationViewModel.isRunning

    readonly property int collapsedWidth: 104

    implicitWidth: root.expanded ? 280 : root.collapsedWidth
    implicitHeight: parent ? parent.height : 320

    function touchOverrides() {
        root.overrideRevision++
    }

    function resetOverrideStateFromEntries() {
        var state = {}
        var entries = entriesViewModel.entries
        for (var i = 0; i < entries.length; i++) {
            var entry = entries[i]
            state[entry.id] = {
                amount: String(entry.amount),
                isActive: entry.is_active
            }
        }
        root.forceOverrideFieldSync = true
        root.overrideState = state
        root.touchOverrides()
        root.forceOverrideFieldSync = false
    }

    function clearOverrides() {
        root.resetOverrideStateFromEntries()
    }

    function overrideAmount(entryId) {
        var state = root.overrideState[entryId]
        return state ? state.amount : ""
    }

    function overrideIsActive(entryId, savedIsActive) {
        var state = root.overrideState[entryId]
        return state ? state.isActive : savedIsActive
    }

    function setOverrideAmount(entryId, amountText) {
        if (!root.overrideState[entryId]) {
            return
        }
        if (root.overrideState[entryId].amount === amountText) {
            return
        }
        root.overrideState[entryId].amount = amountText
        root.touchOverrides()
    }

    function setOverrideIsActive(entryId, active) {
        if (!root.overrideState[entryId]) {
            return
        }
        if (root.overrideState[entryId].isActive === active) {
            return
        }
        root.overrideState[entryId].isActive = active
        root.touchOverrides()
    }

    function isAmountOverridden(entryId, savedAmount) {
        var _revision = root.overrideRevision
        var state = root.overrideState[entryId]
        if (!state) {
            return false
        }
        var parsed = parseFloat(state.amount)
        return !isNaN(parsed) && parsed !== Number(savedAmount)
    }

    function isActiveOverridden(entryId, savedIsActive) {
        var _revision = root.overrideRevision
        var state = root.overrideState[entryId]
        return state ? state.isActive !== savedIsActive : false
    }

    function countOverrides() {
        var entries = entriesViewModel.entries
        var count = 0
        for (var i = 0; i < entries.length; i++) {
            var entry = entries[i]
            if (root.isAmountOverridden(entry.id, entry.amount)
                    || root.isActiveOverridden(entry.id, entry.is_active)) {
                count++
            }
        }
        return count
    }

    function collectOverrides() {
        var result = {}
        var entries = entriesViewModel.entries
        for (var i = 0; i < entries.length; i++) {
            var entry = entries[i]
            var patch = {}
            var state = root.overrideState[entry.id]
            if (!state) {
                continue
            }
            var parsedAmount = parseFloat(state.amount)
            if (!isNaN(parsedAmount) && parsedAmount !== Number(entry.amount)) {
                patch.amount = parsedAmount
            }
            if (state.isActive !== entry.is_active) {
                patch.is_active = state.isActive
            }
            if (Object.keys(patch).length > 0) {
                result[entry.id] = patch
            }
        }
        return result
    }

    function runWhatIf() {
        if (!root.canRunWhatIf) {
            return
        }
        var params = root.simulationControls.buildSimulationParams()
        if (!params) {
            return
        }
        simulationViewModel.runWhatIf(
            root.planId,
            params,
            root.collectOverrides()
        )
    }

    function savedEntryAmount(entryId) {
        var entries = entriesViewModel.entries
        for (var i = 0; i < entries.length; i++) {
            if (entries[i].id === entryId) {
                return Number(entries[i].amount)
            }
        }
        return NaN
    }

    function applySuggestionPrefill(entryId, changeJson) {
        if (!entryId || !changeJson) {
            return
        }
        var change
        try {
            change = JSON.parse(changeJson)
        } catch (error) {
            return
        }
        if (!root.overrideState[entryId]) {
            return
        }
        var savedAmount = root.savedEntryAmount(entryId)
        if (isNaN(savedAmount)) {
            return
        }
        var nextAmount = savedAmount
        if (change.amount_delta !== undefined && change.amount_delta !== null) {
            nextAmount = savedAmount + Number(change.amount_delta)
        } else if (change.percent_delta !== undefined && change.percent_delta !== null) {
            nextAmount = savedAmount * (1 + Number(change.percent_delta) / 100)
        } else {
            return
        }
        if (!isFinite(nextAmount) || nextAmount < 0) {
            return
        }
        root.forceOverrideFieldSync = true
        root.setOverrideAmount(entryId, String(nextAmount))
        root.forceOverrideFieldSync = false
        root.expanded = true
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

    Rectangle {
        visible: !root.expanded
        width: 3
        anchors.left: parent.left
        anchors.top: parent.top
        anchors.bottom: parent.bottom
        anchors.topMargin: ThemeTokens.radiusLg
        anchors.bottomMargin: ThemeTokens.radiusLg
        radius: 2
        color: ThemeTokens.primary
    }

    Button {
        id: toggleButton
        anchors.top: parent.top
        anchors.left: parent.left
        anchors.right: parent.right
        anchors.margins: ThemeTokens.spaceSm
        flat: true
        padding: ThemeTokens.spaceXs
        text: (root.expanded ? "\u203A " : "\u2039 ") + (
            root.expanded ? qsTr("Collapse") : qsTr("Scenario")
        )
        font.pixelSize: ThemeTokens.fontSm
        font.weight: ThemeTokens.weightSemiBold
        Material.foreground: ThemeTokens.primary
        Accessible.name: root.expanded
            ? qsTr("Collapse scenario panel")
            : qsTr("Expand scenario panel")
        onClicked: root.expanded = !root.expanded

        background: Rectangle {
            radius: ThemeTokens.radiusMd
            color: toggleButton.hovered
                   ? (root.isDark
                      ? Qt.lighter(root.cardColor, 1.12)
                      : Qt.darker(root.cardColor, 1.04))
                   : "transparent"
        }
    }

    ColumnLayout {
        anchors.fill: parent
        anchors.margins: ThemeTokens.spaceSm
        anchors.topMargin: toggleButton.height + ThemeTokens.spaceSm * 2
        visible: root.expanded
        spacing: ThemeTokens.spaceSm

        Label {
            Layout.fillWidth: true
            text: qsTr("Scenario")
            font.pixelSize: ThemeTokens.fontMd
            font.weight: ThemeTokens.weightSemiBold
            color: ThemeTokens.primary
        }

        Label {
            Layout.fillWidth: true
            text: qsTr("Override cash flow amounts or active state temporarily without changing saved data.")
            color: Material.secondaryTextColor
            font.pixelSize: ThemeTokens.fontSm
            wrapMode: Text.WordWrap
        }

        Item {
            Layout.fillWidth: true
            Layout.fillHeight: true

            ListView {
                id: entryListView
                anchors.fill: parent
                clip: true
                spacing: ThemeTokens.spaceSm
                boundsBehavior: Flickable.StopAtBounds
                model: entriesViewModel.entryListModel

                delegate: Rectangle {
                    id: entryRow
                    required property string entryId
                    required property string name
                    required property real amount
                    required property bool isActive
                    required property string entryType

                    width: entryListView.width
                    height: 56
                    radius: ThemeTokens.radiusMd
                    color: root.isDark
                           ? Qt.lighter(root.cardColor, 1.08)
                           : Qt.darker(root.cardColor, 1.02)
                    border.color: entryRow.isIncome
                                  ? (root.isDark ? "#065F46" : "#A7F3D0")
                                  : (root.isDark ? "#991B1B" : "#FECACA")
                    border.width: 1

                    readonly property bool isIncome: entryType === "income"
                    readonly property color typeAccent: entryRow.isIncome
                        ? ThemeTokens.incomeGreen
                        : ThemeTokens.expenseRed
                    readonly property color typeAccentText: entryRow.isIncome
                        ? (root.isDark ? "#6EE7B7" : ThemeTokens.incomeGreen)
                        : (root.isDark ? "#FCA5A5" : ThemeTokens.expenseRed)
                    readonly property color typeAccentBg: entryRow.isIncome
                        ? (root.isDark ? "#064E3B" : "#D1FAE5")
                        : (root.isDark ? "#7F1D1D" : "#FEE2E2")
                    readonly property bool amountOverridden: root.isAmountOverridden(entryId, amount)
                    readonly property bool activeOverridden: root.isActiveOverridden(entryId, isActive)
                    readonly property bool rowOverridden: amountOverridden || activeOverridden

                    Rectangle {
                        width: 3
                        anchors.left: parent.left
                        anchors.top: parent.top
                        anchors.bottom: parent.bottom
                        anchors.topMargin: ThemeTokens.radiusMd
                        anchors.bottomMargin: ThemeTokens.radiusMd
                        radius: 2
                        color: entryRow.typeAccent
                    }

                    ColumnLayout {
                        anchors.fill: parent
                        anchors.margins: ThemeTokens.spaceSm
                        spacing: 2

                        RowLayout {
                            Layout.fillWidth: true
                            spacing: ThemeTokens.spaceXs

                            Label {
                                Layout.fillWidth: true
                                text: entryRow.name
                                font.pixelSize: ThemeTokens.fontSm
                                font.weight: ThemeTokens.weightMedium
                                color: entryRow.typeAccentText
                                elide: Text.ElideRight
                            }

                            Label {
                                visible: entryRow.rowOverridden
                                text: qsTr("overridden")
                                font.pixelSize: ThemeTokens.fontXs
                                font.italic: true
                                color: ThemeTokens.accent
                            }
                        }

                        RowLayout {
                            Layout.fillWidth: true
                            spacing: ThemeTokens.spaceXs

                            TextField {
                                id: amountField
                                Layout.preferredWidth: 72
                                inputMethodHints: Qt.ImhFormattedNumbersOnly
                                selectByMouse: true
                                font.pixelSize: ThemeTokens.fontXs
                                color: entryRow.typeAccentText
                                Accessible.name: qsTr("Scenario amount for %1").arg(entryRow.name)

                                property string entryId: entryRow.entryId
                                property bool syncingFromState: false

                                function syncFromState() {
                                    var next = root.overrideAmount(entryId)
                                    if (text === next) {
                                        return
                                    }
                                    syncingFromState = true
                                    text = next
                                    syncingFromState = false
                                }

                                Component.onCompleted: amountField.syncFromState()

                                Connections {
                                    target: root
                                    function onOverrideRevisionChanged() {
                                        if (!amountField.activeFocus || root.forceOverrideFieldSync) {
                                            amountField.syncFromState()
                                        }
                                    }
                                }

                                onActiveFocusChanged: {
                                    if (!activeFocus) {
                                        amountField.syncFromState()
                                    }
                                }

                                onTextChanged: {
                                    if (syncingFromState) {
                                        return
                                    }
                                    root.setOverrideAmount(entryId, text)
                                }

                                background: Rectangle {
                                    radius: ThemeTokens.radiusSm
                                    border.width: entryRow.amountOverridden ? 1 : 0
                                    border.color: ThemeTokens.accent
                                    color: entryRow.typeAccentBg
                                }
                            }

                            Item {
                                Layout.fillWidth: true
                            }

                            Switch {
                                id: activeSwitch
                                property string entryId: entryRow.entryId
                                property bool savedIsActive: entryRow.isActive
                                property bool syncingFromState: false

                                function syncFromState() {
                                    var next = root.overrideIsActive(entryId, savedIsActive)
                                    if (checked === next) {
                                        return
                                    }
                                    syncingFromState = true
                                    checked = next
                                    syncingFromState = false
                                }

                                Component.onCompleted: activeSwitch.syncFromState()

                                Connections {
                                    target: root
                                    function onOverrideRevisionChanged() {
                                        activeSwitch.syncFromState()
                                    }
                                }

                                onToggled: {
                                    if (syncingFromState) {
                                        return
                                    }
                                    root.setOverrideIsActive(entryId, checked)
                                }

                                Accessible.name: qsTr("Scenario active state for %1").arg(entryRow.name)
                            }
                        }
                    }
                }
            }

            Label {
                anchors.centerIn: parent
                width: parent.width - ThemeTokens.spaceMd
                visible: entryListView.count === 0
                text: qsTr("No cash flows in this forecast.")
                color: Material.secondaryTextColor
                font.pixelSize: ThemeTokens.fontSm
                wrapMode: Text.WordWrap
                horizontalAlignment: Text.AlignHCenter
            }
        }

        Button {
            Layout.fillWidth: true
            text: qsTr("Clear overrides")
            flat: true
            enabled: root.hasOverrides
            Accessible.name: qsTr("Clear overrides")
            onClicked: root.clearOverrides()
        }

        Button {
            id: applyWhatIfButton
            Layout.fillWidth: true
            enabled: root.canRunWhatIf
            Accessible.name: qsTr("Apply scenario")
            Material.background: ThemeTokens.primary
            Material.foreground: "white"
            onClicked: root.runWhatIf()

            background: Rectangle {
                radius: ThemeTokens.radiusMd
                color: applyWhatIfButton.Material.background
                opacity: applyWhatIfButton.enabled ? 1.0 : 0.45
            }

            contentItem: Text {
                text: qsTr("Apply scenario")
                font.pixelSize: ThemeTokens.fontSm
                font.weight: ThemeTokens.weightSemiBold
                color: "white"
                horizontalAlignment: Text.AlignHCenter
                verticalAlignment: Text.AlignVCenter
            }
        }

        BusyIndicator {
            Layout.alignment: Qt.AlignHCenter
            running: simulationViewModel.isRunning
            visible: simulationViewModel.isRunning
        }
    }

    Connections {
        target: planViewModel

        function onSelectedPlanChanged() {
            if (root.planId !== "") {
                entriesViewModel.loadEntries(root.planId)
            } else {
                root.overrideState = {}
                root.touchOverrides()
            }
        }
    }

    Connections {
        target: entriesViewModel

        function onEntriesChanged() {
            root.resetOverrideStateFromEntries()
        }
    }

    Component.onCompleted: {
        if (root.planId !== "") {
            entriesViewModel.loadEntries(root.planId)
        }
    }

    Connections {
        target: simulationViewModel

        function onWhatIfPrefillRequested(entryId, changeJson) {
            root.applySuggestionPrefill(entryId, changeJson)
        }
    }
}
