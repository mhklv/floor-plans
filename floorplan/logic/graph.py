class Vertice:
    def __init__(self, id, x, y):
        self.id = id
        self.x = x
        self.y = y
        self.active = True


class Edge:
    def __init__(self, from_id, to_id):
        self.from_id = from_id
        self.to_id = to_id


class Graph:
    def __init__(self, vertices):
        self.vertices = vertices
        self.edges = list()

    def add_edge(self, from_id, to_id):
        self.edges.append(Edge(from_id, to_id))