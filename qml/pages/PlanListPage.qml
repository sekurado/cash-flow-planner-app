import QtQuick
import QtQuick.Controls
import QtQuick.Controls.Material
import QtQuick.Dialogs
import QtQuick.Layouts
import Qt5Compat.GraphicalEffects

import ThemeTokens 1.0
import "../components"

Page {
    id: root

    title: qsTr("Forecasts")

    readonly property bool isDark: Material.theme === Material.Dark
    readonly property color cardColor: isDark ? ThemeTokens.cardDark : ThemeTokens.cardLight
    readonly property bool hasPlans: planViewModel.plans.length > 0

    background: Rectangle {
        color: isDark ? ThemeTokens.surfaceDark : ThemeTokens.surfaceLight
    }

    header: ToolBar {
        Material.elevation: 0
        Material.background: isDark ? ThemeTokens.surfaceDark : ThemeTokens.surfaceLight

        RowLayout {
            anchors.fill: parent
            anchors.leftMargin: ThemeTokens.spaceMd
            anchors.rightMargin: ThemeTokens.spaceMd
            spacing: ThemeTokens.spaceSm

            Label {
                Layout.fillWidth: true
                text: qsTr("Forecasts")
                font.pixelSize: ThemeTokens.fontXl
                font.weight: ThemeTokens.weightSemiBold
            }

            Button {
                flat: true
                text: qsTr("Import forecast")
                icon.source: "qrc:/icons/import.svg"
                icon.color: ThemeTokens.primary
                Accessible.name: qsTr("Import forecast")
                onClicked: planImportDialog.open()
            }

            NewPlanButton {
                text: qsTr("+ New forecast")
                Accessible.name: qsTr("Create new forecast")
                onClicked: newForecastChoiceDialog.open()
            }
        }
    }

    function localFilePath(fileUrl) {
        var path = fileUrl.toString()
        if (!path.startsWith("file://")) {
            return path
        }
        path = decodeURIComponent(path.slice(7))
        if (Qt.platform.os === "windows" && path.length > 0 && path.charAt(0) === "/") {
            path = path.slice(1)
        }
        return path
    }

    function sanitizeFileName(name) {
        var sanitized = name.replace(/[<>:"/\\|?*]/g, "_").trim()
        return sanitized !== "" ? sanitized : "plan"
    }

    function openExportDialog(planId, planName) {
        exportPlanDialog.planId = planId
        exportPlanDialog.currentFile = "file:///" + sanitizeFileName(planName) + ".ftplan"
        exportPlanDialog.open()
    }

    component NewPlanButton: Button {
        height: 48
        Material.background: ThemeTokens.accent
        Material.foreground: "white"
        topPadding: ThemeTokens.spaceSm
        bottomPadding: ThemeTokens.spaceSm
        leftPadding: ThemeTokens.spaceMd
        rightPadding: ThemeTokens.spaceMd
        scale: pressed ? 0.95 : (hovered ? 1.03 : 1.0)

        Behavior on scale {
            NumberAnimation {
                duration: 120
            }
        }

        background: Rectangle {
            radius: ThemeTokens.radiusFull
            color: parent.Material.background
        }

        contentItem: Text {
            text: parent.text
            font: parent.font
            color: parent.Material.foreground
            horizontalAlignment: Text.AlignHCenter
            verticalAlignment: Text.AlignVCenter
        }
    }

    Component {
        id: planDetailComponent
        PlanDetailLayout {}
    }

    function openPlan(planId) {
        planViewModel.selectPlan(planId)
        entriesViewModel.loadEntries(planId)
        if (StackView.view) {
            StackView.view.push(planDetailComponent)
        }
    }

    function formatCreatedAt(isoTimestamp) {
        if (!isoTimestamp || isoTimestamp === "") {
            return ""
        }
        var parsed = new Date(isoTimestamp)
        if (isNaN(parsed.getTime())) {
            return isoTimestamp
        }
        return qsTr("Created: %1").arg(parsed.toLocaleDateString(Qt.locale(), Locale.ShortFormat))
    }

    function planInitial(name) {
        if (!name || name.length === 0) {
            return "?"
        }
        return name.charAt(0).toUpperCase()
    }

    ListView {
        id: planList
        anchors.fill: parent
        anchors.topMargin: ThemeTokens.spaceMd
        anchors.bottomMargin: ThemeTokens.spaceMd
        clip: true
        visible: root.hasPlans
        model: planViewModel.plans
        boundsBehavior: Flickable.StopAtBounds

        delegate: ItemDelegate {
            id: planDelegate
            required property var modelData
            required property int index

            width: planList.width
            height: 72 + ThemeTokens.spaceSm
            padding: 0
            topPadding: ThemeTokens.spaceSm / 2
            bottomPadding: ThemeTokens.spaceSm / 2
            leftPadding: ThemeTokens.spaceMd
            rightPadding: ThemeTokens.spaceMd

            background: Rectangle {
                radius: ThemeTokens.radiusLg
                color: planDelegate.hovered ? Qt.lighter(root.cardColor, 1.04) : root.cardColor
                layer.enabled: true
                layer.effect: DropShadow {
                    radius: 8
                    samples: 17
                    color: "#18000000"
                    verticalOffset: 2
                }
            }

            contentItem: RowLayout {
                spacing: ThemeTokens.spaceMd

                Rectangle {
                    Layout.alignment: Qt.AlignVCenter
                    width: 32
                    height: 32
                    radius: ThemeTokens.radiusSm
                    color: ThemeTokens.primary

                    Text {
                        anchors.centerIn: parent
                        text: root.planInitial(planDelegate.modelData.name)
                        color: "white"
                        font.pixelSize: ThemeTokens.fontMd
                        font.weight: ThemeTokens.weightSemiBold
                    }
                }

                ColumnLayout {
                    Layout.fillWidth: true
                    Layout.minimumWidth: 0
                    spacing: 2

                    RowLayout {
                        Layout.fillWidth: true
                        spacing: ThemeTokens.spaceXs

                        Label {
                            Layout.fillWidth: true
                            Layout.minimumWidth: 0
                            text: planDelegate.modelData.name
                            font.pixelSize: ThemeTokens.fontMd
                            font.weight: ThemeTokens.weightSemiBold
                            elide: Text.ElideRight
                        }

                        Rectangle {
                            Layout.alignment: Qt.AlignVCenter
                            radius: ThemeTokens.radiusSm
                            color: isDark ? ThemeTokens.surfaceDark : ThemeTokens.surfaceLight
                            border.color: Material.dividerColor
                            border.width: 1
                            implicitWidth: baseCurrencyBadge.implicitWidth + ThemeTokens.spaceXs * 2
                            implicitHeight: baseCurrencyBadge.implicitHeight + 2

                            Label {
                                id: baseCurrencyBadge
                                anchors.centerIn: parent
                                text: planDelegate.modelData.base_currency
                                font.pixelSize: ThemeTokens.fontXs
                                font.weight: ThemeTokens.weightMedium
                                color: Material.secondaryTextColor
                            }
                        }
                    }

                    Label {
                        Layout.fillWidth: true
                        text: root.formatCreatedAt(planDelegate.modelData.created_at)
                        color: Material.secondaryTextColor
                        font.pixelSize: ThemeTokens.fontSm
                        elide: Text.ElideRight
                    }
                }

                ToolButton {
                    Layout.alignment: Qt.AlignVCenter
                    icon.source: "qrc:/icons/edit.svg"
                    icon.color: ThemeTokens.primary
                    opacity: planDelegate.hovered ? 1.0 : 0.35
                    Accessible.name: qsTr("Edit forecast")
                    onClicked: {
                        editPlanDialog.planId = planDelegate.modelData.id
                        editPlanDialog.planName = planDelegate.modelData.name
                        editPlanDialog.initialBalance = planDelegate.modelData.initial_balance
                        editPlanDialog.open()
                    }
                }

                ToolButton {
                    Layout.alignment: Qt.AlignVCenter
                    icon.source: "qrc:/icons/export.svg"
                    icon.color: ThemeTokens.primary
                    opacity: planDelegate.hovered ? 1.0 : 0.35
                    Accessible.name: qsTr("Export forecast")
                    onClicked: root.openExportDialog(
                                   planDelegate.modelData.id,
                                   planDelegate.modelData.name)
                }

                ToolButton {
                    Layout.alignment: Qt.AlignVCenter
                    icon.source: "qrc:/icons/delete.svg"
                    icon.color: Material.color(Material.Red)
                    opacity: planDelegate.hovered ? 1.0 : 0.35
                    Accessible.name: qsTr("Delete forecast")
                    onClicked: {
                        deletePlanDialog.planId = planDelegate.modelData.id
                        deletePlanDialog.planName = planDelegate.modelData.name
                        deletePlanDialog.open()
                    }
                }
            }

            onClicked: root.openPlan(planDelegate.modelData.id)
        }
    }

    ColumnLayout {
        anchors.centerIn: parent
        spacing: ThemeTokens.spaceMd
        width: Math.min(parent.width - ThemeTokens.spaceXl * 2, 400)
        visible: !root.hasPlans

        Item {
            Layout.alignment: Qt.AlignHCenter
            width: 80
            height: 80

            Image {
                id: emptyStateIcon
                anchors.fill: parent
                source: "qrc:/icons/app-icon.svg"
                fillMode: Image.PreserveAspectFit
                visible: false
            }

            ColorOverlay {
                anchors.fill: parent
                source: emptyStateIcon
                color: ThemeTokens.primary
            }
        }

        Label {
            Layout.fillWidth: true
            text: qsTr("No forecasts yet")
            font.pixelSize: ThemeTokens.fontXl
            font.weight: ThemeTokens.weightSemiBold
            horizontalAlignment: Text.AlignHCenter
            color: Material.foreground
        }

        Label {
            Layout.fillWidth: true
            text: qsTr("Create your first forecast to start forecasting")
            wrapMode: Text.WordWrap
            horizontalAlignment: Text.AlignHCenter
            font.pixelSize: ThemeTokens.fontMd
            color: Material.secondaryTextColor
        }

        NewPlanButton {
            Layout.alignment: Qt.AlignHCenter
            text: qsTr("+ New forecast")
            Accessible.name: qsTr("Create new forecast")
            onClicked: newForecastChoiceDialog.open()
        }

        Button {
            Layout.alignment: Qt.AlignHCenter
            flat: true
            text: qsTr("Import forecast")
            icon.source: "qrc:/icons/import.svg"
            icon.color: ThemeTokens.primary
            Accessible.name: qsTr("Import forecast")
            onClicked: planImportDialog.open()
        }
    }

    PlanImportDialog {
        id: planImportDialog
    }

    TemplatePickerDialog {
        id: templatePickerDialog
    }

    CenteredDialog {
        id: newForecastChoiceDialog
        standardButtons: Dialog.NoButton
        width: Math.min(root.width - ThemeTokens.spaceXl, 360)

        background: Rectangle {
            radius: ThemeTokens.radiusLg
            color: root.cardColor
        }

        header: Label {
            text: qsTr("New forecast")
            font.pixelSize: ThemeTokens.fontLg
            font.weight: ThemeTokens.weightSemiBold
            topPadding: ThemeTokens.spaceMd
            leftPadding: ThemeTokens.spaceMd
            rightPadding: ThemeTokens.spaceMd
            bottomPadding: ThemeTokens.spaceSm
        }

        contentItem: ColumnLayout {
            width: 320
            spacing: ThemeTokens.spaceMd

            Label {
                Layout.fillWidth: true
                text: qsTr("Start with a blank forecast or use a template with typical cash flows.")
                wrapMode: Text.WordWrap
                font.pixelSize: ThemeTokens.fontSm
                color: Material.secondaryTextColor
            }

            Button {
                Layout.fillWidth: true
                text: qsTr("Blank forecast")
                Material.background: ThemeTokens.primary
                Material.foreground: "white"
                Accessible.name: qsTr("Create blank forecast")
                onClicked: {
                    newForecastChoiceDialog.close()
                    createPlanDialog.open()
                }
            }

            Button {
                Layout.fillWidth: true
                text: qsTr("From template")
                flat: true
                Accessible.name: qsTr("Create forecast from template")
                onClicked: {
                    newForecastChoiceDialog.close()
                    templatePickerDialog.open()
                }
            }
        }

        footer: DialogButtonBox {
            Button {
                text: qsTr("Cancel")
                flat: true
                DialogButtonBox.buttonRole: DialogButtonBox.RejectRole
                onClicked: newForecastChoiceDialog.close()
            }
        }
    }

    FileDialog {
        id: exportPlanDialog
        property string planId: ""
        title: qsTr("Export forecast")
        fileMode: FileDialog.SaveFile
        nameFilters: [qsTr("Forecast files (*.ftplan)")]
        defaultSuffix: "ftplan"
        onAccepted: {
            if (planId !== "") {
                planViewModel.exportPlan(planId, root.localFilePath(selectedFile))
            }
        }
    }

    Connections {
        target: planViewModel

        function onExportSucceeded() {
            exportSnackbar.open()
        }
    }

    Popup {
        id: exportSnackbar
        parent: Overlay.overlay
        modal: false
        focus: false
        closePolicy: Popup.CloseOnEscape | Popup.CloseOnPressOutside
        x: parent ? (parent.width - width) / 2 : 0
        y: parent ? parent.height - height - 24 : 0
        width: Math.min(parent ? parent.width - 48 : 360, 420)
        padding: ThemeTokens.spaceMd

        background: Rectangle {
            radius: ThemeTokens.radiusMd
            color: Material.color(Material.Grey, Material.Shade800)
        }

        contentItem: Label {
            text: qsTr("Forecast exported successfully")
            color: "white"
            wrapMode: Text.WordWrap
        }

        Timer {
            interval: 3000
            running: exportSnackbar.opened
            onTriggered: exportSnackbar.close()
        }
    }

    CenteredDialog {
        id: createPlanDialog
        standardButtons: Dialog.NoButton
        width: Math.min(root.width - ThemeTokens.spaceXl, 360)

        readonly property color dialogCardColor: root.cardColor

        background: Rectangle {
            radius: ThemeTokens.radiusLg
            color: createPlanDialog.dialogCardColor
        }

        header: Label {
            text: qsTr("New forecast")
            font.pixelSize: ThemeTokens.fontLg
            font.weight: ThemeTokens.weightSemiBold
            topPadding: ThemeTokens.spaceMd
            leftPadding: ThemeTokens.spaceMd
            rightPadding: ThemeTokens.spaceMd
            bottomPadding: ThemeTokens.spaceSm
        }

        onAboutToShow: {
            planNameField.text = ""
            planBalanceField.text = "0"
            var usdIndex = baseCurrencyCombo.find("USD")
            baseCurrencyCombo.currentIndex = usdIndex >= 0 ? usdIndex : 0
            planNameField.forceActiveFocus()
        }

        contentItem: ColumnLayout {
            spacing: ThemeTokens.spaceMd
            width: 320

            TextField {
                id: planNameField
                Layout.fillWidth: true
                placeholderText: qsTr("My budget 2026")
                Accessible.name: qsTr("Forecast name")
            }

            TextField {
                id: planBalanceField
                Layout.fillWidth: true
                placeholderText: qsTr("Initial balance")
                inputMethodHints: Qt.ImhFormattedNumbersOnly
                Accessible.name: qsTr("Initial balance")
            }

            Label {
                Layout.fillWidth: true
                text: qsTr("Base currency")
                font.pixelSize: ThemeTokens.fontSm
                font.weight: ThemeTokens.weightMedium
                color: ThemeTokens.primary
            }

            ComboBox {
                id: baseCurrencyCombo
                Layout.fillWidth: true
                model: appViewModel.commonCurrencies
                Accessible.name: qsTr("Base currency")
            }
        }

        footer: DialogButtonBox {
            Button {
                text: qsTr("Cancel")
                flat: true
                DialogButtonBox.buttonRole: DialogButtonBox.RejectRole
                onClicked: createPlanDialog.close()
            }

            Button {
                text: qsTr("Create")
                enabled: planNameField.text.trim() !== ""
                Material.background: ThemeTokens.primary
                Material.foreground: "white"
                DialogButtonBox.buttonRole: DialogButtonBox.AcceptRole
                onClicked: {
                    var balance = parseFloat(planBalanceField.text)
                    if (isNaN(balance)) {
                        balance = 0
                    }
                    planViewModel.createPlan(
                                planNameField.text.trim(),
                                baseCurrencyCombo.currentText,
                                balance)
                    createPlanDialog.close()
                }
            }
        }
    }

    CenteredDialog {
        id: editPlanDialog
        standardButtons: Dialog.NoButton
        width: Math.min(root.width - ThemeTokens.spaceXl, 360)

        property string planId: ""
        property string planName: ""
        property real initialBalance: 0

        readonly property color dialogCardColor: root.cardColor

        background: Rectangle {
            radius: ThemeTokens.radiusLg
            color: editPlanDialog.dialogCardColor
        }

        header: Label {
            text: qsTr("Edit forecast")
            font.pixelSize: ThemeTokens.fontLg
            font.weight: ThemeTokens.weightSemiBold
            topPadding: ThemeTokens.spaceMd
            leftPadding: ThemeTokens.spaceMd
            rightPadding: ThemeTokens.spaceMd
            bottomPadding: ThemeTokens.spaceSm
        }

        onAboutToShow: {
            editPlanNameField.text = editPlanDialog.planName
            editPlanBalanceField.text = String(editPlanDialog.initialBalance)
            editPlanNameField.forceActiveFocus()
        }

        contentItem: ColumnLayout {
            spacing: ThemeTokens.spaceMd
            width: 320

            TextField {
                id: editPlanNameField
                Layout.fillWidth: true
                placeholderText: qsTr("My budget 2026")
                Accessible.name: qsTr("Forecast name")
            }

            TextField {
                id: editPlanBalanceField
                Layout.fillWidth: true
                placeholderText: qsTr("Initial balance")
                inputMethodHints: Qt.ImhFormattedNumbersOnly
                Accessible.name: qsTr("Initial balance")
            }
        }

        footer: DialogButtonBox {
            Button {
                text: qsTr("Cancel")
                flat: true
                DialogButtonBox.buttonRole: DialogButtonBox.RejectRole
                onClicked: editPlanDialog.close()
            }

            Button {
                text: qsTr("Save")
                enabled: editPlanNameField.text.trim() !== ""
                Material.background: ThemeTokens.primary
                Material.foreground: "white"
                DialogButtonBox.buttonRole: DialogButtonBox.AcceptRole
                onClicked: {
                    var balance = parseFloat(editPlanBalanceField.text)
                    if (isNaN(balance)) {
                        balance = 0
                    }
                    planViewModel.updatePlan(
                                editPlanDialog.planId,
                                {
                                    "name": editPlanNameField.text.trim(),
                                    "initial_balance": balance
                                })
                    if (planViewModel.error === "") {
                        editPlanDialog.close()
                    }
                }
            }
        }
    }

    CenteredDialog {
        id: deletePlanDialog
        standardButtons: Dialog.NoButton
        width: Math.min(root.width - ThemeTokens.spaceXl, 360)

        property string planId: ""
        property string planName: ""

        background: Rectangle {
            radius: ThemeTokens.radiusLg
            color: root.cardColor
        }

        header: Label {
            text: qsTr("Delete forecast")
            font.pixelSize: ThemeTokens.fontLg
            font.weight: ThemeTokens.weightSemiBold
            topPadding: ThemeTokens.spaceMd
            leftPadding: ThemeTokens.spaceMd
            rightPadding: ThemeTokens.spaceMd
            bottomPadding: ThemeTokens.spaceSm
        }

        contentItem: ColumnLayout {
            width: 320

            Label {
                Layout.fillWidth: true
                text: qsTr("Delete \"%1\"? All cash flows and projection data for this forecast will be removed.")
                          .arg(deletePlanDialog.planName)
                wrapMode: Text.WordWrap
            }
        }

        footer: DialogButtonBox {
            Button {
                text: qsTr("Cancel")
                flat: true
                DialogButtonBox.buttonRole: DialogButtonBox.RejectRole
                onClicked: deletePlanDialog.close()
            }

            Button {
                text: qsTr("Delete")
                Material.background: Material.color(Material.Red)
                Material.foreground: "white"
                DialogButtonBox.buttonRole: DialogButtonBox.DestructiveRole
                onClicked: {
                    if (deletePlanDialog.planId !== "") {
                        planViewModel.deletePlan(deletePlanDialog.planId)
                    }
                    deletePlanDialog.close()
                }
            }
        }
    }

    Component.onCompleted: {
        if (planViewModel.selectedPlan) {
            Qt.callLater(restoreLastPlan)
        }
    }

    function restoreLastPlan() {
        var savedPlan = planViewModel.selectedPlan
        if (!savedPlan || savedPlan.id === undefined || savedPlan.id === "") {
            return
        }
        entriesViewModel.loadEntries(savedPlan.id)
        if (StackView.view) {
            StackView.view.push(planDetailComponent, null, StackView.Immediate)
        }
    }
}
