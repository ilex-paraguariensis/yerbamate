import {
  WebSocketClient,
  WebSocketServer,
} from "https://deno.land/x/websocket@v0.1.4/mod.ts";

import { Application, Router, send } from "https://deno.land/x/oak/mod.ts";
import { oakCors } from "https://deno.land/x/cors/mod.ts";
enum MessageType {
	handshake = "handshake",
	status = "status",
	start_training = "start_training",
	stop_training = "stop_training",
}
enum Status {
	not_connected = "not_connected",
	connected = "connected",
	training = "training",
}

class Server {
  server: WebSocketServer;
  mateBoardServerProcess: Deno.Process;
	staticServer: Application;
	cwd:string;
	status: Status = Status.not_connected;
	trainingProcess: Deno.Process;
  constructor(cwd:string) {
		this.cwd = cwd;
		const router = new Router();
		router
			.get("/summary", async (context) => {
				console.log("Trying to get mate summary")
				const responseString = await Deno.run({
					cmd: ["mate", "summary"],
					cwd: this.cwd,
					stdout: "piped",
					stderr: "piped",
				}).output();

				context.response.body = responseString
			})
			this.staticServer = new Application();
			this.staticServer.use(oakCors());
			this.staticServer.use(router.routes());
			const wsRoutes:Record<MessageType, (p:Record<string, any>) =>Record<string, any>> = {
				[MessageType.handshake]: () => ({type: MessageType.handshake, data: "ok"}),
				[MessageType.status]: () => ({type: MessageType.status, data: this.status}),
				[MessageType.start_training]: (msg) => {
					this.startTraining(msg.experimentId);
					return {type: MessageType.start_training, data: "ok"}
				},
				[MessageType.stop_training]: () => {
					this.stopTraining();
					return {type: MessageType.stop_training, data: "ok"}
				}
			}
		}
		async startTraining(experimentId:string) {
			this.status = Status.training;
			await Deno.run({
				cmd: ["mate", "train", experimentId],
				cwd: this.cwd,
				stdout: "piped",
				stderr: "piped",
			}).status();
		}
		async stopTraining() {
			this.status = Status.connected;
			this.trainingProcess?.kill(9);
		}
		async start() {
			this.server = new WebSocketServer(8765);
			this.server.on("connection", (socket: WebSocketClient) => {
				socket.on("message", (message: string) => {
					const parsed = JSON.parse(message)
					console.log(parsed)
					if (parsed.type === "handshake"){
						this.status = Status.connected
						socket.send(JSON.stringify({type: "handshake", data: "ok"}))
					}
						
				});
			});
			this.mateBoardServerProcess = Deno.run({
				cmd: ["npm", "start"],
				cwd: "./mateboard",
				stdout: "piped",
				stderr: "piped",
			});
			// Start listening on port 8080 of localhost.
			await this.staticServer.listen({port: 3002});
		}
}
const server = new Server(Deno.args[0]);
await server.start();
