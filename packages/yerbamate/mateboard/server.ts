import {
  WebSocketClient,
  WebSocketServer,
} from "https://deno.land/x/websocket@v0.1.4/mod.ts";

import { Application, Router, send } from "https://deno.land/x/oak/mod.ts";
import { oakCors } from "https://deno.land/x/cors/mod.ts";

class Server {
  server: WebSocketServer;
  mateBoardServerProcess: Deno.Process;
	staticServer: Application;
	cwd:string;
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
		}
		async start() {
			this.server = new WebSocketServer(8765);
			this.server.on("connection", (socket: WebSocketClient) => {
				socket.on("message", (message: string) => {
					console.log(message);
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
