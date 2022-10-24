import { useEffect, useState } from "react";

import NavBar from "./components/NavBar";
import Config from "./ExperimentView/Config";
import ExperimentControl from "./ExperimentView/ExperimentControl";
import { MateSummary } from "./Interfaces";

type View = "default" | "Config";
export default ({ experimentId }: { experimentId: string }) => {
  const [mateSummary, setMateSummary] = useState<MateSummary | null>(null);
  const [view, setView] = useState("" as View);
  const experiment = Object.entries(
    mateSummary !== null ? mateSummary.experiments : {}
  ).filter(([key, e]) => e.id === experimentId)[0][1];
  console.log(mateSummary);
  /*
  useEffect(() => {
    fetch(`../mate_summary.json`)
      .then((res) => {
        console.log(res);
        return res.json();
      })
      .then((data) => {
        console.log("mate summary recieved", data);
        setMateSummary(data);
      });
  }, []);
	*/
  const defaultSections = {
    default: (
      <ExperimentControl experiment={experiment} experimentId={experimentId} />
    ),
    Config: <Config experimentId={experimentId} experiment={experiment} />,
  } as Record<View, JSX.Element>;
  return (
    <div>
      <link
        href="https://cdn.jsdelivr.net/npm/bootstrap@5.2.0/dist/css/bootstrap.min.css"
        rel="stylesheet"
        integrity="sha384-gH2yIJqKdNHPEq0n4Mqa/HGKIhSkIHeL5AyhkYV8i59U5AR6csBvApHHNl/vI1Bx"
        crossOrigin="anonymous"
      />
      <div className="App"></div>
      <script
        src="https://cdn.jsdelivr.net/npm/bootstrap@5.2.0/dist/js/bootstrap.bundle.min.js"
        integrity="sha384-A3rJD856KowSb7dwlZdYEkO39Gagi7vIsF0jrRAoQmDKKtQBHUuLZ9AsSv4jD4Xa"
        crossOrigin="anonymous"
      ></script>
    </div>
  );
};
