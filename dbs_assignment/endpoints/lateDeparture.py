from fastapi import APIRouter
from ..configuration import conf
import psycopg2

late = APIRouter(tags=['late'])

@late.get("/v1/flights/late-departure/{delay}")
async def lateDepartures(delay: int):
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
            SELECT f.flight_id,
                f.flight_no,
                EXTRACT(EPOCH
                        FROM (f.actual_departure - f.scheduled_departure)) / 60.0 AS delay
            FROM bookings.flights f
            WHERE EXTRACT(EPOCH
                        FROM (f.actual_departure - f.scheduled_departure)) > {delay}*60
            ORDER BY delay DESC, flight_id;
                    ''')
        output = cur.fetchall()
        conn.close()

        results = []
        for result in output:
            results.append({
                "flight_id" : result[0],
                "flight_no" : result[1],
                "delay" : int(result[2]),
            })

        return {
            "results" : results
        }

    except:
        return {
            "Connection Failed"
        }
