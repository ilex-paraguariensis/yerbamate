import { Experiment } from "../Interfaces";
import ProgressBar from "./ProgressBar";
import "../../node_modules/xterm/css/xterm.css";
import { useCallback, useEffect, useRef, useState } from "react";
import { Terminal } from "xterm";
import socket from "../socket";

enum MessageType {
  train_started = "train_started",
  train_end = "train_end",
  train_progress = "train_progress",
  train_logs = "train_logs",
  train_error = "train_error",
  handshake = "handshake",
}
type CustomMessageEvent = {
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
  experimentId: string;
}) => {
  const termComponent = useRef(null);
  const [termView, setTermView] = useState<Terminal | null>(null);
  const [viewState, setViewState] = useState(ExperimentPageState.Loading);
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
      setTermView(() => term);
    }
  }, []);

  const onMessageReactions = {
    [MessageType.handshake]: (data: CustomMessageEvent) => {
      setViewState(ExperimentPageState.Connected);
    },
    [MessageType.train_started]: (data: CustomMessageEvent) => {
      setViewState(ExperimentPageState.Training);
    },
    [MessageType.train_end]: (data: CustomMessageEvent) => {
      setViewState(ExperimentPageState.Connected);
    },
    [MessageType.train_progress]: (data: CustomMessageEvent) => {
      setViewState(ExperimentPageState.Training);
    },
    [MessageType.train_logs]: (data: CustomMessageEvent) => {
      console.log(data.data);
      if (termView) {
        termView.write(data.data);
      }
    },
    [MessageType.train_error]: (data: CustomMessageEvent) => {
      console.log(data.data);
      if (termView) {
        termView.write("\x1b[1;31m" + data.data + "\x1b[0m");
      }
    },
  };
  socket.onmessage = (lastMessage) => {
    console.log("Child last message!! ", lastMessage);
    let data: CustomMessageEvent | null = null;
    try {
      data = JSON.parse(lastMessage.data) as CustomMessageEvent;
      console.log(data);
    } catch (e) {
      console.log(e);
    }
    const reaction = onMessageReactions[data!.type](data!);
  };

  useEffect(() => {
    if (viewState == ExperimentPageState.Loading) {
      socket.send(
        JSON.stringify({
          type: "handshake",
          experimentId: experimentId,
        })
      );
    }
  }, [viewState]);

  const startTraining = () => {
    console.log("send message start training");
    socket.send(
      JSON.stringify({
        type: "start_training",
        experiment_id: experimentId,
      })
    );
    setViewState(ExperimentPageState.TrainRequested);
  };

  return (
    <div style={{ width: "100%" }}>
      <div
        ref={termComponent}
        style={{
          width: "100%",
          borderRadius: "10%",
          marginTop: "8vh",
          marginLeft: "auto",
          marginRight: "auto",
          maxWidth: "94vw",
        }}
      ></div>
      <div style={{ textAlign: "center", width: "100%" }}>
        <div
          className="card"
          style={{
            padding: "5px",
            width: "25rem",
            marginLeft: "auto",
            marginRight: "auto",
            marginTop: "2vh",
          }}
        >
          {<StatusView status={viewState}></StatusView>}

          {/* <SocketStatusView readyState={readyState}></SocketStatusView> */}

          <button
            type="button"
            className="btn btn-danger btn-lg btn-block"
            disabled={viewState !== ExperimentPageState.Training}
            onClick={() => {
              socket.send(
                JSON.stringify({
                  type: "stop_training",
                  experiment_id: experimentId,
                })
              );
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
            disabled={
              experiment.status === "running" ||
              experiment.status === "never-run"
            }
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
