import { Experiment } from "./Interfaces";
// imports the CSS file called ExperimentOverview.css
// import "./ExperimentOverview.css";

import Config from "./ExperimentView/Config";
import Training from "./Training";
import Visualizations from "./Visualizations";
import ExperimentControl from "./ExperimentView/ExperimentControl";

function Status({
  statusValue,
}: {
  statusValue: "running" | "run" | "never-run";
}) {
  const status = {
    running: (
      <div style={{ textAlign: "right", padding: 0 }}>
        <div
          style={{
            transform: "scale(0.5)",
            margin: 0,
            padding: 0,
            maxHeight: "20px",
            width: "100%",
            textAlign: "right",
          }}
        >
          <div
            style={{
              textAlign: "right",
              transform: "scale(0.5)",
              marginTop: -13,
              marginLeft: 0,
              marginRight: -45,
              padding: 0,
              backgroundColor: "white",
              border: "3px solid black",
            }}
            className="loader"
          ></div>
        </div>
      </div>
    ),
    run: (
      <div style={{ textAlign: "right" }}>
        <input
          className="form-check-input mt-0"
          style={{
            width: "25px",
            height: "25px",
            backgroundColor: "green",
            borderRadius: "50%",
            border: "2px solid black",
          }}
          checked
          type="checkbox"
          onClick={() => {}}
          value=""
          aria-label="Checkbox for following text input"
        />
      </div>
    ),
    "never-run": (
      <div style={{ textAlign: "right" }}>
        <input
          style={{
            width: "25px",
            height: "25px",
            borderRadius: "50%",
            backgroundColor: "white",
            border: "2px solid black",
          }}
          disabled
          className="form-check-input mt-0"
          type="checkbox"
          value=""
          aria-label="Checkbox for following text input"
        />
      </div>
    ),
  };
  return status[statusValue];
}
export default function ({
  experiments,
  setSections,
  setSection,
  //lastMessage,
  //sendJsonMessage,
}: {
  experiments: Record<string, Experiment>;
  setSections: (sections: Record<string, JSX.Element>) => void;
  setSection: (section: string) => void;
  //lastMessage: MessageEvent | null;
  //sendJsonMessage: (message: MessageEvent) => void;
}) {
  return (
    <div style={{ textAlign: "center", marginTop: "9vh" }}>
      <nav className="navbar fixed-bottom navbar-light bg-light">
        <a className="navbar-brand" style={{ marginLeft: "1vw" }} href="#">
          New Experiment
        </a>
      </nav>
      <div className="list-group" style={{ marginTop: "3vh" }}>
        {Object.entries(experiments).map(([localName, experiment]) => (
          <div
            onClick={() => {
              setSections({
                Control: (
                  <ExperimentControl
                    experiment={experiment}
                    experimentId={localName}
                    //lastMessage={lastMessage}
                    // sendJsonMessage={sendJsonMessage}
                  />
                ),
                Config: <Config experimentId={localName} />,
                Training: <Training />,
                Visualizations: <Visualizations />,
              } as Record<string, JSX.Element>);
              setSection("Control");
            }}
            className="list-group-item list-group-item-action flex-column align-items-start"
            style={{
              marginLeft: "auto",
              marginRight: "auto",
              backgroundColor: "#D0FFC6",
              maxWidth: "500px",
            }}
          >
            <div className="card-body">
              <h5 className="card-title">{localName}</h5>
              <p className="card-text">{experiment.description}</p>
              <table style={{ width: "100%" }}>
                <tbody>
                  <tr>
                    <td style={{ textAlign: "left" }}></td>
                    <td>
                      <Status statusValue={experiment.status} />
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
