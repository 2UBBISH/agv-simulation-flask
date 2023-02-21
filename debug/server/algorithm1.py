import math
import time
from queue import PriorityQueue
from collections import defaultdict

import copy
import networkx as nx


class Node:
    # 作为上层中的节点，包括每个机器人的状态，当前所有路径花费，以及预估冲突个数
    def __init__(self, conflict_number, robots, cost, conflict):
        self.conflict_number = conflict_number
        self.robots = robots
        self.cost = cost
        self.conflict = conflict

    def __lt__(self, other):
        return self.cost < other.cost


class focalNode:
    # 作为上层中的节点，包括distance-to-go, 每个机器人的状态，当前所有路径花费，以及预估冲突个数
    def __init__(self, conflict_number, robots, cost, conflict):
        self.conflict_number = conflict_number
        self.robots = robots
        self.cost = cost
        self.conflict = conflict

    def __lt__(self, other):
        return self.conflict_number < other.conflict_number


class Robot:
    def __init__(self, r_id, pos, speed, tasks):
        self.id = r_id
        self.speed = speed
        self.path = []
        self.pos = (pos["state_id"], pos["pos"]["x"], pos["pos"]["y"], pos["pos"]["theta"])
        self.tasks = tasks
        self.path_cost = 0


def calc_cost(g, src_node, target_node):
    src = g.nodes[src_node]['pos']
    tar = g.nodes[target_node]['pos']
    theta = abs(tar[2] - src[2])
    if theta > 180:
        theta = 90
    theta /= 90
    return math.sqrt(4 * abs(tar[1] - src[1]) * abs(tar[1] - src[1])
                     + 4 * (abs(tar[0] - src[0]) * abs(tar[0] - src[0]))
                     + theta)


