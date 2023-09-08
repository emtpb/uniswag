import QtQuick


State {
    property var deviceTab

    property real latestPercentualHysteresis: 0
    property real latestTriggerLevel: 0
    property real latestRange: 0

    function isSelectedDevice(deviceId, chNo = -1) {
        if (deviceTab.compareDevices(deviceId, deviceTab.selectedDevice) && (chNo === -1 || chNo === deviceTab.selectedChannelNum)) {
            return true
        } else {
            return false
        }
    }

    function triggerSliderIconUpdate(value = "") {
        switch (value) {
            case "rising edge":
                deviceTab.risingEdgeIcon()
                break;
            case "falling edge":
                deviceTab.fallingEdgeIcon()
                break;
            case "in window":
                deviceTab.inWindowIcon()
                break;
            case "out window":
                deviceTab.outWindowIcon()
                break;
            default:
                deviceTab.triangleIcon()
        }
    }

    function triggerSliderPositionUpdate(triggerLevel = latestTriggerLevel) {
        if (Array.isArray(triggerLevel)) {
            triggerLevel = Math.max.apply(Math, triggerLevel)
        }
        latestTriggerLevel = triggerLevel

        deviceTab.triggerIconPosition(triggerLevel)
    }

    function triggerSliderHysteresisUpdate(percentualHysteresis = latestPercentualHysteresis) {
        latestPercentualHysteresis = percentualHysteresis

        if (deviceTab.chart.axes[3].max !== deviceTab.chart.axes[3].min) {
            let visibleAreaOfRangeInPercent = (deviceTab.chart.axes[3].max - deviceTab.chart.axes[3].min) / (parseFloat(latestRange) * 2)
            deviceTab.changeHysteresisSliderSizeInPercent(percentualHysteresis/visibleAreaOfRangeInPercent)
        }
        else {
            deviceTab.changeHysteresisSliderSizeInPercent(percentualHysteresis)
        }
    }

    function triggerSliderRangeUpdate(value) {
        latestRange = value
    }

    function updateBinaryButton(button, booleanValue, trueText, falseText) {
        if (booleanValue === true) {
            button.buttonText = trueText
        }
        else {
            button.buttonText = falseText
        }
    }

    function updateCheckbox(checkbox, isActive, activeText, inactiveText) {
        if (isActive === true) {
            checkbox.box.checkState = Qt.Checked
            checkbox.checkboxText = activeText
        }
        else {
            checkbox.box.checkState = Qt.Unchecked
            checkbox.checkboxText = inactiveText
        }
    }

    function updateComboboxSelection(combobox, value) {
        let modelIndex = deviceTab.findIndexOfModel(combobox.list, value)
        if (modelIndex !== -1) {
            combobox.listIndex = modelIndex
        }
    }

    function updateComboboxList(combobox, value) {
        combobox.list = value
    }

    function updateTextfield(textfield, value) {
        textfield.textInput.clear()
        textfield.textfieldPlaceholder = value
    }

    function updateComboTextfield(comboTextfield, value) {
        comboTextfield.textBox.editText = value
    }

    function appendPrefixedUnit(value, decimalPlaces, listOfIncreasingUnits) {
        let index = 0
        let multiplier = 1000
        for (let i = 0; i < listOfIncreasingUnits.length; i++){
            if (value / multiplier >= 1) {
                index++
                multiplier *= 1000
            }
        }
        multiplier /= 1000
        value /= multiplier
        value = value.toFixed(decimalPlaces)
        return value + " " + listOfIncreasingUnits[index]
    }

    function detachPrefixedUnit(value, listOfIncreasingUnits) {
        for (let i = listOfIncreasingUnits.length - 1; i >= 0; i--){
            if(value.includes(listOfIncreasingUnits[i])){
                value = value.replace(" " + listOfIncreasingUnits[i], "")
                value = parseFloat(value) * 1000 ** i
                break
            }
        }

        return value
    }

    function listToString(list) {
        if (list.length < 1) {
            return ""
        }
        let value = list[0].toString()
        for(let i = 1; i < list.length; i++){
            value += ", " + list[i].toString()
        }
        return value
    }

}
