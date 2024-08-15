from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel


class Flight(BaseModel):
    itinerary_type: str
    carrier_id: str
    carrier: str
    flight_number: str
    source: str
    destination: str
    departure_time: datetime
    arrival_time: datetime
    flight_class: str
    number_of_stops: int
    fare_basis: str
    ticket_type: str


class Price(BaseModel):
    currency: str
    type: str
    charge_type: str
    price: Decimal


class Ticket(BaseModel):
    round_trip: bool
    flights: Flight | list[Flight]
    price: list[Price]
