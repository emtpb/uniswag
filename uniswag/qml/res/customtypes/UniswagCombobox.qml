import QtQuick
import QtQuick.Layouts
import QtQuick.Controls


ColumnLayout {
    id: uniswagCombobox

    property string labelText: "Combobox"
    property var backgroundColor: palette.light
    property int widthExtension: 0
    signal click(selectedText: string)

    property var list: ListModel {}
    property int listIndex: -1

    Label {
        id: comboboxLabel
        text: uniswagCombobox.labelText
    }
    ComboBox {
        id: combobox

        implicitContentWidthPolicy: ComboBox.WidestText
        model: uniswagCombobox.list
        currentIndex: uniswagCombobox.listIndex
        onActivated: {
            click(currentText)
        }
        background: Rectangle {
            implicitWidth: comboboxLabel.width + uniswagCombobox.widthExtension
            implicitHeight: 25
            radius: 2
            color: uniswagCombobox.backgroundColor
            border.color: colorPalette.light
            border.width: 1
        }
    }
}
