from operator import itemgetter

DEFAULT_X_INTERSECTION_TOLERANCE = 2
DEFAULT_Y_INTERSECTIOB_TOLERANCE = 2

def filter_edges(edges, orientation=None,
    edge_type=None,
    min_length=3):
    '''
    过滤edges，将长度<min_length的edge过滤
    '''
    if orientation not in ("v", "h", None):
        raise ValueError("Orientation must be 'v' or 'h'")

    def test(e):
        dim = "height" if e["orientation"] == "v" else "width"
        et = (e["object_type"] == edge_type if edge_type != None else True)
        return et & (
            (True if orientation == None else (e["orientation"] == orientation)) & 
            (e[dim] >= min_length)
        )

    edges = filter(test, edges)
    return list(edges)


def edges_to_intersections(edges, 
	x_intersection_tolerance=DEFAULT_X_INTERSECTION_TOLERANCE,
	y_intersection_tolerance=DEFAULT_Y_INTERSECTIOB_TOLERANCE):
    """
    给出一系列的edges，找到它们的交点，以及构成交点的交线
    intersection是形如{(X, Y):{"v":[V]}, "h":[H]}
    (X, Y)表示交点坐标，V、H表示构成交点的edges
    """
    filtered_edges = filter_edges(edges, min_length=3)
    intersections = {}
    v_edges, h_edges = [ list(filter(lambda x: x["orientation"] == o, filtered_edges))
        for o in ("v", "h") ]
    for v in sorted(v_edges, key=itemgetter("x0", "top")):
        for h in sorted(h_edges, key=itemgetter("top", "x0")):
            if ((v["top"] <= (h["top"] + y_intersection_tolerance)) and
                (v["bottom"] >= (h["top"] - y_intersection_tolerance)) and
                (v["x0"] >= (h["x0"] - x_intersection_tolerance)) and
                (v["x0"] <= (h["x1"] + x_intersection_tolerance))):
                vertex = (v["x0"], h["top"])
                if vertex not in intersections:
                    intersections[vertex] = { "v": [], "h": [] }
                intersections[vertex]["v"].append(v)
                intersections[vertex]["h"].append(h)
    return intersections
