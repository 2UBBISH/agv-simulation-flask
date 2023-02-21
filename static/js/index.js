//全局变量
let assignTaskTimerId = undefined
let computeRouteTimerId = undefined
let genNewTaskTimerId = undefined
let showInfoTimerId = undefined
let socket = undefined

//init UI config
let mapSizeWidth = 30
let mapSizeHeight = 30
let unitSize = 30
let agvNum = 10
let rackPosList=[
    [5,7],[5,8],[6,7],[6,8],
    [5,12],[5,13],[6,12],[6,13],
    [5,17],[5,18],[6,17],[6,18],

    [10,7],[10,8],[11,7],[11,8],
    [10,12],[10,13],[11,12],[11,13],
    [10,17],[10,18],[11,17],[11,18],

    [15,7],[15,8],[16,7],[16,8],
    [15,12],[15,13],[16,12],[16,13],
    [15,17],[15,18],[16,17],[16,18],

    [20,7],[20,8],[21,7],[21,8],
    [20,12],[20,13],[21,12],[21,13],
    [20,17],[20,18],[21,17],[21,18],

]
let startPosList=[
    [3, 0], [5, 0],[7, 0], [9, 0],[11, 0], [13, 0],[15, 0], [17, 0], [19, 0], [21, 0],
]
let endPosList=[
    [0,7], [0,9], [0,11], [0,13],[0,15], [0,17], [0,19], [0,21], [0,23], [0,25],
]

//init tasks config
let tasks = [
    [1, 15, 0],
    [2, 17,0],
    [3, 19,0],
    [4, 21, 0],
    [5,23, 0],
    [6,25, 0],
    [7,23, 0],
    [8, 21, 0],
    [9, 23,0],
    [10,25,0],
]

let checkCollisionFlag = false
//==============================
//动态生成的各个变量
//==============================
let agvs = []
let states = []
let statesMap = {}
let edges = []
let robots = []
let collisionNum = 0
let missionStart = false

let error_robots = [];
let roads = [];
let roadsMap = [];

// some input-box element
let $mapSizeWidth = undefined
let $mapSizeHeight = undefined
let $agvNum = undefined
let $rackPosList = undefined
let $startPosList = undefined
let $endPosList = undefined
let $collisionNum = undefined

// let a = "";
// function  aa(){
//     a = "haha";
// }
// aa();
// alert(a);
let algorithm = 3;
function algorithmChange(){
    console.log("algorithm changed!!!");

    let obj = document.getElementById("mySelect");
    let index = obj.selectedIndex;
    let value = obj.options[index].value;
    algorithm = value;
    stopMission();

    socket.disconnect();

    create_socket();
}



// ----------------- socket -----------------

function create_socket(){
    socket = io("http://localhost:5001/");

    socket.on("connect", function (){
        console.log(socket.id);
        console.log('connection established')

        // ------ mapInit_data ------
        console.log("doing UI map_init...")
        let mapInit_data = buildMapInitData(algorithm)
        socket.emit('mapInit', {'data': mapInit_data})

        // ----------------------
        // 各种自定义监听事件
        // ----------------------
        socket.on("mapInitResponse", function (data){
            console.log('receive mapInitResponse event')
            console.log(data)
        })
        socket.on("computeRouteResponse", function (responseData){
            console.log('receive computeRouteResponse event')
            console.log(responseData)

            if(computeRouteTimerId){
                clearTimeout(computeRouteTimerId)
                computeRouteTimerId = undefined
            }
            //接收到数据后6s调用一次算法
            computeRouteTimerId = setTimeout(function (){
                console.log("emidt computeRoute_data");
                let computeRoute_data = buildComputeRouteData()
                console.log(JSON.stringify(computeRoute_data))
                socket.emit('computeRoute', {'data': computeRoute_data})
            },3000)

            runAllAgv(responseData)

        })
        socket.on("errorRouteResponse", function (responseData){
            console.log('receive errorRouteResponse event')
            console.log(responseData)
            runAllAgv(responseData)
        })
        socket.on("finishResponse", function (data){
            console.log('receive finishResponse event')
            console.log(data)
            stopTask()
        })
    });

    socket.on("connect_error", function (){
        console.log(socket.id);
        console.log('The connection failed!')
        if(computeRouteTimerId){
            clearTimeout(computeRouteTimerId);
            computeRouteTimerId = undefined
        }
        if(assignTaskTimerId){
            clearTimeout(assignTaskTimerId);
            assignTaskTimerId = undefined
        }
        if(genNewTaskTimerId){
            clearInterval(genNewTaskTimerId);
            genNewTaskTimerId = undefined
        }

        if(showInfoTimerId){
            clearInterval(showInfoTimerId);
            showInfoTimerId = undefined
        }

        socket = undefined
    });

    socket.on("disconnect", function(){
        console.log('disconnected from server')
        console.log(socket.id);

        if(computeRouteTimerId){
            clearTimeout(computeRouteTimerId);
            computeRouteTimerId = undefined
        }
        if(assignTaskTimerId){
            clearTimeout(assignTaskTimerId);
            assignTaskTimerId = undefined
        }
        if(genNewTaskTimerId){
            clearInterval(genNewTaskTimerId);
            genNewTaskTimerId = undefined
        }
        if(showInfoTimerId){
            clearInterval(showInfoTimerId);
            showInfoTimerId = undefined
        }

        socket = undefined
    });
}

