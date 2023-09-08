import QtQuick
import QtQuick.Controls


ScrollView {
    id: oscSettingsBar

    signal reloadOscChannelSettings()
    signal triggerSliderPositionChanged(real position)
    signal zoomed()

    property var backgroundColor: darkModeEnabled? palette.dark : palette.light
    property var functions: functionCollection

    property var oscTab: parent.mainRect
    ScrollBar.vertical.policy: ScrollBar.AlwaysOff

    Component.onCompleted: {
       updateDisplayedChannelData()
    }

    function updateDisplayedChannelData(){
        reloadOscChannelSettings()
        oscTab.reloadOscilloscopeSettings()
    }

    UniswagFunctions {
        id: functionCollection

        deviceTab: oscSettingsBar.oscTab
    }

}
