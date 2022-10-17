import { useEffect, useState } from "react";

import NavBar from "./components/NavBar";
import Results from "./Results";
import Models from "./Models";
import Trainers from "./Trainers";
import Datasets from "./Datasets";
import ExperimentsOverview from "./ExperimentsOverview";
import { MateSummary } from "./Interfaces";
import useWebSocket, { ReadyState } from "react-use-websocket";
import socket from "./socket";
type View = "default" | "Results" | "Models" | "Trainers" | "Datasets";

enum ConnectionStatus {
  connecting = "connecting",
  connected = "connected",
  disconnected = "disconnected",
}
const App = () => {
  const [connectionStatus, setConnectionStatus] = useState<ConnectionStatus>(
    ConnectionStatus.connecting
  );
  const [mateSummary, setMateSummary] = useState<MateSummary | null>(null);
    useState<MessageEvent | null>(null);
	socket.onopen = () => {
		console.log("Connected to server")
		socket.send(JSON.stringify({type:"get_summary", data:""}))
		setConnectionStatus(ConnectionStatus.connected)
	}
	socket.onclose = () => {
		console.log("Disconnected from server")
		setConnectionStatus(ConnectionStatus.disconnected)
	}
  const [view, setView] = useState("" as View);
  const defaultSections = {
    Results: <Results setSections={() => {}} />,
    Models: <Models models={mateSummary !== null ? mateSummary.models : []} />,
    Trainers: <Trainers />,
    Datasets: <Datasets />,
  } as Record<View, JSX.Element>;
  const [sections, setSections] = useState(defaultSections);
  const [section, setSection] = useState("default");

	socket.onmessage = (event) => {
		const message = JSON.parse(event.data)
		if (message.type === "get_summary"){
			const data = message.data
			setMateSummary(()=>{
        defaultSections["Models"] = <Models models={message.models} />;
				return data
			})
		}
	}
	/*
  useEffect(() => {
    fetch(`http://localhost:3002/summary`)
      .then((res) => res.json())
      .then((data) =>
        setMateSummary(() => {
          defaultSections["Models"] = <Models models={data.models} />;
          // const experiments =
          console.log(data);
          return data;
        })
      );
  }, []);
	*/
  return (
    <div>
      <title>Maté</title>
      <link
        href="https://cdn.jsdelivr.net/npm/bootstrap@5.2.0/dist/css/bootstrap.min.css"
        rel="stylesheet"
        integrity="sha384-gH2yIJqKdNHPEq0n4Mqa/HGKIhSkIHeL5AyhkYV8i59U5AR6csBvApHHNl/vI1Bx"
        crossOrigin="anonymous"
      />
      <script src="//cdn.jsdelivr.net/npm/sweetalert2@11"></script>
      <script src="https://cdn.plot.ly/plotly-2.14.0.min.js"></script>
      <style>
        {`html, body {
				 		background-color: #37474F;
				}	
				`}
      </style>
      <div className="App">
        <NavBar
          title="MateBoard"
          sections={sections}
          defaultSections={defaultSections}
          connectionStatus={connectionStatus}
          defaultSection={
            <ExperimentsOverview
              experiments={mateSummary !== null ? mateSummary.experiments : {}}
              setSections={setSections}
              setSection={setSection}
            />
          }
          setSections={setSections}
          section={section}
          setSection={setSection}
        />
      </div>
      <script
        src="https://cdn.jsdelivr.net/npm/bootstrap@5.2.0/dist/js/bootstrap.bundle.min.js"
        integrity="sha384-A3rJD856KowSb7dwlZdYEkO39Gagi7vIsF0jrRAoQmDKKtQBHUuLZ9AsSv4jD4Xa"
        crossOrigin="anonymous"
      ></script>
    </div>
  );
};

export default App;
