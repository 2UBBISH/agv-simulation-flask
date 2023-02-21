#pragma once
#include "sio_client.h"
#include <json/json.h>
#include <functional>
#include <iostream>
#include <thread>
#include <mutex>
#include <condition_variable>
#include <string>
#include <thread>
#include <queue>
using namespace sio;
using namespace std;
namespace ecbs {

    std::mutex _lock;

    std::condition_variable_any _cond;
    bool connect_finish = false;

    struct edge {
        int u, v, cost, nxt;
        edge(int u = 0, int v = 0, int c = 0, int nxt = 0) :u(u), v(v), cost(c), nxt(nxt) {}
    };
    edge edges[100000];
    int cnt, first[10000];
    socket::ptr current_socket;
    Json::Value map_value;

    class connection_listener
    {
        sio::client& handler;

    public:

        connection_listener(sio::client& h) :
            handler(h)
        {
        }

        void on_connected()
        {
            std::cout << "sio connected " << std::endl;
            _lock.lock();
            _cond.notify_all();
            connect_finish = true;
            _lock.unlock();
        }
        void on_close(client::close_reason const& /*reason*/)
        {
            std::cout << "sio closed " << std::endl;
            exit(0);
        }

        void on_fail()
        {
            std::cout << "sio failed " << std::endl;
            exit(0);
        }
    };
    struct map_node {
        int x, y, theta;
        map_node(int x = 0, int y = 0, int theta = 0) :x(x), y(y), theta(theta) {}
        map_node(const map_node& b) {
            x = b.x; y = b.y; theta = b.theta;
        }
        bool operator < (const map_node& b) const {
            if (theta == b.theta) {
                if (x == b.x) return y < b.y;
                else return x < b.x;
            }
            else return theta < b.theta;
        }

        friend ostream& operator << (ostream& os, const map_node& temp) {
            cout << temp.x << ' ' << temp.y << ' ' << temp.theta;
            return os;
        }
    };
    int map_cost[3410][3400];
    map<map_node, int> coord2node;
    map<int, map_node> node2coord;
    int nodes_cnt = 0;
    //加边
    sio::client h;
    socket::ptr connect() {
        connection_listener l(h);

        h.set_open_listener(std::bind(&connection_listener::on_connected, &l));
        h.set_close_listener(std::bind(&connection_listener::on_close, &l, std::placeholders::_1));
        h.set_fail_listener(std::bind(&connection_listener::on_fail, &l));
        h.connect("http://127.0.0.1:5001");

        _lock.lock();
        if (!connect_finish)
        {
            _cond.wait(_lock);
        }
        _lock.unlock();
        current_socket = h.socket();
        return current_socket;
    }
    void disconnect() {
        h.sync_close();
        h.clear_con_listeners();
    }
    void add_edge(int u, int v, int cost) {
        edge e = edge(u, v, cost, first[u]);
        edges[++cnt] = e;
        first[u] = cnt;
        map_cost[u][v] = cost;
    }
    void map_init(sio::event& t)
    {
        //printf("map_init_ing\n");
        coord2node.clear();
        node2coord.clear();
        memset(map_cost, 0, sizeof(map_cost));
        memset(first, -1, sizeof(first));
        memset(edges, 0, sizeof(edges));
        cnt = 0;

        //获取json
        auto v = t.get_messages().to_array_message()->get_vector();
        string s = "";
        for (auto temp : v) {
            string str = temp->get_string();
            s += str;
        }
        //cout << s << endl;

        //用jsoncpp库函数处理json
        Json::Reader reader;
        if (!reader.parse(s, map_value)) {
            printf("fuck");
        }

        else {
            //加点
            for (auto node : map_value["data"]["state_graph"]["states"]) {
                nodes_cnt++;
                auto& temp = node["pos"];
                int x = stoi(temp["x"].asString()), y = stoi(temp["y"].asString()), theta = stoi(temp["theta"].asString());
                map_node n = map_node(x, y, theta);
                int id = stoi(node["state_id"].asString());
                coord2node[n] = id;
                node2coord[id] = n;
            }
            //加边
            for (auto node : map_value["data"]["state_graph"]["states"]) {
                auto& temp = node["pos"];
                int x = stoi(temp["x"].asString()), y = stoi(temp["y"].asString()), theta = stoi(temp["theta"].asString());
                int id = stoi(node["state_id"].asString());
                map_node tgt[4] = { map_node(x, y - 1, 90), map_node(x, y + 1, 270),
                                   map_node(x - 1, y, 180),  map_node(x + 1, y, 0) };
                //加一条自己的边，方便计算在原地静止
                map_cost[id][id] = 4;
                for (int j = 0; j < 4; j++) {
                    map_node now = tgt[j];
                    //给相邻节点加边


                    if (now.theta == theta && coord2node.count(now) > 0) {
                        add_edge(id, coord2node[now], 4);
                    }
                }
                //cout << endl << endl;
                //原地左转右转
                map_node left_node = map_node(x, y, (theta + 90) % 360), right_node = map_node(x, y, (theta + 270) % 360);
                if (coord2node.count(left_node) > 0)add_edge(id, coord2node[left_node], 1);
                if (coord2node.count(right_node) > 0)add_edge(id, coord2node[right_node], 1);
            }
            current_socket->emit("mapInitc++Response", string("init_success"));
        }
        /*cout << nodes_cnt << endl;*/
    }

