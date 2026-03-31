import { useState, useEffect } from "react";
import InputBox from "./InputBox";

export default function ChatWindow() {
  const [messages, setMessages] = useState([]);
  const [ws, setWs] = useState(null);

  useEffect(() => {
    const socket = new WebSocket("ws://localhost:8000/ws");

    socket.onmessage = (event) => {
      const data = JSON.parse(event.data);
      setMessages((prev) => [
        ...prev,
        { role: "ai", text: data.answer }
      ]);
    };

    setWs(socket);
  }, []);

  const sendMessage = (text) => {
    setMessages((prev) => [...prev, { role: "user", text }]);

    ws.send(JSON.stringify({
      question: text,
      session_id: "123",
      user_id: "user1",
      company_id: "quickbite"
    }));
  };

  return (
    <div className="chat">
      <div className="header">Enterprise Copilot</div>

      <div className="messages">
        {messages.map((m, i) => (
          <div key={i} className={m.role}>
            <div className="bubble">{m.text}</div>
          </div>
        ))}
      </div>

      <InputBox onSend={sendMessage} />
    </div>
  );
}