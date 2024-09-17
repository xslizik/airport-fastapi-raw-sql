from fastapi import APIRouter
from .. configuration import conf
import psycopg2

destinations = APIRouter(tags=['destinations'])

@destinations.get("/v1/airports/{airport}/destinations")
async def planedDepartures(airport: str):
    try:
        conn = psycopg2.connect(
            database = conf.DATABASE_NAME,
            user     = conf.DATABASE_USER,
            password = conf.DATABASE_PASSWORD,
            host     = conf.DATABASE_HOST,
            port     = conf.DATABASE_PORT
        )
        cur = conn.cursor()
        cur.execute(f'''
            SELECT DISTINCT f.arrival_airport
            FROM bookings.flights f
            WHERE f.departure_airport like '{airport}'
            ORDER BY f.arrival_airport ASC;
                    ''')
        output = cur.fetchall()
        conn.close()

        results = []
        for result in output:
            results.append(result[0])

        return {
            "results" : results
        }

    except:
        return {
            "Connection Failed"
        }
