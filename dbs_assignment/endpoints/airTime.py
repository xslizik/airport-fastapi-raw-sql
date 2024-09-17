from fastapi import APIRouter
from .. configuration import conf
import psycopg2

airTime = APIRouter(tags=['airTime'])

@airTime.get("/v3/air-time/{book_ref}")
async def topAirlines(book_ref: str):
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
            SELECT pass.passenger_name,
                pass.ticket_no,
                json_agg(
                    json_build_object(
                        'departure_airport', pass.departure_airport,
                        'arrival_airport', pass.arrival_airport,
                        'flight_time', pass.flight_time,
                        'total_time', pass.running_total
                        )
                ) AS flights
            FROM
            (SELECT air_t.passenger_name,
                    air_t.ticket_no,
                    air_t.departure_airport,
                    air_t.arrival_airport,
                    to_char(air_t.flight_time, 'fmHH24:MI:SS') AS flight_time,
                    to_char(SUM(air_t.flight_time) OVER (PARTITION BY air_t.ticket_no
                                                        ORDER BY air_t.ticket_no, air_t.actual_departure), 'fmHH24:MI:SS') AS running_total
            FROM
                (SELECT t.passenger_name,
                        t.ticket_no,
                        f.departure_airport,
                        f.arrival_airport,
                        f.actual_arrival - f.actual_departure AS flight_time,
                        f.actual_departure
                FROM bookings.tickets t
                JOIN bookings.ticket_flights tf ON t.ticket_no = tf.ticket_no
                JOIN bookings.flights f ON tf.flight_id = f.flight_id
                WHERE book_ref LIKE '{book_ref}') AS air_t
            ORDER BY air_t.ticket_no,
                        air_t.actual_departure) AS pass
            GROUP BY pass.passenger_name,
                    pass.ticket_no;
                    ''')
        output = cur.fetchall()
        conn.close()

        results = []
        for result in output:
            results.append({
                "flights" : result[2],
                "ticket_no" : result[1],
                "passenger_name" : result[0]
            })

        return {
            "results" : results
        }
    except:
        return {
            "Connection Failed"
        }
