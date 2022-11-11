import QtQuick
import QtQuick.Layouts
import QtQuick.Controls

GridLayout {
    signal reloadOscilloscopeSettings()

    property var background_color: darkModeEnabled? colorPalette.dark : colorPalette.light

    columns: 3
    columnSpacing: 10

    Label {
        id: startStopLabel
        text: "Start/Stop"
    }
    Label {
        id: addChLabel
        text: "Add Channel"
    }
    Label {
        id: removeChLabel
        text: "Remove Channel"
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

    // Add Channel
    Button {
        id: addCh
        text: "+ 1"
        onClicked: OscProperties._add_ch()

        background: Rectangle {
            implicitWidth: addChLabel.width
            implicitHeight: 25
            radius: 2
            color: background_color
            border.color: colorPalette.light
            border.width: 1
        }
    }

    // Remove Channel
    Button {
        id: removeCh
        text: "- 1"
        onClicked: OscProperties._remove_ch()

        background: Rectangle {
            implicitWidth: removeChLabel.width
            implicitHeight: 25
            radius: 2
            color: background_color
            border.color: colorPalette.light
            border.width: 1
        }
    }

    onReloadOscilloscopeSettings: {
        reloadOscSettings()
    }

    function reloadOscSettings(){
        OscProperties._is_running()
    }

    function updateDisplayedOscData(){
        reloadOscSettings()
        oscilloscopeMainRect.reloadOscChannelSettings()
    }


    Component.onCompleted: {
       updateDisplayedOscData()
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
