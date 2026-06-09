import { config } from './config'
import {Pool} from 'pg'

const pool = new Pool({
    user: config.db_user,
    host: config.db_host,
    database:config.db_db,
    password: config.db_pass,
    port: config.db_port,
})

async function verifyConnection(): Promise<void> {
    try{
        const client = await pool.connect();
        console.log("Connected")
        client.release()
    }catch(error){
        console.error(error)
    }
}

export {pool, verifyConnection} 
