"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
var mqttServer_1 = require("./mqttServer");
/**
 * mqtt객체를 생성함과 동시에 mtqq 브로커 연결
 */
var mqtt = new mqttServer_1.default({
    host: '192.168.0.xx',
    port: 1883,
    protocol: 'mqtt',
    username: 'admin',
    password: 'password',
});
// subscribe 실행
mqtt.mqttSubscribe();
//# sourceMappingURL=index.js.map