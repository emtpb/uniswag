import QtQuick
import QtQuick.Layouts
import "./../../res/customtypes"

UniswagGenChSettingsBar {
    id: settingsBar

    onReloadGenChannelSettings: function() {
        GenProperties._sig_types_avail()
        GenProperties._amp(NaN)
        GenProperties._is_amp_auto_range(NaN)
        GenProperties._offset(NaN)
        GenProperties._freq(NaN)
        GenProperties._freq_modes_avail()
        GenProperties._symmetry(NaN)
        GenProperties._modes_avail()
        GenProperties._burst_cnt(NaN)
    }

    RowLayout {
        // Inverted Output not supported
        // Phase not supported
        // Pulse Width not supported
        // Burst Sample Count not supported
        // Burst Segment Count not supported

        UniswagCombobox {
            id: mode

            labelText: "Mode"
            backgroundColor: settingsBar.backgroundColor
            onClick: function(selectedText) {
                GenProperties._mode(selectedText)
                settingsBar.updateDisplayedChannelData()
            }
        }

        UniswagCombobox {
            id: sigType

            labelText: "Signal Type"
            backgroundColor: settingsBar.backgroundColor
            onClick: function(selectedText) {
                GenProperties._sig_type(selectedText)
                settingsBar.updateDisplayedChannelData()
            }
        }

        UniswagCheckbox {
            id: isAmpAutoRange

            labelText: "Amplitude Auto Ranging"
            backgroundColor: settingsBar.backgroundColor
            onClick: function(isActive) {
                GenProperties._is_amp_auto_range(isActive)
                settingsBar.updateDisplayedChannelData()
            }
        }

        UniswagTextfield {
            id: amp

            labelText: "Amplitude"
            backgroundColor: settingsBar.backgroundColor
            onConfirm: function(enteredText) {
                GenProperties._amp(enteredText)
                settingsBar.updateDisplayedChannelData()
            }
        }

        UniswagTextfield {
            id: offset

            labelText: "Offset"
            backgroundColor: settingsBar.backgroundColor
            onConfirm: function(enteredText) {
                GenProperties._offset(enteredText)
                settingsBar.updateDisplayedChannelData()
            }
        }

        UniswagCombobox {
            id: freqMode

            labelText: "Frequency Mode"
            backgroundColor: settingsBar.backgroundColor
            onClick: function(selectedText) {
                GenProperties._freq_mode(selectedText)
                settingsBar.updateDisplayedChannelData()
            }
        }

        UniswagComboTextfield {
            id: frequency

            labelText: "Sample Frequency"
            backgroundColor: settingsBar.backgroundColor
            list: ["2 MHz", "1 MHz", "100 kHz", "50 kHz", "25 kHz", "10 kHz", "5 kHz", "1 kHz", "500 Hz", "200 Hz", "100 Hz", "50 Hz"]
            onClickOrConfirm: function(passedText) {
                let value = functions.detachPrefixedUnit(passedText, ["Hz", "kHz", "MHz"])
                GenProperties._freq(value)
                settingsBar.updateDisplayedChannelData()
            }
        }

        UniswagTextfield {
            id: symmetry

            labelText: "Symmetry"
            backgroundColor: settingsBar.backgroundColor
            onConfirm: function(enteredText) {
                GenProperties._symmetry(enteredText)
                settingsBar.updateDisplayedChannelData()
            }
        }

        UniswagTextfield {
            id: burstCnt

            labelText: "Burst Count"
            backgroundColor: settingsBar.backgroundColor
            onConfirm: function(enteredText) {
                GenProperties._burst_cnt(enteredText)
                settingsBar.updateDisplayedChannelData()
            }
        }

        UniswagButton {
            labelText: "Arbitrary Data"
            buttonText: "Load"
            backgroundColor: settingsBar.backgroundColor
            onClick: function() {
                // open file dialog
                arbData.open()
            }
        }

    }

    UniswagFiledialog {
        id: arbData

        filterList: ["Comma-separated values (*.csv)"]
        onFileSelect: function(fileName) {
            GenProperties._arb_data(fileName)
            settingsBar.updateDisplayedChannelData()
        }
    }

    Connections {
        target: GenProperties

        function onMode(device_id, ch_num, value) {
            if (!functions.isSelectedDevice(device_id, ch_num)) {
                return
            }
            functions.updateComboboxSelection(mode, value)
        }
        function onModesAvail(device_id, ch_num, value) {
            if (!functions.isSelectedDevice(device_id, ch_num)) {
                return
            }
            functions.updateComboboxList(mode, value)
        }

        function onSigType(device_id, ch_num, value) {
            if (!functions.isSelectedDevice(device_id, ch_num)) {
                return
            }
            functions.updateComboboxSelection(sigType, value)
        }
        function onSigTypesAvail(device_id, ch_num, value) {
            if (!functions.isSelectedDevice(device_id, ch_num)) {
                return
            }
            functions.updateComboboxList(sigType, value)
        }

        function onAmp(device_id, ch_num, value) {
            if (!functions.isSelectedDevice(device_id, ch_num)) {
                return
            }
            functions.updateTextfield(amp, value)
        }

        function onIsAmpAutoRange(device_id, ch_num, value) {
            if (!functions.isSelectedDevice(device_id, ch_num)) {
                return
            }
            functions.updateCheckbox(isAmpAutoRange, value, "ON", "OFF")
        }

        function onOffset(device_id, ch_num, value) {
            if (!functions.isSelectedDevice(device_id, ch_num)) {
                return
            }
            functions.updateTextfield(offset, value)
        }

        function onFreq(device_id, ch_num, value) {
            if (!functions.isSelectedDevice(device_id)) {
                return
            }
            let listOfIncreasingUnits = ["Hz", "kHz", "MHz"]
            value = functions.appendPrefixedUnit(value, 3, listOfIncreasingUnits)
            functions.updateComboTextfield(frequency, value)
        }

        function onFreqMode(device_id, ch_num, value) {
            if (!functions.isSelectedDevice(device_id, ch_num)) {
                return
            }
            functions.updateComboboxSelection(freqMode, value)
        }
        function onFreqModesAvail(device_id, ch_num, value) {
            if (!functions.isSelectedDevice(device_id, ch_num)) {
                return
            }
            functions.updateComboboxList(freqMode, value)
        }

        function onSymmetry(device_id, ch_num, value) {
            if (!functions.isSelectedDevice(device_id, ch_num)) {
                return
            }
            functions.updateTextfield(symmetry, value)
        }

        function onBurstCnt(device_id, ch_num, value) {
            if (!functions.isSelectedDevice(device_id, ch_num)) {
                return
            }
            functions.updateTextfield(burstCnt, value)
        }
    }

}
