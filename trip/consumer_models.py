from enum import Enum
from user.models import Ride


class Events(Enum):
    # Request Events
    MockDriverIncomingInitiateEvent = "MockDriverIncomingInitiateEvent"
    MockDriverChangeSpeedEvent = "MockDriverChangeSpeedEvent"
    BroadcastDriverLiveLocationEvent = "BroadcastDriverLiveLocationEvent"
    # Response Events
    MockDriverConnectEventResult = "MockDriverConnectEventResult"
    IdleDriverConnectEventResult = "IdleDriverConnectEventResult"
    MockDriverIncomingInitiateEventResult = "MockDriverIncomingInitiateEventResult"
    MockDriverIncomingInProgressEventResult = "MockDriverIncomingInProgressEventResult"
    MockDriverReadyToPickupEventResult = "MockDriverReadyToPickupEventResult"
    BroadcastDriverLiveLocationEventResult = "BroadcastDriverLiveLocationEventResult"


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


class MockDriverIncomingInitiateEventResultResponse:
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


class MockDriverIncomingInitiateEventResult:

    def __init__(self, driver_loc: dict, customer_loc: dict, total_cords: int, route: list, state: Ride.State):
        self.response = MockDriverIncomingInitiateEventResultResponse(driver_loc, customer_loc, total_cords, route, state)
        self.event = Events.MockDriverIncomingInitiateEventResult.value

    def to_json(self):
        return {
            "response": self.response.to_json(),
            "event": self.event
        }


class MockDriverIncomingInProgressEventResultResponse:
    def __init__(self, driver_loc: dict, state):
        self.driver_loc = driver_loc
        self.state = state

    def to_json(self):
        return {
            "driver_loc": self.driver_loc,
            "state": self.state
        }


class MockDriverIncomingInProgressEventResult:

    def __init__(self, driver_loc: dict, state=Ride.State.DRIVER_INCOMING):
        self.response = MockDriverIncomingInProgressEventResultResponse(driver_loc, state)
        self.event = Events.MockDriverIncomingInProgressEventResult.value

    def to_json(self):
        return {
            "response": self.response.to_json(),
            "event": self.event
        }


class MockDriverReadyToPickupEventResultResponse:
    def __init__(self, driver_loc: dict, state: Ride.State):
        self.driver_loc = driver_loc
        self.state = state

    def to_json(self):
        return {
            "driver_loc": self.driver_loc,
            "state": self.state
        }


class MockDriverReadyToPickupEventResult:

    def __init__(self, driver_loc: dict, state: Ride.State = Ride.State.PICKUP_READY):
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
