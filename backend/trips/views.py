from rest_framework import status
from rest_framework.generics import ListAPIView, RetrieveAPIView
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Trip
from .serializers import TripInputSerializer, TripSerializer
from .services.errors import ServiceError
from .services.geocoding import search_locations
from .services.planner import plan


def _location_input(data, prefix):
    return {
        "query": data[f"{prefix}_location"],
        "lat": data.get(f"{prefix}_lat"),
        "lng": data.get(f"{prefix}_lng"),
    }


class PlanTripView(APIView):
    def post(self, request):
        serializer = TripInputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        try:
            result = plan(
                _location_input(data, "current"),
                _location_input(data, "pickup"),
                _location_input(data, "dropoff"),
                data["current_cycle_used"],
            )
        except ServiceError as error:
            return Response({"detail": error.message}, status=error.status_code)
        trip = Trip.objects.create(
            current_location=data["current_location"],
            pickup_location=data["pickup_location"],
            dropoff_location=data["dropoff_location"],
            current_cycle_used=data["current_cycle_used"],
            result=result,
        )
        return Response(TripSerializer(trip).data, status=status.HTTP_201_CREATED)


class LocationSearchView(APIView):
    def get(self, request):
        query = request.query_params.get("q", "")
        try:
            results = search_locations(query)
        except ServiceError as error:
            return Response({"detail": error.message}, status=error.status_code)
        return Response(results, status=status.HTTP_200_OK)


class TripListView(ListAPIView):
    queryset = Trip.objects.all()
    serializer_class = TripSerializer


class TripDetailView(RetrieveAPIView):
    queryset = Trip.objects.all()
    serializer_class = TripSerializer