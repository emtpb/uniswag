import QtQuick 2.3
import QtQuick.Controls 2.4
import QtQml.Models 2.1
import QtQuick.Layouts 1.4

import "."

RowLayout{
    // https://doc.qt.io/qt-5/qtquickcontrols2-customize.html#customizing-slider
    property string triggerMode: "triangle"
    property real triggerHysteresisInPercent: 0.0
    property real oldTriggerHysteresisInPercent: 0.0
    property real positionInPercentOfAxisLength: 1
    property real positionInPercent: 1
    property real cappedPositionInPercentOfAxisLength: 1
    property string misc_path: "misc/"
    property bool sliderReleased: false

    signal changeSymbolToRisingEdge()
    signal changeSymbolToFallingEdge()
    signal changeSymbolToTriangle()
    signal changeSymbolToInWindow()
    signal changeSymbolToOutWindow()
    signal changeSliderPosition(real position)
    signal changeHysteresisSliderSizeInPercent(real value)
    signal sliderPositionChanged(real position)

    Slider {
        id: control
        from: 0
        to: 100
        value: 25
        orientation: Qt.Vertical
        live: false
        Layout.fillHeight: true

        background: Rectangle {
            x: control.leftPadding
            y: control.topPadding
            width:  4
            height: control.availableHeight
            radius: 2
            color: darkModeEnabled? "lightgrey" : "darkgrey"
        }

        handle:
            Rectangle{
            id:rect1
            x: control.leftPadding + 2 - width / 2
            y: control.topPadding + control.visualPosition * (control.availableHeight - height)
            implicitWidth: 10
            implicitHeight: (triggerMode === "triangle") ? 20 : control.availableHeight * triggerHysteresisInPercent
            color: (triggerMode === "triangle") ? "transparent" : control.pressed ? colorPalette.highlight : colorPalette.text

            // rising edge
            Rectangle{
                anchors.bottom: rect1.top
                anchors.left: rect1.left
                width: 20
                height: 10
                color: control.pressed ? colorPalette.highlight : colorPalette.text
                visible: (triggerMode === "rising edge") ? ((positionInPercentOfAxisLength <= 1)? true: false): false
            }
            Rectangle{
                anchors.top: rect1.bottom
                anchors.right: rect1.right
                width: 20
                height: 10
                color: control.pressed ? colorPalette.highlight : colorPalette.text
                visible: (triggerMode === "rising edge") ? ((positionInPercentOfAxisLength - triggerHysteresisInPercent > 0)? true: false): false
            }

            // falling edge
            Rectangle{
                anchors.bottom: rect1.top
                anchors.right: rect1.right
                width: 20
                height: 10
                color: control.pressed ? colorPalette.highlight : colorPalette.text
                visible: triggerMode === "falling edge" ? ((positionInPercentOfAxisLength <= 1)? true: false): false
            }
            Rectangle{
                anchors.top: rect1.bottom
                anchors.left: rect1.left
                width: 20
                height: 10
                color: control.pressed ? colorPalette.highlight : colorPalette.text
                visible: (triggerMode === "falling edge") ? ((positionInPercentOfAxisLength - triggerHysteresisInPercent > 0)? true: false) : false
            }

            // Triangle
            ColorImage {
                sourceSize.width: 20
                sourceSize.height: 20
                source: misc_path + "triangle.png"
                color: control.pressed ? colorPalette.highlight : colorPalette.text
                visible: (triggerMode === "triangle") ? true: false
            }


            // In- or Outwindow
            ColorImage {
                anchors.bottom: rect1.top
                anchors.horizontalCenter: rect1.horizontalCenter
                sourceSize.width: 20
                sourceSize.height: 20
                source: misc_path + "triangle.png"
                color: control.pressed ? colorPalette.highlight : colorPalette.text
                visible: (triggerMode === "out window" || triggerMode === "in window") ? true: false
                rotation: (triggerMode === "out window")? -90: 90
            }
            ColorImage {
                anchors.top: rect1.bottom
                anchors.horizontalCenter: rect1.horizontalCenter
                sourceSize.width: 20
                sourceSize.height: 20
                source: misc_path + "triangle.png"
                color: control.pressed ? colorPalette.highlight : colorPalette.text
                visible: (triggerMode === "out window" || triggerMode === "in window") ? true: false
                rotation: (triggerMode === "out window")? 90: -90
            }

        }

        onPressedChanged: {
            if(sliderReleased){
                let positionInVolt = position * (rawAxisY.max - rawAxisY.min) + rawAxisY.min
                let triggerHysteresisSize = (rawAxisY.max - rawAxisY.min) * triggerHysteresisInPercent
                sliderPositionChanged((positionInVolt + (1-position) * triggerHysteresisSize).toFixed(2))
                sliderReleased = false
            }
            else{
                sliderReleased = true
            }
        }
    }

    onChangeSymbolToRisingEdge: {
        triggerMode = "rising edge"
    }
    onChangeSymbolToFallingEdge: {
        triggerMode = "falling edge"
    }
    onChangeSymbolToTriangle: {
        triggerMode = "triangle"
    }
    onChangeSymbolToInWindow: {
        triggerMode = "in window"
    }
    onChangeSymbolToOutWindow: {
        triggerMode = "out window"
    }
    onChangeSliderPosition: function (position){
        positionInPercent = position
        if(rawAxisY.min !== rawAxisY.max){
             positionInPercentOfAxisLength = ((position - rawAxisY.min) / (rawAxisY.max - rawAxisY.min)).toFixed(2)
        }
        else {
            positionInPercentOfAxisLength = position
        }


        triggerHysteresisInPercent = oldTriggerHysteresisInPercent

        if(positionInPercentOfAxisLength > 1) {
            cappedPositionInPercentOfAxisLength = 1
        }
        else if(positionInPercentOfAxisLength < 0){
            cappedPositionInPercentOfAxisLength = 0
        }
        else {
            cappedPositionInPercentOfAxisLength = positionInPercentOfAxisLength
        }

        if(triggerHysteresisInPercent > cappedPositionInPercentOfAxisLength){
            triggerHysteresisInPercent  = cappedPositionInPercentOfAxisLength
        }
        else if(positionInPercentOfAxisLength > 1){
            if(triggerHysteresisInPercent - (positionInPercentOfAxisLength - 1) > 0){
                triggerHysteresisInPercent = triggerHysteresisInPercent - (positionInPercentOfAxisLength - 1)
            }
            else {
                triggerHysteresisInPercent = 0
            }
        }

        let correctedSliderPosition = Math.round(((triggerHysteresisInPercent - cappedPositionInPercentOfAxisLength)/(triggerHysteresisInPercent - 1)) * 100)

        control.value = correctedSliderPosition
    }

    onChangeHysteresisSliderSizeInPercent: function(value){
        if(value > 1){
            value = 1
        }
        else if(value < 0){
            value = 0
        }
        if(value > positionInPercentOfAxisLength){
            triggerHysteresisInPercent  = cappedPositionInPercentOfAxisLength
        }
        else if(positionInPercentOfAxisLength > 1){
            if(triggerHysteresisInPercent - (positionInPercentOfAxisLength - 1) > 0){
                triggerHysteresisInPercent = triggerHysteresisInPercent - (positionInPercentOfAxisLength - 1)
            }
            else {
                triggerHysteresisInPercent = 0
            }
        }
        else {
            triggerHysteresisInPercent = value
        }
        oldTriggerHysteresisInPercent = value

        changeSliderPosition(positionInPercent)
    }
}


