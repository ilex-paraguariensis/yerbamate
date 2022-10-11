export default function NavBar({
  title,
  sections,
  defaultSections,
  defaultSection,
  setSections,
  setSection,
  section,
}: {
  title: string;
  sections: Record<string, JSX.Element>;
  defaultSections: Record<string, JSX.Element>;
  defaultSection: JSX.Element;
  setSections: (sections: Record<string, JSX.Element>) => void;
  setSection: (section: string) => void;
  section: string;
}) {
  console.assert(Object.keys(sections).length > 0);
  // const [view, setView] = useState("default");
  return (
    <div>
      <nav
        className="navbar fixed-top navbar-expand-lg"
        style={{ backgroundColor: "#6AA84F" }}
      >
        <div className="container-fluid">
          <a
            className="navbar-brand"
            onClick={() => {
              setSection("default");
              setSections(defaultSections);
            }}
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
                .map((sectionName) => (
                  <li className="nav-item">
                    <a
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
          </div>
        </div>
      </nav>
      <div style={{ marginTop: "10vh" }}></div>
      {section === "default" ? defaultSection : sections[section]}
    </div>
  );
}
