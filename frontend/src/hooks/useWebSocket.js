import { useEffect, useRef } from "react";

export default function useWebSocket(onMessage) {
  const ws = useRef(null);

  useEffect(() => {
    ws.current = new WebSocket("ws://localhost:8000/ws");

    ws.current.onmessage = (event) => {
      const data = JSON.parse(event.data);
      onMessage(data);
    };

    return () => ws.current.close();
  }, []);

  const sendMessage = (payload) => {
    ws.current.send(JSON.stringify(payload));
  };

  return { sendMessage };
}