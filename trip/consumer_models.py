import math
import random
from enum import Enum
from user.models import Ride


class Events(Enum):
    # Request Events
    MockDriverIncomingInitiateEvent = "MockDriverIncomingInitiateEvent"
    MockDriverChangeSpeedEvent = "MockDriverChangeSpeedEvent"
    BroadcastDriverLiveLocationEvent = "BroadcastDriverLiveLocationEvent"
    MockDriverOngoingInitiateEvent = "MockDriverOngoingInitiateEvent"
    CustomerPickedUpOtpEvent = "CustomerPickedUpOtpEvent"
    # Response Events
    MockDriverConnectEventResult = "MockDriverConnectEventResult"
    IdleDriverConnectEventResult = "IdleDriverConnectEventResult"
    MockDriverInitiateEventResult = "MockDriverInitiateEventResult"
    MockDriverInProgressEventResult = "MockDriverInProgressEventResult"
    MockDriverReadyToPickupEventResult = "MockDriverReadyToPickupEventResult"
    BroadcastDriverLiveLocationEventResult = "BroadcastDriverLiveLocationEventResult"
    CustomerPickedUpOtpEventResult = "CustomerPickedUpOtpEventResult"
    DriverSelectedForRideResult = "DriverSelectedForRideResult"
    RideCancelledEventResult = "RideCancelledEventResult"


class MockDriverConnectEventResultResponse:

    def __init__(self, message: str, route: dict, state, connection: bool = True, error=None):
        self.message: str = message
        self.route: dict = route
        self.state = state
        self.connection = connection
        self.error = error

    def to_json(self):
        return {
            "message": self.message,
            "route": self.route,
            "state": self.state,
            "connection": self.connection,
            "error": self.error
        }


class MockDriverConnectEventResult:
    def __init__(self, message: str, route: dict, state, connection: bool = True, error=None):
        self.response = MockDriverConnectEventResultResponse(message, route, state, connection, error)
        self.event = Events.MockDriverConnectEventResult.value

    def to_json(self):
        return {
            "response": self.response.to_json(),
            "event": self.event
        }


class MockDriverInitiateEventResultResponse:
    def __init__(self, driver_loc: dict, customer_loc: dict, total_cords: int, route: list, state: Ride.State):
        self.driver_loc = driver_loc
        self.customer_loc = customer_loc
        self.total_cords = total_cords
        self.route = route
        self.state = state

    def to_json(self):
        return {
            "driver_loc": self.driver_loc,
            "customer_loc": self.customer_loc,
            "total_cords": self.total_cords,
            "route": self.route,
            "state": self.state
        }


class MockDriverInitiateEventResult:

    def __init__(self, driver_loc: dict, customer_loc: dict, total_cords: int, route: list, state: Ride.State):
        self.response = MockDriverInitiateEventResultResponse(driver_loc, customer_loc, total_cords, route, state)
        self.event = Events.MockDriverInitiateEventResult.value

    def to_json(self):
        return {
            "response": self.response.to_json(),
            "event": self.event
        }


class MockDriverInProgressEventResultResponse:
    def __init__(self, driver_loc: dict, state):
        self.driver_loc = driver_loc
        self.state = state

    def to_json(self):
        return {
            "driver_loc": self.driver_loc,
            "state": self.state
        }


class MockDriverInProgressEventResult:

    def __init__(self, driver_loc: dict, state=Ride.State.DRIVER_INCOMING):
        self.response = MockDriverInProgressEventResultResponse(driver_loc, state)
        self.event = Events.MockDriverInProgressEventResult.value

    def to_json(self):
        return {
            "response": self.response.to_json(),
            "event": self.event
        }


class MockDriverReadyToPickupEventResultResponse:
    def __init__(self, driver_loc: dict, state: Ride.State):
        digits = "0123456789"
        self.driver_loc = driver_loc
        self.state = state
        self.otp = ''.join([digits[math.floor(random.random() * 10)] for _ in range(4)])

    def to_json(self):
        return {
            "driver_loc": self.driver_loc,
            "state": self.state,
            "otp": self.otp
        }


class MockDriverReadyToPickupEventResult:

    def __init__(self, driver_loc: dict, state: Ride.State):
        self.response = MockDriverReadyToPickupEventResultResponse(driver_loc, state)
        self.event = Events.MockDriverReadyToPickupEventResult.value

    def to_json(self):
        return {
            "response": self.response.to_json(),
            "event": self.event
        }


class MockDriverIncomingInitiateEventRequest:

    def __init__(self, mock_driver: bool, location: dict = None):
        self.mock_driver = mock_driver
        self.location = location

    def to_json(self):
        return {
            "mock_driver": self.mock_driver,
            "location": self.location
        }


