import { Experiment } from "../Interfaces";
import ProgressBar from "./ProgressBar";
// import SocketAPIHook from "../api/SocketAPIHook";
import useWebSocket, { ReadyState } from "react-use-websocket";
import { useCallback, useEffect, useState } from "react";

enum ExperimentPageState {
  Loading,
  View,
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
  const [viewState, setViewState] = useState(ExperimentPageState.Loading);
  const [socketUrl, setSocketUrl] = useState("ws://localhost:8765");
  const [messageHistory, setMessageHistory] = useState(
    [] as Array<MessageEvent>
  );
  const [connectionStatusListener, setConnectionStatusListener] = useState({
    onError: (event: Event) => {
      console.log(event);
    },
    onOpen: (event: Event) => {
      console.log(event);
    },
    onClose: (event: Event) => {
      console.log(event);
    },
  });
  const { sendMessage, sendJsonMessage, lastMessage, readyState } =
    useWebSocket(socketUrl, connectionStatusListener, true);

  useEffect(() => {
    if (lastMessage !== null) {
      setMessageHistory((prev) => prev.concat(lastMessage));

      console.log(lastMessage);

      try {
        const data = JSON.parse(lastMessage.data);
        if (data.state == "training") {
          setViewState(ExperimentPageState.Training);
        }
        if (data.type == "handshake") {
          setViewState(ExperimentPageState.View);
        }
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
    sendMessage("start training");
    setViewState(ExperimentPageState.TrainRequested);
  };

  return (
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
          disabled={experiment.status !== "running"}
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
          disabled={
            experiment.status === "running" || experiment.status === "never-run"
          }
          style={{ marginBottom: "5px" }}
        >
          Test
        </button>
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
