from django.urls import path

from .views import LocationSearchView, PlanTripView, TripDetailView, TripListView

urlpatterns = [
    path("locations/search/", LocationSearchView.as_view(), name="location-search"),
    path("trips/plan/", PlanTripView.as_view(), name="trip-plan"),
    path("trips/", TripListView.as_view(), name="trip-list"),
    path("trips/<int:pk>/", TripDetailView.as_view(), name="trip-detail"),
]