function buildMapInitData(choice){
    let res= {
        algorithm: choice, //算法选择（1, 2，3），作为备用接口方便以后选择算法
        state_graph:{
            states: states,
        }
    }
    return res
}

function buildComputeRouteData(){
    for(let i=0;i<agvs.length;i++){
        let agv = agvs[i]
        //向server重新请求计算路径的时候，一定要把agv停在原地，不然会有bug
        if(agv.$agv){
            agv.$agv.stop()
        }
    }

    let robots = []
    for(let i=0;i<agvs.length;i++){
        let agv = agvs[i]
        let task = agv.task
        let tasksForOneRobot = []
        if(task && task.length > 0){
            for(let j=0;j<task.length;j+=3) {
                let tgtX = task[j]
                let tgtY = task[j+1]
                let tgtTheta = task[j+2]

                let key = [tgtX, tgtY, tgtTheta].toString()
                let target_state_id = statesMap[key]
                let taskForOneRobot = {
                    target_state_id: target_state_id,
                    task_operation_time_in_sec: 0,
                    index: j / 3
                }
                tasksForOneRobot.push(taskForOneRobot)
            }
        }

        let key = [agv.x, agv.y, agv.theta].toString()
        let state_id = statesMap[key]
        let robot = {
            robot_id: agv.id,
            current_pos:{
                state_id: state_id,
                pos:{
                    x: agv.x,
                    y: agv.y,
                    theta: agv.theta
                }
            },
            tasks: tasksForOneRobot,

        }
        robots.push(robot)
    }
    let res = {
        robots: robots
    }

    // console.log(robots);

    return res
}



// ----------------- mission -----------------

function startMission(){
    collisionNum = 0
    $collisionNum.text(collisionNum)

    missionStart = true

    if(assignTaskTimerId){
        clearTimeout(assignTaskTimerId)
        assignTaskTimerId = undefined
    }
    //给没有任务的小车分配任务
    assignTask()

    //调用服务器算法计算agv路径
    if(computeRouteTimerId){
        clearTimeout(computeRouteTimerId)
        computeRouteTimerId = undefined
    }
    let computeRoute_data = buildComputeRouteData()
    socket.emit('computeRoute', {'data': computeRoute_data})


    // ------ 固定每10秒时间生成一些新的task ------
    if(genNewTaskTimerId){
        clearInterval(genNewTaskTimerId);
        genNewTaskTimerId = undefined
    }
    genNewTaskTimerId = setInterval(function (){
        genNewTask()
    }, 15000)

    //且马上执行一次
    genNewTask()

    // ------ 固定每1秒时间showInfo ------
    if(showInfoTimerId){
        clearInterval(showInfoTimerId);
        showInfoTimerId = undefined
    }
    showInfoTimerId = setInterval(function (){
        showInfo()
    }, 1000)

    
}

function stopMission(){
    missionStart = false

    if(computeRouteTimerId){
        clearTimeout(computeRouteTimerId)
        computeRouteTimerId = undefined
    }

    if(assignTaskTimerId){
        clearTimeout(assignTaskTimerId)
        assignTaskTimerId = undefined
    }

    if(genNewTaskTimerId){
        clearInterval(genNewTaskTimerId)
        genNewTaskTimerId = undefined
    }
    if(showInfoTimerId){
        clearInterval(showInfoTimerId);
        showInfoTimerId = undefined
    }
}

