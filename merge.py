import itertools
from operator import itemgetter

DEFAULT_MERGE_TOLERANCE = 3


def resize_edge(edge, key, value):
    '''
    调整edge大小
    调整的关键字可以是x0，x1，top，bottom四个参数中的一个
    value是希望调整到的数值
    '''
    assert(key in ("x0", "x1", "top", "bottom"))
    old_value = edge[key]
    diff = value - old_value
    if key in ("x0", "x1"):
        if key == "x0":
            assert(value <= edge["x1"]) #x0必须小于x1
        else:
            assert(value >= edge["x0"]) #x1必须大于x0
        new_edge = (
            (key, value),
            ("width", edge["width"] + diff),
        )
    if key == "top":
        assert(value <= edge["bottom"]) #top必须小于bottom
        new_edge = [
            (key, value),
            ("doctop", edge["doctop"] + diff),
            ("height", edge["height"] - diff),
        ]
        if "y1" in edge:
            new_edge += [
                ("y1", edge["y1"] - diff),
            ]
    if key == "bottom":
        assert(value >= edge["top"]) #bottom必须大于top
        new_edge = [
            (key, value),
            ("height", edge["height"] + diff),
        ]
        if "y0" in edge:
            new_edge += [
                ("y0", edge["y0"] - diff),
            ]
    return edge.__class__(tuple(edge.items()) + tuple(new_edge))


def join_edge(edges, orientation, tolerance):
    """
    把水平方向、水平距离足够近的edges归入同一条edge
    把垂直方向、垂直距离足够近的edges归入同一条edge
    """
    if orientation == "h":
        min_prop, max_prop = "x0", "x1"
    elif orientation == "v":
        min_prop, max_prop = "top", "bottom"
    else:
        raise ValueError("Orientation must be 'v' or 'h'")

    sorted_edges = list(sorted(edges, key=itemgetter(min_prop)))
    joined = [ sorted_edges[0] ]
    for e in sorted_edges[1:]:
        last = joined[-1] 
        if e[min_prop] <= (last[max_prop] + tolerance):
            if e[max_prop] > last[max_prop]:
                # 延长last
                joined[-1] = resize_edge(last, max_prop, e[max_prop])
            else:
                # 当前edge已经完全包含在last中
                pass
        else:
            # 当前edge不在这个group
            joined.append(e)

    return joined


def merge_edges(edges, merge_tolerance=DEFAULT_MERGE_TOLERANCE):
    """
    将edges分组，每一个组里面距离足够近的edge合并为一条直线
    """
    def get_group(edge):
        if edge["orientation"] == "h":
            return ("h", edge["top"])
        else:
            return ("v", edge["x0"])

    
    if merge_tolerance > 0:
        _sorted = sorted(edges, key=get_group) # 水平方向的edge按top排序，铅直方向的edge按x0排序
        edge_groups = itertools.groupby(_sorted, key=get_group)
        
        
        edge_gen = (join_edge(items, k[0], merge_tolerance)
            for k, items in edge_groups)
        '''
        这里的k是一个二元组，形如('h', Decimal('45.380')),k[0]代表方向，k[1]代表具体数值
        对与'h'，k[1]代表top，对于'v'，k[1]代表x0
        items是一个包含了多条edge的集合，这些edge的k[1]值相同
        '''
        merged = list(itertools.chain(*edge_gen))
        return merged
    else:
        print("Wrong merge tolerance!")

