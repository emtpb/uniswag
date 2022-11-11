import QtQuick
import QtQuick.Layouts
import QtQuick.Controls

GridLayout {
    columns: 4
    columnSpacing: 10

    signal reloadOscChannelSettings()

    property var background_color: darkModeEnabled? colorPalette.dark : colorPalette.light

    Label {
        id: operand1Label
        text: "1st Operand"
    }
    Label {
        id: operatorLabel
        text: "Operator"
    }
    Label {
        id: operand2Label
        text: "2nd Operand"
    }
    Label {
        id: shiftLabel
        text: "Time Shift (2nd Operand)"
    }

    // Operand 1
    ComboBox {
        id: operand1
        model: ListModel{}
        onActivated: {
            OscProperties._operand1(currentText)
            updateDisplayedChannelData()
        }

        background: Rectangle {
            implicitWidth: operand1Label.width + 200
            implicitHeight: 25
            radius: 2
            color: background_color
            border.color: colorPalette.light
            border.width: 1
        }
    }

    // Operator
    ComboBox {
        id: operator
        model: ListModel{}
        onActivated: {
            OscProperties._operator(currentText)
            updateDisplayedChannelData()
        }

        background: Rectangle {
            implicitWidth: operatorLabel.width + 30
            implicitHeight: 25
            radius: 2
            color: background_color
            border.color: colorPalette.light
            border.width: 1
        }
    }

    // Operand 2
    ComboBox {
        id: operand2
        model: ListModel{}
        onActivated: {
            OscProperties._operand2(currentText)
            updateDisplayedChannelData()
        }

        background: Rectangle {
            implicitWidth: operand2Label.width + 200
            implicitHeight: 25
            radius: 2
            color: background_color
            border.color: colorPalette.light
            border.width: 1
        }
    }

    // Shift
    TextField {
        id: shift
        onAccepted: {
            OscProperties._shift(text)
            updateDisplayedChannelData()
        }

        background: Rectangle {
            implicitWidth: shiftLabel.width
            implicitHeight: 25
            radius: 2
            color: background_color
            border.color: colorPalette.light
            border.width: 1
        }
    }


    onReloadOscChannelSettings: {
        reloadChannelSettings()
    }

    function reloadChannelSettings(){
        OscProperties._operands_avail()
        OscProperties._operators_avail()
        OscProperties._shift(NaN)
    }

    function updateDisplayedChannelData(){
        reloadChannelSettings()
        oscilloscopeMainRect.reloadOscilloscopeSettings()
    }


    Component.onCompleted: {
        updateDisplayedChannelData()
    }


    Connections {
        target: OscProperties

        // Operand 1
        function onOperand1(device_id, ch_num, value) {
            if(compareDevices(device_id, oscilloscopeMainRect.selectedDevice) && ch_num === oscilloscopeMainRect.selectedChannelNum){
                let modelIndex = findIndexOfModel(operand1.model, value)
                if (modelIndex != -1) {
                    operand1.currentIndex = modelIndex
                }
            }
        }
        // Operand 2
        function onOperand2(device_id, ch_num, value) {
            if(compareDevices(device_id, oscilloscopeMainRect.selectedDevice) && ch_num === oscilloscopeMainRect.selectedChannelNum){
                let modelIndex = findIndexOfModel(operand2.model, value)
                if (modelIndex != -1) {
                    operand2.currentIndex = modelIndex
                }
            }
        }
        // Both Operands
        function onOperandsAvail(device_id, ch_num, value) {
            if(compareDevices(device_id, oscilloscopeMainRect.selectedDevice) && ch_num === oscilloscopeMainRect.selectedChannelNum){
                operand1.model = value
                operand2.model = value
            }
        }

        // Operator
        function onOperator(device_id, ch_num, value) {
            if(compareDevices(device_id, oscilloscopeMainRect.selectedDevice) && ch_num === oscilloscopeMainRect.selectedChannelNum){
                let modelIndex = findIndexOfModel(operator.model, value)
                if (modelIndex != -1) {
                    operator.currentIndex = modelIndex
                }
            }
        }
        function onOperatorsAvail(device_id, ch_num, value) {
            if(compareDevices(device_id, oscilloscopeMainRect.selectedDevice) && ch_num === oscilloscopeMainRect.selectedChannelNum){
                operator.model = value
            }
        }

        // Shift
        function onShift(device_id, ch_num, value) {
            if(compareDevices(device_id, oscilloscopeMainRect.selectedDevice) && ch_num === oscilloscopeMainRect.selectedChannelNum){
                shift.text = ""
                shift.placeholderText = value
            }
        }

    }

    Connections {
        target: FrontToBackConnector

        function onReloadMathChProp(device_id, ch_num) {
            if(compareDevices(device_id, oscilloscopeMainRect.selectedDevice) && ch_num === oscilloscopeMainRect.selectedChannelNum){
                updateDisplayedChannelData()
            }
        }

    }
}
