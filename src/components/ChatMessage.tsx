
import React from "react";
import { ChatMessage as ChatMessageType } from "@/lib/types";
import { cn } from "@/lib/utils";

interface ChatMessageProps {
  message: ChatMessageType;
}

const ChatMessage: React.FC<ChatMessageProps> = ({ message }) => {
  const isUser = message.role === "user";
  const isSystem = message.role === "system";

  return (
    <div
      className={cn(
        "mb-4 flex w-full",
        isUser ? "justify-end" : "justify-start"
      )}
    >
      {isSystem ? (
        <div className="max-w-3xl rounded-md bg-gray-100 p-3 text-sm text-gray-600">
          <div className="mb-1 text-xs font-semibold text-gray-500">System</div>
          <div className="whitespace-pre-wrap">{message.content}</div>
        </div>
      ) : (
        <div
          className={cn(
            "max-w-3xl rounded-lg p-4",
            isUser
              ? "bg-primary text-white"
              : "bg-gray-100 text-gray-800"
          )}
        >
          <div className="mb-1 text-xs font-semibold">
            {isUser ? "You" : "Assistant"}
          </div>
          <div className="whitespace-pre-wrap">{message.content}</div>
        </div>
      )}
    </div>
  );
};

export default ChatMessage;
