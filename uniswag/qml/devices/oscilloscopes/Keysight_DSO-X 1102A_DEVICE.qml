import QtQuick
import QtQuick.Layouts
import QtQuick.Controls


GridLayout {
    columns: 7
    columnSpacing: 10

     property var background_color: darkModeEnabled? colorPalette.dark : colorPalette.light

    Label {
        id: startStopLabel
        text: "Start/Stop"
    }
    Label {
        id: resetLabel
        text: "Reset"
    }
    Label {
        id: recordLengthLabel
        text: "Record length"
    }
    Label {
        id: timeBaseLabel
        text: "Time Base"
    }

    Label {
        id: triggerModeLabel
        text: "Trigger Mode"
    }
    Label {
        id: triggerSweepLabel
        text: "Trigger Sweep"
    }
    Label {
        id: triggerSlopeLabel
        text: "Trigger Slope"
    }

    // Start/Stop
    Button {
        id: startStop
        text: ""
        onClicked: OscProperties._start_n_stop()

        background: Rectangle {
            implicitWidth: startStopLabel.width
            implicitHeight: 25
            radius: 2
            color: background_color
            border.color: colorPalette.light
            border.width: 1
        }
    }


    // Reset
    Button {
        id: reset
        text: "Perform"
        onClicked: OscProperties._reset()

        background: Rectangle {
            implicitWidth: resetLabel.width
            implicitHeight: 25
            radius: 2
            color: background_color
            border.color: colorPalette.light
            border.width: 1
        }
    }


    // Record length
    TextField {
        id: recordLength
        onAccepted: OscProperties._rec_len(text)

        background: Rectangle {
            implicitWidth: recordLengthLabel.width
            implicitHeight: 25
            radius: 2
            color: background_color
            border.color: colorPalette.light
            border.width: 1
        }
    }


    // Time Base
    TextField {
        id: timeBase
        onAccepted: OscProperties._time_base(text)

        background: Rectangle {
            implicitWidth: timeBaseLabel.width
            implicitHeight: 25
            radius: 2
            color: background_color
            border.color: colorPalette.light
            border.width: 1
        }
    }

    // Trigger Mode
    ComboBox {
        id: triggerMode
        model: ListModel{}
        onActivated: OscProperties._trig_mode(currentText)

        background: Rectangle {
            implicitWidth: triggerModeLabel.width
            implicitHeight: 25
            radius: 2
            color: background_color
            border.color: colorPalette.light
            border.width: 1
        }
    }

    // Trigger Sweep
    ComboBox {
        id: triggerSweep
        model: ListModel{}
        onActivated: OscProperties._trig_sweep(currentText)

        background: Rectangle {
            implicitWidth: triggerSweepLabel.width
            implicitHeight: 25
            radius: 2
            color: background_color
            border.color: colorPalette.light
            border.width: 1
        }
    }


    // Trigger Slope
    ComboBox {
        id: triggerSlope
        model: ListModel{}
        onActivated: OscProperties._trig_slope(currentText)

        background: Rectangle {
            implicitWidth: triggerSlopeLabel.width
            implicitHeight: 25
            radius: 2
            color: background_color
            border.color: colorPalette.light
            border.width: 1
        }
    }



    Component.onCompleted: {
        OscProperties._is_running()
        OscProperties._rec_len(NaN)
        OscProperties._time_base(NaN)

        OscProperties._trig_modes_avail()

        OscProperties._trig_sweeps_avail()

        OscProperties._trig_slopes_avail()

    }

    Connections {
        target: OscProperties

        function onIsRunning(device_id, value) {
            if(compareDevices(device_id, oscilloscopeMainRect.selectedDevice)){
                if(value === true){
                    startStop.text = "Stop"
                }
                else {
                     startStop.text = "Start"
                }
            }
        }

        function onRecLen(device_id, value) {
            if(compareDevices(device_id, oscilloscopeMainRect.selectedDevice)){
                recordLength.text = ""
                recordLength.placeholderText = value
            }
        }

        function onTimeBase(device_id, value) {
            if(compareDevices(device_id, oscilloscopeMainRect.selectedDevice)){
                timeBase.text = ""
                timeBase.placeholderText = value
            }
        }

        function onTrigMode(device_id, value) {
            if(compareDevices(device_id, oscilloscopeMainRect.selectedDevice)){
                triggerMode.currentIndex = findIndexOfModel(triggerMode.model, value)
            }
        }
        function onTrigModesAvail(device_id, value) {
            if(compareDevices(device_id, oscilloscopeMainRect.selectedDevice)){
                triggerMode.model = value
                oscilloscopeMainRect.triangleIcon()
            }
        }

        function onTrigSweep(device_id, value) {
            if(compareDevices(device_id, oscilloscopeMainRect.selectedDevice)){
                triggerSweep.currentIndex = findIndexOfModel(triggerSweep.model, value)
            }
        }
        function onTrigSweepsAvail(device_id, value) {
            if(compareDevices(device_id, oscilloscopeMainRect.selectedDevice)){
                triggerSweep.model = value
            }
        }

        function onTrigSlope(device_id, value) {
            if(compareDevices(device_id, oscilloscopeMainRect.selectedDevice)){
                triggerSlope.currentIndex = findIndexOfModel(triggerSlope.model, value)
            }
        }
        function onTrigSlopesAvail(device_id, value) {
            if(compareDevices(device_id, oscilloscopeMainRect.selectedDevice)){
                triggerSlope.model = value
            }
        }

    }

    Connections {
        target: FrontToBackConnector

        function onIsRunning(device_id, value) {
            if(compareDevices(device_id, oscilloscopeMainRect.selectedDevice)){
                if(value === true){
                    startStop.text = "Stop"
                }
                else {
                     startStop.text = "Start"
                }
            }
        }

    }
}





