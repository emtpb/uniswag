import QtQuick
import QtQuick.Layouts
import "./../../res/customtypes"

UniswagGenDevSettingsBar {
    id: settingsBar

    onReloadGeneratorSettings: function() {
        GenProperties._is_running()
    }

    RowLayout {
        // Trigger Source not supported
        // Trigger Timer not supported

        UniswagButton {
            id: startStop

            labelText: "Start/Stop"
            backgroundColor: settingsBar.backgroundColor
            onClick: function() {
                GenProperties._start_n_stop()
            }
        }
    }

    Connections {
        target: GenProperties

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
