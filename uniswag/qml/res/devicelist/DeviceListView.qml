

/****************************************************************************
**
** Copyright (C) 2017 The Qt Company Ltd.
** Contact: https://www.qt.io/licensing/
**
** This file is part of the examples of the Qt Toolkit.
**
** $QT_BEGIN_LICENSE:BSD$
** Commercial License Usage
** Licensees holding valid commercial Qt licenses may use this file in
** accordance with the commercial license agreement provided with the
** Software or, alternatively, in accordance with the terms contained in
** a written agreement between you and The Qt Company. For licensing terms
** and conditions see https://www.qt.io/terms-conditions. For further
** information use the contact form at https://www.qt.io/contact-us.
**
** BSD License Usage
** Alternatively, you may use this file under the terms of the BSD license
** as follows:
**
** "Redistribution and use in source and binary forms, with or without
** modification, are permitted provided that the following conditions are
** met:
**   * Redistributions of source code must retain the above copyright
**     notice, this list of conditions and the following disclaimer.
**   * Redistributions in binary form must reproduce the above copyright
**     notice, this list of conditions and the following disclaimer in
**     the documentation and/or other materials provided with the
**     distribution.
**   * Neither the name of The Qt Company Ltd nor the names of its
**     contributors may be used to endorse or promote products derived
**     from this software without specific prior written permission.
**
**
** THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
** "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
** LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR
** A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT
** OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
** SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
** LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
** DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY
** THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
** (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
** OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE."
**
** $QT_END_LICENSE$
**
****************************************************************************/
import QtQuick 2.12
import QtQuick.Controls 2.12

import "."

