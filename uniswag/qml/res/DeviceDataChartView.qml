import QtQuick 2.12
import QtQuick.Layouts 1.12
import QtQuick.Controls 2.12
import QtCharts 2.3

import "."

/*!
    \qmltype ColumnLayout
    \brief A layout containing the oscilloscope data chart.
*/
ChartView {
    id: scopeChartView
     property string deviceType: ""


    //! Indicates whether the chart has been zoomed. In this case, the axes are not refreshed.
    property bool zoomed: false 

    signal sliderPositionChanged(real position)
    signal zoomedWithMouse()

    signal zoomResetClicked()

    theme: darkModeEnabled? ChartView.ChartThemeDark: ChartView.ChartThemeLight
    antialiasing: true
    legend.visible: false


    // fake, only to allow the axes to be displayed in different units (s, ms, us, ns, ...)
    LineSeries {
            axisX: formatedAxisX
            axisY: formatedAxisY
        }
    ValueAxis{
        id: formatedAxisY
        labelFormat: "%2.2f V"
        tickAnchor: 0
        tickInterval: 100
        tickType: deviceType === "Osc"? ValueAxis.TicksDynamic: ValueAxis.TicksFixed
    }
    ValueAxis{
        id: formatedAxisX
        labelFormat: "%2.2f s"
        tickCount: 11
        tickType: ValueAxis.TicksFixed
    }



    //! The real x axis. This axis is not displayed in the chart.
    ValueAxis{
        id: rawAxisX
        visible: false

        onRangeChanged: function(){
            let units = ["s", "ms", "us", "ns"]


            let minimum = rawAxisX.min
            let maximum = rawAxisX.max
            let index = 0
            let value = maximum-minimum
            let multiplier = 1000
            for(let i=0; i<units.length; i++){
                if(value*multiplier < 1000){
                    index++
                    multiplier *=1000
                }
            }
            multiplier/=1000

            formatedAxisX.min = min*multiplier
            formatedAxisX.max = max*multiplier
            formatedAxisX.labelFormat = "%3.2f " + units[index]
        }


    }
    //! The real y axis. This axis is not displayed in the chart.
    ValueAxis{
        id: rawAxisY
        visible: false

        onRangeChanged: function(){
            let units = ["V", "mV"]


            let minimum = rawAxisY.min
            let maximum = rawAxisY.max
            let index = 0
            let value = maximum-minimum
            let multiplier = 1000

            for(let i=0; i<units.length; i++){
                if(value*multiplier < 1000){
                    index++
                    multiplier *=1000
                }
            }
            multiplier/=1000

            let tickInterval = (maximum*multiplier-minimum*multiplier)/6
            let roundFactor = 0.1
            for(let i=1; i<=1000; i*=10){
                if(tickInterval/i >= 1){
                    roundFactor = i
                }
            }
            tickInterval = Math.round(tickInterval/roundFactor)*roundFactor

            formatedAxisY.tickInterval =  Math.round(tickInterval/roundFactor)*roundFactor
            formatedAxisY.min = min*multiplier
            formatedAxisY.max = max*multiplier
            formatedAxisY.labelFormat = "%3.2f " + units[index]
            formatedAxisY.tickAnchor = Math.round((maximum-minimum)/2)
        }
    }

    //! Recognize zooming.
    MouseArea{
        visible: deviceTypeSelectionSwipeView.deviceIsOsc? true: false
        anchors.fill: parent
        hoverEnabled: true
        onDoubleClicked: {
            scopeChartView.zoomReset()
            zoomed = false
            FrontToBackConnector.norm_chart_axes_updates(!zoomed)
            zoomedWithMouse()
        }
        onWheel: function (wheel){
            let scaleIn = 1.2
            let scaleOut = 0.8

            zoomed = true
            FrontToBackConnector.norm_chart_axes_updates(!zoomed)
            if (wheel.angleDelta.y > 0){
                scopeChartView.scrollRight(mouseX-(width/2))
                scopeChartView.scrollDown(mouseY-(height/2))
                scopeChartView.zoom(scaleIn)
                scopeChartView.scrollLeft((mouseX-(width)/2))
                scopeChartView.scrollUp((mouseY-(height)/2))
            }
            else{
                scopeChartView.scrollRight(mouseX-width/2)
                scopeChartView.scrollDown(mouseY-height/2)
                scopeChartView.zoom(scaleOut)
                scopeChartView.scrollLeft(mouseX-width/2)
                scopeChartView.scrollUp(mouseY-height/2)
            }
            zoomedWithMouse()
        }
    }

    TriggerSlider {
        id: triggerSlider
        height: parent.height - 85
        x: 15
        y: 35

        visible: deviceType === "Osc"? true: false

        onSliderPositionChanged: function(position){
            scopeChartView.sliderPositionChanged(position)
        }
    }

    onZoomResetClicked: function(){
        scopeChartView.zoomReset()
        zoomed = false
        FrontToBackConnector.norm_chart_axes_updates(!zoomed)
    }


    Component.onCompleted: {
        var series = scopeChartView.createSeries(ChartView.SeriesTypeLine, "line", rawAxisX, rawAxisY);
        if(deviceType === "Osc"){
            FrontToBackConnector.init_norm_chart(series, rawAxisX, rawAxisY)
            FrontToBackConnector.start_chart_updates()
        }
        else if(deviceType == "Gen"){
            FrontToBackConnector.init_signal_preview_chart(series, rawAxisX, rawAxisY)
        }


    }
}
