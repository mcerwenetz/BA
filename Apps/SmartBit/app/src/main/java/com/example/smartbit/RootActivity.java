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


import java.util.concurrent.atomic.AtomicBoolean;

public class RootActivity extends AppCompatActivity {

    final static String TAG = RootActivity.class.getCanonicalName();
    private MQTTService mqttService;
    private boolean mqttServiceBound;
    private Button action_led;
    private ImageView recording_led;
    private Button button_a;
    private Button button_b;
    private TextView tv_output_text;
    private boolean ButtonToggleBool = true;
    private SensorManager sensorManager;
    private AtomicBoolean keepSending = new AtomicBoolean(false);
    private AccellerometerEventListener accellerometerEventListener;
    private JsonMessageWrapper jsonMessageWrapper;
    private final ServiceConnection serviceConnection = new ServiceConnection() {
        @Override
        public void onServiceConnected(ComponentName name, IBinder service) {
            Log.v(TAG, "onServiceConnected");
            mqttService = ((MQTTService.LocalBinder) service).getMQTTService();
            mqttService.setKeepSending(keepSending);
            mqttService.setRootActivity(RootActivity.this);
            registerAccellEventListener();
        }

        @Override
        public void onServiceDisconnected(ComponentName name) {
            // unintentionally disconnected
            Log.v(TAG, "onServiceDisconnected");
            unbindMQTTService(); // cleanup
        }
    };

    private void registerAccellEventListener() {
        accellerometerEventListener = new AccellerometerEventListener(jsonMessageWrapper, mqttService);
        Sensor accellormeter = sensorManager.getDefaultSensor(Sensor.TYPE_ACCELEROMETER);
        sensorManager.registerListener(accellerometerEventListener, accellormeter, SensorManager.SENSOR_DELAY_NORMAL);
    }

    public void setTextView(String toSet) {
        if (this.tv_output_text != null) {
            this.tv_output_text.setText(toSet);
        }
    }

    public void setAction_led(String activated) {
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
        sensorManager = (SensorManager) getSystemService(Context.SENSOR_SERVICE);
//        List<Sensor> sensorList = sm.getSensorList(Sensor.TYPE_ALL);

        jsonMessageWrapper = new JsonMessageWrapper(this);

    }

    private void bindUI() {
        recording_led = findViewById(R.id.recoding_led);
        action_led = findViewById(R.id.action_led);
        tv_output_text = findViewById(R.id.tv);
        button_a = findViewById(R.id.button_a);
        button_b = findViewById(R.id.button_b);
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
        Sensor accellormeter = sensorManager.getDefaultSensor(Sensor.TYPE_ACCELEROMETER);
        sensorManager.registerListener(accellerometerEventListener, accellormeter, SensorManager.SENSOR_DELAY_NORMAL);
    }

    protected void onPause() {
        Log.v(TAG, "onPause");
        super.onPause();
        unbindMQTTService();
        sensorManager.unregisterListener(accellerometerEventListener);
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
        intent.setAction(MQTTService.ACTION_PRESS);
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
