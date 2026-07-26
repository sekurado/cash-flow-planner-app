import QtQuick
import QtQuick.Controls
import QtQuick.Controls.Material
import QtQuick.Layouts
import Qt5Compat.GraphicalEffects

import ThemeTokens 1.0

Item {
    id: root

    property int day: 1
    property int month: 1
    property int year: 2026
    property bool stacked: false

    property int viewMonth: root.month
    property int viewYear: root.year

    readonly property bool isDark: Material.theme === Material.Dark
    readonly property color cardColor: isDark ? ThemeTokens.cardDark : ThemeTokens.cardLight

    readonly property string formattedDate: {
        return root.year + "-" + root.pad2(root.month) + "-" + root.pad2(root.day)
    }

    readonly property var today: {
        var d = new Date()
        d.setHours(0, 0, 0, 0)
        return d
    }

    implicitWidth: root.stacked ? Math.max(dateButton.implicitWidth, 200) : dateButton.implicitWidth
    implicitHeight: dateButton.implicitHeight

    function pad2(value) {
        return value < 10 ? "0" + value : "" + value
    }

    function daysInMonth(yearValue, monthValue) {
        return new Date(yearValue, monthValue, 0).getDate()
    }

    function clampDay() {
        var maxDay = root.daysInMonth(root.year, root.month)
        if (root.day > maxDay) {
            root.day = maxDay
        }
    }

    function popupX() {
        if (!calendarPopup.parent) {
            return 0
        }
        return dateButton.mapToItem(calendarPopup.parent, 0, 0).x
    }

    function popupY() {
        if (!calendarPopup.parent) {
            return 0
        }
        var mapped = dateButton.mapToItem(calendarPopup.parent, 0, dateButton.height)
        return mapped.y + 4
    }

    function isSameCalendarDay(cellDay, cellMonth, cellYear) {
        return cellDay === root.today.getDate()
            && cellMonth === root.today.getMonth()
            && cellYear === root.today.getFullYear()
    }

    onMonthChanged: root.clampDay()
    onYearChanged: root.clampDay()

    Button {
        id: dateButton
        anchors.left: parent.left
        anchors.right: root.stacked ? parent.right : undefined
        flat: true
        display: AbstractButton.TextBesideIcon
        icon.name: "office-calendar"
        text: root.formattedDate
        Material.foreground: ThemeTokens.primary
        Accessible.name: qsTr("Date")
        onClicked: calendarPopup.open()

        background: Rectangle {
            radius: ThemeTokens.radiusSm
            color: "transparent"
            border.color: ThemeTokens.primary
            border.width: 1
        }
    }

    Popup {
        id: calendarPopup
        parent: Overlay.overlay
        modal: false
        focus: true
        closePolicy: Popup.CloseOnEscape | Popup.CloseOnPressOutside
        padding: ThemeTokens.spaceMd
        width: calendarColumn.implicitWidth + 2 * padding
        implicitHeight: calendarColumn.implicitHeight + 2 * padding
        x: root.popupX()
        y: root.popupY()

        background: Rectangle {
            id: popupBackground
            color: root.cardColor
            radius: ThemeTokens.radiusLg
            layer.enabled: true
            layer.effect: DropShadow {
                radius: 8
                samples: 17
                color: "#18000000"
                verticalOffset: 2
            }
        }

        onOpened: {
            root.viewMonth = root.month
            root.viewYear = root.year
        }

        contentItem: ColumnLayout {
            id: calendarColumn
            spacing: ThemeTokens.spaceSm

            RowLayout {
                Layout.fillWidth: true
                spacing: ThemeTokens.spaceXs

                ToolButton {
                    text: "<"
                    icon.color: ThemeTokens.primary
                    Material.foreground: ThemeTokens.primary
                    Accessible.name: qsTr("Previous month")
                    onClicked: {
                        if (root.viewMonth === 1) {
                            root.viewMonth = 12
                            root.viewYear -= 1
                        } else {
                            root.viewMonth -= 1
                        }
                    }
                }

                Label {
                    Layout.fillWidth: true
                    horizontalAlignment: Text.AlignHCenter
                    text: monthGrid.title
                    font.pixelSize: ThemeTokens.fontMd
                    font.weight: ThemeTokens.weightSemiBold
                }

                ToolButton {
                    text: ">"
                    icon.color: ThemeTokens.primary
                    Material.foreground: ThemeTokens.primary
                    Accessible.name: qsTr("Next month")
                    onClicked: {
                        if (root.viewMonth === 12) {
                            root.viewMonth = 1
                            root.viewYear += 1
                        } else {
                            root.viewMonth += 1
                        }
                    }
                }
            }

            DayOfWeekRow {
                locale: monthGrid.locale
                Layout.fillWidth: true

                delegate: Text {
                    required property string shortName

                    width: 36
                    horizontalAlignment: Text.AlignHCenter
                    text: shortName.toUpperCase()
                    font.pixelSize: ThemeTokens.fontXs
                    color: Material.secondaryTextColor
                }
            }

            MonthGrid {
                id: monthGrid
                month: root.viewMonth - 1
                year: root.viewYear
                locale: Qt.locale()
                Layout.fillWidth: true

                onClicked: function (date) {
                    root.year = date.getFullYear()
                    root.month = date.getMonth() + 1
                    root.day = date.getDate()
                    calendarPopup.close()
                }

                delegate: Item {
                    id: dayCell

                    required property var model

                    readonly property bool inViewMonth: model.month === monthGrid.month
                    readonly property bool isSelected: model.day === root.day
                                                         && model.month === root.month - 1
                                                         && model.year === root.year
                    readonly property bool isToday: root.isSameCalendarDay(
                        model.day, model.month, model.year)

                    implicitWidth: 36
                    implicitHeight: 40

                    Rectangle {
                        id: dayBackground
                        anchors.centerIn: parent
                        width: 32
                        height: 32
                        radius: ThemeTokens.radiusFull
                        color: dayCell.isSelected
                            ? ThemeTokens.primary
                            : (dayMouse.containsMouse
                                ? Qt.rgba(
                                    ThemeTokens.primary.r,
                                    ThemeTokens.primary.g,
                                    ThemeTokens.primary.b,
                                    0.12)
                                : "transparent")
                    }

                    Text {
                        id: dayText
                        anchors.centerIn: parent
                        horizontalAlignment: Text.AlignHCenter
                        verticalAlignment: Text.AlignVCenter
                        text: model.day
                        font: monthGrid.font
                        color: dayCell.isSelected ? "white" : Material.foreground
                        opacity: dayCell.inViewMonth ? 1.0 : 0.35
                    }

                    Rectangle {
                        visible: dayCell.isToday && !dayCell.isSelected
                        width: 4
                        height: 4
                        radius: 2
                        color: ThemeTokens.accent
                        anchors.horizontalCenter: parent.horizontalCenter
                        anchors.top: dayText.bottom
                        anchors.topMargin: 1
                    }

                    MouseArea {
                        id: dayMouse
                        anchors.fill: parent
                        hoverEnabled: true
                        onClicked: monthGrid.clicked(new Date(model.year, model.month, model.day))
                    }
                }
            }
        }
    }
}
