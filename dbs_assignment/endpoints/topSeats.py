from fastapi import APIRouter
from .. configuration import conf
import psycopg2

topSeats = APIRouter(tags=['topSeats'])

@topSeats.get("/v3/airlines/{flight_no}/top_seats")
async def mostPopularSeats(flight_no: str, limit: str):
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
            SELECT island_sizes.seat_no,
                MAX(island_sizes.count) AS max_island_size,
                island_sizes.flights
            FROM
            (SELECT groups.seat_no,
                    COUNT(*) AS COUNT,
                    ARRAY_AGG(groups.flight_id) AS flights
            FROM
                (SELECT *,
                        SUM(CASE
                                WHEN init.previous + 1 = init.flight_id THEN 0
                                ELSE 1
                            END) OVER(PARTITION BY init.seat_no
                                    ORDER BY init.flight_id) AS id
                FROM
                    (SELECT bp.seat_no,
                            f.flight_id,
                            LAG(f.flight_id) OVER(PARTITION BY bp.seat_no
                                                ORDER BY f.flight_id) AS previous
                    FROM bookings.flights f
                    JOIN bookings.boarding_passes bp ON f.flight_id = bp.flight_id
                    WHERE f.flight_no LIKE '{flight_no}'
                    ORDER BY f.flight_id) AS init) AS groups
            GROUP BY groups.seat_no,
                        groups.id) AS island_sizes
            GROUP BY island_sizes.seat_no,
                    island_sizes.flights
            ORDER BY max_island_size DESC
            LIMIT {limit};
                    ''')
        output = cur.fetchall()
        conn.close()

        results = []
        for result in output:
            results.append({
                "flights" : result[2],
                "seat" : result[0],
                "flights_count" : result[1]
            })

        return {
            "results" : results
        }
    except:
        return {
            "Connection Failed"
        }
