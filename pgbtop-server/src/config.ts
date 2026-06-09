// Config.ts

export const config = {
    port: parseInt(process.env.PGBTOP_PORT ?? "4242", 10),
    pgtop_token: process.env.PGBTOP_TOKEN,
    db_host: process.env.DATABASE_HOST,
    db_port: parseInt(process.env.DATABASE_PORT ?? "0000"),
    db_db: process.env.DATABASE,
    db_pass: process.env.DATABASE_PASS,
    db_user: process.env.DATABASE_USER,
}