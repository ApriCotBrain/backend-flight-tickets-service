import xml.etree.ElementTree as ET

from app.schemas import Flight, Price, Ticket

xml_data = "RS_ViaOW.xml"


def parse_all_flights(xml_data: str) -> list[Ticket]:
    tree = ET.parse(xml_data)
    root = tree.getroot()

    tickets = []

    target_tag = root.findall("PricedItineraries/")
    for child in target_tag:
        flight_prices = child.find("Pricing")
        ownard_flight_elements = child.find("OnwardPricedItinerary")
        return_flight_elements = child.find("ReturnPricedItinerary")

        currency = flight_prices.get("currency")
        service_charges = flight_prices.findall("ServiceCharges")

        prices_values = []
        for prices in service_charges:
            type = prices.get("type")
            charge_type = prices.get("ChargeType")
            price = prices.text
            price_schema = Price(
                currency=currency,
                type=type,
                charge_type=charge_type,
                price=price,
            )
            prices_values.append(price_schema)

        flights_values = []
        flights = ownard_flight_elements.findall("Flights/Flight")
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
                itinerary_type="ownard",
                carrier_id=carrier_id,
                carrier=carrier,
                flight_number=flight_number,
                source=source,
                destination=destination,
                departure_time=departure_time,
                arrival_time=arrival_time,
                flight_class=flight_class,
                number_of_stops=number_of_stops,
                fare_basis=fare_basis,
                ticket_type=ticket_type,
                price_schema=price_schema,
            )
            flights_values.append(flight_schema)

        ticket_schema = Ticket(
            round_trip=False,
            flights=flights_values,
            price=prices_values,
        )

        tickets.append(ticket_schema)

    return tickets


parse_all_flights(xml_data)
