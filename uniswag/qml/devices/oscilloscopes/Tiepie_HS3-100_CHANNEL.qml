import QtQuick
import QtQuick.Layouts
import QtQuick.Controls

GridLayout {
    columns: 9
    columnSpacing: 10

    // Trigger Condition not supported
    // Trigger Time not supported

    signal triggerSliderPositionChanged(real position)
    signal zoomed()
    signal reloadOscChannelSettings()

     property var background_color: darkModeEnabled? colorPalette.dark : colorPalette.light

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
        id: autoRangeLabel
        text: "Auto Range State"
    }
    Label {
        id: rangeLabel
        text: "Range"
    }
    Label {
        id: triggerEnabledLabel
        text: "Trigger State"
    }
    Label {
        id: triggerKindsLabel
        text: "Trigger Kinds"
    }
    Label {
        id: triggerLevelLabel
        text: "Trigger Level"
    }
    Label {
        id: triggerHysteresisLabel
        text: "Trigger Hysteresis"
    }

    // Coupling
    ComboBox {
        id: coupling
        model: ListModel{}
        onActivated: {
            OscProperties._coupling(currentText)
            updateDisplayedChannelData()
        }

        background: Rectangle {
            implicitWidth: couplingLabel.width + 5
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
        onAccepted: {
            OscProperties._probe_gain(text)
            updateDisplayedChannelData()
        }

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
        onAccepted: {
            OscProperties._probe_offset(text)
            updateDisplayedChannelData()
        }

        background: Rectangle {
            implicitWidth: probeOffsetLabel.width
            implicitHeight: 25
            radius: 2
            color: background_color
            border.color: colorPalette.light
            border.width: 1
        }
    }

    // Auto Range State
    CheckBox {
        id: autoRange
        text: ""
        implicitHeight: 25
        indicator: Rectangle {
            implicitWidth: 12
            implicitHeight: 12
            x: autoRange.leftPadding
            y: parent.height / 2 - height / 2
            radius: 3
            border.color: autoRange.down ? "#17a81a" : "#21be2b"
            Rectangle {
                width: 6
                height: 6
                x: 3
                y: 3
                radius: 2
                color: autoRange.down ? "#17a81a" : "#21be2b"
                visible: autoRange.checked
            }
        }
        contentItem: Text {
            text: autoRange.text
            font: autoRange.font
            opacity: enabled ? 1.0 : 0.3
            color: autoRange.checked ? "#17a81a" : "#990000"
            verticalAlignment: Text.AlignVCenter
            leftPadding: autoRange.indicator.width + autoRange.spacing
        }
        background: Rectangle {
            implicitWidth: autoRangeLabel.width
            implicitHeight: 25
            radius: 2
            color: background_color
            border.color: colorPalette.light
            border.width: 1
        }
        onCheckStateChanged: {
            if(checkState === Qt.Checked){
                OscProperties._is_auto_range(true)
            }
            else {
                OscProperties._is_auto_range(false)
            }
            updateDisplayedChannelData()
        }
    }

    // Range
    ComboBox {
        id: range
        model: ListModel{}
        onActivated: {
            OscProperties._range(currentText)
            updateDisplayedChannelData()
        }

        background: Rectangle {
            implicitWidth: rangeLabel.width + 10
            implicitHeight: 25
            radius: 2
            color: background_color
            border.color: colorPalette.light
            border.width: 1
        }
    }

    // Trigger State
    CheckBox {
        id: triggerEnabled
        text: ""
        implicitHeight: 25
        indicator: Rectangle {
            implicitWidth: 12
            implicitHeight: 12
            x: triggerEnabled.leftPadding
            y: parent.height / 2 - height / 2
            radius: 3
            border.color: triggerEnabled.down ? "#17a81a" : "#21be2b"
            Rectangle {
                width: 6
                height: 6
                x: 3
                y: 3
                radius: 2
                color: triggerEnabled.down ? "#17a81a" : "#21be2b"
                visible: triggerEnabled.checked
            }
        }
        contentItem: Text {
            text: triggerEnabled.text
            font: triggerEnabled.font
            opacity: enabled ? 1.0 : 0.3
            color: triggerEnabled.checked ? "#17a81a" : "#990000"
            verticalAlignment: Text.AlignVCenter
            leftPadding: triggerEnabled.indicator.width + triggerEnabled.spacing
        }
        background: Rectangle {
            implicitWidth: triggerEnabledLabel.width
            implicitHeight: 25
            radius: 2
            color: background_color
            border.color: colorPalette.light
            border.width: 1
        }
        onCheckStateChanged: {
            if(checkState === Qt.Checked){
                OscProperties._is_trig_enabled(true)
            }
            else {
                OscProperties._is_trig_enabled(false)
            }
            updateDisplayedChannelData()
        }
    }

    // Trigger Kinds
    ComboBox {
        id: triggerKinds
        model: ListModel{}
        onActivated: {
            OscProperties._trig_kind(currentText)
            updateDisplayedChannelData()
        }

        background: Rectangle {
            implicitWidth: triggerKindsLabel.width
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
        onAccepted: {
            OscProperties._trig_lvl(text)
            updateDisplayedChannelData()
        }

        background: Rectangle {
            implicitWidth: triggerLevelLabel.width
            implicitHeight: 25
            radius: 2
            color: background_color
            border.color: colorPalette.light
            border.width: 1
        }
    }

    // Trigger Hysteresis
    TextField {
        id: triggerHysteresis
        onAccepted: {
            OscProperties._trig_hyst(text)
            updateDisplayedChannelData()
        }

        background: Rectangle {
            implicitWidth: triggerHysteresisLabel.width
            implicitHeight: 25
            radius: 2
            color: background_color
            border.color: colorPalette.light
            border.width: 1
        }
    }

    onTriggerSliderPositionChanged: function(position){
        OscProperties._range(NaN)
        OscProperties._trig_lvl(position)
        setHysteresisIconSize(hysteresisValue)
    }

    onZoomed: {
        OscProperties._range(NaN)
        oscilloscopeMainRect.triggerIconPosition(triggerLevelValue)
        setHysteresisIconSize(hysteresisValue)
    }

    onReloadOscChannelSettings: {
        reloadChSettings()
    }

    function reloadChSettings(){
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

    function updateDisplayedChannelData(){
        reloadChSettings()
        oscilloscopeMainRect.reloadOscilloscopeSettings()
    }


    Component.onCompleted: {
        updateDisplayedChannelData()
    }

    Timer {
           interval: 1000;
           running: false
           repeat: true
           onTriggered: OscProperties._range(NaN)
       }


    property real rangeValue: 0
    property real hysteresisValue: 0
    property real triggerLevelValue: 0

    // triggerHysteresis on tiepie in percent of the selected range
    function setHysteresisIconSize(triggerHysteresisInPercent){
        // scilloscopeChart.axes[3]: rawAxisY
        if(oscilloscopeChart.axes[3].max !== oscilloscopeChart.axes[3].min){
            let visibleAreaOfRangeInPercent = (oscilloscopeChart.axes[3].max- oscilloscopeChart.axes[3].min) / (parseFloat(range.currentText)*2)
            oscilloscopeMainRect.changeHysteresisSliderSizeInPercent(triggerHysteresisInPercent/visibleAreaOfRangeInPercent)
        }
        else {
            oscilloscopeMainRect.changeHysteresisSliderSizeInPercent(triggerHysteresisInPercent)
        }
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
            }
        }

        // Auto Range State
        function onIsAutoRange(device_id, ch_num, value) {
            if(compareDevices(device_id, oscilloscopeMainRect.selectedDevice) && ch_num === oscilloscopeMainRect.selectedChannelNum){
                if(value === true){
                    autoRange.checkState = Qt.Checked
                    autoRange.text = "ON"
                }
                else {
                    autoRange.checkState = Qt.Unchecked
                    autoRange.text = "OFF"
                }
            }
        }

        // Range
        function onRange(device_id, ch_num, value) {
            if(compareDevices(device_id, oscilloscopeMainRect.selectedDevice) && ch_num === oscilloscopeMainRect.selectedChannelNum){
                range.currentIndex = findIndexOfModel(range.model, value)
                rangeValue = parseFloat(value)
                setHysteresisIconSize(hysteresisValue)
            }
        }
        function onRangesAvail(device_id, ch_num, value) {
            if(compareDevices(device_id, oscilloscopeMainRect.selectedDevice) && ch_num === oscilloscopeMainRect.selectedChannelNum){
                range.model = value
            }
        }

        // Trigger State
        function onIsTrigEnabled(device_id, ch_num, value) {
            if(compareDevices(device_id, oscilloscopeMainRect.selectedDevice) && ch_num === oscilloscopeMainRect.selectedChannelNum){
                if(value === true){
                    triggerEnabled.checkState = Qt.Checked
                    triggerEnabled.text = "ON"
                }
                else {
                    triggerEnabled.checkState = Qt.Unchecked
                    triggerEnabled.text = "OFF"
                }
            }
        }

        // Trigger Kinds
        function onTrigKind(device_id, ch_num, value) {
            if(compareDevices(device_id, oscilloscopeMainRect.selectedDevice) && ch_num === oscilloscopeMainRect.selectedChannelNum){
                if(value === "rising"){
                    oscilloscopeMainRect.risingEdgeIcon()
                }
                else if(value === "falling"){
                    oscilloscopeMainRect.fallingEdgeIcon()
                }
                else if(value === "in window"){
                    oscilloscopeMainRect.inWindowIcon()
                }
                else if(value === "out window"){
                    oscilloscopeMainRect.outWindowIcon()
                }
                else{
                    oscilloscopeMainRect.triangleIcon()
                }

                triggerKinds.currentIndex = findIndexOfModel(triggerKinds.model, value)
            }
        }
        function onTrigKindsAvail(device_id, ch_num, value) {
            if(compareDevices(device_id, oscilloscopeMainRect.selectedDevice) && ch_num === oscilloscopeMainRect.selectedChannelNum){
                triggerKinds.model = value
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
                // max number in list
                oscilloscopeMainRect.triggerIconPosition(Math.max.apply(Math, value))
                triggerLevelValue = Math.max.apply(Math, value)
            }
        }

        // Trigger Hysteresis
        function onTrigHyst(device_id, ch_num, value) {
            if(compareDevices(device_id, oscilloscopeMainRect.selectedDevice) && ch_num === oscilloscopeMainRect.selectedChannelNum){
                triggerHysteresis.text = ""
                let text = value[0].toString()
                for(let i = 1; i < value.length; i++){
                    text+= ", " + value[i].toString()
                }
                triggerHysteresis.placeholderText = text

                hysteresisValue = parseFloat(value)
                setHysteresisIconSize(value)
            }
        }
    }
}




