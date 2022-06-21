import java.io.File;
import java.io.FileNotFoundException;
import java.io.IOException;
import java.net.DatagramPacket;
import java.net.DatagramSocket;
import java.net.InetAddress;
import java.net.SocketException;
import java.net.UnknownHostException;
import java.nio.charset.StandardCharsets;
import java.util.Scanner;

import org.json.JSONObject;

public class Phone{
    private DatagramSocket socket;
    private final int SENDERPORT = 5006;
    private final int RECEIVERPORT = 5005;
    private JSONObject protocol;
    private final String IP = "127.0.0.1";

    public Phone(String path){
        loadProtocol(path);
    }

    private void loadProtocol(String path){
        File protocolFile = new File(path);
        Scanner myReader = null;
		try {
			myReader = new Scanner(protocolFile);
		} catch (FileNotFoundException e) {
			// TODO Auto-generated catch block
			e.printStackTrace();
		}
        String content = "";
        while(myReader.hasNextLine()){
            content = content += myReader.nextLine();
        }

        protocol = new JSONObject(content);
    }

    private String getRpcRequest(String command, String value){
    	String template = protocol.getJSONObject("messages").getJSONObject("rpc_request").toString();
    	JSONObject ret = new JSONObject(template);
    	ret.put("command",command);
    	ret.put("value", value);
    	return ret.toString();

    }

    private String getSensorRequest(String sensortype){
    	String template = protocol.getJSONObject("messages").getJSONObject("sensor_request").toString();
    	JSONObject ret = new JSONObject(template);
    	ret.put("sensor_type",sensortype);
    	return ret.toString();
    }

    private String send_and_receive(String message){
        
        byte[] response = new byte[256];
        try {
			socket = new DatagramSocket(RECEIVERPORT);
		} catch (SocketException e1) {
			// TODO Auto-generated catch block
			e1.printStackTrace();
		}
        
        DatagramPacket response_packet = new DatagramPacket(response, response.length);
        send(message);
        try {
			socket.receive(response_packet);
		} catch (IOException e) {
			// TODO Auto-generated catch block
			e.printStackTrace();
		}
        socket.close();        
        String response_str = new String(response, StandardCharsets.UTF_8);
		JSONObject jo = new JSONObject(response_str);
        return jo.getString("value");
        
        
    }

    private void send(String message){
        byte[] messageBytes = message.getBytes();
        DatagramSocket sock = null;
		try {
			sock = new DatagramSocket();
		} catch (SocketException e1) {
			// TODO Auto-generated catch block
			e1.printStackTrace();
		}
        InetAddress addr = null;
        try {
            addr = InetAddress.getByName(IP);
        } catch (UnknownHostException e) {
            // TODO Auto-generated catch block
            e.printStackTrace();
        }
        DatagramPacket packet = new DatagramPacket(messageBytes, messageBytes.length , addr, SENDERPORT);
        try {
            sock.send(packet);
        } catch (IOException e) {
            // TODO Auto-generated catch block
            e.printStackTrace();
        }
        sock.close();

    }
    
    
    public float get_prox() {
    	String request = getSensorRequest("prox");
    	String response = send_and_receive(request);
    	return Float.valueOf(response);
    }
    
    public void vibrate(int milis) {
    	String request = getRpcRequest("vibrate", String.valueOf(milis));
    	send(request);
    }
    
    public void buttonToggle() {
    	String request = getRpcRequest("button_toggle", "");
    	send(request);
    }
    
    public void writeText(String text) {
    	String request = getRpcRequest("write_text", text);
    	send(request);
    }

    


}