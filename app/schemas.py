from pydantic import BaseModel


class Flight(BaseModel):
    itinerary_type: str
    carrier_id: str
    carrier: str
    flight_number: str
    source: str
    destination: str
    departure_time: str
    arrival_time: str
    flight_class: str
    number_of_stops: int
    fare_basis: str
    ticket_type: str


class Price(BaseModel):
    currency: str
    type: str
    charge_type: str
    price: float


class Ticket(BaseModel):
    round_trip: bool
    flights: Flight | list[Flight]
    price: list[Price]
