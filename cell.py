from operator import itemgetter


def intersections_to_cells(intersections):
    """
    得到intersection描述的cell，cell的描述形式是四个坐标
    """

    def edge_connects(p1, p2):
        '''
        检查两个点p1，p2是否有公共的edge
        有则返回True
        '''
        def edges_to_set(edges): #得到edge的四个坐标
            return set(map(itemgetter("x0", "top", "x1", "bottom"), edges))
        
        if p1[0] == p2[0]:
            common = edges_to_set(intersections[p1]["v"])\
                .intersection(edges_to_set(intersections[p2]["v"]))
            if len(common): return True

        if p1[1] == p2[1]:
            common = edges_to_set(intersections[p1]["h"])\
                .intersection(edges_to_set(intersections[p2]["h"]))
            if len(common): return True
        return False
    
    points = list(sorted(intersections.keys()))     
    n_points = len(points)
    
    def find_smallest_cell(points, i):
        if i == n_points - 1: return None
        pt = points[i]
        rest = points[i+1:]
        # 得到下边和右边的点
        below = [ x for x in rest if x[0] == pt[0] ]
        right = [ x for x in rest if x[1] == pt[1] ]

        for below_pt in below:
            if not edge_connects(pt, below_pt): continue
                
            for right_pt in right:
                if not edge_connects(pt, right_pt): continue
                
                bottom_right = (right_pt[0], below_pt[1])
                
                if ((bottom_right in intersections) and
                    edge_connects(bottom_right, right_pt) and
                    edge_connects(bottom_right, below_pt)):
                    return (
                        pt[0],
                        pt[1],
                        bottom_right[0],
                        bottom_right[1]
                    )
    cell_gen = (find_smallest_cell(points, i) for i in range(len(points)))
    return list(filter(None, cell_gen))
