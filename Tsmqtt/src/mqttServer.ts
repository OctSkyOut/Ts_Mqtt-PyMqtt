// 작성일 2021.5.12  작성자 김민수
import { connect } from "mqtt";
import 'dotenv/config';
import { createConnection, Connection } from 'mysql'

// 타입
import { connectType, mysqlConnectType, queryResultType } from './Types'

export default class Mqtt {
    cli; // 클라이언트 객체
    mysql: Connection | undefined; // mysql객체
    subscribeResult = {
        deviceId: 0,
        time: '',
        count: 0
    }; // subscibe 설정 후 수신되는 데이터를 저장하는 객체

    /**
     * 생성자 : MQTT의 브로커에 연결하는 역할을 한다.
     * @param connectInfo MQTT연결시 연결될 정보들이다. (connectType에 커서 올림 또는 Types.ts파일 참고) 
     */
    constructor(connectInfo: connectType, topic: string) {
        try {
            this.cli = connect(connectInfo);
            this.cli.on("error", (_) => {
                throw _;
            });
            this.cli.on("connect", (msg) => {
                console.log(`MQTT 연결성공! 현재 MQTT 연결상태 ${msg}`);
                this.cli.subscribe(topic, (err, granted) => {
                    console.log(`${granted[0].topic}에 구독을 시작하였습니다!`);
                    if (err) throw err;
                });
            });
        } catch (error) {
            console.log(`연결에 실패하였습니다. 연결을 종료합니다.`);
            console.log(error);
            process.exit(1);
        }
    }

    /**
     * 데이터베이스에 연결을 시도하는 메소드이다.
     * @param connectInfo DB에 연결할 때 필요한 객체 타입이다.(mysqlConnectType 커서 올림 또는 Type.ts파일 참고)
     */
    connectDB(connectInfo: mysqlConnectType): void {
        try {
            this.mysql = createConnection(connectInfo);
            this.mysql.connect((err) => { throw err })
        } catch (error) {
            console.log(`데이터베이스에 연결을 실패하였습니다. 다시한번 확인해 주세요. \n ${error}`);
        }
    }

    /**
     * DB에 연결 후 SELECT문을 처리하는 메소드이다.
     * @param query SELECT문이 들어간 쿼리
     * @returns 열의 정보가 키값, 셀의 값이 값이되며, 행의 개수가 객체의 개수로 된 배열안의 객체의 값을리턴
     * ##### ex) 리턴값이 2열 2행이라면 -> [{a : 1, b : 'A'}, {a : 2, b : 'B'} ] 
     */
    excuteSelectQuery(query: string): queryResultType[] {
        let res: queryResultType[] = [];
        this.mysql?.query(query, (err, result: queryResultType[]) => {
            try {
                if (err) throw err;
                console.log('SELECT 쿼리 처리완료');
                res = result;
            } catch (error) {
                console.log("쿼리 처리 오류");
                console.log(error);
                return;
            }
        })
        return res;
    }

    /**
     * 데이터베이스의 INSERT, UPDATE, DELETE를 실행하는 메소드이다.
     * @param query INSERT, UPDATE, DELETE 중 하나를 실행하는 쿼리문
     * @returns 정상적으로 처리가되었다면 true를 반환 아니라면 false
     */
    excuteIUD(query: string): boolean {
        let res: boolean = false;
        this.mysql?.query(query, (err, result) => {
            try {
                if (err) throw err;
                console.log('쿼리 처리완료');
                res = true;
            } catch (error) {
                console.log("쿼리 처리 오류");
                console.log(error);
                res = false;
            }
        })
        return res;
    }

    /**
     * SubScribe 통신을 사용할 때 데이터를 받는 메소드
     * 데이터가 수신이 될때마다 아래의 this.cli.on 메소드가 실행됨 (수신안될때는 아무것도 실행안함)
     */
    mqttSubscribe(): void {
        this.cli.on('message', (topic: string, message: string, packet) => {
            this.subscribeResult = { ...JSON.parse(message), topic }
            this.excuteSelectQuery(`
            INSERT INTO EqTagRollUpDataHs 
            (TagId, EventDt, PassDt, TagValue) 
            VALUES ('000${this.subscribeResult.deviceId}', NOW(), 
            '${this.subscribeResult.time}', ${this.subscribeResult.count});
            `)
        });
    }
}