import os from 'os';
import path from 'path';
import fs from 'fs';
import * as pty from 'node-pty';
import { WebSocketServer, WebSocket } from 'ws';
import { spawn, spawnSync } from 'node:child_process';

const shell = os.platform() === 'win32' ? 'powershell.exe' : 'bash';
enum MessageType {
  handshake = 'handshake',
  status = 'status',
  start_training = 'start_training',
  stop_training = 'stop_training',
  get_summary = 'get_summary',
}
enum Status {
  not_connected = 'not_connected',
  connected = 'connected',
  training = 'training',
}
const jsonFromThere = (data: string) => {
	const lines = data.split('\n');
	let result: null | Record<string, any> = null;
	for (let i = 0; i < lines.length; i++) {
		try{
			result = JSON.parse(lines.slice(i, lines.length).join('\n'));
			break;
		}
		catch(e) {}
	}
	return result;
}
class Server {
  ptyProcess: pty.IPty;
  mateBoardServerProcess;
  cwd: string;
  status: Status = Status.not_connected;
  socket: WebSocket | null = null;
  socketServer: WebSocketServer;
  aimLogger;
  currentMessage: null | MessageType = null
  initPty() {
    this.ptyProcess = pty.spawn(shell, [], {
      name: 'xterm-color',
      cols: 80,
      rows: 30,
      cwd: this.cwd,
      env: process.env as { [key: string]: string },
    });

    this.ptyProcess.onData((data: string) => {
			// check if data contains a substring
			this.socket?.send(JSON.stringify({type:"train_logs", data}))
    });
		return this.ptyProcess;
  }
  constructor(cwd: string) {
    this.cwd = cwd;
    this.ptyProcess = this.initPty();
    this.socketServer = new WebSocketServer({ port: 8765 });
    this.socketServer.on('connection', (ws) => {
			this.socket = ws
			console.log('Connection established');
      this.status = Status.connected;
      this.ptyProcess.onData((data: string) => {
        process.stdout.write(data);
        ws.send(data);
      });
      ws.on('message', (message: string) => {
        const parsed = JSON.parse(message);
        console.log('Received message:');
        console.log(parsed);
        this.wsRoutes[parsed.type as MessageType](parsed as Record<string, any>);
      });
      //ptyProcess.resize(100, 40);
      //ptyProcess.write('ls\r');
    });
    this.socketServer.on('close', () => {
      this.status = Status.not_connected;
    });
    if (!fs.existsSync(path.join(cwd, '.aim'))) {
      spawnSync('aim', ['init'], { cwd });
    }
    this.aimLogger = spawn('aim', ['up', '-p', '8000'], { cwd });
    this.mateBoardServerProcess = spawn('npm', ['start'], { cwd: '../client' });

    this.mateBoardServerProcess.stdout.on('data', (data: string) => {
      console.log(`stdout: ${data}`);
    });

    this.mateBoardServerProcess.stderr.on('data', (data: string) => {
      console.error(`stderr: ${data}`);
    });

    this.mateBoardServerProcess.on('close', (code: number) => {
      console.log(`child process exited with code ${code}`);
    });
  }
  wsRoutes = {
    [MessageType.handshake]: () => {
      this.status = Status.connected;
      this.socket?.send(
        JSON.stringify({ type: MessageType.handshake, data: 'ok' }),
      );
    },
    [MessageType.status]: () => ({
      type: MessageType.status,
      data: this.status,
    }),
    [MessageType.start_training]: (msg) => {
      this.socket?.send(
        JSON.stringify({ type: 'train_started', data: this.status }),
      );
      this.startTraining(msg.experiment_id);
    },
    [MessageType.stop_training]: () => {
      this.stopTraining();
      this.socket?.send(
        JSON.stringify({ type: MessageType.stop_training, data: 'ok' }),
      );
    },
    [MessageType.get_summary]: () => {
      this.currentMessage = MessageType.get_summary;
			const result = spawnSync('mate', ['summary'], { cwd: this.cwd });
			const summary = jsonFromThere(result.stdout.toString())
			console.log("Summary:", summary);
			this.socket!.send(
				JSON.stringify({ type: MessageType.get_summary, data: summary }),
			);
    },
  } as Record<MessageType, (p: Record<string, any>) => void>;
  runMateCommand(command: string) {
    const fullCommand = 'mate ' + command;
    console.log(`Command: ${fullCommand}`);
    this.ptyProcess.write(fullCommand + '\r');
  }
  startTraining(experimentId: string) {
    console.log('Trying to start training experiment:', experimentId);
    this.runMateCommand(`train ${experimentId}`);
  }
  stopTraining() {
    this.status = Status.connected;
		this.ptyProcess.write('\x03');
  }
}

export default Server;

