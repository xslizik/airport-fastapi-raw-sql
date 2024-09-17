from fastapi import APIRouter
from .. configuration import conf
import psycopg2

load = APIRouter(tags=['load'])

@load.get("/v1/airlines/{flight_no}/load")
async def calculateLoad(flight_no: str):
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
            SELECT *,
                round(cast(f2.load AS numeric) / cast(f2.aircraft_capacity AS numeric) * 100, 2) AS percentage_load
            FROM (SELECT f.flight_id,
                        (SELECT count(*)
                        FROM bookings.seats s
                        WHERE f.aircraft_code = s.aircraft_code) AS aircraft_capacity,
                        count(*)                                  as load
                FROM bookings.flights f
                        join bookings.ticket_flights tf
                                on tf.flight_id = f.flight_id
                WHERE f.flight_no like '{flight_no}'
                group by f.flight_id) AS f2;
                    ''')
        output = cur.fetchall()
        conn.close()

        results = []
        for result in output:
            if result[3] == 100:
                results.append({
                    "id" : result[0],
                    "aircraft_capacity" : result[1],
                    "load" : result[2],
                    "percentage_load" : int(result[3])
                })
            else:
                results.append({
                    "id" : result[0],
                    "aircraft_capacity" : result[1],
                    "load" : result[2],
                    "percentage_load" : result[3]
                })
        return {
            "results" : results
        }

    except:
        return {
            "Connection Failed"
        }
