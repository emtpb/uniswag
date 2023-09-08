import QtQuick
import QtQuick.Controls


ScrollView {
    id: genSettingsBar

    signal reloadGeneratorSettings()

    property var backgroundColor: darkModeEnabled? palette.dark : palette.light
    property var functions: functionCollection

    property var genTab: parent.mainRect
    ScrollBar.vertical.policy: ScrollBar.AlwaysOff

    Component.onCompleted: {
       updateDisplayedGenData()
    }

    function updateDisplayedGenData(){
        reloadGeneratorSettings()
        genTab.reloadGenChannelSettings()
    }

    UniswagFunctions {
        id: functionCollection

        deviceTab: genSettingsBar.genTab
    }

}
