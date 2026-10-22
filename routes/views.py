from django.utils.dateparse import parse_datetime
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import Node, Edge, RouteHistory
from .serializers import NodeSerializer, EdgeSerializer, RouteHistorySerializer
import heapq


def shortest_path(source, destination):
    graph = {}
    print("==start sortest path")
    for edge in Edge.objects.select_related('source', 'destination').all():
        graph.setdefault(edge.source_id, []).append((edge.destination_id, edge.latency))

    queue = [(0, source.id, [source.name])]
    print("=====que",queue)
    best = {source.id: 0}

    while queue:
        latency, node_id, path = heapq.heappop(queue)
        print(latency, node_id, path,"latency, node_id, path===========")
        if node_id == destination.id:
            return latency, path

        if latency > best.get(node_id, float('inf')):
            continue

        for next_id, edge_latency in graph.get(node_id, []):
            new_latency = latency + edge_latency
            print(new_latency,"===new_latency")
            if new_latency >= best.get(next_id, float('inf')):
                continue

            best[next_id] = new_latency
            next_name = None

            for edge in Edge.objects.filter(destination_id=next_id).select_related('destination')[:1]:
                next_name = edge.destination.name
            print(next_name,"=============next_name")
            heapq.heappush(queue, (new_latency, next_id, path + [next_name]))

    return None, None


class NodeListCreateView(APIView):


    def get(self, request):
        print("=========request",request)
        # return Response(serializer.data, status=status.HTTP_201_CREATED)
        nodes = Node.objects.all().order_by('id')
        print(nodes)
        return Response(NodeSerializer(nodes, many=True).data)


    def post(self, request):
        
        serializer = NodeSerializer(data=request.data)

        if serializer.is_valid():
            serializer.save()
            
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class NodeDeleteView(APIView):
    def delete(self, request, pk):
        
        #  try:
        #             node = Node.objects.get(pk=pk)
        #         except Node.DoesNotExist:
        #             return Response({'error': 'node is not avaiable'}, status=status.HTTP_404_NOT_FOUND)
        
        
        try:
            node = Node.objects.get(pk=pk)
            print(node,"================node found")
        except Node.DoesNotExist:
            return Response({'error': 'node is not avaiable'}, status=status.HTTP_404_NOT_FOUND)

        node.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class EdgeListCreateView(APIView):

    def get(self, request):
        edges = Edge.objects.select_related('source', 'destination').all().order_by('id')
        return Response(EdgeSerializer(edges, many=True).data)
    
    def post(self, request):

        print(request.data,"====request.data")
        serializer = EdgeSerializer(data=request.data)
        
        if serializer.is_valid():    
            serializer.save()
            print(serializer.data,"=========serializer.data")
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class EdgeDeleteView(APIView):

    def delete(self, request, pk):
        
        try:
            print("==============pk",pk)
            edge = Edge.objects.get(pk=pk)
        except Edge.DoesNotExist:
            return Response({'error': 'reqested edges is not avaiable '}, status=status.HTTP_404_NOT_FOUND)

        edge.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class ShortestRouteView(APIView):
    
    def post(self, request):
        
        source_name = str(request.data.get('source', '')).strip()
        destination_name = str(request.data.get('destination', '')).strip()

        if not source_name or not destination_name:
            return Response({'error': 'provide sounce and destination to process '}, status=status.HTTP_400_BAD_REQUEST)

        try:
            source = Node.objects.get(name=source_name)
            destination = Node.objects.get(name=destination_name)
            print(source,destination,"===source")
        except Node.DoesNotExist:
            return Response({'error': 'nodes not found'}, status=status.HTTP_400_BAD_REQUEST)

        total_latency, path = shortest_path(source, destination)

        if path is None:
            return Response(
                {'error': f'there is no a path between {source_name} and {destination_name}'},
                status=status.HTTP_404_NOT_FOUND,
            )

        RouteHistory.objects.create(
            source=source,
            destination=destination,
            total_latency=total_latency,
            path=path,
        )

        return Response({'total_latency': total_latency, 'path': path})


class RouteHistoryView(APIView):

    def get(self, request):
        
        history = RouteHistory.objects.select_related('source', 'destination').all()
        source = request.query_params.get('source')
        destination = request.query_params.get('destination')
        date_from = request.query_params.get('date_from')
        date_to = request.query_params.get('date_to')
        limit = request.query_params.get('limit')

        if source:
           
            history = history.filter(source__name=source)
        
        if destination:
            history = history.filter(destination__name=destination)

        if date_from:
            
            parsed = parse_datetime(date_from)
            if not parsed:
                
                return Response({'error': 'incorrect from date'}, status=status.HTTP_400_BAD_REQUEST)
            
            history = history.filter(created_at__gte=parsed)

        if date_to:
            
            parsed = parse_datetime(date_to)
            
            if not parsed:
                return Response({'error': 'invcoorect date'}, status=status.HTTP_400_BAD_REQUEST)
            history = history.filter(created_at__lte=parsed)

        if limit:
            try:
                limit = int(limit)
                if limit <= 0:
                    raise ValueError
            except ValueError:
                return Response({'error': 'limit is not positive'}, status=status.HTTP_400_BAD_REQUEST)
            history = history[:limit]

        
        
        return Response(RouteHistorySerializer(history, many=True).data)
