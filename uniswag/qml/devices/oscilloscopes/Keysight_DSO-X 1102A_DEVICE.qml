import QtQuick
import QtQuick.Layouts
import "./../../res/customtypes"

UniswagOscDevSettingsBar {
    id: settingsBar

    onReloadOscilloscopeSettings: function() {
        OscProperties._is_running()
        OscProperties._rec_len(NaN)
        OscProperties._time_base(NaN)
        OscProperties._trig_modes_avail()
        OscProperties._trig_sweeps_avail()
        OscProperties._trig_slopes_avail()

        // Trigger Kinds not supported
        functions.triggerSliderIconUpdate()
    }

    RowLayout {

        UniswagTextfield {
            id: recordLength

            labelText: "Record length"
            backgroundColor: settingsBar.backgroundColor
            onConfirm: function(enteredText) {
                OscProperties._rec_len(enteredText)
            }
        }

        UniswagTextfield {
            id: timeBase

            labelText: "Time Base"
            backgroundColor: settingsBar.backgroundColor
            onConfirm: function(enteredText) {
                OscProperties._time_base(enteredText)
            }
        }

        UniswagCombobox {
            id: triggerMode

            labelText: "Trigger Mode"
            backgroundColor: settingsBar.backgroundColor
            onClick: function(selectedText) {
                OscProperties._trig_mode(selectedText)
            }
        }

        UniswagCombobox {
            id: triggerSweep

            labelText: "Trigger Sweep"
            backgroundColor: settingsBar.backgroundColor
            onClick: function(selectedText) {
                OscProperties._trig_sweep(selectedText)
            }
        }

        UniswagCombobox {
            id: triggerSlope

            labelText: "Trigger Slope"
            backgroundColor: settingsBar.backgroundColor
            onClick: function(selectedText) {
                OscProperties._trig_slope(selectedText)
            }
        }

        UniswagButton {
            labelText: "Reset"
            buttonText: "Perform"
            backgroundColor: settingsBar.backgroundColor
            onClick: function() {
                OscProperties._reset()
            }
        }

        UniswagButton {
            id: startStop

            labelText: "Start/Stop"
            backgroundColor: settingsBar.backgroundColor
            onClick: function() {
                OscProperties._start_n_stop()
            }
        }

    }

    Connections {
        target: OscProperties

        function onRecLen(device_id, value) {
            if (!functions.isSelectedDevice(device_id)) {
                return
            }
            let listOfIncreasingUnits = ["Sam", "kSam"]
            value = functions.appendPrefixedUnit(value, 3, listOfIncreasingUnits)
            functions.updateComboTextfield(recordLength, value)
        }

        function onTimeBase(device_id, value) {
            if (!functions.isSelectedDevice(device_id)) {
                return
            }
            let listOfIncreasingUnits = ["Sam", "kSam"]
            value = functions.appendPrefixedUnit(value, 3, listOfIncreasingUnits)
            functions.updateComboTextfield(timeBase, value)
        }

        function onTrigMode(device_id, value) {
            if (!functions.isSelectedDevice(device_id)) {
                return
            }
            functions.updateComboboxSelection(triggerMode, value)
        }
        function onTrigModesAvail(device_id, value) {
            if (!functions.isSelectedDevice(device_id)) {
                return
            }
            functions.updateComboboxList(triggerMode, value)
            /*
            oscilloscopeMainRect.triangleIcon()
            */
        }

        function onTrigSweep(device_id, value) {
            if (!functions.isSelectedDevice(device_id)) {
                return
            }
            functions.updateComboboxSelection(triggerSweep, value)
        }
        function onTrigSweepsAvail(device_id, value) {
            if (!functions.isSelectedDevice(device_id)) {
                return
            }
            functions.updateComboboxList(triggerSweep, value)
        }

        function onTrigSlope(device_id, value) {
            if (!functions.isSelectedDevice(device_id)) {
                return
            }
            functions.updateComboboxSelection(triggerSlope, value)
        }
        function onTrigSlopesAvail(device_id, value) {
            if (!functions.isSelectedDevice(device_id)) {
                return
            }
            functions.updateComboboxList(triggerSlope, value)
        }

        function onReset(device_id, value) {
            if (!functions.isSelectedDevice(device_id)) {
                return
            }
            settingsBar.updateDisplayedOscData()
        }

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
