package com.example.sensortryout;

import android.app.Service;
import android.content.Intent;
import android.os.Binder;
import android.os.IBinder;
import android.util.Log;

import org.eclipse.paho.client.mqttv3.MqttConnectOptions;
import org.json.JSONException;
import org.json.JSONObject;

import java.util.ArrayList;
import java.util.List;
import java.util.Locale;
import java.util.Objects;
import java.util.concurrent.atomic.AtomicBoolean;


/**
 * Die Hauptklasse für jegliche Kommunikation zwischen Teilnehmern und Hosts. Verwendet die
 * {@link MqttMessaging} Klasse.
 */
public class MQTTService extends Service {
    final static String TAG = MQTTService.class.getCanonicalName();
    // for LocalService getInstance
    final public static String ACTION_START = "start"; // connect
    final public static String ACTION_STOP = "stop"; // disconnect
    // for LocalService Messaging
    final public static String ACTION_PRESS = "press";
    final public static String PROTOCOL = "tcp";
//    final public static String PROTOCOL = "ssl";
//        final public static String PROTOCOL = "mqtts";
    final public static String URL = "192.168.178.89";
    final public static int PORT = 1883;
    final public static String CONNECTION_URL = String.format(Locale.GERMAN,
            "%s://%s:%d", PROTOCOL, URL, PORT);
    final public static String USER = "";
//    final public static String USER = "22thesis01";
    final public static String PASSWORT = "";
//    final public static String PASSWORT = "n4xdnp36";
    private static final String TOPIC = "test";

    private MqttMessaging mqttMessaging;
    private final ArrayList<String> topicList = new ArrayList<>();


    final private MqttMessaging.FailureListener failureListener =
            new MqttMessaging.FailureListener() {
        @Override
        public void onConnectionError(Throwable throwable) {
            Log.e(TAG,"ConnectionError: " + throwable.getMessage());
        }

        @Override
        public void onMessageError(Throwable throwable, String msg) {
            Log.e(TAG,"MessageError: " + throwable.getMessage());
        }

        @Override
        public void onSubscriptionError(Throwable throwable, String topic) {
            Log.e(TAG,"SubscriptionError:" + throwable.getMessage());
        }
    };

    final private MqttMessaging.ConnectionListener connectionListener = new MqttMessaging.
            ConnectionListener() {
        @Override
        public void onConnect() {
            Log.v(TAG,"connected");

        }

        @Override
        public void onDisconnect() {
            Log.v(TAG,"disconnected");
        }
    };
    private AtomicBoolean keepSending;

    public void send(JSONObject jo){
        mqttMessaging.send(TOPIC, jo.toString());
        Log.v(TAG, jo.toString());
    }

    @Override
    public void onCreate() {
        Log.v(TAG, "onCreate");
        super.onCreate();
    }

    @Override
    public void onDestroy() {
        Log.v(TAG, "onDestroy");
        disconnect();
        super.onDestroy();
    }

    @Override
    public int onStartCommand(Intent intent, int flags, int startId) {
        Log.v(TAG, "onStartCommand");
        String action;
        if (intent != null) {
            action = intent.getAction();
        } else {
            //initial starten
            Log.w(TAG, "upps, restart");
            action = ACTION_START;
        }
        if (action == null) {
            Log.w(TAG, "  action=null, nothing further to do");
            return START_STICKY;
        }
        switch (action) {
            case ACTION_START:
                Log.v(TAG, "onStartCommand: starting MQTT");

                connect();
                // whatever else needs to be done on start may be done  here
                return START_STICKY;
            case ACTION_STOP:
                Log.v(TAG, "onStartCommand: stopping MQTT");

                disconnect();
                // whatever else needs to be done on stop may be done  here
                return START_NOT_STICKY;
            default:
                Log.w(TAG, "onStartCommand: unkown action=" + action);
                return START_NOT_STICKY;
        }
    }




    private void addTopic(String topic) {
        if (this.topicList.contains(topic))
            return;
        this.topicList.add(topic);
        mqttMessaging.subscribe(topic);
    }

    private void removeTopic(String topic) {
        this.topicList.remove(topic);
        mqttMessaging.unsubscribe(topic);
    }


    //Send and Receive
    final private MqttMessaging.MessageListener messageListener = (topic, stringMsg) -> {
    };

    //Connect and Disconnect
    private void connect() {
        Log.v(TAG, "connect");
        if (mqttMessaging != null) {
            disconnect();
            Log.w(TAG, "reconnect");
        }
        mqttMessaging = new MqttMessaging(failureListener, messageListener, connectionListener);
        Log.v(TAG, "connectionURL=" + CONNECTION_URL);
        MqttConnectOptions options = MqttMessaging.getMqttConnectOptions();
//        options.setUserName(USER);
//        options.setPassword(PASSWORT.toCharArray());
        Log.v(TAG, String.format("username=%s, password=%s, ", USER, PASSWORT));

        mqttMessaging.connect(CONNECTION_URL, options); // secure via URL
        addTopic(this.TOPIC);

        Log.v(TAG, "connected");
    }

    private void disconnect() {
        try {
            Log.v(TAG, "disconnect");
            if (mqttMessaging != null) {
                for (String topic : this.topicList)
                    mqttMessaging.unsubscribe(topic);
                List<MqttMessaging.Pair<String, String>> pending = mqttMessaging.disconnect();
                if (!pending.isEmpty()) {
                    Log.w(TAG, "pending messages: " + pending.size());
                }
            }
            mqttMessaging = null;
        }
        catch (Exception e){
            e.printStackTrace();
        }
    }

    //BINDER

    final private IBinder localBinder = new LocalBinder();

    public void setKeepSending(AtomicBoolean keepSending) {
        this.keepSending=keepSending;
    }


    public class LocalBinder extends Binder {

        public MQTTService getMQTTService() {
            return MQTTService.this;
        }

    }

    @Override
    public IBinder onBind(Intent intent) {
        Log.v(TAG, "onBind");
        String action = intent.getAction();
        if (action != null && action.equals(MQTTService.ACTION_PRESS)) {
            Log.v(TAG, "onBind for Press");
            return localBinder;
            // } else if (action.equals(MQTTService.ACTION_LOG)) {
            //    Log.v(TAG, "onBind for Log");
            //    return messenger.getBinder();
            // we do not provide messaging in this small example
            // you might want to
        } else {
            Log.e(TAG, "onBind only defined for ACTION_PRESS"); // or ACTION_LOG ");
            Log.e(TAG, "       did you want to call startService? ");
            return null;
        }
    }
}
