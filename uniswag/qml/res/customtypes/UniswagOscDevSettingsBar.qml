import QtQuick
import QtQuick.Controls


ScrollView {
    id: oscSettingsBar

    signal reloadOscilloscopeSettings()

    property var backgroundColor: darkModeEnabled? palette.dark : palette.light
    property var functions: functionCollection

    property var oscTab: parent.mainRect
    ScrollBar.vertical.policy: ScrollBar.AlwaysOff

    Component.onCompleted: {
       updateDisplayedOscData()
    }

    function updateDisplayedOscData(){
        reloadOscilloscopeSettings()
        oscTab.reloadOscChannelSettings()
    }

    UniswagFunctions {
        id: functionCollection

        deviceTab: oscSettingsBar.oscTab
    }

}
