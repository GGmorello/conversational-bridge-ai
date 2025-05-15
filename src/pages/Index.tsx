
import React from "react";
import Chat from "@/components/Chat";

const Index: React.FC = () => {
  return (
    <div className="flex h-screen flex-col bg-gradient-to-br from-gray-50 to-gray-100">
      <header className="border-b bg-white p-4 shadow-sm">
        <h1 className="text-xl font-semibold">AI Chat Interface</h1>
        <p className="text-sm text-muted-foreground">
          Connecting to localhost:8000/chat
        </p>
      </header>
      <main className="flex-1 overflow-hidden">
        <div className="mx-auto h-full max-w-4xl">
          <Chat />
        </div>
      </main>
    </div>
  );
};

export default Index;
