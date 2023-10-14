import QtQuick
import QtQuick.Layouts
import "./../../res/customtypes"

UniswagOscChSettingsBar {
    id: settingsBar

    onReloadOscChannelSettings: function() {
        OscProperties._ranges_avail()
        OscProperties._trig_kinds_avail()
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
        // Trigger Condition not supported
        // Trigger Time not supported

        UniswagCombobox {
            id: range

            labelText: "Range"
            backgroundColor: settingsBar.backgroundColor
            onClick: function(selectedText) {
                OscProperties._range(selectedText)
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

    }

    Connections {
        target: OscProperties

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
    }

}
