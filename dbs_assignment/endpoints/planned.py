from fastapi import APIRouter
from .. configuration import conf
import psycopg2

planned = APIRouter(tags=['planned'])

@planned.get("/v1/departures")
async def planedDepartures(airport: str, day: int):
    try:
        if day == 7:
            day = 0
        conn = psycopg2.connect(
            database = conf.DATABASE_NAME,
            user     = conf.DATABASE_USER,
            password = conf.DATABASE_PASSWORD,
            host     = conf.DATABASE_HOST,
            port     = conf.DATABASE_PORT
        )
        cur = conn.cursor()
        cur.execute(f'''
            SELECT
                f.flight_id,
                f.flight_no,
                TO_CHAR(f.scheduled_departure AT TIME ZONE 'UTC', 'YYYY-MM-DD"T"HH24:MI:SS"+00:00"')
            FROM bookings.flights f
            WHERE
                f.departure_airport like '{airport}'
            AND EXTRACT(dow FROM f.scheduled_departure) = {day}
            AND f.status like'Scheduled'
            ORDER BY f.scheduled_departure, f.flight_id;
                    ''')
        output = cur.fetchall()
        conn.close()

        results = []
        for result in output:
            results.append({
                "flight_id" : result[0],
                "flight_no" : result[1],
                "scheduled_departure" : result[2]
            })

        return {
            "results" : results
        }

    except:
        return {
            "Connection Failed"
        }
