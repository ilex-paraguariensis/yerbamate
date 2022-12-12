import { Package } from "../Interfaces";

export default ({
  name,
  modules,
}: {
  name: string;
  modules: Record<string, any>;
}) => {
  const deepModules = ["data"];
  let flattenedModules = modules;
  if (deepModules.includes(name)) {
    const currentModules = modules as Record<string, Record<string, Package>>;
    const flattened: Record<string, Package> = {};
    for (const [key, value] of Object.entries(currentModules)) {
      for (const [subkey, subvalue] of Object.entries(value)) {
        flattened[`${key}.${subkey}`] = subvalue;
      }
    }
    flattenedModules = flattened;
  }
  return (
    <div style={{ width: "100%", textAlign: "center" }}>
      <div
        className="list-group w-50"
        style={{ marginTop: "7vh", marginLeft: "auto", marginRight: "auto" }}
      >
        {Object.entries(flattenedModules).map(([name, module], index) => (
          <div
            className="list-group-item list-group-item-action flex-column align-items-start"
            key={index}
          >
            <h5>{name}</h5>
            {module.url}
          </div>
        ))}
      </div>
    </div>
  );
};
