import heapq
import math

from django.db.models import Q

from .models import NavigationEdge, NavigationPoint, QRLocation, Room


def _distance(a, b):
    return math.dist((a.x, a.y, a.z), (b.x, b.y, b.z))


def resolve_point(value):
    """Resolve a navigation-point code, QR code, or room code to a point."""
    if not value:
        return None
    point = NavigationPoint.objects.filter(code__iexact=value).select_related("floor").first()
    if point:
        return point
    qr = QRLocation.objects.filter(code__iexact=value).select_related("navigation_point__floor").first()
    if qr:
        return qr.navigation_point
    room = (
        Room.objects.filter(Q(room_code__iexact=value) | Q(name__iexact=value), is_active=True)
        .select_related("navigation_point__floor")
        .first()
    )
    return room.navigation_point if room else None


def shortest_path(start_value, destination_value, accessible_only=False):
    start = resolve_point(start_value)
    goal = resolve_point(destination_value)
    if not start or not goal:
        raise ValueError("Choose a valid current location and destination.")
    if start.floor_id != goal.floor_id:
        raise ValueError("Cross-floor routing will be enabled after upper-floor layouts are supplied.")

    points = {
        point.id: point
        for point in NavigationPoint.objects.filter(floor=start.floor).select_related("floor")
    }
    edges = NavigationEdge.objects.filter(
        start_point__floor=start.floor,
        end_point__floor=start.floor,
        is_closed=False,
    ).select_related("start_point", "end_point")

    graph = {point_id: [] for point_id in points}
    for edge in edges:
        if accessible_only and (not edge.accessible or edge.stairs):
            continue
        weight = edge.distance or _distance(edge.start_point, edge.end_point)
        graph[edge.start_point_id].append((edge.end_point_id, weight))
        graph[edge.end_point_id].append((edge.start_point_id, weight))

    frontier = [(0.0, start.id)]
    came_from = {start.id: None}
    cost_so_far = {start.id: 0.0}
    while frontier:
        _, current_id = heapq.heappop(frontier)
        if current_id == goal.id:
            break
        for next_id, weight in graph.get(current_id, []):
            new_cost = cost_so_far[current_id] + weight
            if next_id not in cost_so_far or new_cost < cost_so_far[next_id]:
                cost_so_far[next_id] = new_cost
                heapq.heappush(frontier, (new_cost + _distance(points[next_id], goal), next_id))
                came_from[next_id] = current_id

    if goal.id not in came_from:
        raise ValueError("No available route connects these locations.")

    route_ids = []
    current_id = goal.id
    while current_id is not None:
        route_ids.append(current_id)
        current_id = came_from[current_id]
    route_ids.reverse()
    route = [points[point_id] for point_id in route_ids]
    return {
        "start": start,
        "goal": goal,
        "points": route,
        "distance": round(cost_so_far[goal.id], 1),
        "accessible": accessible_only,
    }
