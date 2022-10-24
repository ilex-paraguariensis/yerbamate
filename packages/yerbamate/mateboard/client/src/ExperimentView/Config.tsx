import { useEffect, useRef, useState } from "react";
import getDAG from "./get_dag";
// @ts-ignore
import BombillaExplorer from "./BombillaExplorer";
import socket from "../socket";
import exp from "constants";

const getNetwork = (
  nodes: Map<string, Record<string, any>>,
  edges: [string, string, string[]][],
  container: HTMLDivElement,
  simplify = false
) => {
  if (simplify) {
    // Simplify the graph, removing nodes with only one edge
    const countEdges = (nodeId: string) => {
      let count = 0;
      for (const edge of edges) {
        if (edge[0] === nodeId || edge[1] === nodeId) {
          count++;
        }
      }
      return count;
    };
    for (const node of nodes.keys()) {
      if (node === "data") {
        debugger;
      }
      if (countEdges(node) === 1) {
        nodes.delete(node);
        // detele edges too
        for (let i = edges.length - 1; i >= 0; i--) {
          if (edges[i][0] === node || edges[i][1] === node) {
            edges.splice(i, 1);
          }
        }
      }
    }
  }
  // @ts-ignore
  const netNodes = new window.vis.DataSet(
    Array.from(nodes.keys()).map((key) => ({
      id: key,
      label: key,
      shape: "box",
    }))
  );
  // @ts-ignore
  const graphEdges = new window.vis.DataSet(
    edges.map(([source, target, path], i) => ({
      id: String(i) + path.join("."),
      from: source,
      to: target,
      label: path.join("."),
      directed: true,
      arrows: "to",
    }))
  );
  const netData = {
    nodes: netNodes,
    edges: graphEdges,
  };
  const options = {
    physics: false,
    layout: {
      randomSeed: 1,
      improvedLayout: true,
      hierarchical: {
        enabled: false,
      },
    },
    edges: {
      smooth: {
        enabled: false,
      },
      scaling: {
        min: 4,
        max: 15,
      },
    },
  };
  // @ts-ignore
  return new window.vis.Network(container, netData, options);
};
const views = ["graph", "explorer"];
const Config = ({
  experimentId,
  experiment,
}: {
  experimentId: string;
  experiment: Record<string, any>;
}) => {
  const [bombilla, setBombilla] = useState<Record<string, any>>(experiment);
  const [view, setView] = useState<string>("explorer");
  const [backExplorer, setBackExplorer] = useState<(() => void) | null>(null);
  const [dag, setDag] = useState<{
    nodes: Map<string, Record<string, any>>;
    edges: [string, string, string[]][];
  }>(getDAG(JSON.parse(JSON.stringify(experiment))));
  // loads bombilla which is a json file
  //@ts-ignore
  if (typeof vis !== "undefined") {
    // @ts-ignore
    window.vis = vis;
    console.log("vis is defined");
  }
  const div = useRef<HTMLDivElement>(null);
  useEffect(() => {
    if (view === "graph") {
      if (div.current !== null) {
        getNetwork(dag.nodes, dag.edges, div.current, false);
      }
    }
  }, [view]);
  /*
  useEffect(() => {
    socket.send(JSON.stringify({ type: "get_summary", data: "" }));
    socket.onmessage = (msg) => {
      const data = JSON.parse(msg.data).data.experiments[experimentId];
      setBombilla(data);
      const dag = getDAG(data);
      setDag(dag);
    };
  }, []);
	*/
  console.log(bombilla);
  // loads visjs
  const marginTop = 70;
  return (
    <>
      {dag &&
        (view === "explorer" ? (
          <BombillaExplorer
            nodes={new Map(dag.nodes)}
            edges={dag.edges.slice()}
            bombilla={Object.assign({}, bombilla)}
            setBackExplorer={setBackExplorer}
          />
        ) : (
          <div
            ref={div}
            style={{
              width: "100%",
              height: `calc(100vh - ${marginTop}px)`,
            }}
          />
        ))}
      <nav
        className="navbar fixed-bottom navbar-expand-lg"
        style={{ backgroundColor: "rgba(255, 255, 255, 0.14)", zIndex: 10000 }}
      >
        <ul className="navbar-nav me-auto mb-2 mb-lg-0">
          <div
            className={
              "btn btn-" + (view === "explorer" ? "secondary" : "disabled")
            }
            key={"ciao"}
            style={{ marginLeft: "10px" }}
            onClick={backExplorer !== null ? backExplorer : () => {}}
          >
            <img height={"30vh"} src="back-arrow.png"></img>
          </div>
          {views.map((viewItem, i) => (
            <div
              onClick={() => setView(viewItem)}
              key={i.toString()}
              className={
                "btn btn-" + (viewItem === view ? "primary" : "secondary")
              }
              style={{ marginLeft: "10px" }}
            >
              {viewItem}
            </div>
          ))}
        </ul>
      </nav>
    </>
  );
};
export default Config;
