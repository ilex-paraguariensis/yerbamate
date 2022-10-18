import { useEffect, useRef, useState } from "react";
import getDAG from "./get_dag";
import vis from "vis-network";
import BombillaExplorer from "./BombillaExplorer";
import socket from "../socket";

const getNetwork = (
  nodes: Map<string, Record<string, any>>,
  edges: [string, string, string[]][],
  container: HTMLDivElement,
  simplify = true,
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
    })),
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
    })),
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
const Config = ({ experimentId }: { experimentId: string }) => {
  const [bombilla, setBombilla] = useState<Record<string, any> | null>(null);
  const [dag, setDag] = useState<
    {
      nodes: Map<string, Record<string, any>>;
      edges: [string, string, string[]][];
    } | null
  >(null);
  // loads bombilla which is a json file
  if (vis !== undefined) {
    // @ts-ignore
    window.vis = vis;
    console.log("vis is defined");
  }
  const div = useRef<HTMLDivElement>(null);
  socket.send(JSON.stringify({ type: "get_summary", data: "" }));
  socket.onmessage = (msg) => {
    const data = JSON.parse(msg.data).data.experiments[experimentId];
    setBombilla(data);
    const dag = getDAG(data);
    setDag(dag);
  };
  /*
  useEffect(() => {
    fetch(`http://localhost:3002/summary`)
      .then((response) => response.json())
      .then((data) => {
        data = data.experiments[experimentId];
        setBombilla(data);
        const dag = getDAG(data);
        setDag(dag);
        const { edges, nodes } = dag;
        // getNetwork(nodes, edges, div.current!, false);
      });
  }, []);
	*/
  console.log(bombilla);
  // loads visjs
	const marginTop = 70
  useEffect(() => {}, [1]);
  return (
    <div style={{marginTop:marginTop}}>
      <link
        href="https://cdn.jsdelivr.net/npm/bootstrap@5.2.2/dist/css/bootstrap.min.css"
        rel="stylesheet"
      />
      <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.2.2/dist/js/bootstrap.bundle.min.js">
      </script>
      {
        /*
      <script
        src="https://cdnjs.cloudflare.com/ajax/libs/vis/4.21.0/vis.min.js"
        integrity="sha512-XHDcSyqhOoO2ocB7sKOCJEkUjw/pQCJViP1ynpy+EGh/LggzrP6U/V3a++LQTnZT7sCQKeHRyWHfhN2afjXjCg=="
      ></script>
			*/
      }
      {
        /*
      <div
        id="mynetwork"
        style={{ height: "100vh", width: "100vw" }}
        ref={div}
      />
			*/
      }
      {dag && (
        <BombillaExplorer
          nodes={dag.nodes}
          edges={dag.edges}
          bombilla={bombilla}
        />
      )}
    </div>
  );
};
export default Config;
