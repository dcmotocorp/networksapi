from django.urls import path
from .views import NodeListCreateView, NodeDeleteView, EdgeListCreateView, EdgeDeleteView, ShortestRouteView, RouteHistoryView

urlpatterns = [
    path('nodes', NodeListCreateView.as_view()),
    path('nodes/<int:pk>', NodeDeleteView.as_view()),
    path('edges', EdgeListCreateView.as_view()),
    path('edges/<int:pk>', EdgeDeleteView.as_view()),
    path('routes/shortest', ShortestRouteView.as_view()),
    path('routes/history', RouteHistoryView.as_view()),
]
