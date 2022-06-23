package com.example.smartbit;

import android.content.ComponentName;
import android.content.Context;
import android.content.Intent;
import android.content.ServiceConnection;
import android.graphics.Color;
import android.hardware.Sensor;
import android.hardware.SensorManager;
import android.os.Bundle;
import android.os.IBinder;
import android.util.Log;
import android.widget.Button;
import android.widget.ImageView;
import android.widget.TextView;

import androidx.annotation.Nullable;
import androidx.appcompat.app.AppCompatActivity;

import com.example.smartbit.SensorEventListener.AccellerometerEventListener;
import com.example.smartbit.SensorEventListener.GyroSensorEventListener;
import com.example.smartbit.SensorEventListener.ProximityEventListener;
import com.example.smartbit.SensorEventListener.SmartBitEventListenerContainer;
import com.google.android.material.button.MaterialButton;


import java.util.concurrent.atomic.AtomicBoolean;

public class RootActivity extends AppCompatActivity {

    final static String TAG = RootActivity.class.getCanonicalName();
    private MQTTService mqttService;
    private boolean mqttServiceBound;
    private MaterialButton action_led;
    private ImageView recording_led;
    public Button button_a;
    public Button button_b;
    private TextView tv_output_text;
    private boolean ButtonToggleBool = true;
    private SensorManager sensorManager;
    private SmartBitEventListenerContainer smartBitEventListenerContainer;
    private AtomicBoolean keepSending = new AtomicBoolean(false);
    private JsonMessageWrapper jsonMessageWrapper;
    private final ServiceConnection serviceConnection = new ServiceConnection() {
        @Override
        public void onServiceConnected(ComponentName name, IBinder service) {
            Log.v(TAG, "onServiceConnected");
            mqttService = ((MQTTService.LocalBinder) service).getMQTTService();
            mqttService.setKeepSending(keepSending);
            mqttService.setRootActivity(RootActivity.this);
            createEventListeners();
            registerEventListeners();
        }

        @Override
        public void onServiceDisconnected(ComponentName name) {
            // unintentionally disconnected
            Log.v(TAG, "onServiceDisconnected");
            unbindMQTTService(); // cleanup
        }
    };


    private void registerEventListeners() {
        Sensor accellometer = sensorManager.getDefaultSensor(Sensor.TYPE_ACCELEROMETER);
        sensorManager.registerListener(this.smartBitEventListenerContainer.getAccellerometerEventListener(), accellometer, SensorManager.SENSOR_DELAY_NORMAL);

        Sensor gyro = sensorManager.getDefaultSensor(Sensor.TYPE_GYROSCOPE);
        sensorManager.registerListener(this.smartBitEventListenerContainer.getGyroSensorEventListener(), gyro, SensorManager.SENSOR_DELAY_NORMAL);

        Sensor proximitySensor = sensorManager.getDefaultSensor(Sensor.TYPE_PROXIMITY);
        sensorManager.registerListener(this.smartBitEventListenerContainer.getProximityEventListener(), proximitySensor, SensorManager.SENSOR_DELAY_NORMAL);

    }

    private void unregisterEventListeners(){
        sensorManager.unregisterListener(this.smartBitEventListenerContainer.getAccellerometerEventListener());
        sensorManager.unregisterListener(this.smartBitEventListenerContainer.getProximityEventListener());
        sensorManager.unregisterListener(this.smartBitEventListenerContainer.getGyroSensorEventListener());
    }

    public void setTextView(String toSet) {
        if (this.tv_output_text != null) {
            this.tv_output_text.setText(toSet);
        }
    }

    public void setActionLed(String activated) {
        runOnUiThread(
                () -> {
                    if (Boolean.valueOf(activated) == true) {
                        action_led.setBackgroundColor(Color.GREEN);
                    } else {
                        action_led.setBackgroundColor(Color.RED);
                    }
                });
    }

     @Override
    protected void onCreate(@Nullable Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.layout);
        bindUI();
        bindMQTTService();
        sensorManager = (SensorManager) getSystemService(Context.SENSOR_SERVICE);
//        List<Sensor> sensorList = sm.getSensorList(Sensor.TYPE_ALL);

        jsonMessageWrapper = new JsonMessageWrapper(this);
     }

    private void createEventListeners() {
        AccellerometerEventListener accellerometerEventListener = new AccellerometerEventListener(jsonMessageWrapper,mqttService);
        GyroSensorEventListener gyroSensorEventListener = new GyroSensorEventListener(jsonMessageWrapper,mqttService);
        ProximityEventListener proximityEventListener = new ProximityEventListener(jsonMessageWrapper,mqttService);
        this.smartBitEventListenerContainer = new SmartBitEventListenerContainer(accellerometerEventListener,gyroSensorEventListener,proximityEventListener);
    }

    private void bindUI() {
        recording_led = findViewById(R.id.recoding_led);
        action_led = findViewById(R.id.action_led);
        tv_output_text = findViewById(R.id.tv);
        button_a = findViewById(R.id.button_a);
        button_b = findViewById(R.id.button_b);
        action_led.setBackgroundColor(Color.GREEN);
        recording_led.setImageAlpha(50);
    }

    public void toggle_recording(){
        if (recording_led.getImageAlpha() < 52){
            recording_led.setImageAlpha(255);
        }else{
            recording_led.setImageAlpha(51);
        }
    }

    public void toogleButton() {
        if (ButtonToggleBool == true) {
            action_led.setBackgroundColor(Color.RED);
        } else {
            action_led.setBackgroundColor(Color.GREEN);
        }
        ButtonToggleBool = !ButtonToggleBool;
    }

    @Override
    protected void onResume() {
        super.onResume();
        onStartService();
        bindMQTTService();
        if(mqttService != null){
//            If not null service was already started and bound. No need for recreating Eventlisteners.
//            If mqtt service is null this would throw null exception because Eventlistener are not already bound
//            because mqtt service is not already bound.
            registerEventListeners();
        }
    }

    protected void onPause() {
        Log.v(TAG, "onPause");
        super.onPause();
        unbindMQTTService();
        unregisterEventListeners();
    }

    @Override
    protected void onStop() {
        Log.v(TAG, "onStop");
        super.onStop();
    }

    @Override
    protected void onDestroy() {
        Log.v(TAG, "onDestroy");
        super.onDestroy();
        unbindMQTTService();
        onStopService();
    }

    public void onStartService() {
        Log.v(TAG, "onStartService");
        Intent intent = new Intent(this, MQTTService.class);
        intent.setAction(MQTTService.ACTION_START);
        startService(intent);
    }

    public void onStopService() {
        Log.v(TAG, "onStopService");
        Intent intent = new Intent(this, MQTTService.class);
        intent.setAction(MQTTService.ACTION_STOP);
        startService(intent); // to stop
    }


    private void bindMQTTService() {
        Log.v(TAG, "bindMQTTService");
        Intent intent = new Intent(this, MQTTService.class);
        intent.setAction(MQTTService.ACTION_START);
        mqttServiceBound = bindService(intent, serviceConnection, Context.BIND_AUTO_CREATE);
        if (!mqttServiceBound) {
            Log.w(TAG, "could not try to bind service, will not be bound");
        }
    }

    private void unbindMQTTService() {
        Log.v(TAG, "unbindMQTTService");
        if (mqttServiceBound) {
            mqttServiceBound = false;
            unbindService(serviceConnection);
        }
    }
}
