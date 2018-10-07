"Collection of reused algorithms."


def find_cycles(in_graph, out_graph):
    cycles = out_graph.copy()
    deps = []
    changed = True
    while changed:
        changed = False
        for node, edges in cycles.items():
            # if you have no incoming edges and do have outgoing edges,
            # then trim those edges away
            if in_graph[node] == [] and edges != []:
                for edge in edges:
                    in_graph[edge].remove(node)
                    cycles[node] = []
                deps.append(node)
                changed = True

    has_cycle = any([len(x) > 0 for x in cycles.values()])
    deps = list(reversed(deps))
    return has_cycle, cycles, deps
