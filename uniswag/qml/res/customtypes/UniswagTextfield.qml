import QtQuick
import QtQuick.Layouts
import QtQuick.Controls


ColumnLayout {
    id: uniswagTextfield

    property string labelText: "Textfield"
    property var backgroundColor: palette.light
    property int widthExtension: 0
    signal confirm(enteredText: string)

    property var textInput: textfield
    property string textfieldPlaceholder: "Enter value"

    Label {
        id: textfieldLabel
        text: uniswagTextfield.labelText
    }
    TextField {
        id: textfield

        placeholderText: uniswagTextfield.textfieldPlaceholder
        onAccepted: {
            confirm(text)
        }

        background: Rectangle {
            implicitWidth: textfieldLabel.width + uniswagTextfield.widthExtension
            implicitHeight: 25
            radius: 2
            color: uniswagTextfield.backgroundColor
            border.color: colorPalette.light
            border.width: 1
        }
    }
}