class MockDriverIncomingInitiateEvent:

    def __init__(self, request, event):
        self.request = MockDriverIncomingInitiateEventRequest(**request)
        self.event = Events.MockDriverIncomingInitiateEvent.value
        assert self.event == event, "passed event is incorrect fot this operation"

    def to_json(self):
        return {
            "request": self.request.to_json(),
            "event": self.event
        }


class MockDriverOngoingInitiateEventRequest:

    def __init__(self, mock_driver: bool, location: dict = None):
        self.mock_driver = mock_driver
        self.location = location

    def to_json(self):
        return {
            "mock_driver": self.mock_driver,
            "location": self.location
        }


class MockDriverOngoingInitiateEvent:

    def __init__(self, request, event):
        self.request = MockDriverOngoingInitiateEventRequest(**request)
        self.event = Events.MockDriverOngoingInitiateEvent.value
        assert self.event == event, "passed event is incorrect fot this operation"

    def to_json(self):
        return {
            "request": self.request.to_json(),
            "event": self.event
        }


class MockDriverChangeSpeedEventRequest:

    def __init__(self, new_speed: int = 3, new_sleep: float = 0.5):
        self.new_speed = new_speed
        self.new_sleep = new_sleep

    def to_json(self):
        return {
            "new_speed": self.new_speed,
            "new_sleep": self.new_sleep,
        }


class MockDriverChangeSpeedEvent:

    def __init__(self, request, event):
        self.request = MockDriverChangeSpeedEventRequest(**request)
        self.event = Events.MockDriverChangeSpeedEvent.value
        assert self.event == event, "passed event is incorrect fot this operation"

    def to_json(self):
        return {
            "request": self.request.to_json(),
            "event": self.event
        }


class CustomerPickedUpOtpEventRequest:

    def __init__(self, picked_up):
        self.picked_up = picked_up

    def to_json(self):
        return {
            'picked_up': self.picked_up
        }


class CustomerPickedUpOtpEvent:

    def __init__(self, request, event):
        self.request = CustomerPickedUpOtpEventRequest(**request)
        self.event = Events.CustomerPickedUpOtpEvent.value
        assert self.event == event, "passed event is incorrect for this operation"

    def to_json(self):
        return {
            'request': self.request.to_json(),
            'event': self.event
        }


class CustomerPickedUpOtpEventResultResponse:

    def __init__(self, otp):
        self.otp = otp

    def to_json(self):
        return {
            'otp': self.otp
        }


class CustomerPickedUpOtpEventResult:

    def __init__(self, otp):
        self.response = CustomerPickedUpOtpEventResultResponse(otp)
        self.event = Events.CustomerPickedUpOtpEventResult.value

    def to_json(self):
        return {
            'response': self.response.to_json(),
            'event': self.event
        }


class BroadcastDriverLiveLocationEventResultResponse:

    def __init__(self, location: list):
        self.location = location

    def to_json(self):
        return {
            "location": self.location
        }


class BroadcastDriverLiveLocationEventResult:

    def __init__(self, location: list):
        self.response = BroadcastDriverLiveLocationEventResultResponse(location)
        self.event = Events.BroadcastDriverLiveLocationEventResult.value

    def to_json(self):
        return {
            "response": self.response.to_json(),
            "event": self.event
        }


class BroadcastDriverLiveLocationEventRequest:
    def __init__(self, location):
        self.location = location

    def to_json(self):
        return {
            "location": self.location
        }


class BroadcastDriverLiveLocationEvent:
    def __init__(self, request, event):
        self.request = BroadcastDriverLiveLocationEventRequest(**request)
        self.event = Events.BroadcastDriverLiveLocationEvent.value
        assert self.event == event, "passed event is incorrect for this operation"

    def to_json(self):
        return {
            "request": self.request.to_json(),
            "event": self.event
        }


class IdleDriverConnectEventResultResponse:

    def __init__(self, message: str, connection: bool = True, error=None):
        self.message: str = message
        self.connection = connection
        self.error = error

    def to_json(self):
        return {
            "message": self.message,
            "connection": self.connection,
            "error": self.error
        }


class IdleDriverConnectEventResult:
    def __init__(self, message: str, connection: bool = True, error=None):
        self.response = IdleDriverConnectEventResultResponse(message, connection, error)
        self.event = Events.IdleDriverConnectEventResult.value

    def to_json(self):
        return {
            "response": self.response.to_json(),
            "event": self.event
        }


class DriverSelectedForRideResultResponse:

    def __init__(self, ride_id):
        self.ride_id = ride_id

    def to_json(self):
        return {
            'ride_id': self.ride_id
        }


class DriverSelectedForRideResult:

    def __init__(self, ride_id):
        self.response = DriverSelectedForRideResultResponse(ride_id)
        self.event = Events.DriverSelectedForRideResult.value

    def to_json(self):
        return {
            'response': self.response.to_json(),
            'event': self.event
        }


class RideCancelledEventResult:
    def __init__(self):
        self.event = Events.RideCancelledEventResult.value

    def to_json(self):
        return {
            'event': self.event
        }
