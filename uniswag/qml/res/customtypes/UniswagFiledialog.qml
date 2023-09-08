import QtQuick
import QtQuick.Dialogs

FileDialog {
    property var filterList: []
    signal fileSelect(fileName: var)

    nameFilters: filterList
    onAccepted: {
        fileSelect(selectedFile)
    }
}
