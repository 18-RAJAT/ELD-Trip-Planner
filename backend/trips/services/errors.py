class ServiceError(Exception):
    def __init__(self, message, status_code=502):
        super().__init__(message)
        self.message = message
        self.status_code = status_code


class GeocodingError(ServiceError):
    def __init__(self, message):
        super().__init__(message, status_code=422)


class RoutingError(ServiceError):
    def __init__(self, message):
        super().__init__(message, status_code=422)