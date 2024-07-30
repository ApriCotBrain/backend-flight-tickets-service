import tempfile
from datetime import datetime
from decimal import Decimal
from pathlib import Path

import aiofiles
import xmltodict
from fastapi import UploadFile


async def get_temp_data_path(xml_file: UploadFile) -> str:
    """Save file in temp folder and return its path."""
    temp_dir = Path(tempfile.gettempdir())
    xml_data_path = temp_dir / xml_file.filename
    contents = xml_file.file.read()
    async with aiofiles.open(xml_data_path, "wb") as file:
        await file.write(contents)
    return str(xml_data_path)


async def get_all_flights(xml_data_path: str) -> list:
    """Read the xml file and convert it to a dictionary."""
    async with aiofiles.open(xml_data_path, "r") as file:
        xml_data = await file.read()
        xml_dict = xmltodict.parse(xml_data)["AirFareSearchResponse"][
            "PricedItineraries"
        ]

        for flight in xml_dict["Flights"]:
            flight["Pricing"]["currency"] = flight["Pricing"].pop("@currency")

            price_values = flight["Pricing"]["ServiceCharges"]
            for item in price_values:
                item["type"] = item.pop("@type")
                item["charge_type"] = item.pop("@ChargeType")
                item["text"] = item.pop("#text")

            flight_values = flight["OnwardPricedItinerary"]["Flights"]["Flight"]
            if isinstance(flight_values, list):
                for item in flight_values:
                    item["Carrier"]["id"] = item["Carrier"].pop("@id", item["Carrier"])
                    item["Carrier"]["text"] = item["Carrier"].pop(
                        "#text", item["Carrier"]
                    )
            if isinstance(flight_values, dict):
                flight_values["Carrier"]["id"] = flight_values["Carrier"].pop("@id")
                flight_values["Carrier"]["text"] = flight_values["Carrier"].pop("#text")

        return xml_dict


async def get_direct_flights(xml_data_path: str) -> list:
    """Get direct flight options."""
    all_values_list = await get_all_flights(xml_data_path=xml_data_path)
    direct_flights_list = []

    for flight in all_values_list["Flights"]:
        possible_direct_flight = flight["OnwardPricedItinerary"]["Flights"]["Flight"]
        if not isinstance(possible_direct_flight, list):
            direct_flights_list.append(flight)

    return direct_flights_list


async def get_flights_with_transfers(xml_data_path: str) -> list:
    """Get flight options with transfers."""
    all_values_list = await get_all_flights(xml_data_path=xml_data_path)
    direct_flights_list = []

    for flight in all_values_list["Flights"]:
        possible_direct_flight = flight["OnwardPricedItinerary"]["Flights"]["Flight"]
        if isinstance(possible_direct_flight, list):
            direct_flights_list.append(flight)

    return direct_flights_list


async def get_most_expensive_tickets(xml_data_path: str) -> list:
    """Get the most expencive tickets in SingleAdult BaseFare values."""
    all_values_list = await get_all_flights(xml_data_path=xml_data_path)
    prices = []
    most_expensive_tikets = []

    for flight in all_values_list["Flights"]:
        possible_most_expensive_tickets_price = Decimal(
            flight["Pricing"]["ServiceCharges"][0]["text"]
        )
        prices.append(possible_most_expensive_tickets_price)

    max_price = max(prices)

    for flight in all_values_list["Flights"]:
        if Decimal(flight["Pricing"]["ServiceCharges"][0]["text"]) == max_price:
            most_expensive_tikets.append(flight)

    return most_expensive_tikets


async def get_cheapest_tickets(xml_data_path: str) -> list:
    """Get the cheapest tickets in SingleAdult BaseFare values."""
    all_values_list = await get_all_flights(xml_data_path=xml_data_path)
    prices = []
    cheapest_tikets = []

    for flight in all_values_list["Flights"]:
        possible_cheapest_tikets_price = Decimal(
            flight["Pricing"]["ServiceCharges"][0]["text"]
        )
        prices.append(possible_cheapest_tikets_price)

    min_price = min(prices)

    for flight in all_values_list["Flights"]:
        if Decimal(flight["Pricing"]["ServiceCharges"][0]["text"]) == min_price:
            cheapest_tikets.append(flight)

    return cheapest_tikets


def calculate_flight_time(flight) -> float:
    """Calculate total flight time."""
    flights = flight["OnwardPricedItinerary"]["Flights"]["Flight"]
    if isinstance(flights, dict):
        flight_start = datetime.strptime(flights["DepartureTimeStamp"], "%Y-%m-%dT%H%M")
        flight_end = datetime.strptime(flights["ArrivalTimeStamp"], "%Y-%m-%dT%H%M")
        possible_longest_time = flight_end - flight_start
    if isinstance(flights, list):
        first_flight_start = datetime.strptime(
            flights[0]["DepartureTimeStamp"], "%Y-%m-%dT%H%M"
        )
        last_flight_end = datetime.strptime(
            flights[-1]["ArrivalTimeStamp"], "%Y-%m-%dT%H%M"
        )
        possible_longest_time = last_flight_end - first_flight_start

    return possible_longest_time.total_seconds()


async def get_longest_flights(xml_data_path: str) -> list:
    """Get the longest flight values."""
    all_values_list = await get_all_flights(xml_data_path=xml_data_path)
    times = []
    longest_flights = []

    for flight in all_values_list["Flights"]:
        calculate_flight_time(flight)
        times.append(calculate_flight_time(flight))

    longest_time = max(times)
    for flight in all_values_list["Flights"]:
        if calculate_flight_time(flight) == longest_time:
            longest_flights.append(flight)

    return longest_flights


async def get_shortest_flights(xml_data_path: str) -> list:
    """Get the shortest flight values."""
    all_values_list = await get_all_flights(xml_data_path=xml_data_path)
    times = []
    shortest_flights = []

    for flight in all_values_list["Flights"]:
        calculate_flight_time(flight)
        times.append(calculate_flight_time(flight))

    shortest_time = min(times)
    for flight in all_values_list["Flights"]:
        if calculate_flight_time(flight) == shortest_time:
            shortest_flights.append(flight)

    return shortest_flights


async def most_optimal_tickets(xml_data_path: str, priority: str) -> list:
    """Get the most optimal tickets by price or flight time."""
    if priority == "cheapest":
        await get_shortest_flights(xml_data_path=xml_data_path)
    if priority == "shortest":
        await get_cheapest_tickets(xml_data_path=xml_data_path)
