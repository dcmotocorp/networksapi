from rest_framework import serializers
from .models import Node, Edge, RouteHistory


class NodeSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = Node
        fields = ['id', 'name']

    
    def validate_name(self, value):
        value = value.strip()
        print(value,"======================value")
        if not value:
            raise serializers.ValidationError('Name is required')
        
        return value


class EdgeSerializer(serializers.ModelSerializer):
    
    source = serializers.CharField()
    destination = serializers.CharField()

    class Meta:
        model = Edge
        fields = ['id', 'source', 'destination', 'latency']

    def validate_latency(self, value):
        if value <= 0:
            raise serializers.ValidationError('value must be greater than 0')
        return value

    def validate(self, attrs):
        source_name = attrs.get('source', '').strip()
        destination_name = attrs.get('destination', '').strip()

        if not source_name or not destination_name:
            raise serializers.ValidationError('Source and destination are required')

        try:
            source = Node.objects.get(name=source_name)
            destination = Node.objects.get(name=destination_name)
        except Node.DoesNotExist:
            raise serializers.ValidationError('Source or destination node not found')

        if Edge.objects.filter(source=source, destination=destination).exists():
            raise serializers.ValidationError('Edge already exists')

        attrs['source'] = source
        attrs['destination'] = destination

        print("===================attr")
        return attrs

    def to_representation(self, instance):
        print("===instace",instance)
        return {
            'id': instance.id,
            'source': instance.source.name,
            'destination': instance.destination.name,
            'latency': instance.latency,
        }


class RouteHistorySerializer(serializers.ModelSerializer):
    
    
    source = serializers.CharField(source='source.name')
    destination = serializers.CharField(source='destination.name')

    class Meta:
        model = RouteHistory
        fields = ['id', 'source', 'destination', 'total_latency', 'path', 'created_at']
