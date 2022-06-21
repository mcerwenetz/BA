package com.example.smartbit.SensorEventListener;

public class SmartBitEventListenerContainer {
    private AccellerometerEventListener accellerometerEventListener;
    private ProximityEventListener proximityEventListener;
    private GyroSensorEventListener gyroSensorEventListener;

    public SmartBitEventListenerContainer(AccellerometerEventListener accellerometerEventListener, GyroSensorEventListener gyroSensorEventListener, ProximityEventListener proximityEventListener) {
        this.accellerometerEventListener = accellerometerEventListener;
        this.proximityEventListener = proximityEventListener;
        this.gyroSensorEventListener = gyroSensorEventListener;
    }


    public AccellerometerEventListener getAccellerometerEventListener() {
        return accellerometerEventListener;
    }

    public GyroSensorEventListener getGyroSensorEventListener() {
        return gyroSensorEventListener;
    }

    public ProximityEventListener getProximityEventListener() {
        return proximityEventListener;
    }



}
