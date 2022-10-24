import { useEffect, useState } from "react";

import NavBar from "./components/NavBar";
import ExperimentsTracker from "./ExperimentsTracker";
import Models from "./Models";
import Trainers from "./Trainers";
import Data from "./Data";
import ExperimentsOverview from "./ExperimentsOverview";
import { MateSummary } from "./Interfaces";
import ModulesList from "./components/ModulesList";
import socket from "./socket";
type View = "default" | "Tracker" | "Models" | "Trainers" | "Data";

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
    console.log("Connected to server");
    socket.send(JSON.stringify({ type: "get_summary", data: "" }));
    setConnectionStatus(ConnectionStatus.connected);
  };
  socket.onclose = () => {
    console.log("Disconnected from server");
    setConnectionStatus(ConnectionStatus.disconnected);
  };
  const [view, setView] = useState("" as View);
  let defaultSections = {
    Tracker: <ExperimentsTracker />,
    Models: (
      <ModulesList
        name="models"
        modules={mateSummary !== null ? mateSummary.models : []}
      />
    ),
    Trainers: (
      <ModulesList
        name="trainers"
        modules={mateSummary !== null ? mateSummary.trainers : []}
      />
    ),
    Data: (
      <ModulesList
        name="data"
        modules={mateSummary !== null ? mateSummary.data : []}
      />
    ),
  } as Record<View, JSX.Element>;
  const [sections, setSections] = useState(defaultSections);
  const [section, setSection] = useState("default");

  socket.onmessage = (event) => {
    const message = JSON.parse(event.data);
    console.log("Got message", message);
    if (message.type === "get_summary") {
      const data = message.data;
      setMateSummary(() => {
        setSections(() => {
          return {
            Tracker: <ExperimentsTracker />,
            Models: (
              <ModulesList
                name="models"
                modules={data !== null ? data.models : []}
              />
            ),
            Trainers: (
              <ModulesList
                name="trainers"
                modules={data !== null ? data.trainers : []}
              />
            ),
            Data: (
              <ModulesList
                name="data"
                modules={data !== null ? data.data : []}
              />
            ),
          } as Record<View, JSX.Element>;
        });
        return data;
      });
    }
  };
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
				 		background-color: #121212;
						color: white
				}	
				`}
      </style>
      <div className="App">
        <NavBar
          title="MatéBoard"
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