function checkCollision(agv, nextX, nextY){
    // if(x == nextX && y == nextY){
    //     return false
    // }
    for(let i=0;i<agvs.length;i++){
        let agv2 = agvs[i]
        if(agv2.id != agv.id){
            if(nextX == agv2.x && nextY == agv2.y){
                console.log("发生碰撞!!")
                collisionNum +=1
                $collisionNum.text(collisionNum)

                let error_state_id_agv = statesMap[[agv.x,agv.y,agv.theta].toString()]
                let error_state_id_agv2 = statesMap[[agv2.x,agv2.y,agv2.theta].toString()]
                let road_error_index_agv = roadsMap[agv.id][error_state_id_agv]
                let road_error_index_agv2 = roadsMap[agv2.id][error_state_id_agv2]
                let collisionPath = agv.pathCache
                let collisionPath2 = agv2.pathCache
                error_robots.push({
                    robot_id: agv.id,
                    road_error_index: road_error_index_agv,
                    collisionPath: collisionPath,
                })
                error_robots.push({
                    robot_id: agv2.id,
                    road_error_index: road_error_index_agv2,
                    collisionPath: collisionPath2,
                })

                agv.path = undefined
                let $agv = agv.$agv
                $agv.stop()

                agv2.path = undefined
                let $agv2 = agv2.$agv
                $agv2.stop()

                return true
            }
        }

    }

    return false
}

function checkInForbiddenArea(x, y) {
    // if(x == 0 || y == 0){
    //     return true
    // }

    if (x < -1 || y < -1 || x > mapSizeWidth || y > mapSizeHeight) {
        return true
    }

    for (let i = 0; i < rackPosList.length; i++) {
        if (x == rackPosList[i][0] && y == rackPosList[i][1]) {
            return true
        }
    }

    return false
}

// ----------------- init -----------------
function renderMap(){
    //render 地图 和 states
    let $map = $("#map").empty()
    let state_id = -1
    for(let i=0;i<mapSizeWidth;i++){
        let $tr = $("<tr></tr>")
        for(let j=0;j<mapSizeHeight;j++){
            if ((i+j) % 2 == 0){
                $tr.append("<td class='grey'></td>")
            }else{
                $tr.append("<td></td>")
            }

            let centerValidCheck = !checkInForbiddenArea(i,j)
            let topValidCheck = !checkInForbiddenArea(i,j-1)
            let downValidCheck = !checkInForbiddenArea(i,j+1)
            let leftValidCheck = !checkInForbiddenArea(i-1,j)
            let rightValidCheck = !checkInForbiddenArea(i+1,j)

            if(centerValidCheck){
                let theta = undefined
                if(topValidCheck){
                    state_id +=1
                    theta = 90
                    states.push({
                        state_id:state_id,
                        pos:{
                            x:i,
                            y:j,
                            theta,
                        },
                    })
                    let key = [i,j,theta].toString()
                    statesMap[key] = state_id
                }
                if(downValidCheck){
                    state_id +=1
                    theta = 270
                    states.push({
                        state_id:state_id,
                        pos:{
                            x:i,
                            y:j,
                            theta,
                        },
                    })
                    let key = [i,j,theta].toString()
                    statesMap[key] = state_id
                }
                if(leftValidCheck){
                    state_id +=1
                    theta = 180
                    states.push({
                        state_id:state_id,
                        pos:{
                            x:i,
                            y:j,
                            theta,
                        },
                    })
                    let key = [i,j,theta].toString()
                    statesMap[key] = state_id
                }
                if(rightValidCheck){
                    state_id +=1
                    theta = 0
                    states.push({
                        state_id:state_id,
                        pos:{
                            x:i,
                            y:j,
                            theta,
                        },
                    })
                    let key = [i,j,theta].toString()
                    statesMap[key] = state_id
                }
            }
        }
        $map.append($tr)
    }

    //init rack 货架位置
    $("#map .rack").removeClass("rack")
    for(let i=0;i<rackPosList.length;i++){
        let pos = rackPosList[i]
        $(`#map tr:nth-child(${pos[1] + 1}) td:nth-child(${pos[0] + 1})`).addClass("rack")
    }

    //init start station 开始位置
    $("#map .start-pos").removeClass("start-pos")
    for(let i=0;i<startPosList.length;i++){
        let pos = startPosList[i]
        $(`#map tr:nth-child(${pos[1] + 1}) td:nth-child(${pos[0] + 1})`).addClass("start-pos")
    }

    //init end station 结束位置
    $("#map .end-pos").removeClass("end-pos")
    for(let i=0;i<endPosList.length;i++){
        let pos = endPosList[i]
        $(`#map tr:nth-child(${pos[1] + 1}) td:nth-child(${pos[0] + 1})`).addClass("end-pos")
    }

    if(startPosList.length < agvNum){
        alert("agv数量超过了startPosList，请修改！")
        return
    }

    //init tasks
    for(let j=0;j<tasks.length;j++){
        let task = tasks[j]
        if(task.agv !== undefined) {
            task.agv = undefined
        }
    }

    //init agv
    $("body > .total-main >.agv").remove()
    agvs = []
    for(let i=0;i<agvNum;i++){
        let id = i;
        let color = `color-${id}`
        let $agv=$(`<div class='agv ${color}'></div>`)
        let x = startPosList[i][0]
        let y = startPosList[i][1]
        let theta = 270 //init时，agv都是头朝下的

        //增加三角形表示agv小车的当前朝向
        let $triangle_container=$(`<div class="triangle-container">`)
        $triangle_container.append(`<div class='triangle'>`)
        $agv.append($triangle_container)

        $agv.css({
            left: x * unitSize + "px",
            top: y * unitSize + "px",
            transform: 'rotate(180deg)'    //270对应的是头朝下
        })
        $("body > .total-main").append($agv)

        let agv = {
            x:x,
            y:y,
            theta:theta,
            id: id,
            $agv: $agv,
        }

        agvs.push(agv)

        let key = [x,y,theta].toString()
        let state_id = statesMap[key]
        let robot = {
            robot_id: id,
            current_pos: {
                state_id: state_id,
                pos:{
                    x:x,
                    y:y,
                    theta:theta,
                }
            },
            tasks:[]
        }

        robots.push(robot)

    }

    //init input-box
    $mapSizeWidth.val(mapSizeWidth)
    $mapSizeHeight.val(mapSizeHeight)
    $agvNum.val(agvNum)
    $rackPosList.val(JSON.stringify(rackPosList))
    $startPosList.val(JSON.stringify(startPosList))
    $endPosList.val(JSON.stringify(endPosList))

}

