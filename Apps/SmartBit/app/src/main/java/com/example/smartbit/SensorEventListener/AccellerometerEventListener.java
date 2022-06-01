package com.example.smartbit.SensorEventListener;

import android.hardware.Sensor;
import android.hardware.SensorEvent;
import android.hardware.SensorEventListener;
import android.util.Log;

import com.example.smartbit.JsonMessageWrapper;
import com.example.smartbit.MQTTService;

import org.json.JSONObject;



public class AccellerometerEventListener implements SensorEventListener {

    final static String TAG = AccellerometerEventListener.class.getCanonicalName();


    private JsonMessageWrapper jsonMessageWrapper;
    private MQTTService mqttService;

    public AccellerometerEventListener(JsonMessageWrapper jsonMessageWrapper, MQTTService mqttService){
        this.jsonMessageWrapper = jsonMessageWrapper;
        this.mqttService = mqttService;
    }

    public void onSensorChanged(SensorEvent event) {
//        Runnable r = () -> {
        float[] linear_acceleration = {0.0F, 0.0F, 0.0F};
        float[] gravity = {0.0F, 0.0F, 0.0F};

        final float alpha = (float) 0.8;

        // Isolate the force of gravity with the low-pass filter.
        gravity[0] = alpha * gravity[0] + (1 - alpha) * event.values[0];
        gravity[1] = alpha * gravity[1] + (1 - alpha) * event.values[1];
        gravity[2] = alpha * gravity[2] + (1 - alpha) * event.values[2];

        // Remove the gravity contribution with the high-pass filter.
        linear_acceleration[0] = event.values[0] - gravity[0];
        linear_acceleration[1] = event.values[1] - gravity[1];
        linear_acceleration[2] = event.values[2] - gravity[2];
        Log.v(TAG, String.valueOf(linear_acceleration[0]));

        JSONObject[] jos = new JSONObject[3];
        jos[0] = jsonMessageWrapper.get_update_request("accell_x", String.valueOf(linear_acceleration[0]));
        jos[1] = jsonMessageWrapper.get_update_request("accell_y", String.valueOf(linear_acceleration[0]));
        jos[2] = jsonMessageWrapper.get_update_request("accell_z", String.valueOf(linear_acceleration[0]));
        for (JSONObject jo : jos) {
            if (mqttService != null) {
                mqttService.send(jo);
            }
        }
    }

        @Override
    public void onAccuracyChanged(Sensor sensor, int i) {

    }
}
