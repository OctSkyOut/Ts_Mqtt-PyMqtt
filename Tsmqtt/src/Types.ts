// 작성일 2021.5.12  작성자 김민수
export type connectType = {
    host: string
    port: number,
    protocol: string,
    username: string,
    password: string,
};

export type mysqlConnectType = {
    host: string,
    user: string,
    password: string,
    database: string
}

export type queryResultType = {
    deviceId: number,
    time: string,
    count: number
}