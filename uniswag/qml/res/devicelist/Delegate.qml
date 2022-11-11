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
import QtQuick.Layouts 1.12
import QtQuick.Controls 2.12
import "."

/*!
    \qmltype ItemDelegate
    \brief The design of one list entry in the device list.

    This view describes the design of a single list entry. For the description of the texts the variables from the list model are used.
*/
ItemDelegate {
    id: delegate

    property int indexOfDelegate: index
    property bool viewExpanded: false
    property string misc_path: "../misc/"


    onPressAndHold: {
        deviceList.longClick(index)
    }

    contentItem: ColumnLayout {
        spacing: 10

        RowLayout {

            /*!
                \qmltype ColorImage
                \brief The arrow on the "expand button"

                The advantage of the ColorImage is that the color of the icon can be changed (for Darkmode).
            */
            ColorImage {
                id: expandButton
                sourceSize.width: 20
                sourceSize.height: 20
                source: misc_path + "right.png"
                color: colorPalette.text

                MouseArea {
                    anchors.fill: parent
                    onClicked: {
                        if(viewExpanded){
                            viewExpanded = false
                            expandButton.source = misc_path + "right.png"
                        }
                        else{
                            viewExpanded = true
                            expandButton.source = misc_path + "down.png"
                        }
                    }
                }
            }
            //! The device name and SerNo
            Label {
                text: '<b>' + DevID["Name"] + '</b>' + " " + DevID["SerNo"]
                wrapMode: Text.Wrap
                color: colorPalette.text
                Layout.fillWidth: true
                background: Rectangle {
                    anchors.fill: parent
                    color: darkModeEnabled? "lightgrey" : "darkgrey"
                    radius: 100
                    opacity: darkModeEnabled? 0.2 : 0.5
                    // Selected in Model
                    visible: (Selected === "true")
                }

                MouseArea {
                    anchors.fill: parent
                    hoverEnabled: true
                    onClicked: {
                        deviceList.itemSelected(indexOfDelegate)
                    }
                }
            }
            //! The ButtonGroup connects the checkboxes of the channels with the checkbox of the device
            ButtonGroup {
                id: deviceSelection
                exclusive: false
                //checkState: deviceCheckbox.checkState
            }
            //! The device checkbox
            CheckBox {
                id: deviceCheckbox
                // https://stackoverflow.com/questions/64794487/how-to-change-qml-checkbox-indicator-and-checkmark-color
                indicator: CheckboxIndicator{
                    id: deviceCheckboxIndicator

                }
                onClicked: {
                    deviceList.itemVisibilityToggled(index)
                }
            }
        }
        /*!
            \qmltype Repeater
            \brief Repeating the design of a single channel

            The repeater repeats for each channel the design described in it.
        */
        Repeater{
            id: channelCheckboxRepeater
            model: ChList
            delegate: RowLayout {
                Layout.alignment: Qt.AlignRight
                Layout.rightMargin: 25
                visible: viewExpanded == true

                //! The color of the channel
                Rectangle {
                    width: 40
                    height: channelNameLabel.height
                    color: qsTr(ColorName)
                    radius: 100
                    visible: deviceType === "Osc"? true: false
                }

                //! The name of the channel.
                Label {
                    id: channelNameLabel
                    text: qsTr(Name + " " + No)
                    wrapMode: Text.Wrap
                    color: colorPalette.text

                    background: Rectangle {
                        anchors.fill: parent
                        color: darkModeEnabled? "lightgrey" : "darkgrey"
                        radius: 100
                        opacity: darkModeEnabled? 0.2 : 0.5
                        visible: (Selected === "true")
                    }

                    MouseArea {
                        anchors.fill: parent
                        hoverEnabled: true
                        onClicked: {
                            deviceList.channelSelected(indexOfDelegate, index)
                        }
                    }
                }
                //! The "channel selected" checkbox.
                CheckBox {
                    id: channelCheckbox
                    ButtonGroup.group: deviceSelection
                    indicator: CheckboxIndicator{
                        id: channelCheckboxIndicator
                    }
                    onClicked: {
                        deviceList.channelVisibilityToggled(indexOfDelegate, index)
                    }
                }
            }
        }

        Connections {
            target: FrontToBackConnector
            // Called, when the enabled channels changing.
            function onEnabledChannelsUpdated(deviceId, enabledChannelNos) {
                let index = deviceList.findDeviceIndexInScopeList(deviceId)

                if(compareDevices(DevID, deviceId)){
                    // all channels enabled
                    if(enabledChannelNos.length === ChList.count){
                        deviceCheckboxIndicator.deviceIndicatorCheckstateChanged("Checked")
                    }
                    else if(enabledChannelNos.length > 0){
                        deviceCheckboxIndicator.deviceIndicatorCheckstateChanged("PartiallyChecked")
                    }
                    else {
                        deviceCheckboxIndicator.deviceIndicatorCheckstateChanged("Unchecked")
                    }
                    // clear channel
                    for(let i=0; i<ChList.count; i++){
                        channelCheckboxRepeater.itemAt(i).children[2].indicator.channelIndicatorCheckstateChanged("Unchecked")
                    }
                    // item with id channelCheckboxIndicator for ech channel
                    for(let i=0; i<enabledChannelNos.length; i++){
                        let chIndex = findChannelIndexInChList(enabledChannelNos[i], ChList)
                        channelCheckboxRepeater.itemAt(chIndex).children[2].indicator.channelIndicatorCheckstateChanged("Checked")
                    }
                }

            }

        }



    }
}
