import QtQuick
import QtQuick.Controls
import QtQuick.Controls.Material
import QtQuick.Layouts
import Qt5Compat.GraphicalEffects

import ThemeTokens 1.0
import "../components"

Page {
    id: root

    title: qsTr("Spending")

    readonly property bool isDark: Material.theme === Material.Dark
    readonly property color cardColor: isDark ? ThemeTokens.cardDark : ThemeTokens.cardLight

    background: Rectangle {
        color: isDark ? ThemeTokens.surfaceDark : ThemeTokens.surfaceLight
    }

    function formatAmount(amount, currency) {
        var formatted = Number(amount).toLocaleString(Qt.locale(), "f", 2)
        return "- " + formatted + " " + currency
    }

    function formatDate(isoDate) {
        if (!isoDate || isoDate === "") {
            return ""
        }
        var parts = isoDate.split("-")
        if (parts.length !== 3) {
            return isoDate
        }
        var date = new Date(parseInt(parts[0], 10), parseInt(parts[1], 10) - 1, parseInt(parts[2], 10))
        return date.toLocaleDateString(Qt.locale(), Locale.ShortFormat)
    }

    header: ToolBar {
        Material.elevation: 0
        Material.background: isDark ? ThemeTokens.surfaceDark : ThemeTokens.surfaceLight

        Label {
            anchors.left: parent.left
            anchors.leftMargin: ThemeTokens.spaceMd
            anchors.verticalCenter: parent.verticalCenter
            text: qsTr("Spending")
            font.pixelSize: ThemeTokens.fontXl
            font.weight: ThemeTokens.weightSemiBold
        }
    }

    component ExpenseCardDelegate: ItemDelegate {
        id: expenseDelegate

        required property int index
        required property string expenseId
        required property real amount
        required property string currency
        required property string occurredOn
        required property string nameLabel
        required property string categoryLabel
        required property string placeLabel
        required property string note

        width: ListView.view ? ListView.view.width : parent.width
        height: 80
        padding: 0
        topPadding: 4
        bottomPadding: 4
        leftPadding: ThemeTokens.spaceMd
        rightPadding: ThemeTokens.spaceMd

        background: Rectangle {
            radius: ThemeTokens.radiusLg
            color: expenseDelegate.hovered ? Qt.lighter(root.cardColor, 1.04) : root.cardColor
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
                    text: expenseDelegate.nameLabel
                    font.pixelSize: ThemeTokens.fontMd
                    font.weight: ThemeTokens.weightSemiBold
                    elide: Text.ElideRight
                }

                Label {
                    Layout.fillWidth: true
                    text: {
                        var parts = []
                        if (expenseDelegate.occurredOn !== "") {
                            parts.push(root.formatDate(expenseDelegate.occurredOn))
                        }
                        if (expenseDelegate.categoryLabel !== "") {
                            parts.push(expenseDelegate.categoryLabel)
                        }
                        if (expenseDelegate.placeLabel !== "") {
                            parts.push(expenseDelegate.placeLabel)
                        }
                        return parts.join(" · ")
                    }
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
                color: root.isDark ? "#7F1D1D" : "#FEE2E2"

                Label {
                    id: amountLabel
                    anchors.centerIn: parent
                    text: root.formatAmount(expenseDelegate.amount, expenseDelegate.currency)
                    font.pixelSize: ThemeTokens.fontSm
                    font.weight: ThemeTokens.weightMedium
                    color: root.isDark ? "#FCA5A5" : ThemeTokens.expenseRed
                }
            }

            ToolButton {
                Layout.alignment: Qt.AlignVCenter
                icon.source: "qrc:/icons/edit.svg"
                opacity: expenseDelegate.hovered ? 1.0 : 0.35
                Accessible.name: qsTr("Edit %1").arg(expenseDelegate.nameLabel)
                onClicked: expenseFormDrawer.openForEdit(expenseDelegate)
            }

            ToolButton {
                Layout.alignment: Qt.AlignVCenter
                icon.source: "qrc:/icons/delete.svg"
                icon.color: Material.color(Material.Red)
                opacity: expenseDelegate.hovered ? 1.0 : 0.35
                Accessible.name: qsTr("Delete %1").arg(expenseDelegate.nameLabel)
                onClicked: {
                    deleteExpenseDialog.expenseId = expenseDelegate.expenseId
                    deleteExpenseDialog.expenseName = expenseDelegate.nameLabel
                    deleteExpenseDialog.open()
                }
            }
        }
    }

    Item {
        anchors.fill: parent

        ListView {
            id: expenseList
            anchors.fill: parent
            anchors.topMargin: ThemeTokens.spaceSm
            anchors.bottomMargin: ThemeTokens.spaceXl + 56
            clip: true
            spacing: 4
            visible: recordedExpensesViewModel.expenseListModel.count > 0
            model: recordedExpensesViewModel.expenseListModel
            boundsBehavior: Flickable.StopAtBounds

            delegate: ExpenseCardDelegate {}
        }

        ColumnLayout {
            anchors.centerIn: parent
            visible: recordedExpensesViewModel.expenseListModel.count === 0
            spacing: ThemeTokens.spaceSm
            width: Math.min(root.width - ThemeTokens.spaceXl * 2, 360)

            Label {
                Layout.fillWidth: true
                text: qsTr("No recorded expenses yet")
                horizontalAlignment: Text.AlignHCenter
                font.pixelSize: ThemeTokens.fontMd
                color: Material.secondaryTextColor
            }

            Label {
                Layout.fillWidth: true
                text: qsTr("Add your first recorded expense using the + button")
                horizontalAlignment: Text.AlignHCenter
                wrapMode: Text.WordWrap
                font.pixelSize: ThemeTokens.fontSm
                color: Material.secondaryTextColor
            }
        }
    }

    Button {
        id: addExpenseFab
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
        Accessible.name: qsTr("Add recorded expense")

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

        onClicked: expenseFormDrawer.openForCreate()
    }

    RecordedExpenseFormDrawer {
        id: expenseFormDrawer
    }

    CenteredDialog {
        id: deleteExpenseDialog
        standardButtons: Dialog.NoButton
        width: Math.min(root.width - ThemeTokens.spaceXl, 360)

        property string expenseId: ""
        property string expenseName: ""

        background: Rectangle {
            radius: ThemeTokens.radiusLg
            color: root.cardColor
        }

        header: Label {
            text: qsTr("Delete recorded expense")
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
                text: qsTr("Delete \"%1\"?").arg(deleteExpenseDialog.expenseName)
                wrapMode: Text.WordWrap
            }
        }

        footer: DialogButtonBox {
            Button {
                text: qsTr("Cancel")
                flat: true
                DialogButtonBox.buttonRole: DialogButtonBox.RejectRole
                onClicked: deleteExpenseDialog.close()
            }

            Button {
                text: qsTr("Delete")
                Material.background: Material.color(Material.Red)
                Material.foreground: "white"
                DialogButtonBox.buttonRole: DialogButtonBox.DestructiveRole
                onClicked: {
                    if (deleteExpenseDialog.expenseId !== "") {
                        recordedExpensesViewModel.deleteExpense(deleteExpenseDialog.expenseId)
                    }
                    deleteExpenseDialog.close()
                }
            }
        }
    }

    Component.onCompleted: recordedExpensesViewModel.loadExpenses()
}
