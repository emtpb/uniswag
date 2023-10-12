import QtQuick 2.12
import QtQuick.Layouts 1.12
import QtQuick.Controls 2.12
import QtCharts 2.3

import "res/"
import "res/devicelist/"

/*!
    \qmltype Rectangle
    \brief The main view containing all views for signal generators.

    This rectangle shows all the stuff that is displayed when the "Signal Generators" tab is clicked in the TapBar.
*/
Rectangle {
    id: signalGenMainRect
    //Layout.fillWidth: true
    //Layout.fillHeight: true

    property string signalGenPath: "devices/generators/"

    property var selectedDevice: NaN
    property var selectedChannelNum: NaN

    /*!
        \qmltype RowLayout
        \brief A layout containing the device list on the left and the signal generator data on the right.

        A layout with two entries next to each other.
        On the left is the device list and on the right the chart showing the selected signal and the box containing the device settings.

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
            id: signalGenListMainWindow
            //implicitWidth: ((signalGenMainRect.width * 0.1) > 180) ? (signalGenMainRect.width * 0.1) : 180
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
                deviceType: "Gen"
                anchors.fill: parent

                //! This callback is called when a new device is selected in the list.
                onNewSelectedItem: function(item) {
                    if(!deviceTypeSelectionSwipeView.deviceIsOsc){
                        signalGenLoader.source = signalGenPath + item["Vendor"] + "_" + item["Name"] + "_DEVICE.qml"
                        selectedDevice = item
                        signalGenLoader.active = true
                    }
                }

                //! This callback is called when a new channel is selected in the list.
                onNewSelectedChannel: function(chNo){
                    if(!deviceTypeSelectionSwipeView.deviceIsOsc){
                        selectedChannelNum = chNo
                        signalGenChannelLoader.source = signalGenPath + selectedDevice["Vendor"] + "_" + selectedDevice["Name"] + "_CHANNEL.qml"
                        signalGenChannelLoader.active = true
                    }
                }
            }
        }

        /*!
            \qmltype ColumnLayout
            \brief A layout containing the signal generator data chart and the device settings box below the chart
        */
        ColumnLayout{
            spacing: -5
            Layout.fillHeight: true
            Layout.fillWidth: true
            
            /*!
                \qmltype DeviceDataChartView
                \brief A view containing the signal chart.
                
                The DeviceDataChartView is the chart which displays the current signal from the signal generator.
            */
            DeviceDataChartView{
                id: signalGenChart
                deviceType: "Gen"
                Layout.fillHeight: true
                Layout.fillWidth: true
            }
            
            ColumnLayout{
                Layout.fillWidth: true

                //! The signal generator settings
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
                                visible: signalGenLoader.active
                            }
                        }

                        Item {
                            Layout.fillWidth: true
                            implicitHeight: 60
                            Loader {
                                id: signalGenLoader
                                active: false
                                anchors.fill: parent

                                property var mainRect: signalGenMainRect
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
                                visible: signalGenChannelLoader.active
                            }
                        }

                        Item {
                            Layout.fillWidth: true
                            implicitHeight: 60
                            Loader {
                                id: signalGenChannelLoader
                                active: false
                                anchors.fill: parent

                                property var mainRect: signalGenMainRect
                            }
                        }
                    }
                }
            }
        }
    }

    //! With these functions the settings of the channels or generators can be reloaded.
    //! This is useful when, for example, an generator setting is made that changes a channel setting.
    function reloadGenChannelSettings() {
        if(signalGenChannelLoader.active){
            try{
                signalGenChannelLoader.children[0].reloadGenChannelSettings()
            }
            catch (error) {
            }
        }
    }
    function reloadGeneratorSettings() {
        if(signalGenLoader.active){
            try{
                signalGenLoader.children[0].reloadGeneratorSettings()
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

    // https://stackoverflow.com/questions/51021511/finding-the-nearest-number-in-an-array
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
