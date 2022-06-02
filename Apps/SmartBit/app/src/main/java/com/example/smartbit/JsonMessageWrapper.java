package com.example.smartbit;

import android.content.Context;

import com.example.smartbit.R;

import org.json.JSONException;
import org.json.JSONObject;

import java.io.BufferedReader;
import java.io.IOException;
import java.io.InputStream;
import java.io.InputStreamReader;
import java.io.Reader;
import java.nio.charset.Charset;
import java.nio.charset.StandardCharsets;

public class JsonMessageWrapper {

    private Context context;
    private JSONObject protocol;
    private MessageTypes messageTypes;

    public JsonMessageWrapper(Context context){

        this.context = context.getApplicationContext();
        this.protocol = readProtocolFromResource(R.raw.protocol);
        try {
            this.messageTypes = new MessageTypes();
        } catch (JSONException e) {
            e.printStackTrace();
        }
    }

    public JSONObject readProtocolFromResource(int resource){
        String file_content_string = readStringFromResources(resource);
        JSONObject jo = null;
        try {
            jo = new JSONObject(file_content_string);
        } catch (JSONException e) {
            e.printStackTrace();
        }
        return jo;
    }

    public String readStringFromResources(int resource) {

        InputStream inputStream = context.getResources().openRawResource(R.raw.protocol);

        StringBuilder textBuilder = new StringBuilder();
        try (Reader reader = new BufferedReader(new InputStreamReader
                (inputStream, Charset.forName(StandardCharsets.UTF_8.name())))) {
            int c = 0;
            while ((c = reader.read()) != -1) {
                textBuilder.append((char) c);
            }
        } catch (IOException e) {
            e.printStackTrace();
        }
        return textBuilder.toString();
    }


    public JSONObject get_update_request(String sensorType, String sensorValue) {
        JSONObject  jo = null;
        try {
            String jos = this.protocol.getJSONObject("messages").getString(messageTypes.UPDATE_REQUEST);
            jo = new JSONObject(jos);
            jo.put("sensor_type",sensorType);
            jo.put("sensor_value", sensorValue);
        } catch (JSONException e) {
            e.printStackTrace();
        }
        return jo;
    }

    public JSONObject get_rpc_response(String command, String value) {
        JSONObject jo = null;
        try {
            jo = this.protocol.getJSONObject(messageTypes.RPC_RESPONSE);
            jo.put("command",command);
            jo.put("value", value);
        } catch (JSONException e) {
            e.printStackTrace();
        }
        return jo;
    }

    public class MessageTypes{


        public final String UPDATE_REQUEST = getOuter().protocol.getJSONObject("messages").getJSONObject("update_request").getString("type");
        public String RPC_RESPONSE= getOuter().protocol.getJSONObject("messages").getJSONObject("rpc_response").getString("type");

        public MessageTypes() throws JSONException {
        }

        private JsonMessageWrapper getOuter() {
            return JsonMessageWrapper.this;
        }
    };

}
