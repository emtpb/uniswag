import QtQuick
import QtQuick.Layouts
import QtQuick.Controls


ColumnLayout {
    id: uniswagButton

    property string labelText: "Button"
    property string buttonText: ""
    property var backgroundColor: palette.light
    property int widthExtension: 0
    signal click()

    Label {
        id: buttonLabel
        text: uniswagButton.labelText
    }
    Button {
        text: uniswagButton.buttonText
        onClicked: click()

        background: Rectangle {
            implicitWidth: buttonLabel.width + uniswagButton.widthExtension
            implicitHeight: 25
            radius: 2
            color: uniswagButton.backgroundColor
            border.color: colorPalette.light
            border.width: 1
        }
    }
}
