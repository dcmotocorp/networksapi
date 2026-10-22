from django.db import models


class Node(models.Model):
    
    name = models.CharField(max_length=100, unique=True)

    


class Edge(models.Model):
    
    source = models.ForeignKey(Node, on_delete=models.CASCADE, related_name='outgoing_edges')
    destination = models.ForeignKey(Node, on_delete=models.CASCADE, related_name='incoming_edges')
    latency = models.FloatField()

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['source', 'destination'], name='unique_edge')
        ]


class RouteHistory(models.Model):
    
    source = models.ForeignKey(Node, on_delete=models.CASCADE, related_name='route_source_history')
    destination = models.ForeignKey(Node, on_delete=models.CASCADE, related_name='route_destination_history')
    total_latency = models.FloatField()
    path = models.JSONField(default=list)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
