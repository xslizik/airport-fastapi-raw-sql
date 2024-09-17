from fastapi import APIRouter
from .. configuration import conf
import psycopg2

top = APIRouter(tags=['top'])

@top.get("/v1/top-airlines")
async def topAirlines(limit: str):
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
            SELECT f.flight_no,
                Count(*) AS count
            FROM bookings.flights AS f
            JOIN bookings.ticket_flights tf ON f.flight_id = tf.flight_id
            WHERE f.status like 'Arrived'
            GROUP BY f.flight_no
            ORDER BY COUNT DESC, f.flight_no
            LIMIT {limit};
                    ''')
        output = cur.fetchall()
        conn.close()

        results = []
        for result in output:
            results.append({
                "count" : result[1],
                "flight_no" : result[0]
            })

        return {
            "results" : results
        }
    except:
        return {
            "Connection Failed"
        }
