import QtQuick 2.12
import QtQuick.Layouts 1.12
import QtQuick.Controls 2.12
import "."

Rectangle {
    signal deviceIndicatorCheckstateChanged(string checkstate)
    signal channelIndicatorCheckstateChanged(string checkstate)

    property int lastState: Qt.Unchecked

    id: checkboxIndicator
    implicitWidth: 20
    implicitHeight: 20

    x: parent.mirrored ? parent.leftPadding : parent.width - width - parent.rightPadding
    y: parent.topPadding + (parent.availableHeight - height) / 2

    // color as long as the mouse button is pressed on the checkbox
    color: parent.down ? parent.palette.light : parent.palette.base
    border.width: parent.visualFocus ? 2 : 1
    border.color: darkModeEnabled? "white" : "black"

    // checked
    ColorImage {
        id: colorImage
        x: (parent.width - width) / 2
        y: (parent.height - height) / 2
        sourceSize.width: 16
        sourceSize.height: 16
        color: darkModeEnabled? "white" : "black"
        source: misc_path + "tick.png"
        visible: false
    }
    // partially checked
    Rectangle {
        id: rect
        x: (parent.width - width) / 2
        y: (parent.height - height) / 2
        width: 16
        height: 3
        color: darkModeEnabled? "white" : "black"
        visible: false
    }

    onDeviceIndicatorCheckstateChanged: function(checkstate){
        if(checkstate === "Checked"){
            colorImage.visible = true
            rect.visible = false
        }
        else if(checkstate === "PartiallyChecked"){
            rect.visible = true
            colorImage.visible = false
        }
        else{
            rect.visible = false
            colorImage.visible = false

        }  
    }
    onChannelIndicatorCheckstateChanged: function(checkstate){
        if(checkstate === "Unchecked"){
            colorImage.visible = false
        }
        else{
            colorImage.visible = true
        }
    }
}
