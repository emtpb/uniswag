import QtQuick
import QtQuick.Layouts
import QtQuick.Controls
import QtQuick.Dialogs

GridLayout {
    columns: 10
    columnSpacing: 10

    property var background_color: darkModeEnabled? colorPalette.dark : colorPalette.light

    // Inverted Output not supported
    // Phase not supported
    // Pulse Width not supported
    // Burst Sample Count not supported
    // Burst Segment Count not supported

    Label {
        id: modeLabel
        text: "Mode"
    }
    Label {
        id: sigTypeLabel
        text: "Signal Type"
    }
    Label {
        id: isAmpAutoRangeLabel
        text: "Amplitude Auto Ranging"
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
        id: freqModeLabel
        text: "Frequency Mode"
    }
    Label {
        id: frequencyLabel
        text: "Frequency"
    }
    Label {
        id: symmetryLabel
        text: "Symmetry"
    }
    Label {
        id: burstCntLabel
        text: "Burst Count"
    }
    Label {
        id: arbSignalLabel
        text: "Arbitrary Data"
    }

    // Mode
    ComboBox {
        id: mode
        model: ListModel{}
        onActivated: {
            GenProperties._mode(currentText)
            reloadChSettings()
        }

        background: Rectangle {
            implicitWidth: modeLabel.width + 55
            implicitHeight: 25
            radius: 2
            color: background_color
            border.color: colorPalette.light
            border.width: 1
        }
    }

    // Signal Type
    ComboBox {
        id: sigType
        model: ListModel{}
        onActivated: {
            GenProperties._sig_type(currentText)
            reloadChSettings()
        }

        background: Rectangle {
            implicitWidth: sigTypeLabel.width
            implicitHeight: 25
            radius: 2
            color: background_color
            border.color: colorPalette.light
            border.width: 1
        }
    }

    // Amplitude Auto Ranging
    CheckBox {
        id: isAmpAutoRange
        text: ""
        implicitHeight: 25
        indicator: Rectangle {
            implicitWidth: 12
            implicitHeight: 12
            x: isAmpAutoRange.leftPadding
            y: parent.height / 2 - height / 2
            radius: 3
            border.color: isAmpAutoRange.down ? "#17a81a" : "#21be2b"
            Rectangle {
                width: 6
                height: 6
                x: 3
                y: 3
                radius: 2
                color: isAmpAutoRange.down ? "#17a81a" : "#21be2b"
                visible: isAmpAutoRange.checked
            }
        }
        contentItem: Text {
            text: isAmpAutoRange.text
            font: isAmpAutoRange.font
            opacity: enabled ? 1.0 : 0.3
            color: isAmpAutoRange.checked ? "#17a81a" : "#990000"
            verticalAlignment: Text.AlignVCenter
            leftPadding: isAmpAutoRange.indicator.width + isAmpAutoRange.spacing
        }
        background: Rectangle {
            implicitWidth: isAmpAutoRangeLabel.width
            implicitHeight: 25
            radius: 2
            color: background_color
            border.color: colorPalette.light
            border.width: 1
        }
        onCheckStateChanged: {
            if(checkState === Qt.Checked){
                GenProperties._is_amp_auto_range(true)
            }
            else {
                GenProperties._is_amp_auto_range(false)
            }
            reloadChSettings()
        }
    }

    // Amplitude
    TextField {
        id: amp
        onAccepted: {
            GenProperties._amp(text)
            reloadChSettings()
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
            reloadChSettings()
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

    // Frequency Mode
    ComboBox {
        id: freqMode
        model: ListModel{}
        onActivated: {
            GenProperties._freq_mode(currentText)
            reloadChSettings()
        }

        background: Rectangle {
            implicitWidth: freqModeLabel.width
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
            reloadChSettings()
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

    // Symmetry
    TextField {
        id: symmetry
        onAccepted: {
            GenProperties._symmetry(text)
            reloadChSettings()
        }

        background: Rectangle {
            implicitWidth: symmetryLabel.width
            implicitHeight: 25
            radius: 2
            color: background_color
            border.color: colorPalette.light
            border.width: 1
        }
    }

    // Burst Count
    TextField {
        id: burstCnt
        onAccepted: {
            GenProperties._burst_cnt(text)
            reloadChSettings()
        }

        background: Rectangle {
            implicitWidth: burstCntLabel.width
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
        onClicked: arbSignalDialog.open()

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
            reloadChSettings()
        }
    }

    Component.onCompleted: {
        reloadChSettings()
    }

    function reloadChSettings(){
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

        // Amplitude Auto Ranging
        function onIsAmpAutoRange(device_id, ch_num, value) {
            if(compareDevices(device_id, signalGenMainRect.selectedDevice) && ch_num === signalGenMainRect.selectedChannelNum){
                if(value === true){
                    isAmpAutoRange.checkState = Qt.Checked
                    isAmpAutoRange.text = "ON"
                }
                else {
                    isAmpAutoRange.checkState = Qt.Unchecked
                    isAmpAutoRange.text = "OFF"
                }
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

        // Frequency Mode
        function onFreqMode(device_id, ch_num, value) {
            if(compareDevices(device_id, signalGenMainRect.selectedDevice) && ch_num === signalGenMainRect.selectedChannelNum){
                freqMode.currentIndex = findIndexOfModel(freqMode.model, value)
            }
        }
        function onFreqModesAvail(device_id, ch_num, value) {
            if(compareDevices(device_id, signalGenMainRect.selectedDevice) && ch_num === signalGenMainRect.selectedChannelNum){
                freqMode.model = value
            }
        }

        // Symmetry
        function onSymmetry(device_id, ch_num, value) {
            if(compareDevices(device_id, signalGenMainRect.selectedDevice) && ch_num === signalGenMainRect.selectedChannelNum){
                symmetry.text = ""
                symmetry.placeholderText = value
            }
        }

        // Mode
        function onMode(device_id, ch_num, value) {
            if(compareDevices(device_id, signalGenMainRect.selectedDevice) && ch_num === signalGenMainRect.selectedChannelNum){
                mode.currentIndex = findIndexOfModel(mode.model, value)
            }
        }
        function onModesAvail(device_id, ch_num, value) {
            if(compareDevices(device_id, signalGenMainRect.selectedDevice) && ch_num === signalGenMainRect.selectedChannelNum){
                mode.model = value
            }
        }

        // Burst Count
        function onBurstCnt(device_id, ch_num, value) {
            if(compareDevices(device_id, signalGenMainRect.selectedDevice) && ch_num === signalGenMainRect.selectedChannelNum){
                burstCnt.text = ""
                burstCnt.placeholderText = value
            }
        }

    }
}




