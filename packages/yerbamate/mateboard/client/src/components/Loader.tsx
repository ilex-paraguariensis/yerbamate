import "./Loader.css";

export default ({ show }: { show: boolean }) =>
  show ? (
    <div
      className="scene"
      style={{
        height: "100%",
        width: "100%",
        paddingTop: "15vh",
        transform: "scale(0.5)",
      }}
    >
      <div className="plane">
        <div className="cube cube--0">
          <div className="cube__side"></div>
          <div className="cube__side"></div>
          <div className="cube__side"></div>
          <div className="cube__side"></div>
          <div className="cube__side"></div>
          <div className="cube__side"></div>
        </div>
        <div className="shadow shadow--0"></div>
        <div className="cube cube--1">
          <div className="cube__side"></div>
          <div className="cube__side"></div>
          <div className="cube__side"></div>
          <div className="cube__side"></div>
          <div className="cube__side"></div>
          <div className="cube__side"></div>
        </div>
        <div className="shadow shadow--1"></div>
        <div className="cube cube--2">
          <div className="cube__side"></div>
          <div className="cube__side"></div>
          <div className="cube__side"></div>
          <div className="cube__side"></div>
          <div className="cube__side"></div>
          <div className="cube__side"></div>
        </div>
        <div className="shadow shadow--2"></div>
        <div className="cube cube--3">
          <div className="cube__side"></div>
          <div className="cube__side"></div>
          <div className="cube__side"></div>
          <div className="cube__side"></div>
          <div className="cube__side"></div>
          <div className="cube__side"></div>
        </div>
        <div className="shadow shadow--3"></div>
        <div className="cube cube--4">
          <div className="cube__side"></div>
          <div className="cube__side"></div>
          <div className="cube__side"></div>
          <div className="cube__side"></div>
          <div className="cube__side"></div>
          <div className="cube__side"></div>
        </div>
        <div className="shadow shadow--4"></div>
        <div className="cube cube--5">
          <div className="cube__side"></div>
          <div className="cube__side"></div>
          <div className="cube__side"></div>
          <div className="cube__side"></div>
          <div className="cube__side"></div>
          <div className="cube__side"></div>
        </div>
        <div className="shadow shadow--5"></div>
        <div className="cube cube--6">
          <div className="cube__side"></div>
          <div className="cube__side"></div>
          <div className="cube__side"></div>
          <div className="cube__side"></div>
          <div className="cube__side"></div>
          <div className="cube__side"></div>
        </div>
        <div className="shadow shadow--6"></div>
        <div className="cube cube--7">
          <div className="cube__side"></div>
          <div className="cube__side"></div>
          <div className="cube__side"></div>
          <div className="cube__side"></div>
          <div className="cube__side"></div>
          <div className="cube__side"></div>
        </div>
        <div className="shadow shadow--7"></div>
      </div>
    </div>
  ) : null;
