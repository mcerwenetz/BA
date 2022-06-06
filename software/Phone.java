import java.io.IOException;
import java.net.DatagramPacket;
import java.net.DatagramSocket;
import java.net.InetAddress;
import java.net.InetSocketAddress;
import java.net.Socket;
import java.net.SocketAddress;
import java.net.SocketException;
import java.net.UnknownHostException;
import java.util.Scanner;

import org.json.simple.JSONObject;





public class Phone{
    private DatagramSocket socket;
    private final int SENDERPORT = 5006;
    private final int RECEIVERPORT = 5005;
    private JSONObject protocol;

    public Phone(String path){
        try {
            socket = new DatagramSocket(RECEIVERPORT);
        } catch (SocketException e1) {
            // TODO Auto-generated catch block
            e1.printStackTrace();
        }

        loadProtocol(path);
    }

    private void loadProtocol(String path){
        File protocolFile = new FIle(path);
        Scanner myReader = new Scanner(protocolFile);
        String content;
        while(myReader.hasNextLine()){
            content = content += myReader.nextLine();
        }
        myReader.close();
        protocol = new JSONObject(content);
    }

    private String getRpcRequest(String command, String value){

    }

    private String getSensorRequest(String sensortype){

    }

    private String send_and_receive(String message){
        
        byte[] response = new byte[256];
        InetAddress addr = null;
        try {
            addr = InetAddress.getLocalHost();
        } catch (UnknownHostException e) {
            // TODO Auto-generated catch block
            e.printStackTrace();
        }
        DatagramPacket response_packet = new DatagramPacket(response, response.length)
        send(message);
        socket.receive(response_packet);
        JSONObject jo = new JSONObject();
        socket.close();
    }

    private void send(String message){
        byte[] messageBytes = message.getBytes();
        DatagramPacket packet = new DatagramPacket(messageBytes, messageBytes.length , addr, SENDERPORT);
        try {
            socket.send(packet);
        } catch (IOException e) {
            // TODO Auto-generated catch block
            e.printStackTrace();
        }

    }
    

    


}