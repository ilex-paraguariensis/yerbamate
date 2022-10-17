import React, { useCallback, useEffect, useState } from "react";
import { useBetween } from "use-between";
import useWebSocket, { ReadyState } from "react-use-websocket";

const SocketAPIHook = () => {
  const [socketUrl, setSocketUrl] = useState("ws://localhost:8765");
  const [messageHistory, setMessageHistory] = useState(
    [] as Array<MessageEvent>
  );
  const [connectionStatusListener, setConnectionStatusListener] = useState({
    onError: (event: Event) => {},
    onOpen: (event: Event) => {},
    onClose: (event: Event) => {},
  });
  const { sendMessage, sendJsonMessage, lastMessage, readyState } =
    useWebSocket(socketUrl, connectionStatusListener, true);

  useEffect(() => {
    if (lastMessage !== null) {
      setMessageHistory((prev) => prev.concat(lastMessage));
    }
  }, [lastMessage, setMessageHistory]);

  return {
    sendMessage,
    sendJsonMessage,
    lastMessage,
    connection_state: readyState,
    messageHistory,
    socketUrl,
    setSocketUrl,
    setConnectionStatusListener,
    connectionStatusListener,
  };
};

const useSharedAPI = () => useBetween(SocketAPIHook);

export default SocketAPIHook;
