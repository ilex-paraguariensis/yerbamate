export default function NavBar({
  title,
  sections,
  defaultSections,
  defaultSection,
  setSections,
  setSection,
  section,
  connectionStatus,
}: {
  title: string;
  sections: Record<string, JSX.Element>;
  defaultSections: Record<string, JSX.Element>;
  defaultSection: JSX.Element;
  setSections: (sections: Record<string, JSX.Element>) => void;
  setSection: (section: string) => void;
  section: string;
  connectionStatus: string;
}) {
  console.assert(Object.keys(sections).length > 0);
  // const [view, setView] = useState("default");
  return (
    <div>
      <nav
        className="navbar fixed-top navbar-expand-lg"
        style={{
          backgroundColor: "rgba(255, 255, 255, 0.14)",
          color: "white",
          zIndex: 100,
        }}
      >
        <div className="container-fluid">
          <a
            className="navbar-brand"
            onClick={() => {
              setSection("default");
              setSections(defaultSections);
            }}
            style={{ color: "rgb(50, 168, 82)", fontWeight: "bold" }}
          >
            {title}
          </a>
          <button
            className="navbar-toggler"
            type="button"
            data-bs-toggle="collapse"
            data-bs-target="#navbarSupportedContent"
            aria-controls="navbarSupportedContent"
            aria-expanded="false"
            aria-label="Toggle navigation"
          >
            <span className="navbar-toggler-icon"></span>
          </button>
          <div className="collapse navbar-collapse" id="navbarSupportedContent">
            <ul className="navbar-nav me-auto mb-2 mb-lg-0">
              {Object.keys(sections)
                .filter((x) => x !== "default")
                .map((sectionName, i) => (
                  <li key={String(i)} className="nav-item">
                    <a
                      style={{ color: "rgb(50, 168, 82)" }}
                      className={`nav-link ${
                        sectionName === section && "active"
                      }`}
                      aria-current="page"
                      onClick={() => {
                        setSection(sectionName);
                      }}
                    >
                      {sectionName}
                    </a>
                  </li>
                ))}
            </ul>
            <ul className="navbar-nav justify-content-end">
              <li key="status" className="nav-item">
                <span
                  className={"nav-link ms-auto"}
                  style={{
                    color: "green",
                    fontSize: "0.7em",
                    marginTop: "0.3em",
                  }}
                >
                  {connectionStatus === "connected" ? "🟢" : "🔴"}
                </span>
              </li>
            </ul>
          </div>
        </div>
      </nav>
      {section === "default" ? defaultSection : sections[section]}
    </div>
  );
}
