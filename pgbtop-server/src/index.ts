import "./ws-server"
import { startServer } from "./ws-server"
import {verifyConnection} from './db'

verifyConnection();
startServer();