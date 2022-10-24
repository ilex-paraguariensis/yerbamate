import Iframe from "react-iframe";
export default () => {
  const windowHeight = window.innerHeight;
  const marginTop = 70; //Math.round(windowHeight*0.06
  const height = window.innerHeight - marginTop;
  return (
    <div style={{ marginTop: marginTop + "px" }}>
      <Iframe
        url="http://127.0.0.1:8000/runs"
        width="100%"
        height={height + "px"}
      />
    </div>
  );
};