class Algorithm1:
    states = []
    statesMap = defaultdict(int)
    edges = []
    graph = {}
    state_graph = nx.DiGraph()
    robots = {}
    time_in_sec = 3

    def __init__(self):
        pass

    @classmethod
    def compute_nodes(cls, ):
        for state in cls.states:
            state_id = state["state_id"]
            x = state["pos"]["x"]
            y = state["pos"]["y"]
            theta = state["pos"]["theta"]
            key = (x, y, theta)
            cls.statesMap[key] = state_id
            cls.graph[state_id] = key
            cls.state_graph.add_node(state["state_id"], **{"pos": (x, y, theta)})

    @classmethod
    def compute_edges(cls, ):
        for state in cls.states:

            x = state["pos"]["x"]
            y = state["pos"]["y"]
            theta = state["pos"]["theta"]
            state_id = state["state_id"]
            # print(state_id, x, y, theta)
            top = (x, y - 1, 90)
            down = (x, y + 1, 270)
            left = (x - 1, y, 180)
            right = (x + 1, y, 0)
            cls.state_graph.add_edge(state_id, state_id, weight=4)
            tgtPointArr = [top, down, left, right]

            for tgt in tgtPointArr:
                key = tgt
                if theta == key[2] and cls.statesMap.get(key, None) is not None:
                    tgt_state_id = cls.statesMap[key]
                    cost = 4
                    edge = {
                        "src_state_id": state_id,
                        "target_state_id": tgt_state_id,
                        "cost": cost,
                    }
                    cls.edges.append(edge)
                    cls.state_graph.add_edge(state_id, tgt_state_id, weight=cost)

            tgtPoint = [(x, y, (theta + 90) % 360), (x, y, (theta + 270) % 360)]
            for tgt in tgtPoint:
                key = tgt
                if cls.statesMap.get(key, None) is not None:
                    tgt_state_id = cls.statesMap[key]
                    cost = 1
                    edge = {
                        "src_state_id": state_id,
                        "target_state_id": tgt_state_id,
                        "cost": cost,
                    }
                    cls.edges.append(edge)
                    cls.state_graph.add_edge(state_id, tgt_state_id, weight=cost)

    @classmethod
    def map_init(cls, data):
        print("do map_init in algorithm")
        cls.states = data["data"]["state_graph"]["states"]
        Algorithm1.compute_nodes()
        Algorithm1.compute_edges()
        return {}

    @classmethod
    def check_conflict(cls, node):
        for (r_id, item) in node.robots.items():
            cost = 0
            last = item.pos[0]
            for i in item.path:
                if i == "sub_task_spliter":
                    continue
                if cost >= 68:
                    break
                pre_cost = cost
                cost = cost + cls.state_graph[last][i]['weight']
                last_x, last_y = cls.state_graph.nodes[last]['pos'][0], cls.state_graph.nodes[last]['pos'][1]
                i_x, i_y = cls.state_graph.nodes[i]['pos'][0], cls.state_graph.nodes[i]['pos'][1]
                for j in range(pre_cost - 0, cost + 6):

                    temp1 = (j, last_x, last_y)
                    t = node.conflict.get(temp1)
                    if t is not None and t != r_id:
                        # print(last)
                        return temp1, node.conflict[temp1], r_id

                    temp = (j, i_x, i_y)
                    t = node.conflict.get(temp)
                    if t is not None and t != r_id:
                        # print(i)
                        return temp, node.conflict[temp], r_id

                last = i

            cost = 0
            last = item.pos[0]
            for i in item.path:
                if i == "sub_task_spliter":
                    continue
                pre_cost = cost
                cost = cost + cls.state_graph[last][i]['weight']
                last_x, last_y = cls.state_graph.nodes[last]['pos'][0], cls.state_graph.nodes[last]['pos'][1]
                i_x, i_y = cls.state_graph.nodes[i]['pos'][0], cls.state_graph.nodes[i]['pos'][1]
                for j in range(pre_cost - 0, cost + 6):
                    # 当前点
                    temp = (j, last_x, last_y)
                    node.conflict[temp] = r_id

                    # 目标点
                    temp = (j, i_x, i_y)
                    node.conflict[temp] = r_id

                last = i
        return None, -1, -1

    @classmethod
    def count_conflict_number(cls, node):
        conflict = {}
        for (r_id, item) in node.robots.items():

            cost = 0
            last = item.pos[0]
            for i in item.path:
                if i == "sub_task_spliter":
                    continue
                if cost >= 68:
                    break
                pre_cost = cost
                cost = cost + cls.state_graph[last][i]['weight']
                last_x, last_y = cls.state_graph.nodes[last]['pos'][0], cls.state_graph.nodes[last]['pos'][1]
                i_x, i_y = cls.state_graph.nodes[i]['pos'][0], cls.state_graph.nodes[i]['pos'][1]
                for j in range(pre_cost - 0, cost + 6):

                    temp1 = (j, last_x, last_y)
                    t = conflict.get(temp1)
                    if t is None:
                        conflict[temp1] = 0

                    conflict[temp1] += 1
                    temp = (j, i_x, i_y)
                    t = conflict.get(temp)
                    if t is None:
                        conflict[temp] = 0
                    conflict[temp] += 1

                last = i

        ans = 0
        for (r_id, item) in node.robots.items():
            cost = 0
            last = item.pos[0]
            for i in item.path:
                if i == "sub_task_spliter":
                    continue
                if cost >= 68:
                    break
                pre_cost = cost
                cost = cost + cls.state_graph[last][i]['weight']
                last_x, last_y = cls.state_graph.nodes[last]['pos'][0], cls.state_graph.nodes[last]['pos'][1]
                i_x, i_y = cls.state_graph.nodes[i]['pos'][0], cls.state_graph.nodes[i]['pos'][1]
                for j in range(pre_cost - 0, cost + 6):
                    temp1 = (j, last_x, last_y)
                    ans += conflict[temp1]

                    temp = (j, i_x, i_y)
                    ans += conflict[temp]

                last = i
        return ans

    @classmethod
    def compute_route(cls, data):
        print("do compute_route in algorithm")
        data = data['data']['robots']

        for item in data:
            cls.robots[item["robot_id"]] = Robot(item["robot_id"], item["current_pos"], 1, item["tasks"])

        conflict = {}
        # 为什么起始点也不能马上走，因为会出现第一个点交换起点的路径，这个时候会是无解的，因为两边的路径都被限制住了，会出现无解的情况
        for (r_id, robot) in cls.robots.items():
            key = (robot.pos[1], robot.pos[2])
            conflict[key] = r_id

        for (r_id, robot) in cls.robots.items():
            if len(robot.tasks) != 0:
                target_id = robot.tasks[-1]["target_state_id"]
                key = (cls.graph[target_id][0], cls.graph[target_id][1])
                if conflict.get(key) is None:
                    conflict[key] = r_id

        init_cost = 0
        for (r_id, robot) in cls.robots.items():
            cost, success = cls.__plan_path_for_single_robot(conflict, robot)
            # print(robot.path)
            init_cost = init_cost + cost

        init_node = Node(0, copy.deepcopy(cls.robots), 0, conflict)
        upper_node = PriorityQueue()
        focalPriq = PriorityQueue()
        upper_node.put(init_node)
        while not upper_node.empty():
            best_node = upper_node.get()
            # 聚焦搜索(1.5倍误差)
            focalPriq.put(focalNode(best_node.conflict_number, best_node.robots, best_node.cost, best_node.conflict))
            while not upper_node.empty():
                node = upper_node.get()
                if node.cost > 1.25 * best_node.cost:
                    upper_node.put(node)
                    break
                focalPriq.put(focalNode(node.conflict_number, node.robots, node.cost, node.conflict))

            while not focalPriq.empty():
                node = focalPriq.get()
                prohibit_node, r1_id, r2_id = cls.check_conflict(node)
                cls.robots = node.robots
                # 即得出解了
                if r2_id == -1:
                    result = []
                    for (r_id, robot) in cls.robots.items():
                        t = {"robot_id": r_id, "path": []}
                        print(r_id)
                        cnt = 0
                        cost = 0
                        last = robot.pos[0]
                        print(robot.pos)
                        for item in robot.path:
                            if item == "sub_task_spliter":
                                t["path"].append(item)
                            else:
                                cost = cost + cls.state_graph[last][item]['weight']
                                temp = cls.graph[item]
                                t["path"] += [temp[0], temp[1], temp[2]]
                                print(cnt, ':', item, [temp[0], temp[1], temp[2]])
                                last = item
                                cnt += 1

                        result.append(t)
                        print(result)
                    return result

                temp_node = copy.deepcopy(node)

                # 重新规划r2_id机器人
                node.cost = node.cost - node.robots[r2_id].path_cost
                cost, success = cls.__plan_path_for_single_robot(node.conflict, node.robots[r2_id])
                node.cost = node.cost + cost
                if success == 1:
                    upper_node.put(Node(cls.count_conflict_number(node), node.robots, node.cost, node.conflict))

                # 重新规划r1_id机器人
                cls.clear_prohibit_node(temp_node.conflict, temp_node.robots[r1_id])
                temp_node.conflict[prohibit_node] = r2_id
                temp_node.cost = temp_node.cost - temp_node.robots[r1_id].path_cost
                cost, success = cls.__plan_path_for_single_robot(temp_node.conflict, temp_node.robots[r1_id])
                temp_node.cost = temp_node.cost + cost
                if success == 1:
                    upper_node.put(
                        Node(cls.count_conflict_number(temp_node), temp_node.robots, temp_node.cost,
                             temp_node.conflict))

    @classmethod
    def clear_prohibit_node(cls, conflict, robot):
        cost = 0
        last = robot.pos[0]
        for i in robot.path:
            if i == "sub_task_spliter":
                continue
            pre_cost = cost
            cost = cost + cls.state_graph[last][i]['weight']
            last_x, last_y = cls.state_graph.nodes[last]['pos'][0], cls.state_graph.nodes[last]['pos'][1]
            i_x, i_y = cls.state_graph.nodes[i]['pos'][0], cls.state_graph.nodes[i]['pos'][1]
            conflict[(last_x, last_y, 'c')] -= 1
            for j in range(pre_cost - 0, cost + 6):
                # 当前点
                temp = (j, last_x, last_y)
                t = conflict.get(temp)
                if t == robot.id:
                    conflict.pop(temp)

                # 目标点
                temp = (j, i_x, i_y)
                t = conflict.get(temp)
                if t == robot.id:
                    conflict.pop(temp)
            last = i

    @classmethod
    def __plan_path_for_single_robot(cls, conflict, robot):
        src = robot.pos[0]
        robot.path = []
        robot.path_cost = 0

        for i in robot.tasks:
            target = i["target_state_id"]
            anspath, anscost, success = shortest_path(cls.state_graph, conflict, src, target, robot.path_cost, robot.id)
            anspath.pop(0)

            robot.path += anspath
            robot.path_cost += anscost
            robot.path.append("sub_task_spliter")
            if success == -1:
                return robot.path_cost, -1
            if robot.path_cost >= 68:
                break

            src = target

        # print(robot.path)
        return robot.path_cost, 1

    @classmethod
    def error_route(cls, data):
        print("do error_route in algorithm")
        return {}


