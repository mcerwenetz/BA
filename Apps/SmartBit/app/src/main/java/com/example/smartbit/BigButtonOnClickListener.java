package com.example.smartbit;

import android.view.View;

import org.json.JSONObject;


public class BigButtonOnClickListener implements View.OnClickListener {

    private String command;

    public BigButtonOnClickListener(String command, String value, MQTTService mqttService, JsonMessageWrapper jsonMessageWrapper, Object buttonPressed) {
        this.command = command;
        this.value = value;
        this.mqttService = mqttService;
        this.jsonMessageWrapper = jsonMessageWrapper;
        this.buttonPressed = buttonPressed;
    }

    private String value;
    private MQTTService mqttService;
    private JsonMessageWrapper jsonMessageWrapper;
    private Object buttonPressed;

    @Override
    public void onClick(View view) {
        JSONObject rpc_answer = jsonMessageWrapper.get_rpc_response(command, String.format("%s", value));
        mqttService.sendRpcAnswer(rpc_answer);
        synchronized (buttonPressed){
            buttonPressed.notifyAll();
        }
    }
}
