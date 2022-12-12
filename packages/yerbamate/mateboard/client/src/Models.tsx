import { Package } from "./Interfaces";
import Swal from "sweetalert2";

export default function ({ models }: { models: Package[] }) {
  const installNewModel = () => {
    Swal.fire({
      title: "Enter Git URL",
      input: "text",
      inputAttributes: {
        autocapitalize: "off",
      },
      showCancelButton: true,
      confirmButtonText: "Install",
      showLoaderOnConfirm: true,
      preConfirm: (login) => {},
      allowOutsideClick: () => !Swal.isLoading(),
    }).then((result) => {
      if (result.isConfirmed) {
      }
    });
  };
  console.log(models);
  return (
    <div style={{ textAlign: "center", marginTop: "10vh" }}>
      <div style={{ textAlign: "center", width: "100%" }}>
        <button
          type="button"
          className="btn btn-success"
          onClick={installNewModel}
          style={{
            textAlign: "center",
            marginBottom: "10px",
            borderRadius: "50%",
            maxHeight: "43px",
            maxWidth: "43px",
          }}
        >
          <span style={{ marginLeft: "auto", marginRight: "auto" }}>+</span>
        </button>
      </div>
      {Object.entries(models).map((entry) => {
        const [localName, model] = entry;
        return (
          <div
            className="card"
            style={{
              width: "25rem",
              display: "block",
              marginLeft: "auto",
              marginRight: "auto",
              marginBottom: "5px",
              backgroundColor: "#D0FFC6",
            }}
          >
            <div className="card-body">
              <h5 className="card-title">Local Name: {localName}</h5>
              <p className="card-text">{model.description}</p>
              <a style={{ fontSize: "15px" }} href={model.url} target="_blank">
                {model.url}
              </a>
            </div>
          </div>
        );
      })}
    </div>
  );
}
