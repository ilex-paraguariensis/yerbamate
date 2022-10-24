interface DeepJSONValue {
  [key: string]: JSONValue;
}
type JSONValue =
  | string
  | number
  | boolean
  | { [x: string]: JSONValue }
  | Array<JSONValue>;

interface Result {
  dataset: string;
  experiments: {
    name: string;
    metrics: Record<string, number>;
  }[];
}
interface Package {
  url: string;
  author: string;
  category: string;
  description: string;
  license: string;
  backbone: "lightning" | "keras" | "jax";
  type: string;
  version: string;
  exports: {
    classes: {
      class_name: string;
      module: string;
      params: Record<string, JSONValue>;
      samples: {
        experiment: Record<string, JSONValue>;
        sample: Record<string, JSONValue>;
      };
    }[];
    functions: {}[];
  };
}
interface PackageReference {
  id: string;
  args: DeepJSONValue;
}
interface Experiment {
  id: string;
  status: "running" | "run" | "never-run";
  name: string;
  description: string;
  config: {
    dataset: PackageReference;
    trainers: PackageReference;
  };
}
interface MateSummary {
  models: Package[];
  trainers: Package[];
  data: Package[];
  experiments: Record<string, Experiment>;
}
interface ExperimentResult {
  id: string;
  metrics: Record<string, number>;
}

export type { Experiment, MateSummary, Package, Result };