    struct robot_data {
        int rid, state_id, x, y, theta, path_cost;
        vector<int> path;
        vector<int> tasks;
        robot_data(int a = 0, int b = 0, int c = 0, int d = 0, int e = 0, int f = 0) :rid(a), state_id(b), x(c), y(d), theta(e), path_cost(f) {
            path.clear();
            tasks.clear();
        }
        robot_data(const robot_data& b) {
            path = b.path;
            tasks = b.tasks;
            rid = b.rid;
            state_id = b.state_id;
            x = b.x;
            y = b.y;
            theta = b.theta;
            rid = b.rid;
            path_cost = b.path_cost;
        }
    };
    vector<robot_data> robots;
    int robot_cnt;
    struct Point {
        int sid, conflict_count;
        double totalcost;
        Point(int a = 0, double b = 0, int c = 0) :sid(a), totalcost(b), conflict_count(c) {}
        Point(const Point& b) {
            sid = b.sid;
            conflict_count = b.conflict_count;
            totalcost = b.totalcost;
        }
        bool operator < (const Point& b) const {
            return totalcost < b.totalcost;
        }
        bool operator > (const Point& b) const {
            return totalcost > b.totalcost;
        }
    };

    struct Point2 {
        int sid, conflict_count;
        double totalcost;
        Point2(int a = 0, double b = 0, int c = 0) :sid(a), totalcost(b), conflict_count(c) {}
        Point2(const Point2& b) {
            sid = b.sid;
            conflict_count = b.conflict_count;
            totalcost = b.totalcost;
        }
        bool operator < (const Point2& b) const {
            return conflict_count < b.conflict_count;
        }
        bool operator > (const Point2& b) const {
            return conflict_count > b.conflict_count;
        }
    };
    int dis[10000], close[10000];
    int fa[10000];

