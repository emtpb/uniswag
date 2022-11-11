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

import QtQuick 2.3
import QtQuick.Controls 2.4
import QtQml.Models 2.1
import QtQuick.Layouts 1.4

import "."

/*!
    \qmltype ApplicationWindow
    \brief The main window of the application.

    In this window the whole content of the program is displayed.
*/

ApplicationWindow {
    title: qsTr("MS-SWAG")
    visible: true
    visibility: "Maximized"
    width: 1400
    height: 700

    //! This property is true when the FFT-Chart is displayed
    property bool fftVisible: false

    ColumnLayout {
        anchors.fill: parent

        //! The menu bar at the top of the screen.
        Rectangle {
            height: 40
            MenuBar {
                //! The entries of the "File" menu.
                Menu {
                    title: qsTr("File")
                    MenuItem {
                        text: qsTr("Exit")
                        onTriggered: Qt.quit()
                    }
                }
                //! The entries of the "View" menu.
                Menu {
                    title: qsTr("View")
                    MenuItem {
                        text: qsTr("Show FFT")
                        onTriggered: {
                            if(fftVisible){
                                fftVisible = false
                            }
                            else{
                                fftVisible = true
                            }


                        }
                    }
                    MenuItem {
                        text: qsTr("Reset Zoom")
                        onTriggered: {
                            if(deviceTypeSelectionSwipeView.deviceIsOsc){
                                oscilloscopeView.zoomResetClicked()
                            }
                        }
                    }
                }
                //! The entries of the "Export" menu.
                Menu {
                    title: qsTr("Export")
                    MenuItem {
                        text: qsTr("As PNG")
                        onTriggered: {
                            if(deviceTypeSelectionSwipeView.deviceIsOsc){
                                oscilloscopeView.saveImage()
                            }
                            else {
                                signalGeneratorView.saveImage()
                            }

                        }
                    }
                    MenuItem {
                        text: qsTr("As CSV")
                        onTriggered: {
                            FrontToBackConnector.save_as_csv()
                        }
                    }
                }
                //! The entries of the "About" menu.
                Menu {
                    title: qsTr("About")
                    MenuItem {
                        text: qsTr("Info")
                        onTriggered: {
                            aboutPage.show()
                        }
                    }
                }
            }
        }

        //! The two buttons to switch between the interface for oscilloscopes and signal generators.
        TabBar {
            Layout.fillWidth: true
            id: deviceTypeSelectionTabButtons
            spacing: 10
            leftPadding: 10
            rightPadding: 10
            //! The "Oscilloscope" button.
            TabButton {
                height: 30
                Text {
                    anchors.fill: parent
                    text: qsTr("<b>Oscilloscopes</b>")
                    color: darkModeEnabled? colorPalette.text : colorPalette.base
                    horizontalAlignment: Text.AlignHCenter
                    verticalAlignment: Text.AlignVCenter
                    font.pointSize: 12
                }
                background: Rectangle {
                    radius: 20
                    color: deviceTypeSelectionTabButtons.currentIndex == 0 ? colorPalette.highlight : colorPalette.dark
                }
            }
            //! The "Signal Generators" button.
            TabButton {
                height: 30
                Text {
                    anchors.fill: parent
                    text: qsTr("<b>Signal Generators</b>")
                    color: darkModeEnabled? colorPalette.text : colorPalette.base
                    horizontalAlignment: Text.AlignHCenter
                    verticalAlignment: Text.AlignVCenter
                    font.pointSize: 12
                }
                background: Rectangle {
                    radius: 20
                    color: deviceTypeSelectionTabButtons.currentIndex == 1 ? colorPalette.highlight : colorPalette.dark
                }
            }

        }
        /*!
            \qmltype SwipeView
            \brief A wrapper containing the views for all devices.

            The view where the tabs for the different devices (oscilloscopes and signal generators) are located.
            Thereby only one view is displayed at a time.
        */
        SwipeView {
            id: deviceTypeSelectionSwipeView

            //! This variable can be used to detect whether the device displayed in the SwipeView is an oscilloscope or a signal generator
            property bool deviceIsOsc: true

            currentIndex: deviceTypeSelectionTabButtons.currentIndex
            Layout.fillHeight: true
            Layout.fillWidth: true
            //! Swiping across the screen allows switching between device types.
            interactive: false
            onCurrentIndexChanged: {
                deviceTypeSelectionTabButtons.currentIndex = deviceTypeSelectionSwipeView.currentIndex
                if(deviceTypeSelectionSwipeView.currentIndex === 0){
                    deviceIsOsc = true
                }
                else{
                    deviceIsOsc = false
                }
            }

            /*!
                \qmltype ScopeView
                \brief The main view containing all views for oscilloscopes.

                This view shows all the stuff that is displayed when the "Oscilloscopes" tab is clicked in the TapBar.
            */
            OscilloscopeView {
                id: oscilloscopeView
                color: colorPalette.window
                Layout.fillWidth: true
                Layout.fillHeight: true
            }
            /*!
                \qmltype SignalGeneratorView
                \brief The main view containing all views for signal generators.

                This view shows all the stuff that is displayed when the "Signal Generators" tab is clicked in the TapBar.
            */
            SignalGeneratorView {
                id: signalGeneratorView
                color: colorPalette.window
                Layout.fillWidth: true
                Layout.fillHeight: true
            }

        }
    }

    AboutPage{
        id: aboutPage
    }

    /*!
        This variable is set to "true" when the operating system is in dark mode.
        For this, a comparison is made whether the default text color is larger than the default background color
    */
    property bool darkModeEnabled: false
    SystemPalette { id: colorPalette; colorGroup: SystemPalette.Active }
    Component.onCompleted: {
        if(colorPalette.windowText > colorPalette.base){
            darkModeEnabled = true
        }
    }

}
