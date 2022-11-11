import QtQuick
import QtQuick.Layouts
import QtQuick.Controls

GridLayout {
    columns: 1
    columnSpacing: 10

    property var background_color: darkModeEnabled? colorPalette.dark : colorPalette.light

    Label {
        id: startStopLabel
        text: "Start/Stop"
    }

    // Start/Stop
    Button {
        id: startStop
        text: ""
        onClicked: GenProperties._start_n_stop()

        background: Rectangle {
            implicitWidth: startStopLabel.width
            implicitHeight: 25
            radius: 2
            color: background_color
            border.color: colorPalette.light
            border.width: 1
        }
    }


    Component.onCompleted: {
        GenProperties._is_running()
    }


    Connections {
        target: GenProperties

        function onIsRunning(device_id, value) {
            if(compareDevices(device_id, signalGenMainRect.selectedDevice)){
                if(value === true){
                    startStop.text = "Stop"
                }
                else {
                     startStop.text = "Start"
                }
            }
        }

    }

    Connections {
        target: FrontToBackConnector

        function onIsRunning(device_id, value) {
            if(compareDevices(device_id, signalGenMainRect.selectedDevice)){
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





