import { Experiment } from "../Interfaces";
import ProgressBar from "./ProgressBar";

export default ({ experiment }: { experiment: Experiment }) => {
  return (
    <div style={{ textAlign: "center", width: "100%" }}>
      {/*
			<ProgressBar totalTime={100} color="red"></ProgressBar>
			*/}
      <ProgressBar totalTime={10000} color="green"></ProgressBar>
      <div
        id="plot"
        style={{
          marginLeft: "auto",
          marginRight: "auto",
          maxWidth: "1000px",
          marginBottom: "10px",
        }}
      ></div>
      <script>
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
      </script>
      <div
        className="card"
        style={{
          padding: "5px",
          width: "25rem",
          marginLeft: "auto",
          marginRight: "auto",
        }}
      >
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
