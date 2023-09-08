import QtQuick
import QtQuick.Layouts
import "./../../res/customtypes"

UniswagOscDevSettingsBar {
    id: settingsBar

    onReloadOscilloscopeSettings: function() {
        OscProperties._seg_cnt(NaN)
        OscProperties._trig_delay(NaN)
        OscProperties._trig_holdoff(NaN)
        OscProperties._is_running()
        OscProperties._res_avail()
        OscProperties._clock_src_avail()
        OscProperties._clock_outs_avail()
        OscProperties._auto_res_avail()
        OscProperties._sample_freq(NaN)
        OscProperties._rec_len(NaN)
        OscProperties._measure_modes_avail()
        OscProperties._trig_timeout(NaN)
        OscProperties._pre_sample_ratio(NaN)
    }

    RowLayout {

        UniswagTextfield {
            id: segmentCount

            labelText: "Segment Count"
            backgroundColor: settingsBar.backgroundColor
            onConfirm: function(enteredText) {
                OscProperties._seg_cnt(enteredText)
                settingsBar.updateDisplayedOscData()
            }
        }

        UniswagTextfield {
            id: triggerDelay

            labelText: "Trigger Delay"
            backgroundColor: settingsBar.backgroundColor
            onConfirm: function(enteredText) {
                OscProperties._trig_delay(enteredText)
                settingsBar.updateDisplayedOscData()
            }
        }

        UniswagTextfield {
            id: triggerHoldOff

            labelText: "Trigger Hold Off"
            backgroundColor: settingsBar.backgroundColor
            onConfirm: function(enteredText) {
                OscProperties._trig_holdoff(enteredText)
                settingsBar.updateDisplayedOscData()
            }
        }

        UniswagCombobox {
            id: clockSource

            labelText: "Clock Source"
            backgroundColor: settingsBar.backgroundColor
            onClick: function(selectedText) {
                OscProperties._clock_src(selectedText)
                settingsBar.updateDisplayedOscData()
            }
        }

        UniswagCombobox {
            id: clockOutput

            labelText: "Clock Output"
            backgroundColor: settingsBar.backgroundColor
            onClick: function(selectedText) {
                OscProperties._clock_out(selectedText)
                settingsBar.updateDisplayedOscData()
            }
        }

        UniswagCombobox {
            id: res

            labelText: "ADU Resolution"
            backgroundColor: settingsBar.backgroundColor
            onClick: function(selectedText) {
                OscProperties._res(selectedText)
                settingsBar.updateDisplayedOscData()
            }
        }

        UniswagCombobox {
            id: autoRes

            labelText: "ADU Auto Resolution"
            backgroundColor: settingsBar.backgroundColor
            onClick: function(selectedText) {
                OscProperties._auto_res(selectedText)
                settingsBar.updateDisplayedOscData()
            }
        }

        UniswagButton {
            labelText: "Trigger"
            buttonText: "Force"
            backgroundColor: settingsBar.backgroundColor
            onClick: function() {
                OscProperties._force_trig()
                settingsBar.updateDisplayedOscData()
            }
        }

        UniswagTextfield {
            id: triggerTimeout

            labelText: "Trigger Timeout"
            backgroundColor: settingsBar.backgroundColor
            onConfirm: function(enteredText) {
                OscProperties._trig_timeout(enteredText)
                settingsBar.updateDisplayedOscData()
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
            list: ["200 MHz", "150 MHz", "100 MHz", "50 MHz", "25 MHz", "10 MHz", "5 MHz", "1 MHz", "100 kHz", "50 kHz", "25 kHz", "10 kHz", "5 kHz", "1 kHz", "500 Hz", "200 Hz", "100 Hz", "50 Hz"]
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
            list: ["50 MSam", "1 MSam", "500 kSam", "100 kSam", "50 kSam", "20 kSam", "10 kSam", "5 kSam", "2 kSam", "1 kSam", "500 Sam", "200 Sam", "100 Sam", "50 Sam"]
            onClickOrConfirm: function(passedText) {
                let value = functions.detachPrefixedUnit(passedText, ["Sam", "kSam", "MSam"])
                OscProperties._rec_len(value)
                settingsBar.updateDisplayedOscData()
            }
        }

        UniswagCombobox {
            id: measureMode

            labelText: "Measure Mode"
            backgroundColor: settingsBar.backgroundColor
            onClick: function(selectedText) {
                OscProperties._measure_mode(selectedText)
                settingsBar.updateDisplayedOscData()
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

        function onSegCnt(device_id, value) {
            if (!functions.isSelectedDevice(device_id)) {
                return
            }
            functions.updateTextfield(segmentCount, value)
        }

        function onTrigDelay(device_id, value) {
            if (!functions.isSelectedDevice(device_id)) {
                return
            }
            functions.updateTextfield(triggerDelay, value)
        }

        function onTrigHoldoff(device_id, value) {
            if (!functions.isSelectedDevice(device_id)) {
                return
            }
            functions.updateTextfield(triggerHoldOff, value)
        }

        function onClockSrc(device_id, value) {
            if (!functions.isSelectedDevice(device_id)) {
                return
            }
            functions.updateComboboxSelection(clockSource, value)
        }
        function onClockSrcAvail(device_id, value) {
            if (!functions.isSelectedDevice(device_id)) {
                return
            }
            functions.updateComboboxList(clockSource, value)
        }

        function onClockOut(device_id, value) {
            if (!functions.isSelectedDevice(device_id)) {
                return
            }
            functions.updateComboboxSelection(clockOutput, value)
        }
        function onClockOutsAvail(device_id, value) {
            if (!functions.isSelectedDevice(device_id)) {
                return
            }
            functions.updateComboboxList(clockOutput, value)
        }

        function onRes(device_id, value) {
            if (!functions.isSelectedDevice(device_id)) {
                return
            }
            functions.updateComboboxSelection(res, value)
        }
        function onResAvail(device_id, value) {
            if (!functions.isSelectedDevice(device_id)) {
                return
            }
            functions.updateComboboxList(res, value)
        }

        function onAutoRes(device_id, value) {
            if (!functions.isSelectedDevice(device_id)) {
                return
            }
            functions.updateComboboxSelection(autoRes, value)
        }
        function onAutoResAvail(device_id, value) {
            if (!functions.isSelectedDevice(device_id)) {
                return
            }
            functions.updateComboboxList(autoRes, value)
        }

        function onMeasureMode(device_id, value) {
            if (!functions.isSelectedDevice(device_id)) {
                return
            }
            functions.updateComboboxSelection(measureMode, value)
        }
        function onMeasureModesAvail(device_id, value) {
            if (!functions.isSelectedDevice(device_id)) {
                return
            }
            functions.updateComboboxList(measureMode, value)
        }

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

        function onTrigTimeout(device_id, value) {
            if (!functions.isSelectedDevice(device_id)) {
                return
            }
            functions.updateTextfield(triggerTimeout, value)
        }

        function onPreSampleRatio(device_id, value) {
            if (!functions.isSelectedDevice(device_id)) {
                return
            }
            functions.updateTextfield(preSampleRatio, value)
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
