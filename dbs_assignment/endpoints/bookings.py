from fastapi import APIRouter
from .. configuration import conf
import psycopg2

bookings = APIRouter(tags=['bookings'])
@bookings.get("/v1/bookings/{booking_id}")
async def bookingsDetail(booking_id: str):
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
                p.book_ref,
                TO_CHAR(p.book_date AT TIME ZONE 'UTC', 'YYYY-MM-DD"T"HH24:MI:SS"+00:00"'),
                json_agg(
                    json_build_object(
                        'id', p.id,
                        'passenger_id', p.passenger_id,
                        'passenger_name', p.passenger_name,
                        'boarding_no', p.boarding_no,
                        'flight_no', p.flight_no,
                        'seat', p.seat,
                        'aircraft_code', p.aircraft_code,
                        'arrival_airport', p.arrival_airport,
                        'departure_airport', p.departure_airport,
                        'scheduled_arrival', p.scheduled_arrival,
                        'scheduled_departure', p.scheduled_departure
                        )
                    ) AS boarding_passes
            FROM
                (SELECT
                        b.book_ref,
                        b.book_date,
                        t.ticket_no AS id,
                        t.passenger_id,
                        t.passenger_name,
                        bp.boarding_no,
                        f.flight_no,
                        bp.seat_no AS seat,
                        f.aircraft_code,
                        f.arrival_airport,
                        f.departure_airport,
                        TO_CHAR(f.scheduled_arrival AT TIME ZONE 'UTC', 'YYYY-MM-DD"T"HH24:MI:SS"+00:00"') AS scheduled_arrival,
                        TO_CHAR(f.scheduled_departure AT TIME ZONE 'UTC', 'YYYY-MM-DD"T"HH24:MI:SS"+00:00"') AS scheduled_departure
                FROM bookings.bookings b
                JOIN bookings.tickets t ON b.book_ref = t.book_ref
                JOIN bookings.boarding_passes bp ON t.ticket_no = bp.ticket_no
                JOIN bookings.flights f ON bp.flight_id = f.flight_id
                WHERE b.book_ref like '{booking_id}'
                ORDER BY id, bp.boarding_no) AS p
            GROUP BY p.book_ref, p.book_date;
                    ''')
        output = cur.fetchall()
        conn.close()

        results = {}
        for result in output:
            results.update({
                "id" : result[0],
                "book_date" : result[1],
                "boarding_passes" : result[2],
            })

        return {
            "result" : results
        }

    except:
        return {
            "Connection Failed"
        }
