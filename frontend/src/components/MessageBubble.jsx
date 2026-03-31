export default function MessageBubble({ message }) {
  const isUser = message.role === "user";

  const routeColors = {
    rag: "bg-gray-200",
    sql: "bg-purple-200",
    escalate: "bg-red-200",
    direct: "bg-green-200",
  };

  return (
    <div className={`flex ${isUser ? "justify-end" : "justify-start"}`}>
      <div
        className={`p-3 rounded-lg max-w-md ${
          isUser
            ? "bg-blue-500 text-white"
            : routeColors[message.route] || "bg-gray-200"
        }`}
      >
        {!isUser && (
          <div className="text-xs text-gray-500 mb-1">
            {message.route || "ai"}
          </div>
        )}
        {message.text}
      </div>
    </div>
  );
}