import QtQuick
import QtQuick.Layouts
import "./../../res/customtypes"

UniswagOscChSettingsBar {
    id: settingsBar

    onReloadOscChannelSettings: function() {
        OscProperties._trig_cond_avail()
        OscProperties._trig_time(NaN)
        OscProperties._couplings_avail()
        OscProperties._probe_gain(NaN)
        OscProperties._probe_offset(NaN)
        OscProperties._is_auto_range(NaN)
        OscProperties._ranges_avail()
        OscProperties._is_trig_enabled(NaN)
        OscProperties._trig_kinds_avail()
        OscProperties._trig_hyst(NaN)
        OscProperties._trig_lvl(NaN)
        OscProperties._range(NaN)
    }

    onTriggerSliderPositionChanged: function(position) {
        OscProperties._range(NaN)
        OscProperties._trig_lvl(position)
        functions.triggerSliderHysteresisUpdate()
    }

    onZoomed: function() {
        OscProperties._range(NaN)
        functions.triggerSliderPositionUpdate()
        functions.triggerSliderHysteresisUpdate()
    }

    RowLayout {
        UniswagCombobox {
            id: triggerCondition

            labelText: "Trigger Condition"
            backgroundColor: settingsBar.backgroundColor
            onClick: function(selectedText) {
                OscProperties._trig_cond(selectedText)
                settingsBar.updateDisplayedChannelData()
            }
        }

        UniswagTextfield {
            id: triggerTime

            labelText: "Trigger Time"
            backgroundColor: settingsBar.backgroundColor
            onConfirm: function(enteredText) {
                OscProperties._trig_time(enteredText)
                settingsBar.updateDisplayedChannelData()
            }
        }

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

        UniswagCheckbox {
            id: autoRange

            labelText: "Auto Range State"
            backgroundColor: settingsBar.backgroundColor
            onClick: function(isActive) {
                OscProperties._is_auto_range(isActive)
                settingsBar.updateDisplayedChannelData()
            }
        }

        UniswagCombobox {
            id: range

            labelText: "Range"
            backgroundColor: settingsBar.backgroundColor
            onClick: function(selectedText) {
                OscProperties._range(selectedText)
                settingsBar.updateDisplayedChannelData()
            }
        }

        UniswagCheckbox {
            id: triggerEnabled

            labelText: "Trigger State"
            backgroundColor: settingsBar.backgroundColor
            onClick: function(isActive) {
                OscProperties._is_trig_enabled(isActive)
                settingsBar.updateDisplayedChannelData()
            }
        }

        UniswagCombobox {
            id: triggerKinds

            labelText: "Trigger Kinds"
            backgroundColor: settingsBar.backgroundColor
            onClick: function(selectedText) {
                OscProperties._trig_kind(selectedText)
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

        UniswagTextfield {
            id: triggerHysteresis

            labelText: "Trigger Hysteresis"
            backgroundColor: settingsBar.backgroundColor
            onConfirm: function(enteredText) {
                OscProperties._trig_hyst(enteredText)
                settingsBar.updateDisplayedChannelData()
            }
        }

    }

    Connections {
        target: OscProperties

        function onTrigCond(device_id, ch_num, value) {
            if (!functions.isSelectedDevice(device_id, ch_num)) {
                return
            }
            functions.updateComboboxSelection(triggerCondition, value)
        }
        function onTrigCondAvail(device_id, ch_num, value) {
            if (!functions.isSelectedDevice(device_id, ch_num)) {
                return
            }
            functions.updateComboboxList(triggerCondition, value)
        }

        function onTrigTime(device_id, ch_num, value) {
            if (!functions.isSelectedDevice(device_id, ch_num)) {
                return
            }
            let stringifiedValue = functions.listToString(value)
            functions.updateTextfield(triggerTime, stringifiedValue)
        }

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

        function onIsAutoRange(device_id, ch_num, value) {
            if (!functions.isSelectedDevice(device_id, ch_num)) {
                return
            }
            functions.updateCheckbox(autoRange, value, "ON", "OFF")
        }

        function onRange(device_id, ch_num, value) {
            if (!functions.isSelectedDevice(device_id, ch_num)) {
                return
            }
            functions.updateComboboxSelection(range, value)
            // affects trigger slider!
            functions.triggerSliderRangeUpdate(value)
            functions.triggerSliderHysteresisUpdate()
        }
        function onRangesAvail(device_id, ch_num, value) {
            if (!functions.isSelectedDevice(device_id, ch_num)) {
                return
            }
            functions.updateComboboxList(range, value)
        }

        function onIsTrigEnabled(device_id, ch_num, value) {
            if (!functions.isSelectedDevice(device_id, ch_num)) {
                return
            }
            functions.updateCheckbox(triggerEnabled, value, "ON", "OFF")
        }

        function onTrigKind(device_id, ch_num, value) {
            if (!functions.isSelectedDevice(device_id, ch_num)) {
                return
            }
            functions.updateComboboxSelection(triggerKinds, value)
            // affects trigger slider!
            switch (value) {
                case "rising":
                    functions.triggerSliderIconUpdate("rising edge")
                    break;
                case "falling":
                    functions.triggerSliderIconUpdate("falling edge")
                    break;
                case "in window":
                    functions.triggerSliderIconUpdate("in window")
                    break;
                case "out window":
                    functions.triggerSliderIconUpdate("out window")
                    break;
                default:
                    functions.triggerSliderIconUpdate()
            }
        }
        function onTrigKindsAvail(device_id, ch_num, value) {
            if (!functions.isSelectedDevice(device_id, ch_num)) {
                return
            }
            functions.updateComboboxList(triggerKinds, value)
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

        function onTrigHyst(device_id, ch_num, value) {
            if (!functions.isSelectedDevice(device_id, ch_num)) {
                return
            }
            let stringifiedValue = functions.listToString(value)
            functions.updateTextfield(triggerHysteresis, stringifiedValue)
            // affects trigger slider!
            functions.triggerSliderHysteresisUpdate(value[0])
        }
    }

}
