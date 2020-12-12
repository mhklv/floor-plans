import math
import base64
import json


def json_convert(graph, outfile, img_local_path):
    json_vertices = list()

    for v in graph.vertices:
        if (v.active != True):
            continue

        json_vert = dict()
        json_vert['id'] = v.id
        json_vert['x_c'] = v.x
        json_vert['y_c'] = v.y
        json_vertices.append(json_vert)

    json_edges = list()

    visited_pairs_inverted = list()

    for e in graph.edges:
        if (e.from_id == e.to_id or [e.from_id, e.to_id] in visited_pairs_inverted):
            continue

        x1 = graph.vertices[e.from_id].x
        x2 = graph.vertices[e.to_id].x
        y1 = graph.vertices[e.from_id].y
        y2 = graph.vertices[e.to_id].y

        json_edge = dict()
        json_edge['source'] = e.from_id
        json_edge['target'] = e.to_id
        json_edges.append(json_edge)

        visited_pairs_inverted.append([e.to_id, e.from_id])

    json_graph = dict()
    json_graph['nodes'] = json_vertices
    json_graph['links'] = json_edges

    # json_plan_bundle = dict()
    # json_plan_bundle['graph'] = json_graph

    outfile.write(json.dumps(json_graph, sort_keys=True))

    # outfile.write(json.dumps(json_plan_bundle, sort_keys=True, indent=4))