import QtQuick
import QtQuick.Layouts
import QtQuick.Controls


GridLayout {
    columns: 2
    columnSpacing: 10

    signal reloadGeneratorSettings()

    property var background_color: darkModeEnabled? colorPalette.dark : colorPalette.light

    // Trigger Source not supported
    // Trigger Timer not supported

    Label {
        id: resetLabel
        text: "Reset"
    }
    Label {
        id: forceTrigLabel
        text: "Trigger"
    }


    // Reset
    Button {
        id: reset
        text: "Perform"
        onClicked: GenProperties._reset()

        background: Rectangle {
            implicitWidth: resetLabel.width
            implicitHeight: 25
            radius: 2
            color: background_color
            border.color: colorPalette.light
            border.width: 1
        }
    }

    // Force Trigger
    Button {
        id: forceTrig
        text: "Force"
        onClicked: GenProperties._force_trig()

        background: Rectangle {
            implicitWidth: forceTrigLabel.width
            implicitHeight: 25
            radius: 2
            color: background_color
            border.color: colorPalette.light
            border.width: 1
        }
    }


    onReloadGeneratorSettings: {

    }

    function loadCurrentSettings(){
        signalGenMainRect.reloadGenChannelSettings()
    }


    Connections {
        target: GenProperties

        // Reset
        function onReset(device_id, value) {
            if(compareDevices(device_id, signalGenMainRect.selectedDevice)){
                loadCurrentSettings()
            }
        }

    }
}





