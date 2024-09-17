from fastapi import APIRouter
from .. configuration import conf
import psycopg2

companions = APIRouter(tags=['companions'])

@companions.get("/v1/passengers/{passenger_id}/companions")
async def findCompanions(passenger_id: str):
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
            SELECT my_table.passenger_id,
                my_table.passenger_name,
                count(my_table.passenger_id) AS flights_count,
                array_agg(my_table.flight_id ORDER BY my_table.flight_id) AS flights
            FROM
            (SELECT t2.passenger_name,
                    t2.passenger_id,
                    tf2.flight_id
            FROM bookings.ticket_flights tf2
            JOIN bookings.tickets t2 ON t2.ticket_no = tf2.ticket_no
            WHERE tf2.flight_id in
                (SELECT tf.flight_id
                    FROM bookings.ticket_flights tf
                    WHERE tf.ticket_no in
                        (SELECT ticket_no
                        FROM bookings.tickets t
                        WHERE t.passenger_id like '{passenger_id}')) ) AS my_table
            WHERE my_table.passenger_id not like '{passenger_id}'
            GROUP BY my_table.passenger_id,
                    my_table.passenger_name
            ORDER BY flights_count DESC,
                    my_table.passenger_id ASC;
                    ''')
        output = cur.fetchall()
        conn.close()

        results = []
        for result in output:
            results.append({
                "flights" : result[3],
                "flights_count" : result[2],
                "id" : result[0],
                "name" : result[1]
            })

        return {
            "results" : results
        }

    except:
        return {
            "Connection Failed"
        }
