package yeti;

import static org.junit.Assert.*;

import java.io.IOException;

import org.json.JSONException;
import org.json.JSONObject;
import org.junit.Test;

import yeti.Messenger.CouldNotResolveMessengerException;

public class MessengerTest {
	
	public JSONObject onMessage(JSONObject message){
		System.out.println("Bingo!");
		System.out.println(message.getString("msg"));
		return new JSONObject("{\"msg\": \"Awesomeness!\";}");
	}

	@Test
	public void test() throws IOException, JSONException, CouldNotResolveMessengerException, InterruptedException {
		Messenger m0 = new Messenger("jm0");
		Messenger m1 = new Messenger("jm1");
		Messenger m2 = new Messenger("jm2");
		
		m0.registerMessageType("telegram", this::onMessage);
		m0.registerMessengerAddress("m5", "127.0.0.1", 9005, 9015);
		m1.registerMessengerAddress("jm0", "127.0.0.1", 9100, 9101);
		m2.registerMessengerAddress("jm1", "127.0.0.1", 9102, 9103);
		
		m0.startServer("127.0.0.1", 9100, 9101);
		m1.startServer("127.0.0.1", 9102, 9103);
		m2.startServer("127.0.0.1", 9103, 9104);
		Thread.sleep(1000);
		//JSONObject response1 = m2.sendMessage("telegram", new JSONObject("{\"msg\": \"String from the land of Java!\";}"), "m0", true);
		//System.out.println(response1.toString());
		//JSONObject response2 = m2.sendMessage("telegram", new JSONObject("{\"msg\": \"String!\";}"), "m0", true);
		//System.out.println(response2.toString());	
		
		Thread.sleep(10000);
		
		m0.stopServer();
		m1.stopServer();
		m2.stopServer();
	}

}
