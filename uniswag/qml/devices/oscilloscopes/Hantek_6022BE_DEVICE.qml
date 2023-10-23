import QtQuick
import QtQuick.Layouts
import "./../../res/customtypes"

UniswagOscDevSettingsBar {
    id: settingsBar

    onReloadOscilloscopeSettings: function() {
        OscProperties._is_running()
        OscProperties._sample_freq(NaN)
        OscProperties._rec_len(NaN)
        OscProperties._pre_sample_ratio(NaN)
        OscProperties._trig_sources_avail()
    }

    RowLayout {
        // Segment Count not supported
        // Trigger Delay not supported
        // Trigger Hold Off not supported

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
            list: ["48 MHz", "30 MHz", "24 MHz", "16 MHz", "15 MHz", "12 MHz", "10 MHz", "8 MHz", "6 MHz", "5 MHz", "4 MHz", "3 MHz", "2 MHz", "1 MHz", "640 kHz", "500 kHz", "400 kHz", "200 kHz", "128 kHz", "100 kHz", "64 kHz", "50 kHz", "40 kHz", "32 kHz", "20 kHz"]
            onClickOrConfirm: function(passedText) {
                let value = functions.detachPrefixedUnit(passedText, ["Hz", "kHz", "MHz"])
                OscProperties._sample_freq(value)
                settingsBar.updateDisplayedOscData()
            }
        }

        UniswagComboTextfield {
            id: recordLength

            labelText: "Record length"
            backgroundColor: settingsBar.backgroundColor
            widthExtension: 20
            list: ["100 kSam", "50 kSam", "20 kSam", "10 kSam", "5 kSam", "2 kSam", "1 kSam", "500 Sam", "200 Sam", "100 Sam", "50 Sam"]
            onClickOrConfirm: function(passedText) {
                let value = functions.detachPrefixedUnit(passedText, ["Sam", "kSam"])
                OscProperties._rec_len(value)
                settingsBar.updateDisplayedOscData()
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

        function onSampleFreq(device_id, value) {
            if (!functions.isSelectedDevice(device_id)) {
                return
            }
            let listOfIncreasingUnits = ["Hz", "kHz", "MHz"]
            value = functions.appendPrefixedUnit(value, 3, listOfIncreasingUnits)
            functions.updateComboTextfield(frequency, value)
        }

        function onRecLen(device_id, value) {
            if (!functions.isSelectedDevice(device_id)) {
                return
            }
            let listOfIncreasingUnits = ["Sam", "kSam"]
            value = functions.appendPrefixedUnit(value, 3, listOfIncreasingUnits)
            functions.updateComboTextfield(recordLength, value)
        }

        function onPreSampleRatio(device_id, value) {
            if (!functions.isSelectedDevice(device_id)) {
                return
            }
            functions.updateTextfield(preSampleRatio, value)
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
