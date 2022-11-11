import QtQuick
import QtQuick.Layouts
import QtQuick.Controls
import QtQuick.Dialogs

GridLayout {
    columns: 11
    columnSpacing: 10

    signal reloadGenChannelSettings()

    property var background_color: darkModeEnabled? colorPalette.dark : colorPalette.light


    // Voltage Max not supported
    // Voltage Min not supported
    // Burst Delay not supported
    // Pulse Width not supported
    // Pulse Delay not supported
    // Pulse Hold not supported
    // Leading Pulse Transition not supported
    // Trailing Pulse Transition not supported

    Label {
        id: sigTypeLabel
        text: "Signal Type"
    }
    Label {
        id: ampLabel
        text: "Amplitude"
    }
    Label {
        id: offsetLabel
        text: "Offset"
    }
    Label {
        id: frequencyLabel
        text: "Frequency"
    }
    Label {
        id: periodLabel
        text: "Period"
    }
    Label {
        id: phaseLabel
        text: "Phase"
    }
    Label {
        id: dutyCycleLabel
        text: "Duty Cycle"
    }
    Label {
        id: impedanceLabel
        text: "Impedance"
    }
    Label {
        id: isBurstOnLabel
        text: "Burst State"
    }
    Label {
        id: burstModeLabel
        text: "Burst Mode"
    }
    Label {
        id: arbSignalLabel
        text: "Arbitrary Data"
    }


    // Signal Type
    ComboBox {
        id: sigType
        model: ListModel{}
        onActivated: {
            GenProperties._sig_type(currentText)
            loadCurrentSettings()
        }

        background: Rectangle {
            implicitWidth: sigTypeLabel.width + 20
            implicitHeight: 25
            radius: 2
            color: background_color
            border.color: colorPalette.light
            border.width: 1
        }
    }

    // Amplitude
    TextField {
        id: amp
        onAccepted: {
            GenProperties._amp(text)
            loadCurrentSettings()
        }

        background: Rectangle {
            implicitWidth: ampLabel.width
            implicitHeight: 25
            radius: 2
            color: background_color
            border.color: colorPalette.light
            border.width: 1
        }
    }

    // Offset
    TextField {
        id: offset
        onAccepted: {
            GenProperties._offset(text)
            loadCurrentSettings()
        }

        background: Rectangle {
            implicitWidth: offsetLabel.width
            implicitHeight: 25
            radius: 2
            color: background_color
            border.color: colorPalette.light
            border.width: 1
        }
    }

    // Frequency
    TextField {
        id: frequency
        onAccepted: {
            GenProperties._freq(text)
            loadCurrentSettings()
        }

        background: Rectangle {
            implicitWidth: frequencyLabel.width
            implicitHeight: 25
            radius: 2
            color: background_color
            border.color: colorPalette.light
            border.width: 1
        }
    }

    // Period
    TextField {
        id: period
        onAccepted: {
            GenProperties._period(text)
            loadCurrentSettings()
        }

        background: Rectangle {
            implicitWidth: periodLabel.width + 25
            implicitHeight: 25
            radius: 2
            color: background_color
            border.color: colorPalette.light
            border.width: 1
        }
    }

    // Phase
    TextField {
        id: phase
        onAccepted: {
            GenProperties._phase(text)
            loadCurrentSettings()
        }

        background: Rectangle {
            implicitWidth: phaseLabel.width + 25
            implicitHeight: 25
            radius: 2
            color: background_color
            border.color: colorPalette.light
            border.width: 1
        }
    }

    // Duty Cycle
    TextField {
        id: dutyCycle
        onAccepted: {
            GenProperties._duty_cycle(text)
            loadCurrentSettings()
        }

        background: Rectangle {
            implicitWidth: dutyCycleLabel.width
            implicitHeight: 25
            radius: 2
            color: background_color
            border.color: colorPalette.light
            border.width: 1
        }
    }

    // Impedance
    TextField {
        id: impedance
        onAccepted: {
            GenProperties._impedance(text)
            loadCurrentSettings()
        }

        background: Rectangle {
            implicitWidth: impedanceLabel.width
            implicitHeight: 25
            radius: 2
            color: background_color
            border.color: colorPalette.light
            border.width: 1
        }
    }

    // Burst State
    CheckBox {
        id: isBurstOn
        text: ""
        implicitHeight: 25
        indicator: Rectangle {
            implicitWidth: 12
            implicitHeight: 12
            x: isBurstOn.leftPadding
            y: parent.height / 2 - height / 2
            radius: 3
            border.color: isBurstOn.down ? "#17a81a" : "#21be2b"
            Rectangle {
                width: 6
                height: 6
                x: 3
                y: 3
                radius: 2
                color: isBurstOn.down ? "#17a81a" : "#21be2b"
                visible: isBurstOn.checked
            }
        }
        contentItem: Text {
            text: isBurstOn.text
            font: isBurstOn.font
            opacity: enabled ? 1.0 : 0.3
            color: isBurstOn.checked ? "#17a81a" : "#990000"
            verticalAlignment: Text.AlignVCenter
            leftPadding: isBurstOn.indicator.width + isBurstOn.spacing
        }
        background: Rectangle {
            implicitWidth: isBurstOnLabel.width
            implicitHeight: 25
            radius: 2
            color: background_color
            border.color: colorPalette.light
            border.width: 1
        }
        onCheckStateChanged: {
            if(checkState === Qt.Checked){
                GenProperties._is_burst_on(true)
            }
            else {
                GenProperties._is_burst_on(false)
            }
            loadCurrentSettings()
        }
    }

    // Burst Mode
    ComboBox {
        id: burstMode
        model: ListModel{}
        onActivated: {
            GenProperties._burst_mode(currentText)
            loadCurrentSettings()
        }

        background: Rectangle {
            implicitWidth: burstModeLabel.width + 20
            implicitHeight: 25
            radius: 2
            color: background_color
            border.color: colorPalette.light
            border.width: 1
        }
    }

    // arbitrary signal
    Button {
        text: "Load"
        onClicked: {
            arbSignalDialog.open()
            loadCurrentSettings()
        }

        background: Rectangle {
            implicitWidth: arbSignalLabel.width
            implicitHeight: 25
            radius: 2
            color: background_color
            border.color: colorPalette.light
            border.width: 1
        }
    }
    FileDialog {
        id: arbSignalDialog
        nameFilters: ["Comma-separated values (*.csv)", "JSON Files (*.json)"]
        //currentFolder: StandardPaths.writableLocation(StandardPaths.DocumentsLocation)
        onAccepted: {
            GenProperties._arb_data(selectedFile)
            loadCurrentSettings()
        }
    }

    onReloadGenChannelSettings: {
        reloadChSettings()
    }

    function reloadChSettings(){
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

    function loadCurrentSettings(){
        reloadChSettings()
        signalGenMainRect.reloadGeneratorSettings()

    }

    Component.onCompleted: {
        loadCurrentSettings()
    }


    Connections {
        target: GenProperties

        // Signal Type
        function onSigType(device_id, ch_num, value) {
            if(compareDevices(device_id, signalGenMainRect.selectedDevice) && ch_num === signalGenMainRect.selectedChannelNum){
                sigType.currentIndex = findIndexOfModel(sigType.model, value)
            }
        }
        function onSigTypesAvail(device_id, ch_num, value) {
            if(compareDevices(device_id, signalGenMainRect.selectedDevice) && ch_num === signalGenMainRect.selectedChannelNum){
                sigType.model = value
            }
        }

        // Amplitude
        function onAmp(device_id, ch_num, value) {
            if(compareDevices(device_id, signalGenMainRect.selectedDevice) && ch_num === signalGenMainRect.selectedChannelNum){
                amp.text = ""
                amp.placeholderText = value
            }
        }

        // Offset
        function onOffset(device_id, ch_num, value) {
            if(compareDevices(device_id, signalGenMainRect.selectedDevice) && ch_num === signalGenMainRect.selectedChannelNum){
                offset.text = ""
                offset.placeholderText = value
            }
        }

        // Frequency
        function onFreq(device_id, ch_num, value) {
            if(compareDevices(device_id, signalGenMainRect.selectedDevice) && ch_num === signalGenMainRect.selectedChannelNum){
                frequency.text = ""
                frequency.placeholderText = value
            }
        }

        // Period
        function onPeriod(device_id, ch_num, value) {
            if(compareDevices(device_id, signalGenMainRect.selectedDevice) && ch_num === signalGenMainRect.selectedChannelNum){
                period.text = ""
                period.placeholderText = value
            }
        }

        // Phase
        function onPhase(device_id, ch_num, value) {
            if(compareDevices(device_id, signalGenMainRect.selectedDevice) && ch_num === signalGenMainRect.selectedChannelNum){
                phase.text = ""
                phase.placeholderText = value
            }
        }

        // Duty Cycle
        function onDutyCycle(device_id, ch_num, value) {
            if(compareDevices(device_id, signalGenMainRect.selectedDevice) && ch_num === signalGenMainRect.selectedChannelNum){
                dutyCycle.text = ""
                dutyCycle.placeholderText = value
            }
        }

        // Impedance
        function onImpedance(device_id, ch_num, value) {
            if(compareDevices(device_id, signalGenMainRect.selectedDevice) && ch_num === signalGenMainRect.selectedChannelNum){
                impedance.text = ""
                impedance.placeholderText = value
            }
        }

        // Burst State
        function onIsBurstOn(device_id, ch_num, value) {
            if(compareDevices(device_id, signalGenMainRect.selectedDevice) && ch_num === signalGenMainRect.selectedChannelNum){
                if(value === true){
                    isBurstOn.checkState = Qt.Checked
                    isBurstOn.text = "ON"
                }
                else {
                    isBurstOn.checkState = Qt.Unchecked
                    isBurstOn.text = "OFF"
                }
            }
        }

        // Burst Mode
        function onBurstMode(device_id, ch_num, value) {
            if(compareDevices(device_id, signalGenMainRect.selectedDevice) && ch_num === signalGenMainRect.selectedChannelNum){
                burstMode.currentIndex = findIndexOfModel(burstMode.model, value)
            }
        }
        function onBurstModesAvail(device_id, ch_num, value) {
            if(compareDevices(device_id, signalGenMainRect.selectedDevice) && ch_num === signalGenMainRect.selectedChannelNum){
                burstMode.model = value
            }
        }

    }
}




