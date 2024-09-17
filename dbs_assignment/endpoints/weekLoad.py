from fastapi import APIRouter
from .. configuration import conf
import psycopg2

week = APIRouter(tags=['week'])

@week.get("/v1/airlines/{flight_no}/load-week")
async def calculateWeekLoad(flight_no: str):
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
            Select
                round(cast(sum(f1.load) as numeric) / cast(sum(f1.aircraft_capacity) as numeric) * 100, 2)
            FROM (
                    SELECT
                        CASE
                    WHEN EXTRACT(dow FROM f.scheduled_departure) = 1
                        THEN '1'
                    WHEN EXTRACT(dow FROM f.scheduled_departure) = 2
                        THEN '2'
                    WHEN EXTRACT(dow FROM f.scheduled_departure) = 3
                        THEN '3'
                    WHEN EXTRACT(dow FROM f.scheduled_departure) = 4
                        THEN '4'
                    WHEN EXTRACT(dow FROM f.scheduled_departure) = 5
                        THEN '5'
                    WHEN EXTRACT(dow FROM f.scheduled_departure) = 6
                        THEN '6'
                    WHEN EXTRACT(dow FROM f.scheduled_departure) = 0
                        THEN '7'
                    END AS day,

                        f.flight_id,

                    (
                        SELECT count(*)
                        FROM bookings.seats s
                        WHERE f.aircraft_code = s.aircraft_code
                    ) AS aircraft_capacity,
                    count(*) as load
                    FROM bookings.flights f
                    join bookings.ticket_flights tf
                    on tf.flight_id = f.flight_id
                    WHERE f.flight_no like '{flight_no}'
                    group by f.flight_id
                ) AS f1
            group by day
            order by day;
                    ''')
        output = cur.fetchall()
        conn.close()

        results = {
            "flight_no" : flight_no,
            "monday" : output[0][0],
            "tuesday" : output[1][0],
            "wednesday" : output[2][0],
            "thursday" : output[3][0],
            "friday" : output[4][0],
            "saturday" : output[5][0],
            "sunday" : output[6][0],
        }

        return {
            "result" : results
        }

    except:
        return {
            "Connection Failed"
        }
