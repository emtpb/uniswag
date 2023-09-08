import QtQuick
import QtQuick.Layouts
import "./../../res/customtypes"

UniswagGenDevSettingsBar {
    id: settingsBar

    onReloadGeneratorSettings: function() {
    }

    RowLayout {
        // Trigger Source not supported
        // Trigger Timer not supported

        UniswagButton {
            labelText: "Reset"
            buttonText: "Perform"
            backgroundColor: settingsBar.backgroundColor
            onClick: function() {
                GenProperties._reset()
            }
        }

        UniswagButton {
            labelText: "Trigger"
            buttonText: "Force"
            backgroundColor: settingsBar.backgroundColor
            onClick: function() {
                GenProperties._force_trig()
            }
        }

    }

    Connections {
        target: GenProperties

        function onReset(device_id, value) {
            if (!functions.isSelectedDevice(device_id)) {
                return
            }
            settingsBar.updateDisplayedGenData()
        }
    }

}
