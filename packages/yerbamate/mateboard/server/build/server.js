"use strict";
var __createBinding = (this && this.__createBinding) || (Object.create ? (function(o, m, k, k2) {
    if (k2 === undefined) k2 = k;
    var desc = Object.getOwnPropertyDescriptor(m, k);
    if (!desc || ("get" in desc ? !m.__esModule : desc.writable || desc.configurable)) {
      desc = { enumerable: true, get: function() { return m[k]; } };
    }
    Object.defineProperty(o, k2, desc);
}) : (function(o, m, k, k2) {
    if (k2 === undefined) k2 = k;
    o[k2] = m[k];
}));
var __setModuleDefault = (this && this.__setModuleDefault) || (Object.create ? (function(o, v) {
    Object.defineProperty(o, "default", { enumerable: true, value: v });
}) : function(o, v) {
    o["default"] = v;
});
var __importStar = (this && this.__importStar) || function (mod) {
    if (mod && mod.__esModule) return mod;
    var result = {};
    if (mod != null) for (var k in mod) if (k !== "default" && Object.prototype.hasOwnProperty.call(mod, k)) __createBinding(result, mod, k);
    __setModuleDefault(result, mod);
    return result;
};
var __importDefault = (this && this.__importDefault) || function (mod) {
    return (mod && mod.__esModule) ? mod : { "default": mod };
};
Object.defineProperty(exports, "__esModule", { value: true });
const os_1 = __importDefault(require("os"));
const path_1 = __importDefault(require("path"));
const fs_1 = __importDefault(require("fs"));
const pty = __importStar(require("node-pty"));
const ws_1 = require("ws");
const node_child_process_1 = require("node:child_process");
const shell = os_1.default.platform() === 'win32' ? 'powershell.exe' : 'bash';
var MessageType;
(function (MessageType) {
    MessageType["handshake"] = "handshake";
    MessageType["status"] = "status";
    MessageType["start_training"] = "start_training";
    MessageType["stop_training"] = "stop_training";
    MessageType["get_summary"] = "get_summary";
})(MessageType || (MessageType = {}));
var Status;
(function (Status) {
    Status["not_connected"] = "not_connected";
    Status["connected"] = "connected";
    Status["training"] = "training";
})(Status || (Status = {}));
const jsonFromThere = (data) => {
    const lines = data.split('\n');
    let result = null;
    for (let i = 0; i < lines.length; i++) {
        try {
            result = JSON.parse(lines.slice(i, lines.length).join('\n'));
            break;
        }
        catch (e) { }
    }
    return result;
};
class Server {
    constructor(cwd) {
        this.status = Status.not_connected;
        this.socket = null;
        this.currentMessage = null;
        this.wsRoutes = {
            [MessageType.handshake]: () => {
                var _a;
                this.status = Status.connected;
                (_a = this.socket) === null || _a === void 0 ? void 0 : _a.send(JSON.stringify({ type: MessageType.handshake, data: 'ok' }));
            },
            [MessageType.status]: () => ({
                type: MessageType.status,
                data: this.status,
            }),
            [MessageType.start_training]: (msg) => {
                var _a;
                (_a = this.socket) === null || _a === void 0 ? void 0 : _a.send(JSON.stringify({ type: 'train_started', data: this.status }));
                this.startTraining(msg.experiment_id);
            },
            [MessageType.stop_training]: () => {
                var _a;
                this.stopTraining();
                (_a = this.socket) === null || _a === void 0 ? void 0 : _a.send(JSON.stringify({ type: MessageType.stop_training, data: 'ok' }));
            },
            [MessageType.get_summary]: () => {
                this.currentMessage = MessageType.get_summary;
                const result = (0, node_child_process_1.spawnSync)('mate', ['summary'], { cwd: this.cwd });
                const summary = jsonFromThere(result.stdout.toString());
                console.log("Summary:", summary);
                this.socket.send(JSON.stringify({ type: MessageType.get_summary, data: summary }));
            },
        };
        this.cwd = cwd;
        this.ptyProcess = this.initPty();
        this.socketServer = new ws_1.WebSocketServer({ port: 8765 });
        this.socketServer.on('connection', (ws) => {
            this.socket = ws;
            console.log('Connection established');
            this.status = Status.connected;
            this.ptyProcess.onData((data) => {
                process.stdout.write(data);
                ws.send(data);
            });
            ws.on('message', (message) => {
                const parsed = JSON.parse(message);
                console.log('Received message:');
                console.log(parsed);
                this.wsRoutes[parsed.type](parsed);
            });
            //ptyProcess.resize(100, 40);
            //ptyProcess.write('ls\r');
        });
        this.socketServer.on('close', () => {
            this.status = Status.not_connected;
        });
        if (!fs_1.default.existsSync(path_1.default.join(cwd, '.aim'))) {
            (0, node_child_process_1.spawnSync)('aim', ['init'], { cwd });
        }
        this.aimLogger = (0, node_child_process_1.spawn)('aim', ['up', '-p', '8000'], { cwd });
        this.mateBoardServerProcess = (0, node_child_process_1.spawn)('npm', ['start'], { cwd: '../client' });
        this.mateBoardServerProcess.stdout.on('data', (data) => {
            console.log(`stdout: ${data}`);
        });
        this.mateBoardServerProcess.stderr.on('data', (data) => {
            console.error(`stderr: ${data}`);
        });
        this.mateBoardServerProcess.on('close', (code) => {
            console.log(`child process exited with code ${code}`);
        });
    }
    initPty() {
        this.ptyProcess = pty.spawn(shell, [], {
            name: 'xterm-color',
            cols: 80,
            rows: 30,
            cwd: this.cwd,
            env: process.env,
        });
        this.ptyProcess.onData((data) => {
            var _a;
            // check if data contains a substring
            (_a = this.socket) === null || _a === void 0 ? void 0 : _a.send(JSON.stringify({ type: "train_logs", data }));
        });
        return this.ptyProcess;
    }
    runMateCommand(command) {
        const fullCommand = 'mate ' + command;
        console.log(`Command: ${fullCommand}`);
        this.ptyProcess.write(fullCommand + '\r');
    }
    startTraining(experimentId) {
        console.log('Trying to start training experiment:', experimentId);
        this.runMateCommand(`train ${experimentId}`);
    }
    stopTraining() {
        this.status = Status.connected;
        this.ptyProcess.write('\x03');
    }
}
exports.default = Server;
