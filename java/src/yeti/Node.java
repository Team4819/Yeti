package yeti;

import java.io.FileNotFoundException;
import java.io.FileReader;
import java.io.IOException;
import java.util.Map;

import org.json.JSONObject;

import com.esotericsoftware.yamlbeans.YamlException;
import com.esotericsoftware.yamlbeans.YamlReader;

import yeti.Messenger.CouldNotResolveMessengerException;

public class Node {
	boolean running = false;
	String nodeId;
	
	Map moduleConf;
	Map monitorConf;
	
	Object moduleStateData;
	Object moduleNetInfo;
	
	Messenger messenger;
	
	Node(String nodeId, String confPath) throws FileNotFoundException, YamlException {
		this.nodeId = nodeId;
		
		YamlReader reader = new YamlReader(new FileReader(confPath));
		Map data = (Map)reader.read();
		moduleConf = (Map)data.get("modules");
		monitorConf = (Map)data.get("monitors");
		
		messenger = new Messenger("node_" + nodeId);
		messenger.registerMessageType("get_state", this::onGetState);
		messenger.registerMessageType("set_state", this::onSetState);
		messenger.registerMessageType("module_restart_condition", this::onRestartCondition);
		
		for (Object monId : monitorConf.keySet()){
			Map mon = (Map) monitorConf.get(monId);
			if (mon.containsKey("addr")){
				messenger.registerMessengerAddress("mon_" + (String)monId, 
						(String)mon.get("addr"), 
						(int)mon.get("udp_port"), 
						(int)mon.get("tcp_port"));
			}
		}
	}
	
	void bootstrapNode(String monId) throws IOException, CouldNotResolveMessengerException{
		JSONObject message = new JSONObject();
		message.put("node_id", nodeId);
		JSONObject response = messenger.sendMessage("node_bootstrap_request", message, "mon_" + monId, true);
		messenger.startServer(response.getString("addr"), response.getInt("udp_port"), response.getInt("tcp_port"));
	}
	
	JSONObject sendMessage(String msgType, JSONObject data, String entityId, boolean blocking) {
		try {
			return messenger.sendMessage(msgType, data, entityId, blocking);
		} catch (IOException | CouldNotResolveMessengerException e) {
			if (entityId.startsWith("mon_"))
				throw new UnreachableMonitorException(entity);
			// TODO Auto-generated catch block
			e.printStackTrace();
		}
		return new JSONObject();
	}
	
	
}

class OutdatedStateException extends Exception {}

class UnreachableModuleException extends Exception {}

class UnreachableMonitorException extends Exception {}
