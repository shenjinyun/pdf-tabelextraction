from decimal import Decimal, ROUND_HALF_UP
from operator import itemgetter
import itertools

DEFAULT_SNAP_TOLERANCE = 3

def filter_edges(edges, orientation=None,
    edge_type=None,
    min_length=1):
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


def cluster_group(xs, tolerance=0):
    '''
    一条有宽度的线由多个edge组成
    把水平方向、垂直距离足够近，铅直方向，水平距离足够近的edge归入一个group
    '''
    tolerance = Decimal(tolerance)
    if tolerance == 0: return [ [x] for x in sorted(xs) ]
    if len(xs) < 2: return [ [x] for x in sorted(xs) ]
    groups = []
    xs = list(sorted(xs))
    current_group = [xs[0]]
    last = xs[0]
    for x in xs[1:]:
        if x <= (last + tolerance):
            current_group.append(x)
        else:
            groups.append(current_group)
            current_group = [x]
        last = x
    groups.append(current_group)
    return groups


def make_cluster_group(values, tolerance):
    tolerance = Decimal(tolerance)
    groups = cluster_group(set(values), tolerance)
    

    nested_tuples = [ [ (val, i) for val in value_group ]
        for i, value_group in enumerate(groups) ]

    cluster_groups = dict(itertools.chain(*nested_tuples))
    return cluster_groups


def cluster_edges(edges, attr, tolerance):
    attr_getter = itemgetter(attr) #注意这里需要将attr转换为itemgetter(attr)
    edges = list(edges)
    values = map(attr_getter, edges)
    '''
    这里values得到的是一个map对象，存储了edge中attr对应的值
    水平方向的edge得到top值，铅直方向的edge得到x0值
    '''
    cluster_groups = make_cluster_group(values, tolerance)
    '''
    cluster_groups形如Decimal('36.024'): 0，得到的是value in values所在的group编号
    '''

    get_0, get_1 = itemgetter(0), itemgetter(1)
    
    cluster_tuples = sorted(((edge, cluster_groups.get(attr_getter(edge)))
        for edge in edges), key=get_1)
    '''
    这里的for edge in edges:
              (edge, cluster_groups.get(attr_getter(edge)))
    得到的是一个二元组(X, Y)
    其中X表示edge，Y表示edge的attr_getter所在的group编号
    cluster_tuples是按group编号排序后的二元组
    '''
    grouped = itertools.groupby(cluster_tuples, key=get_1)
    '''
    这里的grouped是将edges按照group编号分组，每个组里面有很多个edge
    '''
    
    clusters = [ list(map(get_0, v))
        for k, v in grouped ]
    '''
    k是组编号，v是属于这个组的多个edge组成的集合
    '''

    return clusters
    '''
    每一个组的edge被分在一个字典[]里面，clusters是包含了所有组的字典
    '''



def move_edge(edge, axis, value):
    assert(axis in ("h", "v"))
    if axis == "h":
        new_edge = (
            ("x0", edge["x0"] + value),
            ("x1", edge["x1"] + value),
        )
    if axis == "v":
        new_edge = [
            ("top", edge["top"] + value),
            ("bottom", edge["bottom"] + value),
        ]
        if "doctop" in edge:
            new_edge += [ ("doctop", edge["doctop"] + value) ]
        if "y0" in edge:
            new_edge += [
                ("y0", edge["y0"] - value),
                ("y1", edge["y1"] - value),
            ]
    return edge.__class__(tuple(edge.items()) + tuple(new_edge))


def cluster_to_edges(cluster, orientation):
    """
    把一个group里面的edge移动到同一位置（认为是同一条线）
    """
    if orientation not in ("h", "v"):
        raise ValueError("Orientation must be 'v' or 'h'")
    if len(cluster) == 0: return []
    move_axis = "v" if orientation == "h" else "h"
    attr = "top" if orientation == "h" else "x0"
    values = list(map(itemgetter(attr), cluster))
    q = pow(10, Decimal(values[0]).as_tuple().exponent)
    '''
    这里的values[0]是所有的group数值，values[0].as_tuples()是包含指数的数值
    '''
    avg = float(sum(values) / len(values))
    move_avg = Decimal(repr(avg)).quantize(Decimal(repr(q)), rounding=ROUND_HALF_UP)
    new_edges = [ move_edge(edge, move_axis, move_avg - edge[attr])
        for edge in cluster ]
    return new_edges


def snap_edges(edges, tolerance=DEFAULT_SNAP_TOLERANCE):
    """
    把水平方向、垂直距离足够近的edge移动到同一垂直位置
    把铅直方向，水平距离足够近的edge移动到同一水平位置
    """
    if tolerance > 0:
        v = filter_edges(edges, "v")
        h = filter_edges(edges, "h")

        v = [ cluster_to_edges(cluster, "v")
              for cluster in cluster_edges(v, "x0", tolerance) ]

        h = [ cluster_to_edges(cluster, "h")
              for cluster in cluster_edges(h, "top", tolerance) ]

        snapped = list(itertools.chain(*(v + h)))
        return snapped
    else:
        print("Wrong snap tolerance!")
