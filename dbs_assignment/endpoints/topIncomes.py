from fastapi import APIRouter
from .. configuration import conf
import psycopg2

topIncomes = APIRouter(tags=['topIncomes'])

@topIncomes.get("/v3/aircrafts/{aircraft_code}/top-incomes")
async def calculateTopIncomes(aircraft_code: str):
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
            SELECT MONTH,
                DAY,
                max_amount
            FROM
            (SELECT *,
                    MAX(day_amount) OVER (PARTITION BY MONTH) AS max_amount
            FROM
                (SELECT TO_CHAR(t1.month_day::date AT TIME ZONE 'UTC', 'YYYY-fmMM') AS MONTH,
                        TO_CHAR(t1.month_day::date AT TIME ZONE 'UTC', 'DD') AS DAY,
                        t1.day_amount
                FROM
                    (SELECT TO_CHAR(f.actual_departure, 'YYYY-MM-DD') AS month_day,
                            sum(tf.amount) AS day_amount
                    FROM bookings.flights f
                    JOIN bookings.ticket_flights tf ON f.flight_id = tf.flight_id
                    WHERE f.aircraft_code like '{aircraft_code}'
                    AND f.actual_departure IS NOT NULL
                    GROUP BY month_day) AS t1
                GROUP BY MONTH,
                        DAY,
                        day_amount) AS t2) AS t3
            WHERE day_amount = max_amount
            ORDER BY max_amount DESC,
                    MONTH;
                    ''')
        output = cur.fetchall()
        conn.close()

        results = []
        for result in output:
            results.append({
                "day" : str(int(result[1])),
                "month" : result[0],
                "total_amount" : int(result[2])
            })

        return {
            "results" : results
        }
    except:
        return {
            "Connection Failed"
        }
