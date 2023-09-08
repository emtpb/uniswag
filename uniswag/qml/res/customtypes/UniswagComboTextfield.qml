import QtQuick
import QtQuick.Layouts
import QtQuick.Controls


ColumnLayout {
    id: uniswagComboTextfield

    property string labelText: "Combo-Textfield"
    property var backgroundColor: palette.light
    property var list: ListModel {}
    property int widthExtension: 0
    signal clickOrConfirm(passedText: string)

    property var textBox: combobox

    Label {
        id: comboboxLabel
        text: uniswagComboTextfield.labelText
    }
    ComboBox {
        id: combobox

        editable: true
        implicitContentWidthPolicy: ComboBox.WidestText
        model: uniswagComboTextfield.list
        onAccepted: {
            clickOrConfirm(editText)
        }
        onActivated: {
            clickOrConfirm(currentText)
        }
        background: Rectangle {
            implicitWidth: comboboxLabel.width + uniswagComboTextfield.widthExtension
            implicitHeight: 25
            radius: 2
            color: uniswagComboTextfield.backgroundColor
            border.color: colorPalette.light
            border.width: 1
        }
    }
}
