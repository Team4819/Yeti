package yeti;

import java.io.BufferedReader;
import java.io.DataOutputStream;
import java.io.IOException;
import java.io.InputStreamReader;
import java.net.DatagramPacket;
import java.net.DatagramSocket;
import java.net.InetAddress;
import java.net.ServerSocket;
import java.net.Socket;
import java.net.SocketException;
import java.nio.ByteBuffer;
import java.nio.channels.DatagramChannel;
import java.nio.channels.Selector;
import java.nio.channels.ServerSocketChannel;
import java.nio.channels.SocketChannel;
import java.nio.charset.Charset;
import java.net.InetSocketAddress;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.TreeMap;
import java.util.function.Function;

import org.json.JSONArray;
import org.json.JSONException;
import org.json.JSONObject;

public class Messenger {
	
	private class Address{
		public String addr;
		public int udpPort;
		public int tcpPort;
		
		Address(String addr, int udp_port, int tcp_port){
			this.addr = addr;
			this.udpPort = udp_port;
			this.tcpPort = tcp_port;
		}
	}
	
	boolean running = false;
	
	int udpPort;
	int tcpPort;
	String address;
	
	String messengerId;
	
	TreeMap<String, Address> addressBook;
	HashMap<String, Function<JSONObject, JSONObject>> callbacks;
	
	DatagramSocket udpSock;
	
	Thread parentThread;
	Thread udpThread;
	Thread tcpThread;
	
	Messenger(String messengerId) throws IOException{
		this.messengerId = messengerId;
		addressBook = new TreeMap<String, Address>();
		callbacks  = new HashMap<String, Function<JSONObject, JSONObject>>();
		
		udpSock = new DatagramSocket();
		
		udpThread = new Thread(){public void run(){udpReceiveLoop();}};
		tcpThread = new Thread(){public void run(){tcpReceiveLoop();}};
		
		registerMessageType("address_resolution_request", this::onAddressResolutionRequest);
		
	}
	
	public void startServer(String addr, int udpPort, int tcpPort){
		parentThread = Thread.currentThread();
		
		this.udpPort=udpPort;
		this.tcpPort=tcpPort;
		this.address = addr;
		registerMessengerAddress(this.messengerId, addr, udpPort, tcpPort);
		
		running = true;
		udpThread.start();
		tcpThread.start();
		System.out.println("Started " + this.messengerId + " on " + addr + ", " + udpPort + ", " + tcpPort);
	}
	
	public void stopServer() throws InterruptedException{
		System.out.println("Stopping " + this.messengerId);
		running = false;
		
		if (udpThread.isAlive())
			udpThread.join();
		if (tcpThread.isAlive())
			tcpThread.join();
		System.out.println("Stopped " + this.messengerId);
	}
	
	private void udpReceiveLoop(){
		System.out.println("Starting udp loop for " + this.messengerId);
		
		try {
			DatagramChannel channel = DatagramChannel.open();
			channel.socket().bind(new InetSocketAddress(udpPort));
			channel.configureBlocking(false);
			ByteBuffer packet = ByteBuffer.allocate(1024);
			packet.clear();
			while (running && parentThread.isAlive()){
				if(channel.receive(packet) != null){
					String json_text = new String(packet.array(), "ASCII");
					JSONObject message = new JSONObject(json_text);
					String msgType = (String) message.get("msg_type");
					callbacks.get(msgType).apply(message.getJSONObject("data"));
					packet.clear();
				}
				Thread.sleep(10);
			}
			channel.close();
			System.out.println("Stopped udp loop for " + this.messengerId);
		} catch (IOException e) {
			// TODO Auto-generated catch block
			e.printStackTrace();
		} catch (InterruptedException e) {
			// TODO Auto-generated catch block
			e.printStackTrace();
		}
	}
	
	private void tcpReceiveLoop(){
		System.out.println("Starting tcp loop for " + this.messengerId);
		try {
			ServerSocketChannel channel = ServerSocketChannel.open();
			channel.socket().bind(new InetSocketAddress(tcpPort));
			channel.configureBlocking(false);
			
			ByteBuffer packet = ByteBuffer.allocate(1024);
			packet.clear();
			
			while (running && parentThread.isAlive()){
				SocketChannel socketChannel = channel.accept();
				
				if (socketChannel != null){
					socketChannel.configureBlocking(false);
					int msg_len = 0;
					int msg_len_len = 0;
					int bytes_read = 0;
					while (true){
						int res = socketChannel.read(packet);
						bytes_read += res;
						if (res == 0)
							Thread.sleep(10);
						else if (res <= 0)
							throw new IOException(); 
						String buf = new String(packet.array(), "utf-8");
						int ind = buf.indexOf("!");
						if (ind > 0){
							msg_len_len = ind;
							msg_len = Integer.parseInt(buf.substring(1, ind));
							break;
						}
					}
					while (bytes_read < msg_len + msg_len_len){
						int res = socketChannel.read(packet);
						if (res == 0)
							Thread.sleep(10);
						bytes_read += res;
					}
					String json_text = (new String(packet.array(), "utf-8")).substring(msg_len_len+1);
	
					JSONObject message = new JSONObject(json_text);
					String msgType = (String) message.get("msg_type");
					JSONObject response = callbacks.get(msgType).apply(message.getJSONObject("data"));
					byte[] responseData = response.toString().getBytes("utf-8");
					
					packet.clear();
					packet.put(("|" + responseData.length + "!").getBytes("utf-8"));
					packet.put(responseData);
					packet.flip();
					
					while (packet.hasRemaining()){
						socketChannel.write(packet);
					}
					packet.clear();
					socketChannel.close();
				}
				Thread.sleep(10);
			}
			channel.close();
			System.out.println("Stopping tcp loop for " + this.messengerId);
		} catch (IOException e) {
			// TODO Auto-generated catch block
			e.printStackTrace();
		} catch (InterruptedException e) {
			// TODO Auto-generated catch block
			e.printStackTrace();
		}
	}
	
