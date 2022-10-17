import { useEffect, useState } from "react";

export default ({ totalTime, color }: { totalTime: number; color: string }) => {
  const [time, setTime] = useState(0);
  const clear = useEffect(() => {
    const interval = setInterval(() => {
      if (time <= 101) {
        console.log("ho");
        setTime((prevTime) => prevTime + 1);
      } else {
        console.log("hu");
        setTime(0);
      }
    }, totalTime / 100);
    return () => clearInterval(interval);
  }, []);
  return (
    <div
      className="progress"
      style={{
        maxWidth: "1000px",
        marginLeft: "auto",
        marginRight: "auto",
        marginBottom: "10px",
      }}
    >
      <div
        className={`progress-bar progress-bar-striped ${
          color === "red" ? "bg-danger" : "bg-success"
        }`}
        role="progressbar"
        style={{ width: `${time}%` }}
        aria-valuenow={50}
        aria-valuemin={0}
        aria-valuemax={100}
      ></div>
    </div>
  );
};
