import QtQuick
import QtQuick.Layouts
import "./../../res/customtypes"

UniswagOscChSettingsBar {
    id: settingsBar

    onReloadOscChannelSettings: function() {
        OscProperties._couplings_avail()
        OscProperties._probe_gain(NaN)
        OscProperties._probe_offset(NaN)
        OscProperties._trig_lvl(NaN)

        // Trigger Hysteresis not supported
        functions.triggerSliderHysteresisUpdate(0)
    }

    onTriggerSliderPositionChanged: function(position) {
        /*
        OscProperties._range(NaN)
        */
        OscProperties._trig_lvl(position)
    }

    onZoomed: function() {
        /*
        OscProperties._range(NaN)
        functions.triggerSliderPositionUpdate()
        */
    }

    RowLayout {

        UniswagCombobox {
            id: coupling

            labelText: "Coupling"
            backgroundColor: settingsBar.backgroundColor
            onClick: function(selectedText) {
                OscProperties._coupling(selectedText)
                settingsBar.updateDisplayedChannelData()
            }
        }

        UniswagTextfield {
            id: probeGain

            labelText: "Probe Gain"
            backgroundColor: settingsBar.backgroundColor
            onConfirm: function(enteredText) {
                OscProperties._probe_gain(enteredText)
                settingsBar.updateDisplayedChannelData()
            }
        }

        UniswagTextfield {
            id: probeOffset

            labelText: "Probe Offset"
            backgroundColor: settingsBar.backgroundColor
            onConfirm: function(enteredText) {
                OscProperties._probe_offset(enteredText)
                settingsBar.updateDisplayedChannelData()
            }
        }


        UniswagTextfield {
            id: triggerLevel

            labelText: "Trigger Level"
            backgroundColor: settingsBar.backgroundColor
            onConfirm: function(enteredText) {
                OscProperties._trig_lvl(enteredText)
                settingsBar.updateDisplayedChannelData()
            }
        }

    }

    Connections {
        target: OscProperties

        function onCoupling(device_id, ch_num, value) {
            if (!functions.isSelectedDevice(device_id, ch_num)) {
                return
            }
            functions.updateComboboxSelection(coupling, value)
        }
        function onCouplingsAvail(device_id, ch_num, value) {
            if (!functions.isSelectedDevice(device_id, ch_num)) {
                return
            }
            functions.updateComboboxList(coupling, value)
        }

        function onProbeGain(device_id, ch_num, value) {
            if (!functions.isSelectedDevice(device_id, ch_num)) {
                return
            }
            functions.updateTextfield(probeGain, value)
        }

        function onProbeOffset(device_id, ch_num, value) {
            if (!functions.isSelectedDevice(device_id, ch_num)) {
                return
            }
            functions.updateTextfield(probeOffset, value)
        }

        function onTrigLvl(device_id, ch_num, value) {
            if (!functions.isSelectedDevice(device_id, ch_num)) {
                return
            }
            let stringifiedValue = functions.listToString(value)
            functions.updateTextfield(triggerLevel, stringifiedValue)
            // affects trigger slider!
            functions.triggerSliderPositionUpdate(value)
        }
    }

 }
