import QtQuick
import QtQuick.Layouts
import "./../../res/customtypes"

UniswagOscChSettingsBar {
    id: settingsBar

    onReloadOscChannelSettings: function() {
        OscProperties._operands_avail()
        OscProperties._operators_avail()
        OscProperties._shift(NaN)
    }

    onTriggerSliderPositionChanged: function(position) {
    }

    onZoomed: function() {
    }

    RowLayout {

        UniswagCombobox {
            id: operand1

            labelText: "1st Operand"
            backgroundColor: settingsBar.backgroundColor
            onClick: function(selectedText) {
                OscProperties._operand1(selectedText)
                settingsBar.updateDisplayedChannelData()
            }
        }

        UniswagCombobox {
            id: operator

            labelText: "Operator"
            backgroundColor: settingsBar.backgroundColor
            onClick: function(selectedText) {
                OscProperties._operator(selectedText)
                settingsBar.updateDisplayedChannelData()
            }
        }

        UniswagCombobox {
            id: operand2

            labelText: "2nd Operand"
            backgroundColor: settingsBar.backgroundColor
            onClick: function(selectedText) {
                OscProperties._operand2(selectedText)
                settingsBar.updateDisplayedChannelData()
            }
        }

        UniswagTextfield {
            id: shift

            labelText: "Time Shift (2nd Operand)"
            backgroundColor: settingsBar.backgroundColor
            onConfirm: function(enteredText) {
                OscProperties._shift(enteredText)
                settingsBar.updateDisplayedChannelData()
            }
        }

    }

    Connections {
        target: OscProperties

        function onOperator(device_id, ch_num, value) {
            if (!functions.isSelectedDevice(device_id, ch_num)) {
                return
            }
            functions.updateComboboxSelection(operator, value)
        }
        function onOperatorsAvail(device_id, ch_num, value) {
            if (!functions.isSelectedDevice(device_id, ch_num)) {
                return
            }
            functions.updateComboboxList(operator, value)
        }

        function onOperand1(device_id, ch_num, value) {
            if (!functions.isSelectedDevice(device_id, ch_num)) {
                return
            }
            functions.updateComboboxSelection(operand1, value)
        }
        function onOperand2(device_id, ch_num, value) {
            if (!functions.isSelectedDevice(device_id, ch_num)) {
                return
            }
            functions.updateComboboxSelection(operand2, value)
        }
        function onOperandsAvail(device_id, ch_num, value) {
            if (!functions.isSelectedDevice(device_id, ch_num)) {
                return
            }
            functions.updateComboboxList(operand1, value)
            functions.updateComboboxList(operand2, value)
        }

        function onShift(device_id, ch_num, value) {
            if (!functions.isSelectedDevice(device_id, ch_num)) {
                return
            }
            functions.updateTextfield(shift, value)
        }
    }

    Connections {
        target: FrontToBackConnector

        function onReloadMathChProp(device_id, ch_num) {
            if (!functions.isSelectedDevice(device_id, ch_num)) {
                return
            }
            settingsBar.updateDisplayedChannelData()
        }
    }

}