function updateConfig(){
    mapSizeWidth = $.trim($mapSizeWidth.val())
    mapSizeHeight = $.trim($mapSizeHeight.val())
    agvNum = $.trim($agvNum.val())

    try{
        rackPosList = JSON.parse($.trim($rackPosList.val()))
    }catch (ex){
        alert("货架坐标点集合，数据非法")
    }
    try{
        startPosList = JSON.parse($.trim($startPosList.val()))
    }catch (ex){
        alert("起始点坐标集合，数据非法")
    }

    try{
        endPosList = JSON.parse($.trim($endPosList.val()))
    }catch (ex){
        alert("结束点坐标集合，数据非法")
    }
}

// ----------------- gen and assign task -----------------

function checkPosValid(x,y,theta){
    if(checkInForbiddenArea(x, y)){
        return false
    }

    let key = [x, y, theta].toString()
    if(statesMap[key]!==undefined){
        return true
    }
    return false
}

function genNewTask(){
    // 随机产生1-6个新的task
    // let max1 = 6;
    // let min1 = 1;
    // let taskNum = Math.round(Math.random()*(max1-min1)+min1)
    let taskNum = 10

    for(let i=0;i<taskNum;i++){
        let newTask = []

        // 与算法端同学沟通过，前端限制每个task中的子任务数最多为1个
        let tgtNum = 1
        for(let j=0;j<tgtNum;j++) {
            while (true){
                let max = 29;
                let min = 0;
                let randX = Math.round(Math.random()*(max-min)+min)
                let randY = Math.round(Math.random()*(max-min)+min)

                let randIdx = Math.round(Math.random()*3);
                let availThetaArr = [0, 90, 180, 270]
                let randTheta = availThetaArr[randIdx]

                if(checkPosValid(randX, randY, randTheta)){
                    newTask = newTask.concat([randX, randY, randTheta])
                    break
                }
            }

        }

        tasks.push(newTask)
    }
}

