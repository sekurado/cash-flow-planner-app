import QtQuick
import QtQuick.Controls

Dialog {
    id: root

    parent: Overlay.overlay
    modal: true
    focus: true

    x: parent ? (parent.width - width) / 2 : 0
    y: parent ? (parent.height - height) / 2 : 0
}
