// enum class
export enum PageState {
  MainPage,
  ExperimentOverview,
  UpdateExperiment,
  About,
  Other,
}

export default {
  viewState: PageState.MainPage,
  experiments: [],
  selectedExperiment: null,
};
