from fastapi import APIRouter
from .. configuration import conf
import psycopg2

authentication = APIRouter(tags=['authentication'])

@authentication.get("/v1/status")
async def requestStatus():
    try:
        conn = psycopg2.connect(
            database = conf.DATABASE_NAME,
            user     = conf.DATABASE_USER,
            password = conf.DATABASE_PASSWORD,
            host     = conf.DATABASE_HOST,
            port     = conf.DATABASE_PORT
        )
        cur = conn.cursor()
        cur.execute("SELECT VERSION();")
        version = cur.fetchone()
        conn.close()
        return {
            "version" : str(version[0])
        }

    except:
        return {
            "Connection Failed"
        }
