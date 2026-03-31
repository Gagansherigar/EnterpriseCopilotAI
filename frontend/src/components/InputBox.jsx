import { useState } from "react";

export default function InputBox({ onSend }) {
  const [input, setInput] = useState("");

  return (
    <div className="inputBox">
      <input
        value={input}
        onChange={(e) => setInput(e.target.value)}
      />
      <button
        onClick={() => {
          onSend(input);
          setInput("");
        }}
      >
        Send
      </button>
    </div>
  );
}