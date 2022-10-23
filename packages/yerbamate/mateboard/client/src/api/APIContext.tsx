import React from "react";
import { useContext } from "react";
import { ReadyState } from "react-use-websocket";
import { PageState } from "./data/AppState";

export const APIContext = React.createContext({
  viewState: PageState.MainPage,
  experiments: [],
  selectedExperiment: null,
  socketState: ReadyState.UNINSTANTIATED,
});