/*!
    \qmltype ListView
    \brief A ListView that displays the devices that are connected to the computer via USB
*/
ListView {
    id: deviceList

    //! replace oscilloscope and channel settings (load new QML file) for selected item or channel
    signal newSelectedItem(var item)
    signal newSelectedChannel(var chNo)

    //! Set in OscilloscopeView.qml or SignalGeneratorView.qml ("Osc" or "Gen")
    property string deviceType: ""

    //! The selected device and channel (-1, because no device is selected on startup)
    property int selectedItem: -1
    property var selectedChannel: {"DevIndex": -1, "ChIndex": 0}

    //! True if a channel was clicked that does not belong to the currently selected device
    property bool channelFromWrongDeviceSelected: false
    property int wrongSelectedChannelIndex: -1

    ScrollBar.vertical: ScrollBar {}

    focus: true
    boundsBehavior: Flickable.StopAtBounds

    //! The design of the fields containing the vendor of the devices
    section.property: "Vendor"
    section.delegate: SectionDelegate {
        width: deviceList.width
    }

    //! The design of one list entry
    delegate: Delegate {
        id: scopeListDelegate
        width: deviceList.width
    }

    model: Model {
        id: deviceListModel
    }

    //! A device has been selected.
    signal itemSelected(int index)
    onItemSelected: function(index) {
        if(index !== selectedItem){
            let devID = deviceListModel.get(index).DevID
            if(deviceType === "Osc"){
                //! Load the qml file with the oscilloscope settings.
                oscilloscopeLoader.active = false
            }
            else{
                 //! Load the qml file with the signal gen settings.
                signalGenLoader.active = false
            }
            // Python
            FrontToBackConnector.set_selected_device(devID)
        }
    }

    //! A channel has been selected.
    signal channelSelected(int device_index, int channel_index)
    onChannelSelected: function(device_index, channel_index){
        // change the selected device when the channel of another device is selected
        if(selectedItem !== device_index){
            channelFromWrongDeviceSelected = true
            wrongSelectedChannelIndex = channel_index
            itemSelected(device_index)
        }
        else {
            let item = deviceListModel.get(device_index)
            let chList =  item.ChList
            let devID = item.DevID
            let chNo = chList.get(channel_index).No
            if(deviceType === "Osc"){
                //! Load the qml file with the oscilloscopes channel settings.
                oscilloscopeChannelLoader.active = false
            }
            else{
                 //! Load the qml file with the signal gens channel settings.
                signalGenChannelLoader.active = false
            }
            // Python
            FrontToBackConnector.set_selected_channel(devID, chNo)
        }
    }

    //! The item visibility checkbox was clicked.
    signal itemVisibilityToggled(int index)
    onItemVisibilityToggled: function(index){
        let devID = deviceListModel.get(index).DevID
        let channelColors = []
        let numberOfColors = deviceListModel.get(index).ChList.count
        for(let i = 0; i < numberOfColors; i++){
            channelColors.push(deviceListModel.get(index).ChList.get(i).ColorName)
        }
        if(deviceType === "Osc"){
            // Python
            FrontToBackConnector.visibility_checkbox_toggled(devID, NaN, channelColors)
        }
        else{
            // Python
            FrontToBackConnector.output_checkbox_toggled(devID, NaN)
        }
    }

    //! The channel visibility checkbox was clicked.
    signal channelVisibilityToggled(int device_index, int channel_index)
    onChannelVisibilityToggled: function(device_index, channel_index){
        let item = deviceListModel.get(device_index)
        let devID = item.DevID
        let chNo = item.ChList.get(channel_index).No
        let color = [item.ChList.get(channel_index).ColorName]
        if(deviceType === "Osc"){           
            // Python
            FrontToBackConnector.visibility_checkbox_toggled(devID, chNo, color)
        }
        else{
            // Python
            FrontToBackConnector.output_checkbox_toggled(devID, chNo)
        }
    }




    function findDeviceIndexInScopeList(deviceId){
        for(let i = 0; i < deviceListModel.count; i++){
            if(compareDevices(deviceListModel.get(i).DevID, deviceId)){
                return i
            }
        }
    }

    function findChannelIndexInChList(chNo, chList){
        for(let i = 0; i < chList.count; i++){
            if(chList.get(i).No === chNo){
                return i
            }
        }
    }

    Connections {
        target: FrontToBackConnector

        //! This function is called when a new device is plugged in on the USB port.
        function onAddToDeviceList(devID, chList) {
            if(devID["DevType"] === deviceType){
                let listEntry = {"DevID": devID, "ChList": chList, "Selected": "false"}
                for(let i = 0; i < chList.length; i++){
                    listEntry["ChList"][i]["Selected"] = "false"

                    listEntry["ChList"][i]["ColorName"] = cssColors[colorIndex]
                    colorIndex++
                    if(colorIndex >= cssColors.length){
                        colorIndex = 0
                    }
                }
                deviceListModel.append(listEntry)
            }
        }
        //! This function is called when a device is removed from the USB port.
        function onRemoveFromDeviceList(devID, isSelectedDevice) {
            if(devID["DevType"] === deviceType){
                let listIndex = deviceList.findDeviceIndexInScopeList(devID)
                if(isSelectedDevice){
                    if(deviceType === "Osc"){
                        oscilloscopeLoader.active = false
                        oscilloscopeChannelLoader.active = false
                    }
                    else{
                        signalGenLoader.active = false
                        signalGenChannelLoader.active = false
                    }
                    selectedItem = -1
                    selectedChannel = {"DevIndex": -1, "ChIndex": 0}
                }
                deviceListModel.remove(listIndex, 1)
            }
        }
        //! Add a Channel (for the math-osc).
        function onAddChannelToDevice(devID, chID) {
            if(devID["DevType"] === deviceType){
                let listIndex = deviceList.findDeviceIndexInScopeList(devID)

                let channelInfo = chID
                channelInfo["Selected"] = "false"
                channelInfo["ColorName"] = cssColors[colorIndex]
                colorIndex++
                if(colorIndex >= cssColors.length){
                    colorIndex = 0
                }

                deviceListModel.get(listIndex)["ChList"].append(channelInfo)
            }

        }
        //! Remove a Channel (for the math-osc).
        function onRemoveChannelFromDevice(devID, chID) {

            if(devID["DevType"] === deviceType){
                let listIndex = deviceList.findDeviceIndexInScopeList(devID)
                let channelList = deviceListModel.get(listIndex)["ChList"]
                let channelIndex = findChannelIndexInChList(chID["No"], channelList)

                deviceListModel.get(listIndex)["ChList"].remove(channelIndex, 1)
            }

        }
        //! This function is called when a new device is selected.
        function onSelectedDeviceUpdated(devID){
            if(devID["DevType"] === deviceType){
                let index = findDeviceIndexInScopeList(devID)

                if(selectedItem >= 0){
                    deviceListModel.setProperty(selectedItem, "Selected", "false")
                }
                deviceListModel.setProperty(index, "Selected", "true")
                selectedItem = index
                deviceList.newSelectedItem(devID)

                if(channelFromWrongDeviceSelected){
                    channelFromWrongDeviceSelected = false
                    channelSelected(index, wrongSelectedChannelIndex)
                }
                else {
                    channelSelected(index, 0)
                }
            }
        }
        //! This function is called when a new channel is selected.
        function onSelectedChannelUpdated(devID, chNo){
            if(devID["DevType"] === deviceType){
                let device_index = findDeviceIndexInScopeList(devID)
                if(selectedChannel["DevIndex"] >= 0){
                    var oldItem = deviceListModel.get(selectedChannel["DevIndex"])
                    var oldChildList = oldItem.ChList
                    oldChildList.setProperty(selectedChannel["ChIndex"], "Selected", "false")
                }
                let item = deviceListModel.get(device_index)
                let chList =  item.ChList
                let channel_index = findChannelIndexInChList(chNo, chList)
                chList.setProperty(channel_index, "Selected", "true")

                selectedChannel["DevIndex"] = device_index
                selectedChannel["ChIndex"] = channel_index

                newSelectedChannel(chNo)
            }
        }
    }

    property int colorIndex: 0
    property var cssColors: [
      "#1f77b4",
      "#aec7e8",
      "#ff7f0e",
      "#ffbb78",
      "#2ca02c",
      "#98df8a",
      "#d62728",
      "#ff9896",
      "#9467bd",
      "#c5b0d5",
      "#8c564b",
      "#c49c94",
      "#e377c2",
      "#f7b6d2",
      "#7f7f7f",
      "#c7c7c7",
      "#bcbd22",
      "#dbdb8d",
      "#17becf",
      "#9edae5"
    ];
}
