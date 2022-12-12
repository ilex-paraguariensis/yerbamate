import React, { useCallback, useEffect, useState } from "react";
import useWebSocket, { ReadyState } from "react-use-websocket";
import { Experiment } from "../Interfaces";
import ProgressBar from "./ProgressBar";

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

export default ({ experiment }: { experiment: Experiment }) => {
  const [socketUrl, setSocketUrl] = useState("ws://localhost:8765");
  const [messageHistory, setMessageHistory] = useState(
    [] as Array<MessageEvent>
  );

  const { sendMessage, sendJsonMessage, lastMessage, readyState } =
    useWebSocket(
      socketUrl,
      {
        onError: (event) => console.log(event),
        onOpen: (event) => console.log(event),
        onClose: (event) => console.log(event),
        shouldReconnect: (ss) => true,
      },
      true
    );

  // sendJsonMessage({
  //   "type": "experiment",
  //   "event": "select",
  //   "experiment": experiment
  // }, true)
  sendMessage(
    JSON.stringify({
      hello: "world",
    })
  );

  useEffect(() => {
    if (lastMessage !== null) {
      setMessageHistory((prev) => prev.concat(lastMessage));
    }
  }, [lastMessage, setMessageHistory]);

  const handleTrainClick = useCallback(() => {
    sendMessage(JSON.stringify({ type: "train", experiment: experiment }));
  }, []);

  const handleClickSendMessage = useCallback(() => sendMessage("Hello"), []);

  const connectionStatus = {
    [ReadyState.CONNECTING]: "Connecting",
    [ReadyState.OPEN]: "Open",
    [ReadyState.CLOSING]: "Closing",
    [ReadyState.CLOSED]: "Closed",
    [ReadyState.UNINSTANTIATED]: "Uninstantiated",
  }[readyState];

  console.log(connectionStatus);
  console.log(messageHistory);

  return (
    <div style={{ textAlign: "center", width: "100%" }}>
      {/*
			<ProgressBar totalTime={100} color="red"></ProgressBar>
			*/}
      {/* <ProgressBar totalTime={10000} color="green"></ProgressBar> */}
      {/* <div
        id="plot"
        style={{
          marginLeft: "auto",
          marginRight: "auto",
          maxWidth: "1000px",
          marginBottom: "10px",
        }}
      ></div> */}
      {/* <script>
        {`
				var xs = [1, 2, 3, 4, 5];
				var y = xs.map((x) => 1/Math.exp(x));
				var trace1 = {
					x: xs,
					y: y,
					type: 'scatter'
				};

				var data = [trace1];

				Plotly.newPlot('plot', data);
				`}
      </script> */}
      <div
        className="card"
        style={{
          padding: "5px",
          width: "25rem",
          marginLeft: "auto",
          marginRight: "auto",
        }}
      >
        {SocketStatusView({ readyState })}

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
          disabled={experiment.status === "running"}
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
