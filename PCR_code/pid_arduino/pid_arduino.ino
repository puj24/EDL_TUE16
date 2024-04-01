#include <Arduino.h>
#include <math.h>
#include <Adafruit_MAX31865.h>

// Use software SPI: CS, DI, DO, CLK
Adafruit_MAX31865 thermo = Adafruit_MAX31865(10, 11, 12, 13);

#define RREF      430.0
#define RNOMINAL  100.0

#define PELTIER_PIN1 7  // Replace with the GPIO pin connected to IN1 of H-bridge (e.g., Arduino pin 7)
#define PELTIER_PIN2 6  // Replace with the GPIO pin connected to IN2 of H-bridge (e.g., Arduino pin 6)

#define SETPOINT_1 95.5
#define SETPOINT_2 63
#define SETPOINT_3 72.5

// constant temperature of the stages
#define  CONST_S1 62
#define CONST_S2 75
#define CONST_S3 43
#define RAMP_RATE 2  

int stage;
unsigned long previousMillis, currentMillis;

#define PWM_RANGE 255    // PWM range for Arduino (8-bit)

#define KP 1  // Proportional gain
#define KI 0.01 // Integral gain
#define KD 0.05 // Derivative gain

float current_setpoint; float current_temp ;

float integral, prev_error, prev_time , output;
#define const_duty_cycle 0.5

void maintain_temp(float duration){
    currentMillis = millis()/1000.0;

    while ((currentMillis - previousMillis) < duration) { 
       unsigned long seconds = currentMillis;
      unsigned long minutes = seconds / 60;
      unsigned long hours = minutes / 60;

      // Format the timestamp
      String timestamp = String(hours) + ":" + String(minutes % 60) + ":" + String(seconds % 60);

      Serial.print(timestamp);
      Serial.print(",");

      Serial.print("Setpoint:"); Serial.print(current_setpoint);  Serial.print(",");
      current_temp = thermo.temperature(RNOMINAL, RREF);
      Serial.print("Temperature:"); Serial.print(current_temp);   Serial.print(",");
             
      float error = current_setpoint - current_temp;
  
      float current_time = millis() / 1000.0;
      float dt = current_time - prev_time;
  
      integral += error * dt;
      float derivative = (error - prev_error) / dt;
  
      output = KP * error + KI * integral + KD * derivative;
      output = output / (KP * 10);
      prev_error = error;    prev_time = current_time;
      control_peltier(output);

      currentMillis = millis()/1000.0; 
    }
}

void control_peltier(float duty_cycle) {
    duty_cycle = min(max(duty_cycle, 0.0), 1.0);  // Ensure duty cycle is within valid range
    Serial.print("Duty:"); Serial.print(duty_cycle*100); Serial.println(",");

    int pwm_value = duty_cycle * PWM_RANGE;   // Convert duty cycle to PWM value

    analogWrite(PELTIER_PIN1, pwm_value);
    analogWrite(PELTIER_PIN2, PWM_RANGE - pwm_value);
}

void pid_control() {
     current_temp = thermo.temperature(RNOMINAL, RREF);
     Serial.print("Temperature:"); Serial.print(current_temp);   Serial.print(",");
     
    float error = current_setpoint - current_temp;

    float current_time = millis() / 1000.0;
    float dt = current_time - prev_time;

    integral += error * dt;
    float derivative = (error - prev_error) / dt;

    output = KP * error + KI * integral + KD * derivative;
    output = output / (KP * 10);

    if(current_setpoint > current_temp){
      if ((current_setpoint - current_temp) > 2){
        output = 1;        
      }
    }
    else {
      if ((current_temp - current_setpoint) > 2){
        output = 0;        
      }
    }
    
    prev_error = error;    prev_time = current_time;

    control_peltier(output);
//  Serial.print(current_time); Serial.print(",");  Serial.println(current_temp);
}

void setup() {
    Serial.begin(115200);
    pinMode(PELTIER_PIN1, OUTPUT);
    pinMode(PELTIER_PIN2, OUTPUT);
    thermo.begin(MAX31865_3WIRE); 
     
    current_setpoint = SETPOINT_1;  stage = 1;
    integral = 0.0;  prev_error = 0.0;  prev_time = 0.0;
}

void loop() {

    unsigned long currentTime = millis();
    unsigned long seconds = currentTime / 1000;
    unsigned long minutes = seconds / 60;
    unsigned long hours = minutes / 60;

    // Format the timestamp
    String timestamp = String(hours) + ":" + String(minutes % 60) + ":" + String(seconds % 60);

    Serial.print(timestamp);
    Serial.print(",");

    uint8_t fault = thermo.readFault();
    if (fault) {
    Serial.print("Fault 0x"); Serial.println(fault, HEX);
    if (fault & MAX31865_FAULT_HIGHTHRESH) {
      Serial.println("RTD High Threshold"); 
    }
    if (fault & MAX31865_FAULT_LOWTHRESH) {
      Serial.println("RTD Low Threshold"); 
    }
    if (fault & MAX31865_FAULT_REFINLOW) {
      Serial.println("REFIN- > 0.85 x Bias"); 
    }
    if (fault & MAX31865_FAULT_REFINHIGH) {
      Serial.println("REFIN- < 0.85 x Bias - FORCE- open"); 
    }
    if (fault & MAX31865_FAULT_RTDINLOW) {
      Serial.println("RTDIN- < 0.85 x Bias - FORCE- open"); 
    }
    if (fault & MAX31865_FAULT_OVUV) {
      Serial.println("Under/Over voltage"); 
    }
    thermo.clearFault();
  }
    Serial.print("Setpoint:"); Serial.print(current_setpoint);   Serial.print(",");

    pid_control();
    if ( (stage == 1 )&& (current_temp > SETPOINT_1)) {
//      Serial.println("SETPOINT GREATER THAN 95");
        previousMillis = millis()/1000.0;
        maintain_temp(CONST_S1);
        current_setpoint = SETPOINT_2;
        stage++;
    }
    else if ( (stage == 2 )&& (current_temp < SETPOINT_2)) {
      //      Serial.println("SETPOINT LESSER THAN 63");
        previousMillis = millis()/1000.0;
        maintain_temp(CONST_S2);
        current_setpoint = SETPOINT_3;
        stage++;
    }
    else if ((stage == 3) && (current_temp > SETPOINT_3)){         
//        Serial.println("SETPOINT GREATER THAN 72.5");
          previousMillis = millis()/1000.0;
          maintain_temp(CONST_S3);
          current_setpoint = SETPOINT_1;
          stage = 1;
    }
    delay(10);
}
