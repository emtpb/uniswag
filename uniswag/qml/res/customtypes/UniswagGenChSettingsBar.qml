import QtQuick
import QtQuick.Controls


ScrollView {
    id: genSettingsBar

    signal reloadGenChannelSettings()

    property var backgroundColor: darkModeEnabled? palette.dark : palette.light
    property var functions: functionCollection

    property var genTab: parent.mainRect
    ScrollBar.vertical.policy: ScrollBar.AlwaysOff

    Component.onCompleted: {
       updateDisplayedChannelData()
    }

    function updateDisplayedChannelData(){
        reloadGenChannelSettings()
        genTab.reloadGeneratorSettings()
    }

    UniswagFunctions {
        id: functionCollection

        deviceTab: genSettingsBar.genTab
    }

}
