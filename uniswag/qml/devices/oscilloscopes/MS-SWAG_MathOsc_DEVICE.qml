import QtQuick
import QtQuick.Layouts
import "./../../res/customtypes"

UniswagOscDevSettingsBar {
    id: settingsBar

    onReloadOscilloscopeSettings: function() {
        OscProperties._is_running()

        // Trigger Kinds not supported
        functions.triggerSliderIconUpdate()
    }

    RowLayout {

        UniswagButton {
            id: startStop

            labelText: "Start/Stop"
            backgroundColor: settingsBar.backgroundColor
            onClick: function() {
                OscProperties._start_n_stop()
            }
        }

        UniswagButton {
            labelText: "Add Channel"
            buttonText: "+ 1"
            backgroundColor: settingsBar.backgroundColor
            onClick: function() {
                OscProperties._add_ch()
            }
        }

        UniswagButton {
            labelText: "Remove Channel"
            buttonText: "- 1"
            backgroundColor: settingsBar.backgroundColor
            onClick: function() {
                OscProperties._remove_ch()
            }
        }

    }

    Connections {
        target: OscProperties

        function onIsRunning(device_id, value) {
            if (!functions.isSelectedDevice(device_id)) {
                return
            }
            functions.updateBinaryButton(startStop, value, "Stop", "Start")
        }
    }

    Connections {
        target: FrontToBackConnector

        function onIsRunning(device_id, value) {
            if (!functions.isSelectedDevice(device_id)) {
                return
            }
            functions.updateBinaryButton(startStop, value, "Stop", "Start")
        }
    }

}
