"""
DRINK MIXING & SERVING ROBOT SYSTEM (simple first-year style)
"""

import time
import random
from enum import Enum
from queue import Queue
from datetime import datetime


# -------------------------
# ENUMS
# -------------------------

class DrinkType(Enum):
    WATER = "Water"
    GREEN_TEA = "Green Tea"
    COFFEE = "Coffee"
    MILK_TEA = "Milk Tea"
    JUICE = "Juice"


class RobotStatus(Enum):
    IDLE = "Idle"
    MOVING = "Moving"
    SERVING = "Serving"
    RETURNING = "Returning to base"


class StationStatus(Enum):
    AVAILABLE = "Available"
    BUSY = "Busy"
    EMPTY = "Out of stock"


# -------------------------
# DATA CLASSES (manual style)
# -------------------------

class Position:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def distance_to(self, other):
        # Manhattan distance
        return abs(self.x - other.x) + abs(self.y - other.y)

    def __str__(self):
        return f"({self.x}, {self.y})"


class DrinkRequest:
    def __init__(self, request_id, drink_type, customer_name):
        self.request_id = request_id
        self.drink_type = drink_type
        self.customer_name = customer_name
        self.timestamp = datetime.now().strftime("%H:%M:%S")
        self.fulfilled = False

    def __str__(self):
        if self.fulfilled:
            status = "Completed"
        else:
            status = "Waiting"

        return f"[#{self.request_id}] {self.customer_name} requested {self.drink_type.value} at {self.timestamp} - {status}"


# -------------------------
# DRINK STATION
# -------------------------

class DrinkStation:
    def __init__(self, station_id, drink_type, position, capacity=10):
        self.station_id = station_id
        self.drink_type = drink_type
        self.position = position
        self.capacity = capacity
        self.current_stock = capacity
        self.status = StationStatus.AVAILABLE
        self.serve_time = self._default_serve_time()

    def _default_serve_time(self):
        # simple if-elif style
        if self.drink_type == DrinkType.WATER:
            return 1
        elif self.drink_type == DrinkType.GREEN_TEA:
            return 2
        elif self.drink_type == DrinkType.COFFEE:
            return 3
        elif self.drink_type == DrinkType.MILK_TEA:
            return 3
        elif self.drink_type == DrinkType.JUICE:
            return 2
        return 2

    def is_available(self):
        return self.status == StationStatus.AVAILABLE and self.current_stock > 0

    def dispense(self):
        if not self.is_available():
            return False

        self.status = StationStatus.BUSY
        print(f"      Station [{self.drink_type.value}] is preparing... ({self.serve_time}s)")
        time.sleep(self.serve_time * 0.3)  # speed-up for demo

        self.current_stock -= 1

        if self.current_stock <= 0:
            self.current_stock = 0
            self.status = StationStatus.EMPTY
        else:
            self.status = StationStatus.AVAILABLE

        return True

    def refill(self):
        self.current_stock = self.capacity
        self.status = StationStatus.AVAILABLE
        print(f"   Station [{self.drink_type.value}] refilled.")

    def info(self):
        return (
            f"Station #{self.station_id} | {self.drink_type.value:10s} | "
            f"Position {self.position} | Stock: {self.current_stock}/{self.capacity} | "
            f"{self.status.value}"
        )


# -------------------------
# ROBOT
# -------------------------

class Robot:
    HOME = Position(0, 0)

    def __init__(self, robot_id, speed=1):
        self.robot_id = robot_id
        self.speed = speed
        self.position = Position(0, 0)
        self.status = RobotStatus.IDLE
        self.total_served = 0
        self.current_request = None

    def _travel_to(self, target, label=""):
        dist = self.position.distance_to(target)
        travel_sec = dist / self.speed
        print(f"   Robot#{self.robot_id} moving to {label} {target} - distance: {dist} (~{travel_sec:.1f}s)")
        time.sleep(travel_sec * 0.2)
        self.position = Position(target.x, target.y)

    def serve(self, request, station, customer_pos):
        self.current_request = request
        self.status = RobotStatus.MOVING

        print("\n   --------------------------------------")
        print(f"   Robot#{self.robot_id} received request #{request.request_id}")
        print(f"      Customer: {request.customer_name} | Drink: {request.drink_type.value}")

        # 1) move to station
        self._travel_to(station.position, f"Station [{station.drink_type.value}]")

        # 2) prepare drink
        self.status = RobotStatus.SERVING
        ok = station.dispense()
        if not ok:
            print("   Station out of stock. Request failed.")
            self.status = RobotStatus.IDLE
            self.current_request = None
            return False

        # 3) move to customer
        self._travel_to(customer_pos, f"Customer ({request.customer_name})")
        print(f"   Delivered {request.drink_type.value} to {request.customer_name}!")

        # 4) return home
        self.status = RobotStatus.RETURNING
        self._travel_to(Robot.HOME, "Home")

        # finish
        request.fulfilled = True
        self.total_served += 1
        self.status = RobotStatus.IDLE
        self.current_request = None
        print(f"   Robot#{self.robot_id} finished. Total served: {self.total_served}")
        return True

    def info(self):
        return (
            f"Robot#{self.robot_id} | Position: {self.position} | "
            f"Status: {self.status.value} | Total served: {self.total_served}"
        )


