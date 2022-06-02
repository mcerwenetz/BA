package com.example.smartbit.SensorEventListener;

import android.hardware.SensorEvent;

import com.example.smartbit.JsonMessageWrapper;
import com.example.smartbit.MQTTService;

import org.json.JSONObject;

public class ProximityEventListener extends SmartBitSensorEventListener{
    public ProximityEventListener(JsonMessageWrapper jsonMessageWrapper, MQTTService mqttService) {
        super(jsonMessageWrapper, mqttService);
    }

    @Override
    public void onSensorChanged(SensorEvent sensorEvent) {
        JSONObject update_request = null;
        update_request = jsonMessageWrapper.get_update_request("prox", String.valueOf(sensorEvent.values[0]));
        if(mqttService != null){
            mqttService.send(update_request);
        }
    }
}
