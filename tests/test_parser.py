import pytest

from app.parser import get_all_tickets, parse_all_flights, parse_flights, parse_pricing
from app.schemas import Flight, Price, Ticket


@pytest.mark.asyncio
@pytest.mark.parametrize("xml_data", ["RS_Via-3.xml", "RS_ViaOW.xml"])
async def test_parse_all_flights(xml_data):
    target_tags = await parse_all_flights(xml_data)
    assert len(target_tags) > 0


@pytest.mark.asyncio
@pytest.mark.parametrize("xml_data", ["RS_Via-3.xml", "RS_ViaOW.xml"])
async def test_parse_pricing(xml_data):
    target_tags = await parse_all_flights(xml_data)
    prices = await parse_pricing(target_tags)
    assert len(prices) > 0
    assert all(isinstance(price, Price) for price in prices)


@pytest.mark.asyncio
@pytest.mark.parametrize("xml_data", ["RS_Via-3.xml", "RS_ViaOW.xml"])
async def test_parse_flights(xml_data):
    target_tags = await parse_all_flights(xml_data)
    flights = await parse_flights(target_tags, itenary_type="OnwardPricedItinerary")
    assert len(flights) > 0
    assert all(isinstance(flight, Flight) for flight in flights)


@pytest.mark.asyncio
@pytest.mark.parametrize("xml_data", ["RS_Via-3.xml", "RS_ViaOW.xml"])
async def test_get_all_tickets(xml_data):
    tickets = await get_all_tickets(xml_data)
    assert len(tickets) > 0
    assert all(isinstance(ticket, Ticket) for ticket in tickets)
    assert all(isinstance(ticket.flights, list) for ticket in tickets)
    assert all(isinstance(ticket.price, list) for ticket in tickets)
