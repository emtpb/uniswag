import QtQuick
import QtQuick.Layouts
import QtQuick.Controls


ColumnLayout {
    id: uniswagCheckbox

    property string labelText: "Checkbox"
    property string checkboxText: ""
    property var backgroundColor: palette.light
    property int widthExtension: 0
    signal click(isActive: bool)

    property var box: checkbox

    Label {
        id: checkboxLabel
        text: uniswagCheckbox.labelText
    }
    CheckBox {
        id: checkbox

        text: uniswagCheckbox.checkboxText
        implicitHeight: 25
        indicator: Rectangle {
            implicitWidth: 12
            implicitHeight: 12
            x: checkbox.leftPadding
            y: parent.height / 2 - height / 2
            radius: 3
            border.color: checkbox.checked ? "#17a81a" : "#990000"
            Rectangle {
                width: 6
                height: 6
                x: 3
                y: 3
                radius: 2
                color: "#21be2b"
                visible: checkbox.checked
            }
        }
        contentItem: Text {
            text: checkbox.text
            font: checkbox.font
            opacity: enabled ? 1.0 : 0.3
            color: checkbox.checked ? "#17a81a" : "#990000"
            verticalAlignment: Text.AlignVCenter
            leftPadding: checkbox.indicator.width + checkbox.spacing
        }
        background: Rectangle {
            implicitWidth: checkboxLabel.width + uniswagCheckbox.widthExtension
            implicitHeight: 25
            radius: 2
            color: uniswagCheckbox.backgroundColor
            border.color: colorPalette.light
            border.width: 1
        }
        onToggled: {
            let value = (checkbox.checkState == 0 ? false : true)
            click(value)
        }
    }
}
