import QtQuick
import QtQuick.Controls
import QtQuick.Controls.Material
import QtQuick.Layouts
import Qt5Compat.GraphicalEffects

import ThemeTokens 1.0
import "../components"

Item {
    id: root

    readonly property string planId: planViewModel.selectedPlan ? planViewModel.selectedPlan.id : ""
    readonly property bool isDark: Material.theme === Material.Dark
    readonly property color cardColor: isDark ? ThemeTokens.cardDark : ThemeTokens.cardLight
    readonly property string uiLanguage: settingsViewModel ? settingsViewModel.language : "en"

    function entryCountForType(type) {
        var entries = entriesViewModel.entries
        var count = 0
        for (var i = 0; i < entries.length; i++) {
            if (entries[i].entry_type === type) {
                count++
            }
        }
        return count
    }

    function formatAmountBadge(amount, currency, isIncome) {
        var prefix = isIncome ? "+" : "-"
        var formatted = Number(amount).toLocaleString(Qt.locale(), "f", 2)
        return prefix + " " + formatted + " " + currency
    }

    function openEditDrawer(rowIndex) {
        var entries = entriesViewModel.entries
        if (rowIndex < 0 || rowIndex >= entries.length) {
            return
        }
        entryFormDrawer.openForEdit(entries[rowIndex])
    }

    component EntryCardDelegate: ItemDelegate {
        id: entryDelegate
        required property int index
        required property string entryId
        required property string name
        required property string datePattern
        required property real amount
        required property string currency
        required property string entryType
        required property string category
        required property bool isActive
        required property string listEntryType

        readonly property bool isIncome: listEntryType === "income"

        width: ListView.view ? ListView.view.width : parent.width
        height: entryType === listEntryType ? 72 : 0
        visible: entryType === listEntryType
        padding: 0
        topPadding: 4
        bottomPadding: 4
        leftPadding: ThemeTokens.spaceMd
        rightPadding: ThemeTokens.spaceMd

        background: Rectangle {
            radius: ThemeTokens.radiusLg
            color: entryDelegate.hovered ? Qt.lighter(root.cardColor, 1.04) : root.cardColor
            layer.enabled: true
            layer.effect: DropShadow {
                radius: 8
                samples: 17
                color: "#18000000"
                verticalOffset: 2
            }
        }

        contentItem: RowLayout {
            spacing: ThemeTokens.spaceSm

            ColumnLayout {
                Layout.fillWidth: true
                Layout.minimumWidth: 0
                spacing: 2

                Label {
                    Layout.fillWidth: true
                    text: entryDelegate.name
                    font.pixelSize: ThemeTokens.fontMd
                    font.weight: ThemeTokens.weightSemiBold
                    elide: Text.ElideRight
                }

                Label {
                    Layout.fillWidth: true
                    readonly property string _uiLanguage: root.uiLanguage
                    text: entriesViewModel.describePattern(entryDelegate.datePattern)
                    color: Material.secondaryTextColor
                    font.pixelSize: ThemeTokens.fontSm
                    elide: Text.ElideRight
                }
            }

            Rectangle {
                Layout.alignment: Qt.AlignVCenter
                implicitWidth: amountLabel.implicitWidth + ThemeTokens.spaceSm * 2
                implicitHeight: amountLabel.implicitHeight + ThemeTokens.spaceXs * 2
                radius: ThemeTokens.radiusSm
                color: {
                    if (entryDelegate.isIncome) {
                        return root.isDark ? "#064E3B" : "#D1FAE5"
                    }
                    return root.isDark ? "#7F1D1D" : "#FEE2E2"
                }

                Label {
                    id: amountLabel
                    anchors.centerIn: parent
                    text: root.formatAmountBadge(
                              entryDelegate.amount,
                              entryDelegate.currency,
                              entryDelegate.isIncome)
                    font.pixelSize: ThemeTokens.fontSm
                    font.weight: ThemeTokens.weightMedium
                    color: entryDelegate.isIncome
                           ? (root.isDark ? "#6EE7B7" : ThemeTokens.incomeGreen)
                           : (root.isDark ? "#FCA5A5" : ThemeTokens.expenseRed)
                }
            }

            Switch {
                Layout.alignment: Qt.AlignVCenter
                checked: entryDelegate.isActive
                Accessible.name: qsTr("Active toggle for %1").arg(entryDelegate.name)
                onToggled: entriesViewModel.updateEntry(
                               entryDelegate.entryId,
                               { is_active: checked })
            }

            ToolButton {
                Layout.alignment: Qt.AlignVCenter
                icon.source: "qrc:/icons/edit.svg"
                opacity: entryDelegate.hovered ? 1.0 : 0.35
                Accessible.name: qsTr("Edit %1").arg(entryDelegate.name)
                onClicked: root.openEditDrawer(entryDelegate.index)
            }

            ToolButton {
                Layout.alignment: Qt.AlignVCenter
                icon.source: "qrc:/icons/delete.svg"
                icon.color: Material.color(Material.Red)
                opacity: entryDelegate.hovered ? 1.0 : 0.35
                Accessible.name: qsTr("Delete %1").arg(entryDelegate.name)
                onClicked: {
                    deleteEntryDialog.entryId = entryDelegate.entryId
                    deleteEntryDialog.entryName = entryDelegate.name
                    deleteEntryDialog.open()
                }
            }
        }
    }

    component TabEmptyState: ColumnLayout {
        property string message

        anchors.centerIn: parent
        spacing: ThemeTokens.spaceSm
        width: Math.min(parent.width - ThemeTokens.spaceXl * 2, 360)

        Item {
            Layout.alignment: Qt.AlignHCenter
            width: 50
            height: 50

            Image {
                id: emptyIcon
                anchors.fill: parent
                source: "qrc:/icons/app-icon.svg"
                fillMode: Image.PreserveAspectFit
                visible: false
            }

            ColorOverlay {
                anchors.fill: parent
                source: emptyIcon
                color: Material.secondaryTextColor
            }
        }

        Label {
            Layout.fillWidth: true
            text: parent.message
            horizontalAlignment: Text.AlignHCenter
            font.pixelSize: ThemeTokens.fontMd
            color: Material.secondaryTextColor
        }

        Label {
            Layout.fillWidth: true
            text: qsTr("Add your first cash flow using the + button")
            horizontalAlignment: Text.AlignHCenter
            wrapMode: Text.WordWrap
            font.pixelSize: ThemeTokens.fontSm
            color: Material.secondaryTextColor
        }
    }

    ColumnLayout {
        anchors.fill: parent
        spacing: ThemeTokens.spaceSm

        RowLayout {
            Layout.fillWidth: true
            Layout.leftMargin: ThemeTokens.spaceMd
            Layout.rightMargin: ThemeTokens.spaceMd
            Layout.topMargin: ThemeTokens.spaceSm

            Item {
                Layout.fillWidth: true
            }

            Button {
                text: qsTr("Import")
                icon.source: "qrc:/icons/import.svg"
                display: AbstractButton.TextBesideIcon
                flat: true
                Material.foreground: ThemeTokens.primary
                Accessible.name: qsTr("Import cash flows")
                onClicked: importDialog.open()

                background: Rectangle {
                    radius: ThemeTokens.radiusMd
                    color: parent.hovered
                           ? Qt.rgba(ThemeTokens.primary.r, ThemeTokens.primary.g, ThemeTokens.primary.b, 0.08)
                           : "transparent"
                    border.color: ThemeTokens.primary
                    border.width: 1
                }
            }
        }

        Item {
            Layout.fillWidth: true
            Layout.preferredHeight: 36

            SegmentedControl {
                id: typeControl
                anchors.horizontalCenter: parent.horizontalCenter
                model: [qsTr("Income"), qsTr("Expense")]
                accessibleNames: [qsTr("Income tab"), qsTr("Expense tab")]
            }
        }

        StackLayout {
            id: entryTabStack
            Layout.fillWidth: true
            Layout.fillHeight: true
            currentIndex: typeControl.currentIndex

            Item {
                Layout.fillWidth: true
                Layout.fillHeight: true

                ListView {
                    id: incomeList
                    anchors.fill: parent
                    anchors.topMargin: ThemeTokens.spaceSm
                    anchors.bottomMargin: ThemeTokens.spaceXl + 56
                    clip: true
                    spacing: 4
                    visible: root.entryCountForType("income") > 0
                    model: entriesViewModel.entryListModel
                    boundsBehavior: Flickable.StopAtBounds

                    delegate: EntryCardDelegate {
                        listEntryType: "income"
                    }
                }

                TabEmptyState {
                    visible: root.entryCountForType("income") === 0
                    message: qsTr("No income cash flows yet")
                }
            }

            Item {
                Layout.fillWidth: true
                Layout.fillHeight: true

                ListView {
                    id: expenseList
                    anchors.fill: parent
                    anchors.topMargin: ThemeTokens.spaceSm
                    anchors.bottomMargin: ThemeTokens.spaceXl + 56
                    clip: true
                    spacing: 4
                    visible: root.entryCountForType("expense") > 0
                    model: entriesViewModel.entryListModel
                    boundsBehavior: Flickable.StopAtBounds

                    delegate: EntryCardDelegate {
                        listEntryType: "expense"
                    }
                }

                TabEmptyState {
                    visible: root.entryCountForType("expense") === 0
                    message: qsTr("No expense cash flows yet")
                }
            }
        }
    }

    Button {
        id: addEntryFab
        anchors.bottom: parent.bottom
        anchors.right: parent.right
        anchors.margins: ThemeTokens.spaceLg
        implicitWidth: 48
        implicitHeight: 48
        display: AbstractButton.IconOnly
        icon.source: "qrc:/icons/add.svg"
        icon.color: "white"
        Material.background: ThemeTokens.accent
        Material.foreground: "white"
        Material.elevation: 0
        scale: pressed ? 0.95 : (hovered ? 1.03 : 1.0)
        Accessible.name: qsTr("Add cash flow")

        Behavior on scale {
            NumberAnimation {
                duration: 120
            }
        }

        background: Rectangle {
            anchors.fill: parent
            radius: ThemeTokens.radiusFull
            color: parent.Material.background
        }

        onClicked: {
            var type = typeControl.currentIndex === 0 ? "income" : "expense"
            entryFormDrawer.openForCreate(type, root.planId)
        }
    }

    EntryFormDrawer {
        id: entryFormDrawer
    }

    ImportDialog {
        id: importDialog
        planId: root.planId
    }

    CenteredDialog {
        id: deleteEntryDialog
        standardButtons: Dialog.NoButton
        width: Math.min(root.width - ThemeTokens.spaceXl, 360)

        property string entryId: ""
        property string entryName: ""

        background: Rectangle {
            radius: ThemeTokens.radiusLg
            color: root.cardColor
        }

        header: Label {
            text: qsTr("Delete cash flow")
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
                text: qsTr("Delete \"%1\"?").arg(deleteEntryDialog.entryName)
                wrapMode: Text.WordWrap
            }
        }

        footer: DialogButtonBox {
            Button {
                text: qsTr("Cancel")
                flat: true
                DialogButtonBox.buttonRole: DialogButtonBox.RejectRole
                onClicked: deleteEntryDialog.close()
            }

            Button {
                text: qsTr("Delete")
                Material.background: Material.color(Material.Red)
                Material.foreground: "white"
                DialogButtonBox.buttonRole: DialogButtonBox.DestructiveRole
                onClicked: {
                    if (deleteEntryDialog.entryId !== "") {
                        entriesViewModel.deleteEntry(deleteEntryDialog.entryId)
                    }
                    deleteEntryDialog.close()
                }
            }
        }
    }

    Component.onCompleted: {
        if (root.planId !== "") {
            entriesViewModel.loadEntries(root.planId)
        }
    }
}