function assignTask(){
    for(let i=0;i<agvs.length;i++){
        let agv = agvs[i]
        if(agv.task === undefined){
            for(let j=0;j<tasks.length;j++){
                let task = tasks[j]
                if(task.agv === undefined){
                    if (task[j] === agv.x && task[j+1] === agv.y) {
                        console.log("任务与小车当前坐标重合");
                        continue;
                    }
                    agv.task = task
                    task.agv = agv

                    for(let j=0;j<task.length;j+=3){
                        let x = task[j]
                        let y = task[j+1]
                        let theta = task[j+2]
                        let color = `color-${agv.id}`
                        $(`#map tr:nth-child(${y + 1}) td:nth-child(${x + 1})`).addClass(`target-pos ${color}`)
                        console.log(`agv.id= ${agv.id} assignTask target:${x},${y},${theta}`)
                    }
                    break;
                }
            }
        }
    }

    if(missionStart){
        if(assignTaskTimerId){
            clearTimeout(assignTaskTimerId)
            assignTaskTimerId = undefined
        }
        //3秒后重新再assignTask
        assignTaskTimerId = setTimeout(function (){
            assignTask()
        },3000)
    }
}

// ----------------- gen and run path -------------
let lastInvokeTime = undefined

function _run1Agv(agv){
    if (!missionStart){
        return
    }

    if(agv.path !== undefined && agv.path.length > 0){
        if(agv.path[0] == "sub_task_spliter"){
            agv.path.splice(0, 1)
            if(agv.task && agv.task.length > 3){
                //说明完成第一步task了
                agv.task.splice(0, 3)
            }
            _run1Agv(agv)
            return
        }

        let tgtX = agv.path[0]
        let tgtY = agv.path[1]
        let tgtTheta = agv.path[2]

        // tmp fix bug, qiuyuwei
        // 邱煜炜，如果后端算法已经将theta=90和theta=270弄颠倒的问题解决了
        // 请注释掉以下四行代码
        // if(tgtTheta==90){
        //     tgtTheta = 270
        // }else if(tgtTheta==270){
        //     tgtTheta = 90
        // }

        if(checkCollisionFlag && checkCollision(agv, tgtX, tgtY)){
            // 最多10秒调用一次
            let nowInvokeTime = new Date().getTime()
            if(lastInvokeTime === undefined || (nowInvokeTime - lastInvokeTime) > 10000){
                lastInvokeTime = nowInvokeTime
                // console.log("发送errorRoute事件!")
                let errorRoute_data = buildComputeRouteData()
                //附加error_robots信息方便算法端调试
                errorRoute_data.error_robots = error_robots
                socket.emit('errorRoute', {'data': errorRoute_data})
                //发送完error_robots信息后，error_robots已经没有用了，必须将error_robots变成空数组
                error_robots = []
            }
            //return别忘记了，很重要！！
            //发现碰撞了，就不要动了
            return
        }

        let $agv = agv.$agv

        // 随机数模拟速度变化
        max = 30
        min = 0
        rand = Math.random()*(max-min)+min

        let duration = 0
        if(agv.x != tgtX || agv.y != tgtY){
            // 移动到目标点
            duration = 200 + rand

            $agv.animate({
                left: tgtX * unitSize + "px",
                top: tgtY * unitSize + "px",
            }, duration , "linear", function (){
                agv.x = tgtX
                agv.y = tgtY
                agv.theta = tgtTheta

                let $td =$(`#map tr:nth-child(${tgtY + 1}) td:nth-child(${tgtX + 1})`)
                let color = `color-${agv.id}`
                if($td.is(`.target-pos.${color}`)){
                    $td.removeClass("target-pos")
                    $td.removeClass(color)
                }

                if(agv.path !== undefined && agv.path.length > 0){
                    // 删除path中前三项x,y,theta
                    agv.path.splice(0, 3)
                }

                _run1Agv(agv)
            })

        }else if(agv.theta != tgtTheta){
            duration = 50  //转弯时间为固定的50ms
            // console.log("转弯ing")
            let rotateAnimationClass = ""
            let endRotateTransform = undefined
            switch (agv.theta){
                case 0:
                    rotateAnimationClass += "right";
                    break;
                case 90:
                    rotateAnimationClass += "up";
                    break;
                case 180:
                    rotateAnimationClass += "left";
                    break;
                case 270:
                    rotateAnimationClass += "down";
                    break;
                default:
                    rotateAnimationClass += "error"
                    break;
            }

            rotateAnimationClass += "To"
            switch (tgtTheta){
                case 0:
                    rotateAnimationClass += "Right";
                    endRotateTransform = "rotate(90deg)"
                    break;
                case 90:
                    rotateAnimationClass += "Up";
                    endRotateTransform = "rotate(0deg)"
                    break;
                case 180:
                    rotateAnimationClass += "Left";
                    endRotateTransform = "rotate(-90deg)"
                    break;
                case 270:
                    rotateAnimationClass += "Down";
                    endRotateTransform = "rotate(180deg)"
                    break;
                default:
                    rotateAnimationClass += "Error"
                    endRotateTransform = "error"
                    break;
            }

            $agv.addClass(rotateAnimationClass)
            setTimeout( function (){
                $agv.removeClass(rotateAnimationClass)
                $agv.css({
                    "transform": endRotateTransform
                })

                agv.x = tgtX
                agv.y = tgtY
                agv.theta = tgtTheta

                let $td =$(`#map tr:nth-child(${tgtY + 1}) td:nth-child(${tgtX + 1})`)
                let color = `color-${agv.id}`
                if($td.is(`.target-pos.${color}`)){
                    $td.removeClass("target-pos")
                    $td.removeClass(color)
                }

                if(agv.path !== undefined && agv.path.length > 0){
                    // 删除path中前三项x,y,theta
                    agv.path.splice(0, 3)
                }

                _run1Agv(agv)
            }, duration)
        }else{
            // console.log("原地不动")
            //原地不动，所以忽略此点
            if(agv.path !== undefined && agv.path.length > 0){
                // 删除path中前三项x,y,theta
                agv.path.splice(0, 3)
            }

            _run1Agv(agv)
        }

    }else{
        // 从tasks中删除task
        for(let i=0;i<tasks.length;i++){
            if(tasks[i].agv !==undefined && tasks[i].agv.id === agv.id){
                tasks.splice(i, 1)
            }
        }

        agv.task = undefined
        agv.path = undefined

        // let task = agv.task
        // if(task){
        //     task.agv = undefined
        // }

    }
}

