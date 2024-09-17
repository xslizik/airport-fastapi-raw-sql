from fastapi import APIRouter
from .. configuration import conf
import psycopg2

kSeat = APIRouter(tags=['kSeat'])

@kSeat.get("/v3/aircrafts/{aircraft_code}/seats/{seat_choice}")
async def bookedSeats(aircraft_code: str, seat_choice: str):
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
            SELECT
                ranked.seat_no,
                count(*) AS COUNT
            FROM
            (SELECT
                bp.seat_no,
                dense_rank() over(PARTITION BY f.flight_id ORDER BY b.book_date) AS rank
            FROM bookings.flights f
            JOIN bookings.boarding_passes bp ON f.flight_id = bp.flight_id
            JOIN bookings.tickets t ON bp.ticket_no = t.ticket_no
            JOIN bookings.bookings b ON t.book_ref = b.book_ref
            WHERE f.aircraft_code like '{aircraft_code}'
            ORDER BY f.flight_id) AS ranked
            WHERE ranked.rank = {seat_choice}
            GROUP BY ranked.seat_no
            ORDER BY COUNT DESC
            LIMIT 1;
                    ''')
        output = cur.fetchall()
        conn.close()

        results = []
        for result in output:
            results.append({
                "seat" : result[0],
                "count" : result[1]
            })

        return {
            "result" : results[0]
        }
    except:
        return {
            "Connection Failed"
        }
