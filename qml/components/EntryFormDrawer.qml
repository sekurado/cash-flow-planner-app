import QtQuick
import QtQuick.Controls
import QtQuick.Controls.Material
import QtQuick.Layouts

import ThemeTokens 1.0

Drawer {
    id: root

    edge: Qt.RightEdge
    width: parent ? Math.min(400, parent.width * 0.9) : 400
    modal: true
    interactive: true

    readonly property bool isDark: Material.theme === Material.Dark
    readonly property color drawerColor: isDark ? ThemeTokens.cardDark : ThemeTokens.cardLight

    property string entryId: ""
    property string planId: ""

    function normalizeEntry(entry) {
        return {
            entryId: entry.id || entry.entryId || "",
            planId: entry.plan_id || entry.planId || "",
            entryType: entry.entry_type || entry.entryType || "income",
            name: entry.name || "",
            datePattern: entry.date_pattern || entry.datePattern || "",
            amount: entry.amount !== undefined ? entry.amount : 0,
            currency: entry.currency || "USD",
            category: entry.category || ""
        }
    }

    function openForCreate(type, plan) {
        entriesViewModel.clearError()
        var currency = planViewModel.selectedPlan
                ? planViewModel.selectedPlan.base_currency
                : "USD"
        entryForm.loadEntry({
            entryId: "",
            planId: plan,
            entryType: type,
            name: "",
            datePattern: "",
            amount: 0,
            currency: currency,
            category: ""
        })
        root.entryId = ""
        root.planId = plan
        open()
    }

    function openForEdit(entry) {
        entriesViewModel.clearError()
        var normalized = normalizeEntry(entry)
        entryForm.loadEntry(normalized)
        root.entryId = normalized.entryId
        root.planId = normalized.planId
        open()
    }

    background: Rectangle {
        color: root.drawerColor
        topLeftRadius: ThemeTokens.radiusLg
        topRightRadius: ThemeTokens.radiusLg
    }

    ColumnLayout {
        anchors.fill: parent
        spacing: 0

        Item {
            Layout.fillWidth: true
            Layout.preferredHeight: ThemeTokens.spaceMd

            Rectangle {
                anchors.horizontalCenter: parent.horizontalCenter
                anchors.verticalCenter: parent.verticalCenter
                width: 40
                height: 4
                radius: 2
                color: "#CBD5E1"
            }
        }

        RowLayout {
            Layout.fillWidth: true
            Layout.leftMargin: ThemeTokens.spaceMd
            Layout.rightMargin: ThemeTokens.spaceMd
            Layout.bottomMargin: ThemeTokens.spaceSm
            spacing: ThemeTokens.spaceSm

            Label {
                Layout.fillWidth: true
                Layout.minimumWidth: 0
                text: root.entryId === "" ? qsTr("Add cash flow") : qsTr("Edit cash flow")
                font.pixelSize: ThemeTokens.fontLg
                font.weight: ThemeTokens.weightBold
                elide: Text.ElideRight
            }

            ToolButton {
                text: "✕"
                font.pixelSize: ThemeTokens.fontMd
                Accessible.name: qsTr("Close")
                onClicked: root.close()
            }
        }

        ScrollView {
            id: formScroll
            Layout.fillWidth: true
            Layout.fillHeight: true
            Layout.leftMargin: ThemeTokens.spaceMd
            Layout.rightMargin: ThemeTokens.spaceMd
            clip: true
            contentWidth: availableWidth
            ScrollBar.horizontal.policy: ScrollBar.AlwaysOff

            EntryForm {
                id: entryForm
                width: formScroll.availableWidth
            }
        }

        Button {
            Layout.fillWidth: true
            Layout.margins: ThemeTokens.spaceMd
            text: qsTr("Save")
            enabled: entryForm.canSave
            Material.background: ThemeTokens.primary
            Material.foreground: "white"
            Accessible.name: qsTr("Save cash flow")

            background: Rectangle {
                radius: ThemeTokens.radiusMd
                color: parent.enabled ? parent.Material.background : Material.color(Material.Grey, Material.Shade400)
            }

            onClicked: entryForm.save()
        }
    }

    Connections {
        target: entriesViewModel

        function onEntryCreated(createdId) {
            if (root.visible && root.entryId === "") {
                root.close()
            }
        }

        function onEntryUpdated(updatedId) {
            if (root.visible && updatedId === root.entryId) {
                root.close()
            }
        }
    }
}
