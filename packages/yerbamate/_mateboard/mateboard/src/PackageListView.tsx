import { Package } from "./Interfaces";

export default ({ packages }: { packages: Record<string, Package> }) => {
  return (
    <div className="list-view">
      {Object.entries(packages).map(([name, pkg]) => (
        <div className="list-view-item">
          <div className="list-view-item-name">{name}</div>
          <div className="list-view-item-version">{pkg.version}</div>
          <div className="list-view-item-description">{pkg.description}</div>
          <div className="list-view-item-author">{pkg.author}</div>
          <div className="list-view-item-license">{pkg.license}</div>
        </div>
      ))}
    </div>
  );
};
