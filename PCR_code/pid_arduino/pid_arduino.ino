#include <Arduino.h>
#include <math.h>
#include <Adafruit_MAX31865.h>

// Use software SPI: CS, DI, DO, CLK
Adafruit_MAX31865 thermo = Adafruit_MAX31865(10, 11, 12, 13);

#define RREF      430.0
#define RNOMINAL  100.0

#define PELTIER_PIN1 7  // Replace with the GPIO pin connected to IN1 of H-bridge
#define PELTIER_PIN2 6  // Replace with the GPIO pin connected to IN2 of H-bridge

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

// PID constants for Heating
#define KP 1  // Proportional gain
#define KI 0.02 // Integral gain
#define KD 0.08 // Derivative gain

// PID constants for Cooling
#define KP_cool 0.1  
#define KI_cool 0.01 
#define KD_cool 0.7 

float current_setpoint, current_temp ;
float ideal_temp, prev_setpoint;

float i_e, prev_error, prev_time , output;
int mode;
#define const_duty_cycle 0.5

void maintain_temp(float duration){
    previousMillis = millis()/1000.0;
    currentMillis = millis()/1000.0;

    while ((currentMillis - previousMillis) < duration) { 
      print_time(currentMillis);

      Serial.print("Ideal:"); Serial.print(ideal_temp);   Serial.print(",");
      Serial.print("Setpoint:"); Serial.print(current_setpoint);  Serial.print(",");
      current_temp = thermo.temperature(RNOMINAL, RREF);
      Serial.print("Temperature:"); Serial.print(current_temp);   Serial.print(",");
             
      pid(current_setpoint, current_temp, mode);      
      control_peltier(output);

      currentMillis = millis()/1000.0; 
    }
    i_e = 0.0;
}

void control_peltier(float duty_cycle) {
    duty_cycle = min(max(duty_cycle, -1.0), 1.0);  // Ensure duty cycle is within valid range
    Serial.print("Duty:"); Serial.print(duty_cycle*100); Serial.println(",");

    int pwm_value = abs(duty_cycle) * PWM_RANGE;   // Convert duty cycle to PWM value

    if(duty_cycle >= 0){
      analogWrite(PELTIER_PIN1, pwm_value);
      analogWrite(PELTIER_PIN2, PWM_RANGE - pwm_value);
    }
    else{
      analogWrite(PELTIER_PIN2, pwm_value);
      analogWrite(PELTIER_PIN1, PWM_RANGE - pwm_value);
    }
    
}

void pid_control() {
     current_temp = thermo.temperature(RNOMINAL, RREF);
     Serial.print("Temperature:"); Serial.print(current_temp);   Serial.print(",");
    
    if(current_setpoint > current_temp){
      if ((current_setpoint - current_temp) > 1){
        output = 1;      
        // Serial.print("i_e:"); Serial.print(i_e);   Serial.print(",");  
        prev_time = millis() / 1000.0;
        prev_error = current_setpoint - current_temp;
      }
      else{
        pid(current_setpoint, current_temp, mode);
      }
    }
    else {
      if ((current_temp - current_setpoint) > 5){
        output = 0;       
        // Serial.print("i_e:"); Serial.print(i_e);   Serial.print(","); 
        prev_time = millis() / 1000.0;
        prev_error = current_setpoint - current_temp;
      }
      else{
        pid(current_setpoint, current_temp, mode);
      }
    }    
    
    control_peltier(output);
}

void setup() {
    Serial.begin(115200);
    pinMode(PELTIER_PIN1, OUTPUT);
    pinMode(PELTIER_PIN2, OUTPUT);
    thermo.begin(MAX31865_3WIRE); 
    prev_setpoint = thermo.temperature(RNOMINAL, RREF);  // initial temperature
     
    current_setpoint = SETPOINT_1;  stage = 1; 
    mode = 0; // 0 for Heating, 1 for Cooling

    i_e = 0.0;  prev_error = 0.0;  prev_time = 0.0;
}

void loop() {

    unsigned long seconds = millis()/ 1000;
    print_time(seconds);

    if(mode == 0){
      ideal_temp = prev_setpoint + 2*(seconds - currentMillis);
      if(ideal_temp > current_setpoint) ideal_temp = current_setpoint;
    }
    else{
      ideal_temp = prev_setpoint - 2*(seconds - currentMillis);
      if(ideal_temp < current_setpoint) ideal_temp = current_setpoint;
    }

    uint8_t fault = thermo.readFault();
//    print_thermo_fault(fault);

    Serial.print("Ideal:"); Serial.print(ideal_temp);   Serial.print(",");
    
    Serial.print("Setpoint:"); Serial.print(current_setpoint);   Serial.print(",");

    pid_control();

    if ( (stage == 1 )&& (current_temp > SETPOINT_1 - 0.8)) { //  Serial.println("SETPOINT GREATER THAN 95");
        maintain_temp(CONST_S1);
        prev_setpoint = SETPOINT_1;
        current_setpoint = SETPOINT_2;
        mode = 1;   stage++;  // next stage - cooling
    }
    else if ( (stage == 2 )&& (current_temp < SETPOINT_2 + 0.5)) {  // Serial.println("SETPOINT LESSER THAN 63");
        maintain_temp(CONST_S2);
        prev_setpoint = SETPOINT_2;
        current_setpoint = SETPOINT_3;
        mode = 0;   stage++; // next stage - heating
    }
    else if ((stage == 3) && (current_temp > SETPOINT_3 - 0.5)){    //  Serial.println("SETPOINT GREATER THAN 72.5");        
        maintain_temp(CONST_S3);
        prev_setpoint = SETPOINT_3;
        current_setpoint = SETPOINT_1;
        mode = 0;    stage = 1; // next stage - heating
    }
    delay(10);
}

void pid(float current_setpoint, float current_temp, int mode){
    //  Serial.print("call pid");
    float error = current_setpoint - current_temp;
    float current_time = millis() / 1000.0;
    float dt = current_time - prev_time;

    i_e += error * dt;
    float de = (error - prev_error) / dt;

    if (mode == 0){
      output = KP * error + KI * i_e + KD * de;
      output = output/KP;
    }
    else{
      output = KP_cool * error + KI_cool * i_e + KD_cool * de;
      output = output/(KP_cool*5);
    }
    
    prev_error = error;    prev_time = current_time;
    
//    Serial.print("output:"); Serial.print(output);   Serial.print(",");
//    Serial.print("i_e:"); Serial.print(i_e);   Serial.print(",");
}

void print_time(unsigned long seconds ){
    unsigned long minutes = seconds / 60;
    unsigned long hours = minutes / 60;

    // Format the timestamp
    String timestamp = String(hours) + ":" + String(minutes % 60) + ":" + String(seconds % 60);

    Serial.print("Time:");
    Serial.print(timestamp);
    Serial.print(",");
}

void print_thermo_fault(uint8_t fault){
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
}
