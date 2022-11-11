import QtQuick
import QtQuick.Layouts
import QtQuick.Controls

GridLayout {
    columns: 5
    columnSpacing: 10

    signal triggerSliderPositionChanged(real position)

    property var background_color: darkModeEnabled? colorPalette.dark : colorPalette.light

    property real probeOffsetValue: 0.0
    property real rangeValue: 1.0

    Label {
        id: couplingLabel
        text: "Coupling"
    }
    Label {
        id: probeGainLabel
        text: "Probe Gain"
    }
    Label {
        id: probeOffsetLabel
        text: "Probe Offset"
    }
    Label {
        id: rangeLabel
        text: "Range"
    }
    Label {
        id: triggerLevelLabel
        text: "Trigger Level"
    }

    // Coupling
    ComboBox {
        id: coupling
        model: ListModel{}
        onActivated: OscProperties._coupling(currentText)

        background: Rectangle {
            implicitWidth: couplingLabel.width
            implicitHeight: 25
            radius: 2
            color: background_color
            border.color: colorPalette.light
            border.width: 1
        }
    }

    // Probe Gain
    TextField {
        id: probeGain
        onAccepted: OscProperties._probe_gain(text)

        background: Rectangle {
            implicitWidth: probeGainLabel.width
            implicitHeight: 25
            radius: 2
            color: background_color
            border.color: colorPalette.light
            border.width: 1
        }
    }

    // Probe Offset
    TextField {
        id: probeOffset
        onAccepted: OscProperties._probe_offset(text)

        background: Rectangle {
            implicitWidth: probeOffsetLabel.width
            implicitHeight: 25
            radius: 2
            color: background_color
            border.color: colorPalette.light
            border.width: 1
        }
    }

    // Range
    TextField {
        id: range
        onAccepted: OscProperties._range(text)

        background: Rectangle {
            implicitWidth: rangeLabel.width
            implicitHeight: 25
            radius: 2
            color: background_color
            border.color: colorPalette.light
            border.width: 1
        }
    }

    // Trigger Level
    TextField {
        id: triggerLevel
        onAccepted: OscProperties._trig_lvl(text)

        background: Rectangle {
            implicitWidth: triggerLevelLabel.width
            implicitHeight: 25
            radius: 2
            color: background_color
            border.color: colorPalette.light
            border.width: 1
        }
    }

    onTriggerSliderPositionChanged: function(position){
        OscProperties._trig_lvl(position)
    }

    Component.onCompleted: {
        OscProperties._couplings_avail()
        OscProperties._probe_gain(NaN)
        OscProperties._probe_offset(NaN)
        OscProperties._trig_lvl(NaN)
        OscProperties._range(NaN)

        // set hysteresis to 0
        oscilloscopeMainRect.changeHysteresisSliderSizeInPercent(0)
    }

    Connections {
        target: OscProperties

        // Coupling
        function onCoupling(device_id, ch_num, value) {
            if(compareDevices(device_id, oscilloscopeMainRect.selectedDevice) && ch_num === oscilloscopeMainRect.selectedChannelNum){
                coupling.currentIndex = findIndexOfModel(coupling.model, value)
            }
        }
        function onCouplingsAvail(device_id, ch_num, value) {
            if(compareDevices(device_id, oscilloscopeMainRect.selectedDevice) && ch_num === oscilloscopeMainRect.selectedChannelNum){
                coupling.model = value
            }
        }

        // Probe Gain
        function onProbeGain(device_id, ch_num, value) {
            if(compareDevices(device_id, oscilloscopeMainRect.selectedDevice) && ch_num === oscilloscopeMainRect.selectedChannelNum){
                probeGain.text = ""
                probeGain.placeholderText = value
            }
        }

        // Probe Offset
        function onProbeOffset(device_id, ch_num, value) {
            if(compareDevices(device_id, oscilloscopeMainRect.selectedDevice) && ch_num === oscilloscopeMainRect.selectedChannelNum){
                probeOffset.text = ""
                probeOffset.placeholderText = value
                probeOffsetValue = value
            }
        }

        // Range
        function onRange(device_id, ch_num, value) {
            if(compareDevices(device_id, oscilloscopeMainRect.selectedDevice) && ch_num === oscilloscopeMainRect.selectedChannelNum){
                range.text = ""
                range.placeholderText = value
                rangeValue = value
            }
        }

        // Trigger Level
        function onTrigLvl(device_id, ch_num, value) {
            if(compareDevices(device_id, oscilloscopeMainRect.selectedDevice) && ch_num === oscilloscopeMainRect.selectedChannelNum){
                triggerLevel.text = ""
                let text = value[0].toString()
                for(let i = 1; i < value.length; i++){
                    text+= ", " + value[i].toString()
                }
                triggerLevel.placeholderText = text
                let triggerPos = Math.max.apply(Math, value)
                oscilloscopeMainRect.triggerIconPosition(triggerPos)
            }
        }

    }
}




