import {Package} from "../Interfaces"

const ModulesList = (props: { modules: Package[] }) => {
	const { modules } = props
	return (
		<div>
			{modules.map((module, index) => (
				<div key={index}>{module.url}</div>
			))}
		</div>
	)
}
