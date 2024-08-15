from datetime import datetime
from decimal import Decimal
import xml.etree.ElementTree as ET

from app.schemas import Flight, Price, Ticket


async def parse_all_flights(xml_data: str) -> list[ET.Element]:
    """
    Parse an XML string containing flight data and extract all priced itineraries.

    Returns a list of ElementTree elements representing the priced itineraries.
    """
    tree = ET.parse(xml_data)
    root = tree.getroot()

    target_tags = root.findall("PricedItineraries/")

    return target_tags


async def parse_pricing(target_tags: list[ET.Element]) -> list[Price]:
    """
    Extract pricing information from a list of ElementTree elements.

    Returns a list of Price objects containing the extracted pricing data.
    """
    prices_values = []

    for child in target_tags:
        flight_prices = child.find("Pricing")
        currency = flight_prices.get("currency")
        service_charges = flight_prices.findall("ServiceCharges")

        for prices in service_charges:
            type = prices.get("type")
            charge_type = prices.get("ChargeType")
            price = prices.text
            price_schema = Price(
                currency=currency,
                type=type,
                charge_type=charge_type,
                price=Decimal(price),
            )
            prices_values.append(price_schema)
    return prices_values


async def parse_flights(
    target_tags: list[ET.Element], itenary_type: str
) -> list[Flight]:
    """
    Extract flight information from a list of ElementTree elements.

    Returns a list of Flight objects containing the extracted flight data.
    """
    flights_values = []

    for child in target_tags:
        flight_elements = child.find(itenary_type)
        flights = flight_elements.findall("Flights/Flight")
        for flight in flights:
            carrier_id = flight.find("Carrier").get("id")
            carrier = flight.find("Carrier").text
            flight_number = flight.find("FlightNumber").text
            source = flight.find("Source").text
            destination = flight.find("Destination").text
            departure_time = flight.find("DepartureTimeStamp").text
            arrival_time = flight.find("ArrivalTimeStamp").text
            flight_class = flight.find("Class").text
            number_of_stops = flight.find("NumberOfStops").text
            fare_basis = flight.find("FareBasis").text
            ticket_type = flight.find("TicketType").text
            flight_schema = Flight(
                itinerary_type=itenary_type,
                carrier_id=carrier_id,
                carrier=carrier,
                flight_number=flight_number,
                source=source,
                destination=destination,
                departure_time=datetime.strptime(departure_time, "%Y-%m-%dT%H%M"),
                arrival_time=datetime.strptime(arrival_time, "%Y-%m-%dT%H%M"),
                flight_class=flight_class,
                number_of_stops=number_of_stops,
                fare_basis=fare_basis,
                ticket_type=ticket_type,
                price_schema=itenary_type,
            )
            flights_values.append(flight_schema)

    return flights_values


async def get_all_tickets(xml_data: str) -> list[Ticket]:
    """
    Extracts and returns a list of ticket objects from the provided XML data.

    Returns a list of Ticket objects, each representing a flight ticket.
    """
    target_tag = await parse_all_flights(xml_data)
    tickets = []

    for child in target_tag:
        prices = await parse_pricing(target_tag)

        ownard_flight_elements = child.find("OnwardPricedItinerary")
        if ownard_flight_elements:
            flights = await parse_flights(
                target_tag, itenary_type="OnwardPricedItinerary"
            )

        return_flight_elements = child.find("ReturnPricedItinerary")
        if return_flight_elements:
            flights = await parse_flights(
                target_tag, itenary_type="ReturnPricedItinerary"
            )

        ticket_schema = Ticket(
            round_trip=True if return_flight_elements else False,
            flights=flights,
            price=prices,
        )

        tickets.append(ticket_schema)

    return tickets
