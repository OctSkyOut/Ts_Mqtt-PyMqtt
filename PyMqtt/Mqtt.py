import paho.mqtt.client as mqtt_client
import paho.mqtt.publish as publish
import json

import DBConncet as db

# 다중 디바이스 접근시 클라이언트 이름이 중복되지않게 device_id 값 설정
# 중복시 MQTT에서 접근 거부
device_id = 0
# 브로커의 로컬 IP주소
broker_address = "192.168.0.xx"
# 브로커의 포트 번호 기본값 : 1883
broker_port = 1883
# public, subscribe 연결 요청시 송신 또는 수신 데이터의 호출 주소
topic = "/topic"  # 브라우저의 URL과 비슷한 개념
# 모스키토에서 설정한 로컬 ID
username = "admin"
# 모스키토에서 설정한 로컬 PW
client_pw = "로컬 모스키토 클라이언트 비밀번호"

# 클라이언트 객체 (아래 확인)
client = None

# subscribe_result의 약자로 수신데이터를 저장하는 변수이다
sub_res = None

# db 연결 정보
dbInfo = {
    "host": "",
    "user": "",
    "password": "",
    "db": "",
}

# 브로커에 연결하여 MQTT 통신 활성화하는 함수
def connect_mqtt() -> mqtt_client:
    global client, username, client_pw, device_id
    try:
        # 연결완료 이벤트 발생시
        def on_connect(client, userdata, flags, rc):
            if rc == 0:
                print("MQTT Broker에 연결하였습니다.")
            else:
                print(f"브로커에 연결실패햐였습니다., Returned code: {rc}")

        # 연결 종료 이벤트
        def on_disconnect(client, userdata, flags, rc=0):
            print(f"브로커 연결종료 {str(rc)}")

        # 연결 후 콘솔알림이 발생시 해당 이벤트 자동 사용
        def on_log(client, userdata, level, buf):
            print(f"log: {buf}")

        # 클라이언트 아이디 할당 (클라이언트 아이디는 자유)
        client_id = f"""Hidata_device{device_id}"""

        # 클라이언트 생성
        client = mqtt_client.Client(client_id)

        # 위에서 선언한 콜백 함수 설정
        client.on_connect = on_connect
        client.on_disconnect = on_disconnect
        client.on_log = on_log

        # 전역변수로 할당된 username과 client_pw가 모스키토 MQTT통신 연결의 ID, 비밀번호가 된다.
        client.username_pw_set(username, client_pw)

        # broker 연결
        client.connect(
            host=broker_address,
            port=broker_port,
        )

        return client
    except Exception as err:
        raise err


# 브로커 연결 후 publish 송신 후 바로 브로커 연결 종료
def single_publish(sendData: dict):
    global topic, broker_address, broker_port, username, client_pw, device_id
    try:
        # publish하려는 데이터를 JSON형태로 변환
        json = json.dumps(sendData, sort_keys=True, indent=4)

        # publish로 브로커에 1번 데이터 송신
        publish.single(
            topic,
            payload=json,
            qos=2,
            retain=False,
            hostname=broker_address,
            port=broker_port,
            client_id=f"""Hidata_device{device_id}""",
            keepalive=60,
            will=None,
            auth={"username": username, "password": client_pw},
            tls=None,
        )
    except Exception as err:
        raise err


# Subscribe 등록 후 DB에 SQL 문을 작성하여 데이터를 저장
def subscribe_and_sendDB(client: mqtt_client):
    global topic, sub_res
    try:
        # Subscribe후 데이터가 수신이 될때마다 실행
        def on_message(client, userdata, msg):
            # 수신된 데이터를 JSON에서 사전형 객체로 변환시킴
            sub_res = json.loads(msg.payload)
            # topic이라는 키 및 값 추가
            sub_res["topic"] = msg.topic

            # 데이터베이스 연결 객체 생성
            conn = db.DBConnect(
                host=dbInfo.get("host"),
                user=dbInfo.get("user"),
                password=dbInfo.get("pwd"),
                db=dbInfo.get("db"),
            )

            # 쿼리 작성
            ################### 이곳에서 쿼리 변경 ###################
            query = f"""
                        INSERT INTO EqTagRollUpDataHs
                        (TagId, EventDt, PassDt, TagValue)
                        VALUES
                        ('000{sub_res["deviceId"]}', NOW(), '{sub_res["time"]}', {sub_res["count"]});
                    """
            #########################################################
            # 쿼리 처리
            conn.excute_query(query=query)

        # topic에 정해진값으로 subscribe시작
        client.subscribe(topic)
        # 위에서 선언한 콜백 함수 설정
        client.on_message = on_message
    except Exception as err:
        raise err


# 데이터베이스 연결정보 저장 dbInfo에 값을 해당 함수를 통해 적용
def set_db_info(host: str = "", user: str = "", pwd: str = "", dbTarget: str = ""):
    global dbInfo
    dbInfo["host"] = host
    dbInfo["user"] = user
    dbInfo["pwd"] = pwd
    dbInfo["db"] = dbTarget


# subscribe를 사용시 아래의 힘수사용
# 연결을 종료하지않고 계속해서 데이터를 받아 DB에 저장하는 함수
def run_loop_subscribe():
    cli = connect_mqtt()
    subscribe_and_sendDB(cli)
    client.loop_forever()