    double calc_cost(int u, int v) {
        map_node x = node2coord[u], y = node2coord[v];
        double theta = abs(x.theta - y.theta);
        if (theta > 180) theta = 90;
        theta /= 90;
        return 4 * sqrt((pow(x.x - y.x, 2)) + (pow(x.y - y.y, 2))) + theta;

    }
    int shortest_path(map<map_node, int>& conflict, robot_data& robot, int source, int target) {
        //cout << robot.rid << ':' << source << ' ' << target << endl;
        priority_queue<Point, vector<Point>, greater<Point> > priq;
        priority_queue<Point2, vector<Point2>, greater<Point2> > priq2;
        memset(dis, -1, sizeof(dis));
        memset(close, -1, sizeof(close));
        memset(fa, -1, sizeof(fa));
        priq.push(Point(source, 0, 0));
        dis[source] = robot.path_cost;
        int bad_point = source;
        while (!priq.empty()) {
            Point bestp = priq.top(); priq.pop();
            priq2.push(Point2(bestp.sid, bestp.totalcost, bestp.conflict_count));
            while (!priq.empty()) {
                Point temp = priq.top();
                Point2 p = Point2(temp.sid, temp.totalcost, temp.conflict_count);
                if (p.totalcost <= 1.05 * bestp.totalcost) {
                    priq2.push(p);
                    priq.pop();
                }
                else {
                    break;
                }
            }
            while (!priq2.empty()) {
                Point2 temp = priq2.top(); priq2.pop();
                Point p = Point(temp.sid, temp.totalcost, temp.conflict_count);
                //现在点的坐标
                int point = p.sid;
                if (close[point] == 1) continue;
                map_node point_coord = node2coord[point];
                // 失败规划的处理
                int cost = dis[point];
                if (cost - robot.path_cost <= 88 && cost - robot.path_cost >= 68) {
                    bad_point = point;
                }
                close[point] = 1;

                for (int i = first[point]; i != -1; i = edges[i].nxt) {
                    edge e = edges[i];
                    if (dis[e.v] != -1) continue;
                    map_node tar_coord = node2coord[e.v];  tar_coord.theta = -1;
                    // 如果是预设不能走的点就别走
                    if (conflict.count(tar_coord) > 0 && conflict[tar_coord] != robot.rid && cost < 68) continue;
                    //  最多在原地等一步
                    for (int j = cost; j < cost + 1; j += 4) {
                        // 判断能不能走
                        bool flag = false;
                        // 误差范围为4
                        for (int c = j; c < j + e.cost + 2; c++) {
                            tar_coord.theta = c;

                            if (conflict.count(tar_coord) > 0 && conflict[tar_coord] != robot.rid) {
                                flag = true;
                                break;
                            }

                        }
                        if (flag) continue;
                        for (int c = cost; c < j + e.cost + 2; c++) {
                            point_coord.theta = c;
                            if (conflict.count(point_coord) > 0 && conflict[point_coord] != robot.rid) {
                                flag = true;
                                break;
                            }

                        }
                        if (flag) break;
                        if (dis[e.v] == -1) {
                            dis[e.v] = j + e.cost;
                            fa[e.v] = i;

                            // 当前点的平替版统计
                            tar_coord.theta = -2;

                            if (conflict.count(tar_coord) == 0) conflict[tar_coord] = 0;
                            priq.push(Point(e.v, dis[e.v] + 1.2 * calc_cost(e.v, target), p.conflict_count + conflict[tar_coord]));
                            if (e.v == target) {
                                int temp = target;
                                int path[100], path_len = 0;
                                while (temp != source) {
                                    edge ed = edges[fa[temp]];
                                    int steps = int((dis[temp] - dis[ed.u] - ed.cost) / 4);
                                    path[++path_len] = temp;
                                    for (int c = 0; c < steps; c++) {
                                        path[++path_len] = ed.u;
                                    }                                  
                                    temp = ed.u;
                                }

                                for (int c = path_len; c >= 1; c--) {
                                    robot.path.push_back(path[c]);
                                    map_node now_node = node2coord[path[c]]; now_node.theta = -2;
                                    conflict[now_node] += 1;
                                }
                                robot.path_cost = dis[target];
                                return 1;
                            }
                            break;
                        }
                        else {
                            dis[e.v] = min(dis[e.v], j + cost);
                        }
                    }
                }
            }

        }
        //失败处理
        int temp = bad_point;
        int path[100], path_len = 0;
        while (temp != source) {
            edge e = edges[fa[temp]];
            int steps = int((dis[temp] - dis[e.u] - e.cost) / 4);
            for (int i = 0; i < steps; i++) {
                path[++path_len] = temp;
            }
            temp = e.u;
        }
        for (int c = path_len; c >= 1; c--) robot.path.push_back(path[c]);
        robot.path_cost = dis[target];
        return 0;

    }
    int plan_path_for_single_robot(map<map_node, int>& x, robot_data& robot, bool& success) {
        success = 1;
        int src = robot.state_id;
        for (auto task : robot.tasks) {
            //这里后面要改成有操作时间的
            int target = task;

            success = shortest_path(x, robot, src, target);
            robot.path.push_back(-1);
            if (success == false) return robot.path_cost;
            if (robot.path_cost >= 68) break;
            src = target;

            //加"sub_task_spliter"

        }
        return robot.path_cost;
    }
    struct Node {
        vector<robot_data> robots;
        int cost;
        map<map_node, int> conflict;
        int conflict_count;
        Node(vector<robot_data>& robot, int cos, map<map_node, int>& conflic, int count) {
            robots = robot;
            cost = cos;
            conflict = conflic;
            conflict_count = count;
        }
        Node(const Node& b) {
            robots = b.robots;
            cost = b.cost;
            conflict = b.conflict;
            conflict_count = b.conflict_count;
        }
        bool operator < (const Node& b) const {
            return cost < b.cost;
        }
        bool operator > (const Node& b) const {
            return cost > b.cost;
        }
    };

