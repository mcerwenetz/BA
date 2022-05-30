package com.example.smartbit;

import android.app.Activity;
import android.content.ComponentName;
import android.content.Context;
import android.content.Intent;
import android.content.ServiceConnection;
import android.graphics.Color;
import android.hardware.Sensor;
import android.hardware.SensorEvent;
import android.hardware.SensorEventListener;
import android.hardware.SensorManager;
import android.hardware.TriggerEvent;
import android.hardware.TriggerEventListener;
import android.os.Bundle;
import android.os.IBinder;
import android.util.Log;
import android.widget.Button;
import android.widget.CheckBox;
import android.widget.TextView;

import androidx.annotation.Nullable;

import org.json.JSONObject;

import java.util.concurrent.atomic.AtomicBoolean;

public class RootActivity extends Activity implements SensorEventListener {

    final static String TAG = RootActivity.class.getCanonicalName();
    private TriggerEventListener tel;
    private MQTTService mqttService;
    private boolean mqttServiceBound;
    private Button btn;
    private boolean ButtonToggleBool = true;
    private SensorManager sm;
    private Sensor acc;
    private TextView tv;
    private CheckBox cb;
    private AtomicBoolean keepSending = new AtomicBoolean(false);
    private JsonMessageWrapper jsonMessageWrapper;
    private final ServiceConnection serviceConnection = new ServiceConnection() {
        @Override
        public void onServiceConnected(ComponentName name, IBinder service) {
            Log.v(TAG, "onServiceConnected");
            mqttService = ((MQTTService.LocalBinder) service).getMQTTService();
            tel = new TriggerEventListener() {
                @Override
                public void onTrigger(TriggerEvent triggerEvent) {
                    Log.v("TEL", "Motion detected");
                }
            };
            sm.requestTriggerSensor(tel, acc);

            mqttService.setKeepSending(keepSending);
            mqttService.setRootActivity(RootActivity.this);
        }

        @Override
        public void onServiceDisconnected(ComponentName name) {
            // unintentionally disconnected
            Log.v(TAG, "onServiceDisconnected");
            unbindMQTTService(); // cleanup
        }
    };

    public void setTextView(String toSet) {
        if (this.tv != null) {
            this.tv.setText(toSet);
        }
    }

    public void setBtn(String activated) {
        runOnUiThread(
                () -> {
                    if (Boolean.valueOf(activated) == true) {
                        btn.setBackgroundColor(Color.GREEN);
                    } else {
                        btn.setBackgroundColor(Color.RED);
                    }
                });
    }

    public void setCheckBox(String value) {
        runOnUiThread(() ->
                this.cb.setPressed(Boolean.valueOf(value))
        );
    }

    @Override
    protected void onCreate(@Nullable Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.layout);
        btn = findViewById(R.id.button);
        tv = findViewById(R.id.tv);
        cb = findViewById(R.id.checkbox);
        sm = (SensorManager) getSystemService(Context.SENSOR_SERVICE);
//        List<Sensor> sensorList = sm.getSensorList(Sensor.TYPE_ALL);
        acc = sm.getDefaultSensor(Sensor.TYPE_ACCELEROMETER);
        sm.registerListener(this, acc, SensorManager.SENSOR_DELAY_NORMAL);
        jsonMessageWrapper = new JsonMessageWrapper(this);

    }


    public void toogleButton() {
        if (ButtonToggleBool == true) {
            btn.setBackgroundColor(Color.RED);
        } else {
            btn.setBackgroundColor(Color.GREEN);
        }
        ButtonToggleBool = !ButtonToggleBool;
    }

    @Override
    protected void onResume() {
        super.onResume();
        onStartService();
        bindMQTTService();
    }

    protected void onPause() {
        Log.v(TAG, "onPause");
        super.onPause();
        unbindMQTTService();
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

    @Override
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

        JSONObject[] jos = new JSONObject[3];
        jos[0] = jsonMessageWrapper.get_update_request("accell_x", String.valueOf(linear_acceleration[0]));
        jos[1] = jsonMessageWrapper.get_update_request("accell_y", String.valueOf(linear_acceleration[0]));
        jos[2] = jsonMessageWrapper.get_update_request("accell_z", String.valueOf(linear_acceleration[0]));
        for (JSONObject jo : jos) {
            if (mqttService != null) {
                mqttService.send(jo);
            }
        }
        //            for (float la : linear_acceleration) {
//                JSONObject jo = null;
//                try {
//                    jo = RequestJsonAdapter.get_update_request("accell_x", String.valueOf(la));
//                } catch (JSONException e) {
//                    e.printStackTrace();
//                }
//                mqttService.send(jo);
//            }
//        };
//        Thread t = new Thread(r);
//        t.start();
    }

    @Override
    public void onAccuracyChanged(Sensor sensor, int i) {

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
