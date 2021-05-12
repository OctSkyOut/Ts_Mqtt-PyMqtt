
/**
 * ---------------------------------------------------------------------------------------------------------------------
 * #include <ArduinoJson.h> => 시간 및 가공수를 JSON형태의 데이터로 변환 후 출력하기 위해서
 *                             해당 라이브러리를 사용한다. 
 *                             출력은 다음과같다. { "Total_Count" : 값, "Sec" : 값 } 
 *                             
 *     * A0 = 생산갯수 출력 PIN, A1 = 제품 가공중일때의 출력PIN
 *     
 *     float vout = 0.0; => 전압센서를 거쳐나온 전압값
 *     
 *     float vin = 0.0; => 회로의 원본 출력값
 *     
 *     float R1 = 30000.0; => 전압센서의 저항 30kΩ
 *     
 *     float R2 = 7500.0;  => 전압센서의 저항 7.5kΩ => R1과 R2의 저항은 직렬로 연결되어있다.
 *     
 *     int SPIN = A0;, int SPIN2 = A1; => 아두이노 아날로그 출력 PIN을 함축한 것 
 * 
 *     int value = 0;, int value2 = 0; => 아두이노 아날로그 PIN출력을 읽은 값
 *     
 *     int Total_Count = 0; => 제품의 가공이 완료시 출력되는 전압값을 받기 위한 변수
 *     
 *     int Sec = 0; => 제품이 가공중일때 출력되는 전압값을 받기위한 변수
 *     
 *     value = analogRead(SPIN); => PIN A0를 아날로그 신호값을 받아 value 변수에 저장
 *     vout = (value * 5.0) / 1024.0; => value값을 입력전압과 곱한 후 1024분주로 나눈다
 *     vin = vout / ( R2 / ( R1 + R2) ); => 해당 식을 이용해서 R2에 들어오는 전압값을 구한 후 vout과 나눈다   
 *     
 *     if(vin > 4 && vin < 5) => 입력 전압이 4볼트 ~ 5볼트 사이라면 시간 또는 카운트에 1씩 더해준다
 *     
 *     DynamicJsonDocument doc(1024); => JSON변환 변수 선언
 *     
 *      doc["Total_Count"] = Total_Count;, doc["Sec"] = Sec; => 두 변수를  JSON화 시키기위해 doc변수안에 값을 할당시킨다.
 *      
 *      serializeJson(doc, Serial); => JSON 값을 시리얼 출력하기위한 작업이다.
 *      
 *      delay(1000); => 1초 지연시킨다.
 * ---------------------------------------------------------------------------------------------------------------------
 */


#include <ArduinoJson.h>
#include <stdio.h>

//A0 = 생산갯수
float vout = 0.0;
float vin = 0.0;
float R1 = 30000.0;  
float R2 = 7500.0; 
// A1 = 가동시간
float vout2 = 0.0;
float vin2 = 0.0;
float R1_2 = 30000.0;  
float R2_2 = 7500.0; 

// A0, A1의 값을 함축
int SPIN = A0;
int SPIN2 = A1;

int value = 0;
int value2 = 0;

int Total_Count = 0;

int Sec = 0;

void setup(){
   pinMode(SPIN, INPUT);
   pinMode(SPIN2, INPUT);
   
   Serial.begin(9600);
}

void loop(){
   value = analogRead(SPIN);
   vout = (value * 5.0) / 1024.0;
   vin = vout / ( R2 / ( R1 + R2) ); 

   value2 = analogRead(SPIN2);
   vout2 = (value2 * 5.0) / 1024.0;
   vin2 = vout2 / ( R2_2 / ( R1_2 + R2_2) ); 

   if(vin > 4 && vin < 5)
   {
    Total_Count = 1;
   }
   else {
    Total_Count = 0;
   }
   
   if(vin2 > 4 && vin2 < 5)
   {
      Sec = 1;
   }
   else{
    Sec = 0;
   }
   
    DynamicJsonDocument doc(1024);

    doc["Total_Count"] = Total_Count; 
    
    doc["Sec"] = Sec;
    
   serializeJson(doc, Serial);
   Serial.print("\n");
   
   delay(1000);
}
