import ResultDisplay from "./Results/ResultDisplay";
import { Result } from "./Interfaces";
export default ({
  setSections,
}: {
  setSections: (sections: Record<string, JSX.Element>) => void;
}) => {
  const results: Result[] = [
    {
      dataset: "MNIST",
      experiments: [
        {
          name: "ResNet",
          metrics: {
            Accuracy: 0.95,
            Precision: 0.95,
            Recall: 0.95,
          },
        },
        {
          name: "ViT",
          metrics: {
            Accuracy: 0.95,
            Precision: 0.95,
            Recall: 0.95,
          },
        },
      ],
    },
    {
      dataset: "CIFAR10",
      experiments: [
        {
          name: "ResNet",
          metrics: {
            Accuracy: 0.8,
            Precision: 0.95,
            Recall: 0.95,
          },
        },
        {
          name: "ViT",
          metrics: {
            Accuracy: 0.95,
            Precision: 0.95,
            Recall: 0.95,
          },
        },
      ],
    },
  ];
  return (
    <div style={{ marginTop: "10vh", textAlign: "center" }}>
      {results.map((result) => <ResultDisplay result={result} />)}
    </div>
  );
};
