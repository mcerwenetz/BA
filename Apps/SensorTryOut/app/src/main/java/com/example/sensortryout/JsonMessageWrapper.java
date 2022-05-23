package com.example.sensortryout;

import org.json.JSONException;
import org.json.JSONObject;

public class JsonMessageWrapper {

    private JSONObject protocol;
    private MessageTypes messageTypes;

    public JsonMessageWrapper(JSONObject protocol){
        this.protocol = protocol;
        try {
            this.messageTypes = new MessageTypes();
        } catch (JSONException e) {
            e.printStackTrace();
        }
    }

    public static JSONObject get_protocol_request() throws JSONException {
        JSONObject jo = new JSONObject();
        jo.put("type", "protocol_response");
        return  jo;
    }

    public JSONObject get_update_request(String sensorType, String sensorValue) throws JSONException {
        JSONObject jo = this.protocol.getJSONObject(messageTypes.UPDATE_REQUEST);
        jo.put("sensor_type",sensorType);
        jo.put("sensor_value", sensorValue);
        return jo;
    }

    public JSONObject get_rpc_response(String command, String value) throws JSONException {
        JSONObject jo = this.protocol.getJSONObject(messageTypes.RPC_RESPONSE);
        jo.put("command",command);
        jo.put("value", value);
        return jo;
    }

    public class MessageTypes{

        public final String UPDATE_REQUEST = getOuter().protocol.getJSONObject("update_request").getString("type");
        public final String SENSOR_REQUEST = getOuter().protocol.getJSONObject("sensor_request").getString("type");
        public String SENSOR_RESPONSE = getOuter().protocol.getJSONObject("sensor_response").getString("type");
        public String RPC_REQUEST = getOuter().protocol.getJSONObject("rpc_request").getString("type");
        public String RPC_RESPONSE= getOuter().protocol.getJSONObject("rpc_response").getString("type");
        public String PROTOCOL_REQUEST= getOuter().protocol.getJSONObject("protocol_request").getString("type");
        public String PROTOCOL_RESPONSE= getOuter().protocol.getJSONObject("protocol_response").getString("type");


        public MessageTypes() throws JSONException {
        }

        private JsonMessageWrapper getOuter() {
            return JsonMessageWrapper.this;
        }
    };

}