	public void registerMessageType(String messageType, Function<JSONObject, JSONObject> callback){
		callbacks.put(messageType, callback);
	}
	
	public void registerMessengerAddress(String messengerId, String addr, int udpPort, int tcpPort){
		addressBook.put(messengerId, new Address(addr, udpPort, tcpPort));
	}
	
	public JSONObject sendMessage(String messageType, JSONObject data, String clientId, boolean blocking) throws IOException, CouldNotResolveMessengerException{
		Address address = resolveAddress(clientId);
		JSONObject message = new JSONObject();
		message.put("msg_type", messageType);
		message.put("data", data);
		byte messageData[] = message.toString().getBytes("utf-8");
		
		if (blocking){
			Socket sock = new Socket();
			sock.connect(new InetSocketAddress(address.addr, address.tcpPort));
			DataOutputStream outToServer = new DataOutputStream(sock.getOutputStream());
			BufferedReader inFromServer = new BufferedReader(new InputStreamReader(sock.getInputStream(), "UTF-8"));
			
			outToServer.writeBytes("|" + messageData.length + "!");
			outToServer.write(messageData);
			outToServer.flush();
			String buffer = "";
			int msgLen = 0;
			while (true) {
				char c = (char) inFromServer.read();
				if (c == '|')
					continue;
				if (c == '!'){
					msgLen = Integer.parseInt(buffer);
					break;
				}
				buffer += c;
			}
			String jsonResponseStr = "";
			while (jsonResponseStr.length() < msgLen)
				jsonResponseStr += (char) inFromServer.read();
			sock.close();
			return new JSONObject(jsonResponseStr);
		}
		else {
			DatagramPacket packet = new DatagramPacket(messageData, messageData.length, InetAddress.getByName(address.addr), address.udpPort);
			udpSock.send(packet);
			return new JSONObject();
		}
	}
	
	private JSONObject onAddressResolutionRequest(JSONObject message){
		// Repack responseBlacklist from a JSONArray to an ArrayList
		ArrayList<String> requestBlacklist = new ArrayList<String>();
		JSONArray jsonRequestBlacklist = message.getJSONArray("request_blacklist");
		for (int i = 0; i < jsonRequestBlacklist.length(); i++) {
			requestBlacklist.add(jsonRequestBlacklist.getString(i));
		}
		
		// Resolve the address.
		Address result;
		try {
			result = resolveAddress(message.getString("messenger_id"), requestBlacklist);
		} catch (JSONException | CouldNotResolveMessengerException e) {
			result = null;
		}
		
		// Pack the response
		JSONObject responseData = new JSONObject();
		if (result != null){
			responseData.put("addr", result.addr);
			responseData.put("udp_port", result.udpPort);
			responseData.put("tcp_port", result.tcpPort);
		}
		responseData.put("request_blacklist", requestBlacklist);
		return responseData;
	}
	
	private Address resolveAddress(String messengerId) throws CouldNotResolveMessengerException{
		return resolveAddress(messengerId, new ArrayList<String>());
	}
	
	private Address resolveAddress(String messengerId, ArrayList<String> requestBlacklist) throws 
	CouldNotResolveMessengerException {
		
		if (!addressBook.containsKey(messengerId)){
			// Blacklist any client ids that point to us.
			for (String clientId : addressBook.keySet()){
				Address address = addressBook.get(clientId);
				if (address.addr.equals(this.address) && address.udpPort == this.udpPort && address.tcpPort == this.tcpPort)
					requestBlacklist.add(clientId);
			}
			// Search over all known clients for a valid address
			for (String clientId : addressBook.keySet()){
				if (requestBlacklist.contains(clientId))
					continue;
				try{
					JSONObject requestData = new JSONObject();
					requestData.put("messenger_id", messengerId);
					requestData.put("request_blacklist", requestBlacklist);
					JSONObject responseData = sendMessage("address_resolution_request", requestData, clientId, true);
					if (responseData.has("addr")){
						Address newAddress = new Address(responseData.getString("addr"),
								responseData.getInt("udp_port"),
								responseData.getInt("tcp_port"));
						addressBook.put(messengerId, newAddress);
						return newAddress;
					}
					else {
						// Reset requestBlacklist to new list from client
						requestBlacklist.clear();
						JSONArray newRequestBlacklist = responseData.getJSONArray("request_blacklist");
						for (int i = 0; i < newRequestBlacklist.length(); i++){
							requestBlacklist.add(newRequestBlacklist.getString(i));
						}
					}
				} catch (IOException e){
					requestBlacklist.add(clientId);
				}
			}	
			throw new Messenger.CouldNotResolveMessengerException(messengerId);
		}
		return addressBook.get(messengerId);
	}
	
	public class CouldNotResolveMessengerException extends Exception{
		private String messengerId;
		
		public CouldNotResolveMessengerException(String messengerId){
			super(messengerId);
			this.messengerId = messengerId;
		}
	}
}