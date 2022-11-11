import QtQuick 2.12
import QtQuick.Layouts 1.12
import QtQuick.Controls 2.12
import QtCharts 2.3

import "."

/*!
    \qmltype ColumnLayout
    \brief A layout containing the oscilloscope data chart and a "reset zoom" button.
*/

//! the chart containing the oscilloscope data
ChartView {
    id: fftChartView

    //! Indicates whether the chart has been zoomed. In this case, the axes are not refreshed.
    property bool zoomed: false

    signal zoomResetClicked()

    theme: darkModeEnabled? ChartView.ChartThemeDark: ChartView.ChartThemeLight
    antialiasing: true
    legend.visible: false

    ValueAxis{
        id: xAxis
    }
    ValueAxis{
        id: yAxis
    }

    MouseArea{
        visible: deviceTypeSelectionSwipeView.deviceIsOsc? true: false
        anchors.fill: parent
        hoverEnabled: true
        onDoubleClicked: {
            fftChartView.zoomReset()
            zoomed = false
            FrontToBackConnector.fft_chart_axes_updates(!zoomed)
        }
        onWheel: function (wheel){
            let scaleIn = 1.2
            let scaleOut = 0.8

            zoomed = true
            FrontToBackConnector.fft_chart_axes_updates(!zoomed)
            if (wheel.angleDelta.y > 0){
                fftChartView.scrollRight(mouseX-(width/2))
                fftChartView.scrollDown(mouseY-(height/2))
                fftChartView.zoom(scaleIn)
                fftChartView.scrollLeft((mouseX-(width)/2))
                fftChartView.scrollUp((mouseY-(height)/2))
            }
            else{
                fftChartView.scrollRight(mouseX-width/2)
                fftChartView.scrollDown(mouseY-height/2)
                fftChartView.zoom(scaleOut)
                fftChartView.scrollLeft(mouseX-width/2)
                fftChartView.scrollUp(mouseY-height/2)
            }
        }
    }

    onZoomResetClicked: function(){
        fftChartView.zoomReset()
        zoomed = false
        FrontToBackConnector.fft_chart_axes_updates(!zoomed)
    }


    Component.onCompleted: {
        var series =fftChartView.createSeries(ChartView.SeriesTypeLine, "line", xAxis, yAxis);
        FrontToBackConnector.init_fft_chart(series, xAxis, yAxis)
    }
}