class Point(object):
    # 作为下层中的节点，包括当前点的状态，路径花费
    def __init__(self, conflict_number, pricost, nowcost, rid):
        self.conflict_number = conflict_number
        self.id = rid
        self.nowcost = nowcost
        self.pricost = pricost

    def __lt__(self, other):
        return self.pricost < other.pricost


class focalPoint(object):
    # 作为下层中的节点，包括当前点的状态，路径花费
    def __init__(self, conflict_number, pricost, nowcost, rid):
        self.conflict_number = conflict_number
        self.id = rid
        self.nowcost = nowcost
        self.pricost = pricost

    def __lt__(self, other):
        return self.conflict_number < other.conflict_number


def shortest_path(g, conflict, source, target, init_cost, rid):
    priq = PriorityQueue()
    focalPriq = PriorityQueue()
    priq.put(Point(0, init_cost, init_cost, source))
    map_close = {}
    map_open = {source: init_cost}
    fa = {}
    path = []
    bad_point = source
    init_node = (g.nodes[source]["pos"][0], g.nodes[source]["pos"][1])
    conflict[(g.nodes[source]["pos"][0], g.nodes[source]["pos"][1], 'c')] = 1
    while not priq.empty():
        best_node = priq.get()
        # 聚焦搜索(1.5倍误差)
        focalPriq.put(focalPoint(best_node.conflict_number, best_node.pricost, best_node.nowcost, best_node.id))
        while not priq.empty():
            node = priq.get()
            if node.pricost > 1.25 * best_node.pricost:
                priq.put(node)
                break
            focalPriq.put(focalPoint(node.conflict_number, node.pricost, node.nowcost, node.id))

        while not focalPriq.empty():
            # print(node)
            node = focalPriq.get()
            point = node.id
            # 如果这个点已经走过一遍了，别走了
            t = map_close.get(point)
            if t is not None:
                continue
            map_close[point] = 1
            cost = map_open[point]
            if 68 <= cost - init_cost <= 88:
                bad_point = point
            for item in list(g.neighbors(point)):
                # 判断是否已经进队列
                # print(item)

                temp_node = (g.nodes[item]["pos"][0], g.nodes[item]["pos"][1])
                if conflict.get(temp_node) is not None and temp_node != init_node and conflict[temp_node] != rid \
                        and cost < 68:
                    continue
                t = map_close.get(item)
                if t is not None:
                    continue
                # 判断当前邻居在等待一定时间后能否到达

                edge_cost = g[point][item]['weight']
                point_x, point_y = g.nodes[point]['pos'][0], g.nodes[point]['pos'][1]
                item_x, item_y = g.nodes[item]['pos'][0], g.nodes[item]['pos'][1]
                for j in range(cost, cost + 6, 4):
                    # 判断目标点这段时间可以不可以
                    flag = 0

                    for c in range(j - 0, j + edge_cost + 6):
                        now_node = (c, item_x, item_y)
                        # conflict里面已经限制了当前时间不能走
                        t = conflict.get(now_node)
                        if t is not None and t != rid:
                            flag = 1
                            break
                    if flag == 1:
                        continue
                    # 判断当前点这段时间可以不可以
                    for c in range(cost - 0, j + edge_cost + 6):
                        test_node = (c, point_x, point_y)
                        # conflict里面已经限制了当前时间不能走，
                        t = conflict.get(test_node)
                        if t is not None and t != rid:
                            flag = 1
                            break
                    if flag == 1:
                        break

                    # 如果更优才把它再放进去
                    temp = j + edge_cost
                    if map_open.get(item) is None or \
                            (map_open.get(item) is not None and temp < map_open[item]):
                        # 这里采用平替版预估参数，因为去统计冲突数的话效率太低了
                        temp_node = (g.nodes[item]["pos"][0], g.nodes[item]["pos"][1], 'c')
                        t = conflict.get(temp_node)
                        if t is None:
                            t = 0
                            conflict[temp_node] = 0
                        priq.put(Point(node.conflict_number + t, temp + 1.25 * calc_cost(g, item, target), temp, item))

                        map_open[item] = temp
                        fa[item] = point

                        if item == target:
                            temp = target
                            while temp != source:
                                tcost = g[fa[temp]][temp]['weight']
                                # 计算两步之间的花费，看看有没有停留
                                cnt = int((map_open[temp] - map_open[fa[temp]] - tcost) / 4)

                                path.append(temp)
                                for i in range(cnt):
                                    path.append(fa[temp])
                                temp = fa[temp]
                                temp_node = (g.nodes[temp]["pos"][0], g.nodes[temp]["pos"][1], 'c')
                                conflict[temp_node] += 1

                            path.append(source)
                            path.reverse()

                            return path, map_open[target], 1

                        break

    temp = bad_point
    while temp != source:
        tcost = g[fa[temp]][temp]['weight']
        # 计算两步之间的花费，看看有没有停留
        cnt = int((map_open[temp] - map_open[fa[temp]] - tcost) / 4)
        path.append(temp)
        for i in range(cnt):
            path.append(fa[temp])
        temp = fa[temp]
    path.append(source)
    path.reverse()
    return path, map_open[bad_point], -1


if __name__ == "__main__":
    start = time.time()
    f = open("map.json", "r")
    map_data = f.read()
    Algorithm1.map_init(eval(map_data))
    f.close()
    f = open("robot.json", "r")
    map_data = f.read()
    print(map_data)
    Algorithm1.compute_route(eval(map_data))
    f.close()
    end = time.time()
    print(end - start)
