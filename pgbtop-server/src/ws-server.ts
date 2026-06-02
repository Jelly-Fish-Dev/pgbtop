//Websocket server

import { WebSocketServer, WebSocket } from "ws";
import { config } from "./config";
import { IncomingMessage } from "node:http";
import { setInterval } from "node:timers";

const wss = new WebSocketServer({ port: config.port });

const clients = new Set<WebSocket>();
var id = 0;

//TODO: Example data payload for just when I'm testing stuff REMOVE THIS
interface DataPayload {
  type: string;
  ts: number;
  data: unknown[];
}

function poll(): void {
  console.log(`sending message id:${id}`);
  const payload: DataPayload = {
    type: "update",
    ts: Date.now(),
    data: [{ id, value: Math.random().toFixed(4) }],
  };
  id++;
  broadcast(payload);
}

function broadcast(payload: DataPayload): void {
  const msg = JSON.stringify(payload);
  for (const client of clients) {
    if (client.readyState === WebSocket.OPEN) {
      client.send(msg);
    }
  }
}

export function startServer(): void {
  wss.on("listening", () => {
    console.log(`Listening on ws://localhost:${config.port}`);
    setInterval(poll, 2000);
  });

  wss.on("connection", (socket: WebSocket, _req: IncomingMessage) => {
    console.log("Client connected");
    clients.add(socket);
    socket.on("close", () => clients.delete(socket));
  });
}
