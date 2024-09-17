from fastapi import APIRouter

from .endpoints.requestStatus import authentication
from .endpoints.companions import companions
from .endpoints.bookings import bookings
from .endpoints.lateDeparture import late
from .endpoints.topAirlines import top
from .endpoints.planned import planned
from .endpoints.destinations import destinations
from .endpoints.load import load
from .endpoints.weekLoad import week
from .endpoints.airTime import airTime
from .endpoints.topIncomes import topIncomes
from .endpoints.topSeats import topSeats
from .endpoints.kSeat import kSeat


router = APIRouter()
router.include_router(authentication, tags=["authentication"])
router.include_router(companions, tags=["companions"])
router.include_router(bookings, tags=["bookings"])
router.include_router(late, tags=["late"])
router.include_router(top, tags=["top"])
router.include_router(planned, tags=["planned"])
router.include_router(destinations, tags=["destinations"])
router.include_router(load, tags=["load"])
router.include_router(week, tags=["week"])
router.include_router(topIncomes, tags=["topIncomes"])
router.include_router(airTime, tags=["airTime"])
router.include_router(topSeats, tags=["topSeats"])
router.include_router(kSeat, tags=["kSeat"])
