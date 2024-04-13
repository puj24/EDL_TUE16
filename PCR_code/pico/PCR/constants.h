
// PID constants for Heating
#define KP 1  // Proportional gain
#define KI 0.02 // Integral gain
#define KD 0.008 // Derivative gain

// PID constants for Cooling
#define KP_cool 1  
#define KI_cool 0.01 
#define KD_cool 0.7 

#define PELTIER_PIN1 14 // Replace with the GPIO pin connected to IN1 of H-bridge
#define PELTIER_PIN2 15  // Replace with the GPIO pin connected to IN2 of H-bridge
#define FAN_PIN 10       // Replace with the GPIO pin connected to the fan
#define TEMPERATURE_SENSOR_PIN 27  // Replace with the GPIO pin connected to the temperature sensor

// setpoints of thermal profile
#define SETPOINT_1 95.5
#define SETPOINT_2 63
#define SETPOINT_3 72.5

#define marginal_temp_error 1

// constant temperature of the stages
#define  CONST_S1 62
#define CONST_S2 75
#define CONST_S3 43
#define RAMP_RATE 2  

#define PWM_RANGE 65535    // PWM range for Raspberry Pi Pico (16-bit)

#define SAMPLE_INTERVAL_MS 10  // Sampling interval in milliseconds