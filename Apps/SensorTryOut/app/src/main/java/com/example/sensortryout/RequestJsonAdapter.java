package com.example.sensortryout;

import org.json.JSONException;
import org.json.JSONObject;

public class RequestJsonAdapter {

    public static JSONObject get_update_request(String sensorType, String sensorValue) throws JSONException {
        JSONObject jo = new JSONObject();
        jo.put("type", "update_request");
        jo.put("sensor_type",sensorType);
        jo.put("sensor_value", sensorValue);
        return jo;
    }

    public static JSONObject get_rpc_response(String command, String value) throws JSONException {
        JSONObject jo = new JSONObject();
        jo.put("type", "rpc_response");
        jo.put("command",command);
        jo.put("value", value);
        return jo;
    }


}
