import websocket
import json
import rel
import requests
import os
from datetime import datetime
replyList = [
    ["有人吗", "没人"],
    ["傻逼", "智障"],
    ["在吗", "不在"],
    ["qwq", "qaq"],
    ["awa", "quq"],
]
jsonPath = "./checkin.json"
if not os.path.exists(jsonPath):
    initDict = {"user": [], "name": [], "count": [], "day": []}
    initJson = json.dumps(initDict)
    print("正在生成用于存储签到次数的json")
    openInitJson = open(jsonPath, "w")
    openInitJson.write(initJson)
    openInitJson.close()
def sendPrivateMessage(id, message):
    requests.get(
        "http://127.0.0.1:5700/send_msg?user_id=%d&message=%s" % (id, message))
def sendGroupMessage(id, message):
    requests.get(
        "http://127.0.0.1:5700/send_group_msg?group_id=%d&message=%s" % (id, message))
def getMessage(ws, message):
    m = dict(json.loads(message))
    #if m['post_type'] == 'heartbreat' or m["post_type"] == "meta_event":
    #    return None
    if m["message"] == ".签到" or m["message"] == ".check in":
        print("有人在签到！")
        readJson = open(jsonPath, "r")
        jsonDict = json.load(readJson)
        userList = jsonDict["user"]
        nameList = jsonDict["name"]
        countList = jsonDict["count"]
        dayList = jsonDict["day"]
        '''
        try:
            day = dayList[0]
        except:
            dayList.append(datetime.today().day)
            print("添加日期")
        '''
        try:
            index = userList.index(m["user_id"])
            if dayList[index] != datetime.today().day:
                dayList.clear()
                dayList.append(datetime.today().day)
                countList[index] += 1
                createJson = {"user": userList, "name": nameList,
                              "count": countList, "day": dayList}
                newJson = json.dumps(createJson)
                openJson = open(jsonPath, "w")
                openJson.write(newJson)
                openJson.close()
            if m["message_type"] == "private":
                sendPrivateMessage(m["user_id"],"%s签到了%d天" % (m["sender"]["nickname"], countList[index]))
            if m["message_type"] == "group":
                sendGroupMessage(m["group_id"],"%s签到了%d天" % (m["sender"]["nickname"], countList[index]))
        except:
            userList.append(m["user_id"])
            countList.append(1)
            nameList.append(m["sender"]["nickname"])
            dayList.append(datetime.today().day)
            createJson = {"user": userList, "name": nameList,"count": countList, "day": dayList}
            newJson = json.dumps(createJson)
            openJson = open(jsonPath, "w")
            openJson.write(newJson)
            openJson.close()
            if m["message_type"] == "private":
                sendPrivateMessage(m["user_id"], "%s签到了%d天" % (m["sender"]["nickname"],1))
            if m["message_type"] == "group":
                sendGroupMessage(m["group_id"],"%s签到了%d天" % (m["sender"]["nickname"],1))
        return None
    if m["message"] == ".签到板" or m["message"] == ".check board":
        print("有人在看签到板")
        readJson = open(jsonPath, "r")
        jsonDict = json.load(readJson)
        nameList = jsonDict["name"]
        countList = jsonDict["count"]
        tempStr = ""
        try:
            testName = nameList[0]
            tempStr += "签到的人数与天数：\n"
            for listIndex in range(0,len(nameList)):
                tempStr += "%s签到了%d天\n" % (nameList[listIndex],countList[listIndex])
            if m["message_type"] == "private":
                sendPrivateMessage(m["user_id"],tempStr)
            if m["message_type"] == "group":
                sendGroupMessage(m["group_id"],tempStr)
        except:
            if m["message_type"] == "private":
                    sendPrivateMessage(m["user_id"],"没有人签到")
            if m["message_type"] == "group":
                sendGroupMessage(m["group_id"],"没有人签到")
    if m["post_type"] == "message":
        flag = False
        for index in range(0, len(replyList)):
            if m["message"] in replyList[index][0]:
                flag = True
                if m["message_type"] == "private":
                    sendPrivateMessage(m["user_id"], replyList[index][1])
                if m["message_type"] == "group":
                    sendGroupMessage(m["group_id"], replyList[index][1])
        '''
        if flag == False:
            if m["message_type"] == "private":
                sendPrivateMessage(m["user_id"], "啊吧啊吧")
        '''
if __name__ == "__main__":
    #websocket.enableTrace(True)
    ws = websocket.WebSocketApp("ws://127.0.0.1:5701/", on_message=getMessage)
    ws.run_forever(dispatcher=rel)
    rel.signal(2, rel.abort)
    rel.dispatch()
