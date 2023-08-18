import QtQuick 
import QtQuick.Controls.Material



Rectangle {
    id: loginPage

    signal loginSuccess(string username)

    width: 360
    height: 520
    color: "#f0f0f0"

    Text {
        id: loginTitle
        text: qsTr("Login")
        anchors.horizontalCenter: parent.horizontalCenter
        font.pointSize: 24
        font.bold: true
        padding: 20
    }

    TextField {
        id: usernameField
        width: parent.width - 40
        height: 40
        anchors.top: loginTitle.bottom
        anchors.topMargin: 20
        anchors.horizontalCenter: parent.horizontalCenter
        placeholderText: qsTr("Username")
    }

    TextField {
        id: passwordField
        width: parent.width - 40
        height: 40
        anchors.top: usernameField.bottom
        anchors.topMargin: 20
        anchors.horizontalCenter: parent.horizontalCenter
        placeholderText: qsTr("Password")
        echoMode: TextInput.Password
    }

    Button {
        id: loginButton
        text: qsTr("Log in")
        anchors.top: passwordField.bottom
        anchors.topMargin: 40
        anchors.horizontalCenter: parent.horizontalCenter
        onClicked: {
            // Add login function here
            loginPage.loginSuccess(usernameField.text)
            console.log("Login success")
        }
    }
}
