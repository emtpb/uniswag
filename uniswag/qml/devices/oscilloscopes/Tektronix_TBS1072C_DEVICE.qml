import QtQuick
import QtQuick.Layouts
import "./../../res/customtypes"

UniswagOscDevSettingsBar {
    id: settingsBar

    onReloadOscilloscopeSettings: function() {
        OscProperties._is_running()
        OscProperties._sample_freq(NaN)
        OscProperties._rec_len(NaN)
        OscProperties._trig_modes_avail()
        OscProperties._trig_slopes_avail()
        OscProperties._trig_sources_avail()
        OscProperties._pre_sample_ratio(NaN)

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
            id: preSampleRatio

            labelText: "Pre Sample Ratio"
            backgroundColor: settingsBar.backgroundColor
            onConfirm: function(enteredText) {
                OscProperties._pre_sample_ratio(enteredText)
                settingsBar.updateDisplayedOscData()
            }
        }

        UniswagComboTextfield {
            id: frequency

            labelText: "Sample Frequency"
            backgroundColor: settingsBar.backgroundColor
            list: ["100 MHz", "50 MHz", "25 MHz", "10 MHz", "5 MHz", "1 MHz", "100 kHz", "50 kHz", "25 kHz", "10 kHz", "5 kHz", "1 kHz", "500 Hz", "200 Hz", "100 Hz", "50 Hz"]
            onClickOrConfirm: function(passedText) {
                let value = functions.detachPrefixedUnit(passedText, ["Hz", "kHz", "MHz"])
                OscProperties._sample_freq(value)
                settingsBar.updateDisplayedOscData()
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
            id: triggerSlope

            labelText: "Trigger Slope"
            backgroundColor: settingsBar.backgroundColor
            onClick: function(selectedText) {
                OscProperties._trig_slope(selectedText)
            }
        }

        UniswagCombobox {
            id: triggerSource

            labelText: "Trigger Source"
            backgroundColor: settingsBar.backgroundColor
            onClick: function(selectedText) {
                OscProperties._trig_source(selectedText)
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
            functions.updateTextfield(recordLength, value)
        }

        function onSampleFreq(device_id, value) {
            if (!functions.isSelectedDevice(device_id)) {
                return
            }
            let listOfIncreasingUnits = ["Hz", "kHz", "MHz"]
            value = functions.appendPrefixedUnit(value, 3, listOfIncreasingUnits)
            functions.updateComboTextfield(frequency, value)
        }

        function onPreSampleRatio(device_id, value) {
            if (!functions.isSelectedDevice(device_id)) {
                return
            }
            functions.updateTextfield(preSampleRatio, value)
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


        function onTrigSource(device_id, value) {
            if (!functions.isSelectedDevice(device_id)) {
                return
            }
            functions.updateComboboxSelection(triggerSource, value)
        }
        function onTrigSourcesAvail(device_id, value) {
            if (!functions.isSelectedDevice(device_id)) {
                return
            }
            functions.updateComboboxList(triggerSource, value)
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
