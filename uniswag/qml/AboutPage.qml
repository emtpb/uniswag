import QtQuick 2.4
import QtQuick.Layouts 2.4
import QtQuick.Window 2.4
import QtQuick.Controls 2.4
import QtWebEngine 1.0

ApplicationWindow {
    width: 500; height: 500
    title: "About"

    ColumnLayout {

        GridLayout {
            Layout.leftMargin: 10
            Layout.topMargin: 10
            columns:2
            columnSpacing: 50
            rowSpacing: 20

            Label {
                color: colorPalette.text
                Layout.fillWidth: true
                text: "Created by:"
            }
            Label{

            }

            Label {
                text: "Bruno Mecke"
            }
            ColumnLayout{
                Label {
                    text: "Paderborn University"
                }
                Label {
                    text: "bmecke@mail.upb.de"
                }
            }


            Label {
                text: "Eric Kondratenko"
            }
            ColumnLayout{
                Label {
                    text: "Paderborn University"
                }
                Label {
                    text: "erickon@mail.upb.de"
                }
            }
        }
    }
}
