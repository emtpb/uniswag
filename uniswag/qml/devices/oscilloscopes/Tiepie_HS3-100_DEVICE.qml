import QtQuick
import QtQuick.Layouts
import QtQuick.Controls

GridLayout {
    signal reloadOscilloscopeSettings()

     property var background_color: darkModeEnabled? colorPalette.dark : colorPalette.light
    columns: 11
    columnSpacing: 10

    // Segment Count not supported
    // Trigger Delay not supported
    // Trigger Hold Off not supported

    Label {
        id: clockSourceLabel
        text: "Clock Source"
    }

    Label {
        id: clockOutputLabel
        text: "Clock Output"
    }

    Label {
        id: resLabel
        text: "ADU Resolution"
    }

    Label {
        id: autoResLabel
        text: "ADU Auto Resolution"
    }
    Label {
        id: forceTriggerLabel
        text: "Trigger"
    }
    Label {
        id: triggerTimeoutLabel
        text: "Trigger Timeout"
    }
    Label {
        id: preSampleRatioLabel
        text: "Pre Sample Ratio"
    }
    Label {
        id: frequencyLabel
        text: "Frequency"
    }
    Label {
        id: recordLengthLabel
        text: "Record length"
    }
    Label {
        id: measureModeLabel
        text: "Measure Mode"
    }
    Label {
        id: startStopLabel
        text: "Start/Stop"
    }



    // Clock Source
    ComboBox {
        id: clockSource
        model: ListModel{}
        onActivated: {
            OscProperties._clock_src(currentText)
            updateDisplayedOscData()
        }

        background: Rectangle {
            implicitWidth: clockSourceLabel.width
            implicitHeight: 25
            radius: 2
            color: background_color
            border.color: colorPalette.light
            border.width: 1
        }
    }


    // Clock Output
    ComboBox {
        id: clockOutput
        model: ListModel{}
        onActivated: {
            OscProperties._clock_out(currentText)
            updateDisplayedOscData()
        }

        background: Rectangle {
            implicitWidth: clockOutputLabel.width
            implicitHeight: 25
            radius: 2
            color: background_color
            border.color: colorPalette.light
            border.width: 1
        }
    }


    // ADU Resolution
    ComboBox {
        id: res
        model: ListModel{}
        onActivated: {
            OscProperties._res(currentText)
            updateDisplayedOscData()
        }

        background: Rectangle {
            implicitWidth: resLabel.width
            implicitHeight: 25
            radius: 2
            color: background_color
            border.color: colorPalette.light
            border.width: 1
        }
    }


    // ADU Auto Resolution
    ComboBox {
        id: autoRes
        model: ListModel{}
        onActivated: {
            OscProperties._auto_res(currentText)
            updateDisplayedOscData()
        }

        background: Rectangle {
            implicitWidth: autoResLabel.width
            implicitHeight: 25
            radius: 2
            color: background_color
            border.color: colorPalette.light
            border.width: 1
        }
    }


    // Force trigger
    Button {
        id: forceTrigger
        text: "Force"
        onClicked: {
            OscProperties._force_trig()
            updateDisplayedOscData()
        }

        background: Rectangle {
            implicitWidth: forceTriggerLabel.width
            implicitHeight: 25
            radius: 2
            color: background_color
            border.color: colorPalette.light
            border.width: 1
        }
    }


    // Trigger Timeout
    TextField {
        id: triggerTimeout
        onAccepted: {
            OscProperties._trig_timeout(text)
            updateDisplayedOscData()
        }

        background: Rectangle {
            implicitWidth: triggerTimeoutLabel.width
            implicitHeight: 25
            radius: 2
            color: background_color
            border.color: colorPalette.light
            border.width: 1
        }
    }


    // Pre Sample Ratio
    TextField {
        id: preSampleRatio
        onAccepted: {
            OscProperties._pre_sample_ratio(text)
            updateDisplayedOscData()
        }

        background: Rectangle {
            implicitWidth: preSampleRatioLabel.width
            implicitHeight: 25
            radius: 2
            color: background_color
            border.color: colorPalette.light
            border.width: 1
        }
    }


    // Frequency
    ComboBox {
        id: frequency
        model: ListModel{
            ListElement { text: "100 MHz" }
            ListElement { text: "50 MHz" }
            ListElement { text: "25 MHz" }
            ListElement { text: "10 MHz" }
            ListElement { text: "5 MHz" }
            ListElement { text: "1 MHz" }
            ListElement { text: "100 kHz" }
            ListElement { text: "50 kHz" }
            ListElement { text: "25 kHz" }
            ListElement { text: "10 kHz" }
            ListElement { text: "5 kHz" }
            ListElement { text: "1 kHz" }
            ListElement { text: "500 Hz" }
            ListElement { text: "200 Hz" }
            ListElement { text: "100 Hz" }
            ListElement { text: "50 Hz" }
        }
        editable: true

        onActivated: {
            let value = currentText.replace(" MHz", "000000").replace(" kHz", "000").replace(" Hz", "")
            OscProperties._sample_freq(value)
            updateDisplayedOscData()
        }

        onAccepted: {
            let value = editText
            if(editText.includes("MHz")){
                value = editText.replace(" MHz", "")
                value = parseFloat(value)*1000000
            }
            else if(editText.includes("kHz")){
                value = editText.replace(" kHz", "")
                value = parseFloat(value)*1000
            }
            else if(editText.includes("Hz")){
                value = editText.replace(" Hz", "")
            }
            OscProperties._sample_freq(value)
            updateDisplayedOscData()
        }


        background: Rectangle {
            implicitWidth: frequencyLabel.width + 40
            implicitHeight: 25
            radius: 2
            color: background_color
            border.color: colorPalette.light
            border.width: 1
        }
    }


    // Record length
    ComboBox {
        id: recordLength
        model: ListModel{
            ListElement { text: "100 kSam" }
            ListElement { text: "50 kSam" }
            ListElement { text: "20 kSam" }
            ListElement { text: "10 kSam" }
            ListElement { text: "5 kSam" }
            ListElement { text: "2 kSam" }
            ListElement { text: "1 kSam" }
            ListElement { text: "500 Sam" }
            ListElement { text: "200 Sam" }
            ListElement { text: "100 Sam" }
            ListElement { text: "50 Sam" }
        }
        editable: true

        onActivated: {
            let value = currentText.replace(" kSam", "000").replace(" Sam", "")
            OscProperties._rec_len(value)
            updateDisplayedOscData()
        }
        onAccepted: {
            let value = editText
            if(editText.includes("kSam")){
                value = editText.replace(" kSam", "")
                value = parseFloat(value)*1000
            }
            else if(editText.includes("Sam")){
                value = editText.replace(" Sam", "")
            }
            OscProperties._rec_len(value)
            updateDisplayedOscData()

        }

        background: Rectangle {
            implicitWidth: recordLengthLabel.width + 20
            implicitHeight: 25
            radius: 2
            color: background_color
            border.color: colorPalette.light
            border.width: 1
        }
    }


    // Measure Mode
    ComboBox {
        id: measureMode
        model: {}
        onActivated: {
            OscProperties._measure_mode(currentText)
            updateDisplayedOscData()
        }

        background: Rectangle {
            implicitWidth: measureModeLabel.width
            implicitHeight: 25
            radius: 2
            color: background_color
            border.color: colorPalette.light
            border.width: 1
        }
    }


    // Start/Stop
    Button {
        id: startStop
        text: ""
        onClicked: OscProperties._start_n_stop()

        background: Rectangle {
            implicitWidth: startStopLabel.width
            implicitHeight: 25
            radius: 2
            color: background_color
            border.color: colorPalette.light
            border.width: 1
        }
    }

    onReloadOscilloscopeSettings: {
        reloadOscSettings()
    }

    function reloadOscSettings(){
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

    function updateDisplayedOscData(){
        reloadOscSettings()
        oscilloscopeMainRect.reloadOscChannelSettings()
    }


    Component.onCompleted: {
       updateDisplayedOscData()
    }


    Connections {
        target: OscProperties

        function onClockSrc(device_id, value) {
            if(compareDevices(device_id, oscilloscopeMainRect.selectedDevice)){
                clockSource.currentIndex = findIndexOfModel(clockSource.model, value)
            }
        }
        function onClockSrcAvail(device_id, value) {
            if(compareDevices(device_id, oscilloscopeMainRect.selectedDevice)){
                clockSource.model = value
            }
        }

        function onClockOut(device_id, value) {
            if(compareDevices(device_id, oscilloscopeMainRect.selectedDevice)){
                clockOutput.currentIndex = findIndexOfModel(clockOutput.model, value)
            }
        }
        function onClockOutsAvail(device_id, value) {
            if(compareDevices(device_id, oscilloscopeMainRect.selectedDevice)){
                clockOutput.model = value
            }
        }

        function onRes(device_id, value) {
            if(compareDevices(device_id, oscilloscopeMainRect.selectedDevice)){
                res.currentIndex = findIndexOfModel(res.model, value)
            }
        }
        function onResAvail(device_id, value) {
            if(compareDevices(device_id, oscilloscopeMainRect.selectedDevice)){
                res.model = value
            }
        }

        function onAutoRes(device_id, value) {
            if(compareDevices(device_id, oscilloscopeMainRect.selectedDevice)){
                autoRes.currentIndex = findIndexOfModel(autoRes.model, value)
            }
        }
        function onAutoResAvail(device_id, value) {
            if(compareDevices(device_id, oscilloscopeMainRect.selectedDevice)){
                autoRes.model = value
            }
        }

        function onSampleFreq(device_id, value) {
            if(compareDevices(device_id, oscilloscopeMainRect.selectedDevice)){
                //frequency.currentIndex = findNearestIndexOfModel(frequency.model, value)
                let units = ["Hz", "kHz", "MHz"]
                let index = 0
                let multiplier = 1000
                for(let i=0; i<units.length; i++){
                    if(value/multiplier >= 1){
                        index++
                        multiplier *=1000
                    }
                }
                multiplier/=1000
                value/=multiplier
                value = value.toFixed(2)
                frequency.editText = value + " " + units[index]
            }
        }

        function onRecLen(device_id, value) {
            if(compareDevices(device_id, oscilloscopeMainRect.selectedDevice)){
                //recordLength.currentIndex = findNearestIndexOfModel(recordLength.model, value)
                let units = ["Sam", "kSam"]
                let index = 0
                let multiplier = 1000
                for(let i=0; i<units.length; i++){
                    if(value/multiplier >= 1){
                        index++
                        multiplier *=1000
                    }
                }
                multiplier/=1000
                value/=multiplier
                value = value.toFixed(2)
                recordLength.editText = value + " " + units[index]
            }
        }

        function onMeasureMode(device_id, value) {
            if(compareDevices(device_id, oscilloscopeMainRect.selectedDevice)){
                measureMode.currentIndex = findIndexOfModel(measureMode.model, value)
            }
        }
        function onMeasureModesAvail(device_id, value) {
            if(compareDevices(device_id, oscilloscopeMainRect.selectedDevice)){
                measureMode.model = value
            }
        }

        function onTrigTimeout(device_id, value) {
            if(compareDevices(device_id, oscilloscopeMainRect.selectedDevice)){
                triggerTimeout.text = ""
                triggerTimeout.placeholderText = value
            }
        }

        function onPreSampleRatio(device_id, value) {
            if(compareDevices(device_id, oscilloscopeMainRect.selectedDevice)){
                preSampleRatio.text = ""
                preSampleRatio.placeholderText = value
            }
        }

        function onIsRunning(device_id, value) {
            if(compareDevices(device_id, oscilloscopeMainRect.selectedDevice)){
                if(value === true){
                    startStop.text = "Stop"
                }
                else {
                     startStop.text = "Start"
                }
            }
        }
    }

    Connections {
        target: FrontToBackConnector

        function onIsRunning(device_id, value) {
            if(compareDevices(device_id, oscilloscopeMainRect.selectedDevice)){
                if(value === true){
                    startStop.text = "Stop"
                }
                else {
                     startStop.text = "Start"
                }
            }
        }

    }
}





