import { useEffect, useState } from "react";

import NavBar from "./NavBar";
import Results from "./Results";
import Models from "./Models";
import Trainers from "./Trainers";
import Datasets from "./Datasets";
import ExperimentsOverview from "./ExperimentsOverview";
import { MateSummary } from "./Interfaces";

type View = "default" | "Results" | "Models" | "Trainers" | "Datasets";

const App = () => {
  const [mateSummary, setMateSummary] = useState({
    models: [],
    experiments: [],
  } as unknown as MateSummary);
  const [view, setView] = useState("" as View);
  const defaultSections = {
    Results: <Results setSections={()=>{}}/>,
    Models: <Models models={mateSummary.models} />,
    Trainers: <Trainers />,
    Datasets: <Datasets />,
  } as Record<View, JSX.Element>;
  const [sections, setSections] = useState(defaultSections);
  const [section, setSection] = useState("default");
  useEffect(() => {
    fetch(`http://localhost:3001/mate_summary`)
      .then((res) => res.json())
      .then((data) =>
        setMateSummary(() => {
          defaultSections["Models"] = <Models models={data.models} />;
          // const experiments =

          return data;
        })
      );
  }, [1]);
  const experiments = mateSummary.experiments;

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
          defaultSection={
            <ExperimentsOverview
              experiments={experiments}
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
