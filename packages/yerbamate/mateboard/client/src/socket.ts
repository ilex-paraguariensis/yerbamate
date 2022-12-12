import openSocket from "socket.io-client";

const webSocket = new WebSocket("ws://localhost:8765");
/*
webSocket.onopen = () => {
	console.log("Connected to server")
	webSocket.send(JSON.stringify({type:"handshake", data:"Hello from client"}))
}
webSocket.onmessage = (event) => {
	console.log("Message from server", event.data)
}
*/
export default webSocket;
