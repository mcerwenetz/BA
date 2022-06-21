package com.example.smartbit.SensorEventListener;

import android.hardware.Sensor;
import android.hardware.SensorEvent;
import android.hardware.SensorEventListener;
import android.util.Log;

import com.example.smartbit.JsonMessageWrapper;
import com.example.smartbit.MQTTService;

import org.json.JSONObject;

public class GyroSensorEventListener extends SmartBitSensorEventListener {

    final static String TAG = GyroSensorEventListener.class.getCanonicalName();


    public GyroSensorEventListener(JsonMessageWrapper jsonMessageWrapper, MQTTService mqttService) {
        super(jsonMessageWrapper, mqttService);
    }

    @Override
    public void onSensorChanged(SensorEvent sensorEvent) {
        JSONObject[] update_requests = new JSONObject[3];
        update_requests[0] = jsonMessageWrapper.get_update_request("gyro_x", String.valueOf(sensorEvent.values[0]));
        update_requests[1] = jsonMessageWrapper.get_update_request("gyro_y", String.valueOf(sensorEvent.values[0]));
        update_requests[2] = jsonMessageWrapper.get_update_request("gyro_z", String.valueOf(sensorEvent.values[0]));
//        Log.v(TAG, String.valueOf((sensorEvent.values[0])));
        if(mqttService != null){
            for (JSONObject update_request : update_requests){
                mqttService.send(update_request);
            }
        }

    }

    @Override
    public void onAccuracyChanged(Sensor sensor, int i) {

    }
}