# -------------------------
# DISPATCH SYSTEM
# -------------------------

class DispatchSystem:
    def __init__(self):
        self.stations = {}          # key: DrinkType -> DrinkStation
        self.robots = []            # list of Robot
        self.requests = []          # history list
        self.request_queue = Queue()
        self._request_counter = 0

        print("=" * 60)
        print("  DRINK SERVICE ROBOT SYSTEM - STARTUP")
        print("=" * 60)

    def add_station(self, drink_type, position, capacity=10):
        station_id = len(self.stations) + 1
        station = DrinkStation(station_id, drink_type, position, capacity)
        self.stations[drink_type] = station
        print("  Added:", station.info())

    def add_robot(self, speed=1):
        robot = Robot(len(self.robots) + 1, speed=speed)
        self.robots.append(robot)
        print(f"  Robot#{robot.robot_id} ready (speed: {speed})")
        return robot

    def _get_idle_robot(self):
        for robot in self.robots:
            if robot.status == RobotStatus.IDLE:
                return robot
        return None

    def _find_station(self, drink_type):
        station = self.stations.get(drink_type)
        if station and station.is_available():
            return station
        return None

    def submit_request(self, customer_name, drink_type):
        self._request_counter += 1
        req = DrinkRequest(self._request_counter, drink_type, customer_name)
        self.requests.append(req)
        self.request_queue.put(req)
        print("\nNew request:", req)
        return req

    def process_next(self):
        if self.request_queue.empty():
            print("  No requests in queue.")
            return

        req = self.request_queue.get()
        robot = self._get_idle_robot()
        station = self._find_station(req.drink_type)

        if robot is None:
            print(f"  No idle robot. Request #{req.request_id} sent back to queue.")
            self.request_queue.put(req)
            return

        if station is None:
            print(f"  Station [{req.drink_type.value}] unavailable.")
            req.fulfilled = False
            return

        customer_pos = Position(random.randint(1, 8), random.randint(1, 8))
        robot.serve(req, station, customer_pos)

    def process_all(self):
        print(f"\nProcessing {self.request_queue.qsize()} requests...\n")
        while not self.request_queue.empty():
            self.process_next()

    def print_status(self):
        print("\n" + "=" * 60)
        print("  SYSTEM STATUS")
        print("=" * 60)

        print("\n  STATIONS:")
        for st in self.stations.values():
            print("   ", st.info())

        print("\n  ROBOTS:")
        for rb in self.robots:
            print("   ", rb.info())

        print("\n  REQUEST HISTORY:")
        for req in self.requests:
            print("   ", req)

        done = sum(1 for r in self.requests if r.fulfilled)
        print(f"\n  Completed: {done}/{len(self.requests)}")
        print("=" * 60)


# -------------------------
# RUN DEMO
# -------------------------

def main():
    system = DispatchSystem()
    print()

    print("Setting up stations:")
    system.add_station(DrinkType.WATER, Position(2, 0), capacity=20)
    system.add_station(DrinkType.GREEN_TEA, Position(5, 0), capacity=10)
    system.add_station(DrinkType.COFFEE, Position(8, 0), capacity=8)
    system.add_station(DrinkType.MILK_TEA, Position(5, 5), capacity=6)
    system.add_station(DrinkType.JUICE, Position(2, 5), capacity=5)

    print("\nInitializing robots:")
    system.add_robot(speed=2)
    system.add_robot(speed=1)

    print("\nCustomers place orders:")
    orders = [
        ("An", DrinkType.COFFEE),
        ("Binh", DrinkType.WATER),
        ("Chi", DrinkType.GREEN_TEA),
        ("Dung", DrinkType.MILK_TEA),
        ("Em", DrinkType.JUICE),
        ("Phu", DrinkType.COFFEE),
    ]

    for name, drink in orders:
        system.submit_request(name, drink)
        time.sleep(0.1)

    system.process_all()
    system.print_status()


if __name__ == "__main__":
    main()
    try:
        input("\nPress Enter to close...")
    except EOFError:
        pass
