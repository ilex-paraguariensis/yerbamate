import {
  WebSocketClient,
  WebSocketServer,
} from "https://deno.land/x/websocket@v0.1.4/mod.ts";
import { stdOutStream } from "./stdoutstream.ts";
import { Application, Router, send } from "https://deno.land/x/oak/mod.ts";
import { oakCors } from "https://deno.land/x/cors/mod.ts";
import {
  readableStreamFromReader,
} from "https://deno.land/std@0.158.0/streams/conversion.ts";
import { mergeReadableStreams } from "https://deno.land/std@0.158.0/streams/merge.ts";

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
  cwd: string;
  status: Status = Status.not_connected;
  trainingProcess: Deno.Process;
  socket?: WebSocketClient;
  wsRoutes: Record<
    MessageType,
    (p: Record<string, any>) => Record<string, any>
  >;
  constructor(cwd: string) {
    this.cwd = cwd;
    const router = new Router();
    router
      .get("/summary", async (context) => {
        console.log("Trying to get mate summary");
        const responseString = await Deno.run({
          cmd: ["mate", "summary"],
          cwd: this.cwd,
          stdout: "piped",
          stderr: "piped",
        }).output();

        context.response.body = responseString;
      });
    this.staticServer = new Application();
    this.staticServer.use(oakCors());
    this.staticServer.use(router.routes());
    this.wsRoutes = {
      [MessageType.handshake]: async () => {
        this.status = Status.connected;
        this.socket?.send(
          JSON.stringify({ type: MessageType.handshake, data: "ok" }),
        );
      },
      [MessageType.status]: () => ({
        type: MessageType.status,
        data: this.status,
      }),
      [MessageType.start_training]: async (msg) => {
        this.socket?.send(
          JSON.stringify({ type: "train_started", data: this.status }),
        );
        await this.startTraining(msg.experiment_id);
      },
      [MessageType.stop_training]: () => {
        this.stopTraining();
        return { type: MessageType.stop_training, data: "ok" };
      },
    };
  }
  async startTraining(experimentId: string) {
    console.log("Trying to start training experiment", experimentId);
    const stdoutStream = new stdOutStream(this.cwd);
    const p = Deno.run({
      cmd: ["mate", "train", experimentId],
      cwd: this.cwd,
      stdout: "piped",
      stderr: "piped",
    });
    this.trainingProcess = p;
    const decoder = new TextDecoder();
    const merged = mergeReadableStreams(
      readableStreamFromReader(p.stdout),
      readableStreamFromReader(p.stderr),
    );
    for await (const chunk of merged) {
      console.log("Chunk:", decoder.decode(chunk));
      this.socket?.send(JSON.stringify({
        type: "train_logs",
        data: Array.from(chunk),
      }));
    }
    /*
			for await (const chunk of readableStreamFromReader(p.stderr)) {
				// console.log("Sending chunk:", chunk)
				this.socket?.send(JSON.stringify({type: "train_error", data: decoder.decode(chunk)}))
			}
			*/
    const status = await p.status();
    this.socket?.send(JSON.stringify({ type: "train_end", data: status }));
    return;
  }
  async stopTraining() {
    this.status = Status.connected;
		if (this.trainingProcess){
			Deno.kill(this.trainingProcess, "SIGINT");
		}
  }
  async start() {
    this.server = new WebSocketServer(8765);
    this.server.on("connection", (socket: WebSocketClient) => {
      this.socket = socket;
      socket.on("message", async (message: string) => {
        const parsed = JSON.parse(message);
        console.log("Received message:");
        console.log(parsed);
        const response = await this.wsRoutes[parsed.type](parsed);
      });
    });
    this.mateBoardServerProcess = Deno.run({
      cmd: ["npm", "start"],
      cwd: "./mateboard",
      stdout: "piped",
      stderr: "piped",
    });
    // Start listening on port 8080 of localhost.
    await this.staticServer.listen({ port: 3002 });
  }
}
const server = new Server(Deno.args[0]);
await server.start();
