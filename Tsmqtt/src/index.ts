// 작성일 2021.5.12  작성자 김민수
import Mqtt from "./mqttServer";

/**
 * mqtt객체를 생성함과 동시에 mtqq 브로커 연결
 */
const mqtt = new Mqtt({
    host: '192.168.0.xx',
    port: 1883,
    protocol: 'mqtt',
    username: 'admin',
    password: 'password',
}, '/topic');

// subscribe 실행
mqtt.mqttSubscribe();