function runAllAgv(responseData){
    let serverPathArr = responseData.data.result
    for(let i=0;i<serverPathArr.length;i++){
        let serverRobotId = serverPathArr[i].robot_id
        let serverPath = serverPathArr[i].path
        if(!serverPath || serverPath.length == 0){
            // 算法端没有规划路径的情况，跳过此agv，不然可能导致agv任务消失
            continue
        }
        for(let j=0;j<agvs.length;j++) {
            let agv = agvs[j]
            if(agv.id == serverRobotId){
                agv.path = serverPath
                //pathCache只是作为缓存，给算法端发送调试信息用的，没有任何其它作用
                let road = []
                let roadMap = []
                let num = 0
                for (let k=0;k<serverPath.length;k+=3){
                    if(serverPath[k] == "sub_task_spliter"){
                        k+=1
                        num+=1
                    }
                    let roadX = serverPath[k]
                    let roadY = serverPath[k+1]
                    let roadTheta = serverPath[k+2]
                    let key = [roadX,roadY,roadTheta].toString()
                    let state_id = statesMap[key]
                    let index = (k-num) / 3
                    roadMap[state_id] = index
                    road.push({
                        state_id: state_id,
                        index: index
                    })
                }
                roads[agv.id] = road
                roadsMap[agv.id] = roadMap
                _run1Agv(agv)
            }
        }
    }
}

// ----------------- showInfo -------------
function showInfo(){
    let $ul = $("#agv-pos-list").empty()
    for(let i=0;i<agvs.length;i++){
        let agv = agvs[i]
        let $li=$(`<li><span class='agv-id'>agv-${agv.id}:</span><span class='agv-pos'>(${agv.x},${agv.y},${agv.theta})</span></li>`)
        $ul.append($li)
    }
}

$(function () {
    $mapSizeWidth = $("#mapSizeWidth")
    $mapSizeHeight = $("#mapSizeHeight")
    $agvNum = $("#agvNum")
    $rackPosList = $("#rackPosList")
    $startPosList = $("#startPosList")
    $endPosList = $("#endPosList")
    $collisionNum = $("#collision-num")


    //init map
    renderMap()

    // init socketio client

    create_socket()

    $("#btn-update-config").on("click", function (){
        //停止任务
        stopMission()

        //更新配置
        updateConfig()

        //render地图
        renderMap()

        console.log("更新配置成功！")

    })

    $("#btn-start-mission").on("click", function (){
        console.log("开始作业！")
        startMission()
    })

    $("#btn-stop-mission").on("click", function (){
        console.log("结束作业！")
        stopMission()
    })

    $("#checkbox-check-collision").on("click", function (){
        checkCollisionFlag = $(this).is(":checked")
    })

});