    struct Node2 {
        vector<robot_data> robots;
        int cost;
        map<map_node, int> conflict;
        int conflict_count;
        Node2(vector<robot_data>& robot, int cos, map<map_node, int>& conflic, int count) {
            robots = robot;
            cost = cos;
            conflict = conflic;
            conflict_count = count;
        }
        Node2(const Node2& b) {
            robots = b.robots;
            cost = b.cost;
            conflict = b.conflict;
            conflict_count = b.conflict_count;
        }
        bool operator < (const Node2& b) const {
            return conflict_count < b.conflict_count;
        }
        bool operator > (const Node2& b) const {
            return conflict_count > b.conflict_count;
        }
    };



    map_node check_conflict(Node& node, int& r1_id, int& r2_id) {
        for (auto robot : node.robots) {
            int cost = 0, last = robot.state_id;
            for (auto i : robot.path) {
                if (i == -1) continue;
                if (cost >= 68) break;
                map_node last_coord = node2coord[last], now_coord = node2coord[i];
                for (int j = cost; j < cost + map_cost[last][i] + 2; j++) {
                    last_coord.theta = now_coord.theta = j;
                    if (node.conflict.count(last_coord) > 0 && node.conflict[last_coord] != robot.rid) {
                        r1_id = node.conflict[last_coord];
                        r2_id = robot.rid;
                        return last_coord;
                    }
                    if (node.conflict.count(now_coord) > 0 && node.conflict[now_coord] != robot.rid) {
                        r1_id = node.conflict[now_coord];
                        r2_id = robot.rid;
                        return now_coord;
                    }
                }

                // 迭代
                cost = cost + map_cost[last][i];
                last = i;
            }
            cost = 0; last = robot.state_id;
            for (auto i : robot.path) {
                if (i == -1) continue;
                if (cost >= 68) break;
                map_node last_coord = node2coord[last], now_coord = node2coord[i];
                for (int j = cost; j < cost + map_cost[last][i] + 2; j++) {
                    last_coord.theta = now_coord.theta = j;
                    node.conflict[last_coord] = node.conflict[now_coord] = robot.rid;

                }
                // 迭代
                cost = cost + map_cost[last][i];
                last = i;
            }
        }
        r1_id = -1;  r2_id = -1;
        return map_node(0, 0, 0);
    }
    int calc_conflict_count(Node& node) {
        int ans = 0;
        map<map_node, int> conflict;
        for (auto robot : node.robots) {
            int cost = 0, last = robot.state_id;
            for (auto i : robot.path) {
                if (i == -1) continue;
                if (cost >= 68) break;
                map_node last_coord = node2coord[last], now_coord = node2coord[i];
                for (int j = cost; j < cost + map_cost[last][i] + 2; j++) {
                    last_coord.theta = now_coord.theta = j;
                    if (conflict.count(last_coord) == 0) conflict[last_coord] = 0;
                    if (conflict.count(now_coord) == 0) conflict[now_coord] = 0;
                    conflict[last_coord]++;
                    conflict[now_coord]++;
                }
                // 迭代
                cost = cost + map_cost[last][i];
                last = i;
            }
        }
        for (auto robot : node.robots) {
            int cost = 0, last = robot.state_id;
            for (auto i : robot.path) {
                if (i == -1) continue;
                if (cost >= 68) break;
                map_node last_coord = node2coord[last], now_coord = node2coord[i];
                for (int j = cost; j < cost + map_cost[last][i] + 2; j++) {
                    last_coord.theta = now_coord.theta = j;
                    ans += conflict[last_coord];
                    ans += conflict[now_coord];
                }
                // 迭代
                cost = cost + map_cost[last][i];
                last = i;
            }
        }
        return ans;
    }
    void clear_prohibit_node(Node& node, robot_data& robot) {
        int cost = 0, last = robot.state_id;
        for (auto i : robot.path) {
            if (i == -1) continue;
            if (cost >= 68) break;
            map_node last_coord = node2coord[last], now_coord = node2coord[i];
            last_coord.theta = now_coord.theta = -2;
            node.conflict[now_coord]--;
            for (int j = cost; j < cost + map_cost[last][i] + 2; j++) {
                last_coord.theta = now_coord.theta = j;
                if (node.conflict.count(last_coord) > 0 && node.conflict[last_coord] == robot.rid) node.conflict.erase(last_coord);
                if (node.conflict.count(now_coord) > 0 && node.conflict[now_coord] == robot.rid) node.conflict.erase(now_coord);

            }
            // 迭代
            cost = cost + map_cost[last][i];
            last = i;
        }
    }
    void compute_route(sio::event& t) {
        robot_cnt = 0;
        //printf("do compute_route in algorithm\n");
        //获取json
        auto v = t.get_messages().to_array_message()->get_vector();
        string s = "";
        for (auto temp : v) {
            string str = temp->get_string();
            s += str;
        }
        //cout << s << endl;

        //用jsoncpp库函数处理json
        Json::Reader reader;
        Json::Value robot_value;
        robots.clear();
        robot_cnt = 0;
        reader.parse(s, robot_value);
        for (auto x : robot_value["data"]["robots"]) {
            robot_data robot = robot_data
            (stoi(x["robot_id"].asString()), stoi(x["current_pos"]["state_id"].asString()),
                stoi(x["current_pos"]["pos"]["x"].asString()), stoi(x["current_pos"]["pos"]["y"].asString()), stoi(x["current_pos"]["pos"]["theta"].asString()));
            robots.push_back(robot);
            for (auto task : x["tasks"]) {
                robots[robot.rid].tasks.push_back(stoi(task["target_state_id"].asString()));
            }
            robot_cnt++;
        }

        //起始点加限制
        map<map_node, int> conflict;
        for (robot_data& robot : robots) {
            map_node key = map_node(robot.x, robot.y, -1);
            conflict[key] = robot.rid;
        }

        //最终任务点加限制

        for (robot_data& robot : robots) {
            if (!robot.tasks.empty()) {
                map_node temp = node2coord[robot.tasks.back()];
                map_node key = map_node(temp.x, temp.y, -1);
                if (conflict.count(key) == 0) {
                    conflict[key] = robot.rid;
                }
            }
        }
        for (robot_data& robot : robots) {
            if (!robot.tasks.empty()) {
                map_node temp = node2coord[robot.tasks.back()];
                map_node key = map_node(temp.x, temp.y, -1);
                if (conflict.count(key) == 0) {
                    conflict[key] = robot.rid;
                }
            }
        }

        //初始点规划
        int init_cost = 0;
        for (robot_data& robot : robots) {
            bool success = false;
            init_cost += plan_path_for_single_robot(conflict, robot, success);
        }
        //printf("fuck");
        Node init_node = Node(robots, init_cost, conflict, 0);
        priority_queue<Node, vector<Node>, greater<Node> > priq;
        priority_queue<Node2, vector<Node2>, greater<Node2> > priq2;
        priq.push(init_node);
        while (!priq.empty()) {
            Node bestnode = priq.top(); priq.pop();
            priq2.push(Node2(bestnode.robots, bestnode.cost, bestnode.conflict, bestnode.conflict_count));
            while (!priq.empty()) {
                Node temp = priq.top();
                Node2 node = Node2(temp.robots, temp.cost, temp.conflict, temp.conflict_count);
                if (node.cost <= 1.05 * bestnode.cost) {
                    priq2.push(node);
                    priq.pop();
                }
                else {
                    break;
                }
            }
            while (!priq2.empty()) {
                Node2 temp = priq2.top(); priq2.pop();
                Node node = Node(temp.robots, temp.cost, temp.conflict, temp.conflict_count);
                
                //cout << node.conflict_count << endl;
                int r1_id = -1, r2_id = -1;
                map_node prohibit_node = check_conflict(node, r1_id, r2_id);
                //cout << prohibit_node << ' ' << r1_id << ' ' << r2_id << endl;
                if (r2_id == -1) {
                    robots = node.robots;
                    break;
                }
                bool success = false;

                clear_prohibit_node(node, node.robots[r2_id]);
                node.cost -= node.robots[r2_id].path_cost;
                node.robots[r2_id].path_cost = 0;
                node.robots[r2_id].path.clear();
                int cost = plan_path_for_single_robot(node.conflict, node.robots[r2_id], success);
                node.cost += cost;
                node.conflict_count = calc_conflict_count(node);
                //cout << "success:" << success << endl;
                if (success) priq.push(node);

                Node temp_node(node);
                success = 1;
                clear_prohibit_node(temp_node, temp_node.robots[r1_id]);
                temp_node.cost -= temp_node.robots[r1_id].path_cost;
                temp_node.conflict[prohibit_node] = r2_id;
                temp_node.robots[r1_id].path_cost = 0;
                temp_node.robots[r1_id].path.clear();
                cost = plan_path_for_single_robot(temp_node.conflict, temp_node.robots[r1_id], success);
                temp_node.cost += cost;
                temp_node.conflict_count = calc_conflict_count(temp_node);
                //cout << "success:" << success << endl;
                if (success) priq.push(temp_node);
            }
        }
        Json::Value result;
        result.clear();
        for (robot_data& robot : robots) {
            Json::Value temp;
            int cnt = 0, cost = 0, last = robot.state_id;
            //cout << endl << robot.rid << ' ' << endl << node2coord[last] << endl;

            Json::Value path;
            for (auto item : robot.path) {
                if (item == -1) path.append("sub_task_spliter");
                else {
                    cost = cost + map_cost[last][item];
                    map_node coord = node2coord[item];
                    //cout << cnt++ << ' ' << item << ' ' << coord << endl;
                    last = item;
                    path.append(coord.x);
                    path.append(coord.y);
                    path.append(coord.theta);
                }
            }
            temp["path"] = path;
            temp["robot_id"] = robot.rid;
            result.append(temp);
        }
        Json::FastWriter writer;
        string ans = writer.write(result);
        //cout << ans << endl;
        current_socket->emit("computeRoutec++Response", ans);
    }

   


}