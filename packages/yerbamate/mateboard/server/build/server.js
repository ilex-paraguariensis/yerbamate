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
var os_1 = __importDefault(require("os"));
var path_1 = __importDefault(require("path"));
var fs_1 = __importDefault(require("fs"));
var pty = __importStar(require("node-pty"));
var ws_1 = require("ws");
var node_child_process_1 = require("node:child_process");
var shell = os_1.default.platform() === 'win32' ? 'powershell.exe' : 'bash';
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
var Server = /** @class */ (function () {
    function Server(cwd) {
        var _a;
        var _this = this;
        this.status = Status.not_connected;
        this.socket = null;
        this.currentMessage = null;
        this.wsRoutes = (_a = {},
            _a[MessageType.handshake] = function () {
                var _a;
                _this.status = Status.connected;
                (_a = _this.socket) === null || _a === void 0 ? void 0 : _a.send(JSON.stringify({ type: MessageType.handshake, data: 'ok' }));
            },
            _a[MessageType.status] = function () { return ({
                type: MessageType.status,
                data: _this.status,
            }); },
            _a[MessageType.start_training] = function (msg) {
                var _a;
                (_a = _this.socket) === null || _a === void 0 ? void 0 : _a.send(JSON.stringify({ type: 'train_started', data: _this.status }));
                _this.startTraining(msg.experiment_id);
            },
            _a[MessageType.stop_training] = function () {
                var _a;
                _this.stopTraining();
                (_a = _this.socket) === null || _a === void 0 ? void 0 : _a.send(JSON.stringify({ type: MessageType.stop_training, data: 'ok' }));
            },
            _a[MessageType.get_summary] = function () {
                _this.currentMessage = MessageType.get_summary;
                _this.runMateCommand('summary');
            },
            _a);
        this.cwd = cwd;
        this.ptyProcess = this.initPty();
        this.socketServer = new ws_1.WebSocketServer({ port: 8765 });
        this.socketServer.on('connection', function (ws) {
            _this.status = Status.connected;
            _this.ptyProcess.onData(function (data) {
                process.stdout.write(data);
                ws.send(data);
            });
            ws.on('message', function (message) {
                var parsed = JSON.parse(message);
                console.log('Received message:');
                console.log(parsed);
                _this.wsRoutes[parsed.type](parsed);
            });
            //ptyProcess.resize(100, 40);
            //ptyProcess.write('ls\r');
        });
        this.socketServer.on('close', function () {
            _this.status = Status.not_connected;
        });
        if (!fs_1.default.existsSync(path_1.default.join(cwd, '.aim'))) {
            (0, node_child_process_1.spawnSync)('aim', ['init'], { cwd: cwd });
        }
        this.aimLogger = (0, node_child_process_1.spawn)('aim', ['up', '-p', '8000'], { cwd: cwd });
        this.mateBoardServerProcess = (0, node_child_process_1.spawn)('npm', ['start'], { cwd: '../client' });
        this.mateBoardServerProcess.stdout.on('data', function (data) {
            console.log("stdout: ".concat(data));
        });
        this.mateBoardServerProcess.stderr.on('data', function (data) {
            console.error("stderr: ".concat(data));
        });
        this.mateBoardServerProcess.on('close', function (code) {
            console.log("child process exited with code ".concat(code));
        });
    }
    Server.prototype.initPty = function () {
        var _this = this;
        this.ptyProcess = pty.spawn(shell, [], {
            name: 'xterm-color',
            cols: 80,
            rows: 30,
            cwd: this.cwd,
            env: process.env,
        });
        this.ptyProcess.onData(function (data) {
            var _a;
            // check if data contains a substring
            console.log("currentMessage:".concat(_this.currentMessage));
            var toSend = null;
            if (_this.currentMessage === MessageType.get_summary) {
                try {
                    var summary = JSON.parse(data);
                    toSend = {
                        type: MessageType.get_summary,
                        data: summary
                    };
                }
                catch (e) { }
            }
            else if (_this.currentMessage) {
                // console.log(data);
                toSend = { type: _this.currentMessage, data: data };
            }
            console.log({ toSend: toSend });
            if (toSend) {
                (_a = _this.socket) === null || _a === void 0 ? void 0 : _a.send(JSON.stringify(toSend));
            }
        });
        return this.ptyProcess;
    };
    Server.prototype.runMateCommand = function (command) {
        var fullCommand = 'mate ' + command;
        console.log("Command: ".concat(fullCommand));
        this.ptyProcess.write(fullCommand + '\r');
    };
    Server.prototype.startTraining = function (experimentId) {
        console.log('Trying to start training experiment:', experimentId);
        this.runMateCommand("train ".concat(experimentId));
    };
    Server.prototype.stopTraining = function () {
        this.status = Status.connected;
        this.ptyProcess.kill('SIGINT');
    };
    return Server;
}());
exports.default = Server;
