import Iframe from 'react-iframe'
export default ({
  setSections,
}: {
  setSections: (sections: Record<string, JSX.Element>) => void;
}) => {
	const height = window.innerHeight;
  return (
		<Iframe url="http://127.0.0.1:8000/" width="100%" height={height + "px"}/>
  );
};
