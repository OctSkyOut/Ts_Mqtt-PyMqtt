"use strict";
var __assign = (this && this.__assign) || function () {
    __assign = Object.assign || function(t) {
        for (var s, i = 1, n = arguments.length; i < n; i++) {
            s = arguments[i];
            for (var p in s) if (Object.prototype.hasOwnProperty.call(s, p))
                t[p] = s[p];
        }
        return t;
    };
    return __assign.apply(this, arguments);
};
Object.defineProperty(exports, "__esModule", { value: true });
var mqtt_1 = require("mqtt");
require("dotenv/config");
var mysql_1 = require("mysql");
var Mqtt = /** @class */ (function () {
    /**
     * 생성자 : MQTT의 브로커에 연결하는 역할을 한다.
     * @param connectInfo MQTT연결시 연결될 정보들이다. (connectType에 커서 올림 또는 Types.ts파일 참고)
     */
    function Mqtt(connectInfo) {
        var _this = this;
        this.subscribeResult = {}; // subscibe 설정 후 수신되는 데이터를 저장하는 객체
        try {
            this.cli = mqtt_1.connect(connectInfo);
            this.cli.on("error", function (_) {
                throw _;
            });
            this.cli.on("connect", function (msg) {
                console.log("MQTT \uC5F0\uACB0\uC131\uACF5! \uD604\uC7AC MQTT \uC5F0\uACB0\uC0C1\uD0DC " + msg);
                _this.cli.subscribe('/device/MCT', function (err, granted) {
                    console.log(granted[0].topic + "\uC5D0 \uAD6C\uB3C5\uC744 \uC2DC\uC791\uD558\uC600\uC2B5\uB2C8\uB2E4!");
                    if (err)
                        throw err;
                });
            });
        }
        catch (error) {
            console.log("\uC5F0\uACB0\uC5D0 \uC2E4\uD328\uD558\uC600\uC2B5\uB2C8\uB2E4. \uC5F0\uACB0\uC744 \uC885\uB8CC\uD569\uB2C8\uB2E4.");
            console.log(error);
            process.exit(1);
        }
    }
    /**
     * 데이터베이스에 연결을 시도하는 메소드이다.
     * @param connectInfo DB에 연결할 때 필요한 객체 타입이다.(mysqlConnectType 커서 올림 또는 Type.ts파일 참고)
     */
    Mqtt.prototype.connectDB = function (connectInfo) {
        try {
            this.mysql = mysql_1.createConnection(connectInfo);
            this.mysql.connect(function (err) { throw err; });
        }
        catch (error) {
            console.log("\uB370\uC774\uD130\uBCA0\uC774\uC2A4\uC5D0 \uC5F0\uACB0\uC744 \uC2E4\uD328\uD558\uC600\uC2B5\uB2C8\uB2E4. \uB2E4\uC2DC\uD55C\uBC88 \uD655\uC778\uD574 \uC8FC\uC138\uC694. \n " + error);
        }
    };
    /**
     * DB에 연결 후 SELECT문을 처리하는 메소드이다.
     * @param query SELECT문이 들어간 쿼리
     * @returns 열의 정보가 키값, 셀의 값이 값이되며, 행의 개수가 객체의 개수로 된 배열안의 객체의 값을리턴
     * ##### ex) 리턴값이 2열 2행이라면 -> [{a : 1, b : 'A'}, {a : 2, b : 'B'} ]
     */
    Mqtt.prototype.excuteSelectQuery = function (query) {
        var _a;
        var res = [];
        (_a = this.mysql) === null || _a === void 0 ? void 0 : _a.query(query, function (err, result) {
            try {
                if (err)
                    throw err;
                console.log('SELECT 쿼리 처리완료');
                res = result;
            }
            catch (error) {
                console.log("쿼리 처리 오류");
                console.log(error);
                return;
            }
        });
        return res;
    };
    /**
     * 데이터베이스의 INSERT, UPDATE, DELETE를 실행하는 메소드이다.
     * @param query INSERT, UPDATE, DELETE 중 하나를 실행하는 쿼리문
     * @returns 정상적으로 처리가되었다면 true를 반환 아니라면 false
     */
    Mqtt.prototype.excuteIUD = function (query) {
        var _a;
        var res = false;
        (_a = this.mysql) === null || _a === void 0 ? void 0 : _a.query(query, function (err, result) {
            try {
                if (err)
                    throw err;
                console.log('쿼리 처리완료');
                res = true;
            }
            catch (error) {
                console.log("쿼리 처리 오류");
                console.log(error);
                res = false;
            }
        });
        return res;
    };
    /**
     * SubScribe 통신을 사용할 때 데이터를 받는 메소드
     * 데이터가 수신이 될때마다 아래의 this.cli.on 메소드가 실행됨 (수신안될때는 아무것도 실행안함)
     */
    Mqtt.prototype.mqttSubscribe = function () {
        var _this = this;
        this.cli.on('message', function (topic, message, packet) {
            _this.subscribeResult = __assign(__assign({}, JSON.parse(message)), { topic: topic });
            console.log(_this.subscribeResult);
        });
    };
    return Mqtt;
}());
exports.default = Mqtt;
//# sourceMappingURL=mqttServer.js.map