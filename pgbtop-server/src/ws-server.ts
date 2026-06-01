//Websocket server

import { WebSocketServer } from "ws";
import {config} from './config'
import { IncomingMessage } from "node:http";

const wss = new WebSocketServer({ port: config.port })

export function startServer(){
    
    wss.on ( "listening", () =>{
        console.log(`Listening on ws://localhost:${config.port}`)
    })

    wss.on( "connection", (socket: WebSocket, _req: IncomingMessage ) => {
        console.log("Incoming message")
    })


}