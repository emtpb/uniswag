import QtQuick 2.12
import QtQuick.Layouts 1.12
import QtQuick.Controls 2.12
import QtCharts 2.3

import "res/"
import "res/devicelist/"

/*!
    \qmltype Rectangle
    \brief The main view containing all views for oscilloscopes.

    This rectangle shows all the stuff that is displayed when the "Oscilloscopes" tab is clicked in the TapBar.
*/
Rectangle {
    id: oscilloscopeMainRect
    //Layout.fillWidth: true
    //Layout.fillHeight: true

    property string oscPath: "devices/oscilloscopes/"

    property var selectedDevice: NaN
    property var selectedChannelNum: NaN

    property var chart: oscilloscopeChart

    /*!
        \qmltype RowLayout
        \brief A layout containing the device list on the left and the oscilloscope data on the right.

        A layout with two entries next to each other.
        On the left is the device list and on the right the chart showing the oscilloscope data and the box containing the device settings.

    */
    RowLayout {
        anchors.fill: parent
        spacing: -5

        /*!
            \qmltype Rectangle
            \brief A rectangle containing the device list.

            This rectangle contains the appropriate device list.
            It only serves as a wrapper to specify the size of the device list
        */
        Rectangle {
            id: oscilloscopeListMainWindow
            //implicitWidth: ((oscilloscopeMainRect.width * 0.1) > 180) ? (oscilloscopeMainRect.width * 0.1) : 180
            implicitWidth: 180

            Layout.fillHeight: true

            Layout.leftMargin: 3
            Layout.topMargin: 10

            color: colorPalette.window

            /*!
                \qmltype DeviceList
                \brief A device list that displays the devices that are connected to the computer via USB
            */
            DeviceListView {
                deviceType: "Osc"
                anchors.fill: parent

                //! This callback is called when a new device is selected in the list.
                onNewSelectedItem: function(item) {
                    if(deviceTypeSelectionSwipeView.deviceIsOsc){
                        oscilloscopeLoader.source = oscPath + item["Vendor"] + "_" + item["Name"] + "_DEVICE.qml"
                        selectedDevice = item
                        oscilloscopeLoader.active = true
                    }
                }

                //! This callback is called when a new channel is selected in the list.
                onNewSelectedChannel: function(chNo){
                    if(deviceTypeSelectionSwipeView.deviceIsOsc){
                        selectedChannelNum = chNo
                        oscilloscopeChannelLoader.source = oscPath + selectedDevice["Vendor"] + "_" + selectedDevice["Name"] + "_CHANNEL.qml"
                        oscilloscopeChannelLoader.active = true
                    }
                }
            }
        }

        /*!
            \qmltype ColumnLayout
            \brief A layout containing the oscilloscope data chart and the device settings box below the chart
        */
        ColumnLayout{
            //! This makes the border between the chartview and the settings bar not so big.
            spacing: -5
            Layout.fillHeight: true
            Layout.fillWidth: true
            
            /*!
                \qmltype DeviceDataChartView
                \brief A view containing the oscilloscope data chart.
                
                The DeviceDataChartView is the chart which displays the measurement data.
            */
            DeviceDataChartView{
                id: oscilloscopeChart
                deviceType: "Osc"
                Layout.fillHeight: true
                Layout.fillWidth: true


                //! This notifies the files associated with a device when zooming in the chart.
                //! This can then be used to reload device settings, for example.
                onZoomedWithMouse: {
                    if(oscilloscopeChannelLoader.active){
                        try{
                            oscilloscopeChannelLoader.children[0].zoomed()
                        }
                        catch (error) {
                        }
                    }
                    if(oscilloscopeLoader.active){
                        try{
                            oscilloscopeLoader.children[0].zoomed()
                        }
                        catch (error) {
                        }
                    }
                }

                //! This notifies the files associated with a device when changing the slider position in the chart.
                //! This can then be used to reload device settings, for example.
                onSliderPositionChanged: function(position){
                    if(oscilloscopeChannelLoader.active){
                        try{
                            oscilloscopeChannelLoader.children[0].triggerSliderPositionChanged(position)
                        }
                        catch (error) {
                        }
                    }
                    if(oscilloscopeLoader.active){
                        try{
                            oscilloscopeLoader.children[0].triggerSliderPositionChanged(position)
                        }
                        catch (error) {
                        }
                    }
                }
            }

            /*!
                \qmltype FastFourierChart
                \brief A view containing the fft data chart.

                The FastFourierChart is the chart which displays the fft data.
            */
            FastFourierChart{
                id: fftChart
                Layout.fillHeight: fftVisible? true: false
                Layout.fillWidth: true
                visible:  fftVisible? true: false

            }
            

            /*!
                \qmltype GridLayout
                \brief A layout containing the device settings box below the chart
            */

            ColumnLayout{
                Layout.fillWidth: true

                //! The oscilloscope settings
                Rectangle{
                    Layout.fillWidth: true
                    height: 60
                    color: colorPalette.window
                    Layout.leftMargin: 10
                    Layout.rightMargin: 10

                    RowLayout {
                        anchors.fill: parent
                        spacing: 10
                        clip: true

                        Rectangle{
                            width: 60
                            height: deviceTextLabel.contentHeight
                            color: "transparent"
                            Label {
                                id: deviceTextLabel
                                text: qsTr("Device:")
                                visible: oscilloscopeLoader.active
                            }
                        }

                        Item {
                            Layout.fillWidth: true
                            implicitHeight: 60
                            Loader {
                                id: oscilloscopeLoader
                                active: false
                                anchors.fill: parent

                                property var mainRect: oscilloscopeMainRect
                            }
                        }
                    }
                }
                //! The channel settings
                Rectangle{
                    Layout.fillWidth: true
                    height: 60
                    color: colorPalette.window
                    Layout.leftMargin: 10
                    Layout.rightMargin: 10

                    RowLayout {
                        anchors.fill: parent
                        spacing: 10
                        clip: true

                        Rectangle{
                            width: 60
                            height: channelTextLabel.contentHeight
                            color: "transparent"
                            Label {
                                id: channelTextLabel
                                text: qsTr("Channel " + selectedChannelNum + ":")
                                visible: oscilloscopeChannelLoader.active
                            }
                        }

                        Item {
                            Layout.fillWidth: true
                            implicitHeight: 60
                            Loader {
                                id: oscilloscopeChannelLoader
                                active: false
                                anchors.fill: parent

                                property var mainRect: oscilloscopeMainRect
                            }
                        }
                    }
                }
            }

        }
    }


    //! With these functions the position of the trigger slider and the icon can be set.
    function risingEdgeIcon() {
        oscilloscopeChart.children[1].changeSymbolToRisingEdge()
    }
    function fallingEdgeIcon() {
        oscilloscopeChart.children[1].changeSymbolToFallingEdge()
    }
    function triangleIcon() {
        oscilloscopeChart.children[1].changeSymbolToTriangle()
    }
    function inWindowIcon() {
        oscilloscopeChart.children[1].changeSymbolToInWindow()
    }
    function outWindowIcon() {
        oscilloscopeChart.children[1].changeSymbolToOutWindow()
    }
    function triggerIconPosition(position){
         oscilloscopeChart.children[1].changeSliderPosition(position)
    }
    function changeHysteresisSliderSizeInPercent(value){
        oscilloscopeChart.children[1].changeHysteresisSliderSizeInPercent(value)
    }


    //! With these functions the settings of the channels or oscilloscopes can be reloaded.
    //! This is useful when, for example, an oscilloscope setting is made that changes a channel setting.
    function reloadOscChannelSettings() {
        if(oscilloscopeChannelLoader.active){
            try{
                oscilloscopeChannelLoader.children[0].reloadOscChannelSettings()
            }
            catch (error) {
            }
        }
    }
    function reloadOscilloscopeSettings() {
        if(oscilloscopeLoader.active){
            try{
                oscilloscopeLoader.children[0].reloadOscilloscopeSettings()
            }
            catch (error) {
            }
        }
    }

    //! Signal to save an image as png which is called when the "save image" button is pressed.
    signal saveImage()
    onSaveImage: {
        oscilloscopeChart.grabToImage(function(result) {
            FrontToBackConnector.save_as_png(result)
        });
    }


    //! Signal to reset the zoom when the "zoom reset" button is clicked.
    signal zoomResetClicked()
    onZoomResetClicked: {
        oscilloscopeChart.zoomResetClicked()
        fftChart.zoomResetClicked()
    }

    //! Function to compare 2 devices.
    //! This is used to check if the current device is the selected device
    function compareDevices(device1, device2){
        if(device1["Name"] === device2["Name"] && device1["Vendor"] === device2["Vendor"] && device1["SerNo"] === device2["SerNo"] && device1["DevType"] === device2["DevType"]){
            return true
        }
        else {
            return false
        }
    }

    function findIndexOfModel(model, value){
        for(let i = 0; i < model.length; i++){
            if(model[i] === value){
                return i
            }
        }
        return -1
    }

    //! https://stackoverflow.com/questions/51021511/finding-the-nearest-number-in-an-array
    function findNearestIndexOfModel(model, value){
        let array = []
        for(let i = 0; i < model.count; i++){
            array.push(Number(model.get(i).text))
        }
        let nearest = array.reduce((a, b) => Math.abs(a - value) < Math.abs(b - value) ? a : b);
        let index = array.findIndex(x => x === nearest)

        return index
    }
}
