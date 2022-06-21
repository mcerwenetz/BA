package com.example.smartbit.SensorEventListener;

import android.hardware.Sensor;
import android.hardware.SensorEvent;
import android.hardware.SensorEventListener;

import com.example.smartbit.JsonMessageWrapper;
import com.example.smartbit.MQTTService;

public class SmartBitSensorEventListener implements SensorEventListener {


    protected JsonMessageWrapper jsonMessageWrapper;
    protected MQTTService mqttService;

    public SmartBitSensorEventListener(JsonMessageWrapper jsonMessageWrapper, MQTTService mqttService){
        this.jsonMessageWrapper = jsonMessageWrapper;
        this.mqttService = mqttService;
    }

    @Override
    public void onSensorChanged(SensorEvent sensorEvent) {

    }

    @Override
    public void onAccuracyChanged(Sensor sensor, int i) {

    }
}
