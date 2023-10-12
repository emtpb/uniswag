import QtQuick
import QtQuick.Layouts
import "./../../res/customtypes"

UniswagGenChSettingsBar {
    id: settingsBar

    onReloadGenChannelSettings: function() {
        GenProperties._sig_types_avail()
        GenProperties._amp(NaN)
        GenProperties._offset(NaN)
        GenProperties._freq(NaN)
        GenProperties._period(NaN)
        GenProperties._phase(NaN)
        GenProperties._duty_cycle(NaN)
        GenProperties._is_burst_on(NaN)
        GenProperties._burst_modes_avail()
        GenProperties._impedance(NaN)
    }

    RowLayout {
        // Voltage Max not supported
        // Voltage Min not supported
        // Burst Delay not supported
        // Pulse Width not supported
        // Pulse Delay not supported
        // Pulse Hold not supported
        // Leading Pulse Transition not supported
        // Trailing Pulse Transition not supported

        UniswagCombobox {
            id: sigType

            labelText: "Signal Type"
            backgroundColor: settingsBar.backgroundColor
            onClick: function(selectedText) {
                GenProperties._sig_type(selectedText)
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

        UniswagTextfield {
            id: frequency

            labelText: "Frequency"
            widthExtension: 30
            backgroundColor: settingsBar.backgroundColor
            onConfirm: function(enteredText) {
                GenProperties._freq(enteredText)
                settingsBar.updateDisplayedChannelData()
            }
        }

        UniswagTextfield {
            id: period

            labelText: "Period"
            backgroundColor: settingsBar.backgroundColor
            onConfirm: function(enteredText) {
                GenProperties._period(enteredText)
                settingsBar.updateDisplayedChannelData()
            }
        }

        UniswagTextfield {
            id: phase

            labelText: "Phase"
            backgroundColor: settingsBar.backgroundColor
            onConfirm: function(enteredText) {
                GenProperties._phase(enteredText)
                settingsBar.updateDisplayedChannelData()
            }
        }

        UniswagTextfield {
            id: dutyCycle

            labelText: "Duty Cycle"
            backgroundColor: settingsBar.backgroundColor
            onConfirm: function(enteredText) {
                GenProperties._duty_cycle(enteredText)
                settingsBar.updateDisplayedChannelData()
            }
        }

        UniswagTextfield {
            id: impedance

            labelText: "Impedance"
            backgroundColor: settingsBar.backgroundColor
            onConfirm: function(enteredText) {
                GenProperties._impedance(enteredText)
                settingsBar.updateDisplayedChannelData()
            }
        }

        UniswagCheckbox {
            id: isBurstOn

            labelText: "Burst State"
            backgroundColor: settingsBar.backgroundColor
            onClick: function(isActive) {
                GenProperties._is_burst_on(isActive)
                settingsBar.updateDisplayedChannelData()
            }
        }

        UniswagCombobox {
            id: burstMode

            labelText: "Burst Mode"
            backgroundColor: settingsBar.backgroundColor
            onClick: function(selectedText) {
                GenProperties._burst_mode(selectedText)
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

        function onOffset(device_id, ch_num, value) {
            if (!functions.isSelectedDevice(device_id, ch_num)) {
                return
            }
            functions.updateTextfield(offset, value)
        }

        function onFreq(device_id, ch_num, value) {
            if (!functions.isSelectedDevice(device_id, ch_num)) {
                return
            }
            functions.updateTextfield(frequency, value)
        }

        function onPeriod(device_id, ch_num, value) {
            if (!functions.isSelectedDevice(device_id, ch_num)) {
                return
            }
            functions.updateTextfield(period, value)
        }

        function onPhase(device_id, ch_num, value) {
            if (!functions.isSelectedDevice(device_id, ch_num)) {
                return
            }
            functions.updateTextfield(phase, value)
        }

        function onDutyCycle(device_id, ch_num, value) {
            if (!functions.isSelectedDevice(device_id, ch_num)) {
                return
            }
            functions.updateTextfield(dutyCycle, value)
        }

        function onImpedance(device_id, ch_num, value) {
            if (!functions.isSelectedDevice(device_id, ch_num)) {
                return
            }
            functions.updateTextfield(impedance, value)
        }

        function onIsBurstOn(device_id, ch_num, value) {
            if (!functions.isSelectedDevice(device_id, ch_num)) {
                return
            }
            functions.updateCheckbox(isBurstOn, value, "ON", "OFF")
        }

        function onBurstMode(device_id, ch_num, value) {
            if (!functions.isSelectedDevice(device_id, ch_num)) {
                return
            }
            functions.updateComboboxSelection(burstMode, value)
        }
        function onBurstModesAvail(device_id, ch_num, value) {
            if (!functions.isSelectedDevice(device_id, ch_num)) {
                return
            }
            functions.updateComboboxList(burstMode, value)
        }
    }

}
