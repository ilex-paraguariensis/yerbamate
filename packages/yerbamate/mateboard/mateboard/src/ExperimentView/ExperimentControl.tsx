import { Experiment } from "../Interfaces";
import ProgressBar from "./ProgressBar";
import "../../node_modules/xterm/css/xterm.css";
// import SocketAPIHook from "../api/SocketAPIHook";
import useWebSocket, { ReadyState } from "react-use-websocket";
import { useCallback, useEffect, useRef, useState } from "react";
import { Terminal } from "xterm";

enum MessageType {
  train_started = "train_started",
  train_end = "train_end",
  train_progress = "train_progress",
  train_logs = "train_logs",
  train_error = "train_error",
  handshake = "handshake",
}
type MessageEvent = {
  type: MessageType;
  data: string;
};
enum ExperimentPageState {
  Loading,
  Connected,
  TrainRequested,
  Training,
  Test,
  TestRequested,
}
export default ({
  experiment,
  experimentId,
}: {
  experiment: Experiment;
  experimentId: String;
}) => {
  const termComponent = useRef(null);
  const [termView, setTermView] = useState<Terminal | null>(null);
  const [viewState, setViewState] = useState(ExperimentPageState.Loading);
  const [socketUrl, setSocketUrl] = useState("ws://localhost:8765");
  const [messageHistory, setMessageHistory] = useState(
    [] as Array<MessageEvent>,
  );
  useEffect(() => {
    if (
      termComponent.current &&
      (termComponent.current as HTMLElement).innerHTML === ""
    ) {
      const term = new Terminal({
        cursorBlink: true,
        cols: 200,
        convertEol: true,
        theme: { background: "black" },
      });
      term.open(termComponent.current);
      // @ts-ignore
      // term.setOption("theme", { background: "black" });
      setTermView(() => term);
    }
  }, []);
  const [connectionStatusListener, setConnectionStatusListener] = useState({
    onError: (event: Event) => {
      console.log(event);
    },
    onOpen: (event: Event) => {
      console.log(event);
    },
    onClose: (event: Event) => {
      console.log(event);
      setViewState(ExperimentPageState.Loading);
    },
  });
  const { sendMessage, sendJsonMessage, lastMessage, readyState } =
    useWebSocket(socketUrl, connectionStatusListener, true);

  const onMessageReactions = {
    [MessageType.handshake]: (data: MessageEvent) => {
      setViewState(ExperimentPageState.Connected);
    },
    [MessageType.train_started]: (data: MessageEvent) => {
      setViewState(ExperimentPageState.Training);
    },
    [MessageType.train_end]: (data: MessageEvent) => {
      setViewState(ExperimentPageState.Connected);
    },
    [MessageType.train_progress]: (data: MessageEvent) => {
      setViewState(ExperimentPageState.Training);
    },
    [MessageType.train_logs]: (data: MessageEvent) => {
      console.log(data.data);
      if (termView) {
        termView.write(data.data);
      }
    },
    [MessageType.train_error]: (data: MessageEvent) => {
      console.log(data.data);
      if (termView) {
        termView.write("\x1b[1;31m" + data.data + "\x1b[0m");
      }
      // setViewState(ExperimentPageState.View);
    },
  };
  useEffect(() => {
    if (lastMessage !== null) {
      try {
        const data = JSON.parse(lastMessage.data) as MessageEvent;
        console.log(data);
        setMessageHistory((prev) => prev.concat(data));
        const reaction = onMessageReactions[data.type](data);
        /*
        if (data.type === "training") {
          setViewState(ExperimentPageState.Training);
        }
        if (data.type === "handshake") {
          setViewState(ExperimentPageState.View);
        }
				*/
      } catch (e) {
        console.log(e);
      }
    }
  }, [lastMessage, setMessageHistory]);

  useEffect(() => {
    if (viewState == ExperimentPageState.Loading) {
      sendJsonMessage({ type: "handshake", experimentId: experimentId });
    }
  }, [viewState]);

  const startTraining = () => {
    console.log("send message start training");
    sendJsonMessage({
      type: "start_training",
      experiment_id: experimentId,
    });
    setViewState(ExperimentPageState.TrainRequested);
  };

  return (
    <div style={{ width: "100%" }}>
      <div ref={termComponent} style={{ width: "100%", borderRadius: "10%" }}>
      </div>
      <div style={{ textAlign: "center", width: "100%" }}>
        <div
          className="card"
          style={{
            padding: "5px",
            width: "25rem",
            marginLeft: "auto",
            marginRight: "auto",
          }}
        >
          {<StatusView status={viewState}></StatusView>}

          {/* <SocketStatusView readyState={readyState}></SocketStatusView> */}

          <button
            type="button"
            className="btn btn-danger btn-lg btn-block"
            disabled={viewState !== ExperimentPageState.Training}
            onClick={() => {
              sendJsonMessage({
                type: "stop_training",
                experiment_id: experimentId,
              });
            }}
            style={{ marginBottom: "5px" }}
          >
            Stop Training
          </button>
          <button
            type="button"
            className="btn btn-success btn-lg btn-block"
            onClick={() => startTraining()}
            style={{ marginBottom: "5px" }}
          >
            Train
          </button>
          <button
            type="button"
            className="btn btn-success btn-lg btn-block"
            disabled={experiment.status === "running" ||
              experiment.status === "never-run"}
            style={{ marginBottom: "5px" }}
          >
            Test
          </button>
        </div>
      </div>
    </div>
  );
};

function StatusView({ status }: { status: ExperimentPageState }) {
  const style = {
    padding: 20,
  };

  // str value of enum name
  const statusName = ExperimentPageState[status];

  return <div style={style}>{statusName}</div>;
}

function SocketStatusView({ readyState }: { readyState: ReadyState }) {
  const style = {
    padding: 20,
  };

  switch (readyState) {
    case ReadyState.CONNECTING:
      return <ProgressBar totalTime={10000} color="green"></ProgressBar>;

    case ReadyState.OPEN:
      return <div style={style}>Connected</div>;
    case ReadyState.CLOSING:
      return <div>Closing...</div>;
    case ReadyState.CLOSED:
      return <div>Disconnected</div>;
    case ReadyState.UNINSTANTIATED:
    default:
      return <div>Uninstantiated</div>;
  }
}
