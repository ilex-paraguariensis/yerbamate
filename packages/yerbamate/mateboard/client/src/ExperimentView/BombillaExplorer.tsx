import { useEffect, useState } from "react";

type Module = {
  object_key: string;
  class_name: string;
  module: string;
  params: Record<string, any>;
};
const isSimpleType = (obj: any) => {
  return (
    typeof obj === "string" ||
    typeof obj === "number" ||
    typeof obj === "boolean" ||
    obj === null
  );
};
const re = RegExp("{(.*?)}");
const render = (value: any, indent = 20): any => {
  if (typeof value === "string" && re.test(value)) {
    return re.test(value) ? (
      <span
        className="badge rounded-pill bg-success"
        style={{ textAlign: "center" }}
      >
        <span style={{ marginLeft: "auto", marginRight: "auto" }}>
          {re.exec(value)![1]}
        </span>
      </span>
    ) : (
      JSON.stringify(value)
    );
  } else if (isSimpleType(value)) {
    return JSON.stringify(value);
  } else {
    return Array.isArray(value) ? (
      <p>
        {value.map((val) => (
          <div style={{ textIndent: indent + "px" }}>
            {render(val, indent + 20)}
          </div>
        ))}
      </p>
    ) : (
      <p>
        &#123;
        {Object.entries(value).map(([key, value]) => (
          <div style={{ textIndent: indent + "px" }}>
            {key}: {render(value, indent + 20)}
          </div>
        ))}
        <div style={{ textIndent: indent - 20 + "px" }}>&#125;</div>
      </p>
    );
  }
};
const Card = ({
  listKey,
  module,
  selectNode,
}: {
  listKey: number;
  module: Module;
  selectNode: (node: Record<string, any>) => void;
}) => {
  const capitalizeFirstLetter = (val: string) => {
    return val.charAt(0).toUpperCase() + val.slice(1);
  };
  const toSingular = (val: string) => {
    return val.at(-1) === "s" ? val.slice(0, -1) : val;
  };
  const folders = ["data", "trainers", "models"];
  type Folder = "data" | "trainers" | "models";
  const rootModule = module.module.split(".")[0];
  const isInternalModule = folders.includes(rootModule);
  const renderingColor = {
    data: "bg-primary",
    trainers: "bg-success",
    models: "bg-warning",
  };
  return (
    <a
      key={listKey}
      href="#"
      className={
        "list-group-item list-group-item-action flex-column align-items-start" +
        (isInternalModule
          ? " " + renderingColor[rootModule as Folder]
          : " bg-danger")
      }
      onClick={() => selectNode(module)}
      style={{ zIndex: 0 }}
    >
      <div className="d-flex w-100 justify-content-between">
        {/*<h5 className="mb-1">Name: {module.object_key}</h5>*/}
        <h5 className="mb-1">
          {isInternalModule
            ? toSingular(capitalizeFirstLetter(module.module.split(".")[0]))
            : ""}
        </h5>
        <small>edit</small>
      </div>
      <p className="mb-1">
        <small>{module.module}</small>
        <h5>{module.class_name}</h5>
      </p>
      {module.params &&
        Object.entries(module.params).map(([key, value]) => (
          <div className="input-group mb-3">
            <div className="input-group-prepend">
              <span className="input-group-text" id="basic-addon1">
                {key}
              </span>
            </div>
            <div
              className="form-control enabled"
              aria-label="Username"
              aria-describedby="basic-addon1"
              style={{ textAlign: "left" }}
            >
              {render(value)}
            </div>
          </div>
        ))}
    </a>
  );
};
const at = (obj: any, path: string[]) => {
  return path.reduce((xs, x) => (xs && xs[x] ? xs[x] : null), obj);
};
const setAt = (obj: any, path: string[], value: any) => {
  const last = path.pop() as string;

  const parent = path.reduce((xs, x) => (xs && xs[x] ? xs[x] : null), obj);
  if (parent) {
    parent[last] = value;
  }
};
const BombillaExplorer = ({
  nodes,
  edges,
  bombilla,
  setBackExplorer,
}: {
  nodes: Map<string, Record<string, any>>;
  edges: [string, string, string[]][];
  bombilla: any;
  setBackExplorer: (c: () => void) => void;
}) => {
  const minPath = Array.from(nodes.values()).reduce((min, node) => {
    return node._path.length < min ? node._path.length : min;
  }, Infinity);
  const [lastSelectedNode, setLastSelectedNode] = useState<Record<
    string,
    any
  > | null>(null);
  // const rootNodes = Array.from(nodes.values()).filter(
  //   (n) => n._path.length === minPath
  // );
  const folders = ["trainers", "models", "data"];
  const rootNodes = Array.from(nodes.values()).filter(
    (n) => folders.indexOf(n.module.split(".")[0]) !== -1
  );
  const [selectedNodes, setSelectedNodes] = useState(rootNodes);
  useEffect(() => {
    setBackExplorer(() => () => {
      console.log("back");
      if (lastSelectedNode) {
        selectNode(lastSelectedNode);
      }
    });
  }, []);
  const selectNode = (node: Record<string, any>) => {
    setLastSelectedNode(() => node);
    // selects the node and all its children using the edges
    const selected = [
      node,
      ...edges
        .filter((edge) => edge[1] === node.object_key)
        .map((edge) => nodes.get(edge[0])),
    ] as Record<string, any>[];
    const uniqueSelected = Array.from(
      new Set(selected.map((n) => n.object_key)).values()
    ).map((key) => nodes.get(key)) as Record<string, any>[];
    setSelectedNodes(uniqueSelected);
  };
  return (
    <div
      className="list-group w-50"
      style={{
        marginLeft: "auto",
        marginRight: "auto",
        marginTop: "7vh",
        height: "85vh",
        overflowY: "scroll",
      }}
      /*
      style={{
        marginLeft: "auto",
        marginRight: "auto",
        // marginTop: "7vh",
        // maxHeight: "70vh",
        textAlign: "center",
        // zIndex: 1000,
				zIndex: 0,
      }}
			*/
    >
      {selectedNodes.map((node, i) => {
        const edgesToNode = edges.filter((edge) => edge[1] === node.object_key);
        console.log(node.object_key);
        /*
			for (const edge of edgesToNode) {
				const [from, to, path] = edge;
				if (from === "optimizer"){
							debugger;
						}
				setAt(bombilla, path, "ref:" + from);
				console.log(node)
			}
			*/
        console.log(node);
        return (
          <Card
            key={i}
            listKey={i}
            module={node as Module}
            selectNode={selectNode}
          />
        );
      })}
    </div>
  );
};

export default BombillaExplorer;
