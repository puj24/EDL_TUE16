#include <stdio.h>
#include <math.h>
#include "pico/stdlib.h"
#include "hardware/gpio.h"
#include "hardware/adc.h"
#include "hardware/pwm.h"
#include "time.h"
#include <unistd.h>

#define PELTIER_PIN1 10  // Replace with the GPIO pin connected to IN1 of H-bridge
#define PELTIER_PIN2 11  // Replace with the GPIO pin connected to IN2 of H-bridge
#define FAN_PIN 12       // Replace with the GPIO pin connected to the fan
#define TEMPERATURE_SENSOR_PIN 26  // Replace with the GPIO pin connected to the temperature sensor

// Thermistor constants factor of 1e-3
#define Ath 3.9083
#define Bth -5.775e-4

#define SETPOINT_1 95.5
#define SETPOINT_2 63
#define SETPOINT_3 72.5
#define RAMP_RATE 2  // Ramp rate in degrees Celsius per second

#define PWM_RANGE 65535    // PWM range for Raspberry Pi Pico (16-bit)

#define SAMPLE_INTERVAL_MS 1000  // Sampling interval in milliseconds

#define KP 0.1  // Proportional gain
#define KI 0.01 // Integral gain
#define KD 0.05 // Derivative gain

float current_setpoint = SETPOINT_1;  // Initial setpoint
float integral = 0.0;
float prev_error = 0.0;
float prev_time = 0.0;

// File to sore temperature vs. time data
FILE *fp;


float read_temperature() {
    float Vth = adc_read()/ (1 << 12);
    float Rth = 10*(3.3/Vth - 1);

    // Temperature sensor BT^2 + AT + 1 = Rt/1k
    float T;
    T = (-Ath + sqrt(Ath*Ath - 4*Bth*(1-Rth)))/(2*Bth);
    return T;
}

// Function to control Peltier module using H-bridge
void control_peltier(float duty_cycle) {
    // Ensure duty cycle is within valid range
    duty_cycle = fminf(fmaxf(duty_cycle, 0.0), 1.0);

    // Convert duty cycle to PWM value
    uint16_t pwm_value = (uint16_t)(duty_cycle * PWM_RANGE);

    // Set PWM duty cycle for Peltier pin1
    pwm_set_gpio_level(PELTIER_PIN1, pwm_value);

    // Set inverse of PWM duty cycle for Peltier pin2
    pwm_set_gpio_level(PELTIER_PIN2, PWM_RANGE - pwm_value);
}

// Function to control fan
void control_fan(bool enable) {
    // Enable or disable the fan based on the input
    gpio_put(FAN_PIN, enable ? 1 : 0);
}

// PID control algorithm
void pid_control() {
    float current_temp = read_temperature();
    float error = current_setpoint - current_temp;

    // Calculate time since last iteration
    float current_time = (float)time_us_64() / 1000000.0;
    float dt = current_time - prev_time;

    // Calculate integral and derivative terms
    integral += error * dt;
    float derivative = (error - prev_error) / dt;

    // Calculate PID output
    float output = KP * error + KI * integral + KD * derivative;

    // Update previous error and time
    prev_error = error;
    prev_time = current_time;

    // Adjust setpoint based on ramp rate
    if (error > 0) {
        current_setpoint -= RAMP_RATE * dt;
    } else {
        current_setpoint += RAMP_RATE * dt;
    }

    // Control Peltier module and fan based on PID output
    if (current_setpoint == SETPOINT_1) {
        control_peltier(output);
        control_fan(false);  // Disable fan
    } else if (current_setpoint == SETPOINT_2) {
        control_peltier(output);
        control_fan(true);  // Disable fan
    } else if (current_setpoint == SETPOINT_3) {
        control_peltier(output);
        control_fan(false);   // Enable fan
    }

    // Write temperature vs. time data to file
    fprintf(fp, "%.2f,%.2f\n", current_time, current_temp);
    fflush(fp); // Flush the buffer to ensure data is written immediately
}

int main() {
    stdio_init_all();
    adc_init();

    adc_gpio_init(TEMPERATURE_SENSOR_PIN);
    adc_select_input(0);        // Select ADC input 0 (GPIO26)

    // Open file to store temperature vs. time data
    fp = fopen("temperature_vs_time.csv", "w");
    if (fp == NULL) {
        printf("Error opening file!\n");
        return 1;
    }

    gpio_set_function(PELTIER_PIN1, GPIO_FUNC_PWM);
    gpio_set_function(PELTIER_PIN2, GPIO_FUNC_PWM);
    
    // Initialize GPIO pins
    gpio_init(FAN_PIN);
    gpio_set_dir(FAN_PIN, GPIO_OUT);

    // Write header to file
    fprintf(fp, "Time (s),Temperature (C)\n");

    // Main loop
    while (true) {
        pid_control();
        sleep_ms(SAMPLE_INTERVAL_MS);
        if (current_setpoint < SETPOINT_3) {
            break;  // End of PCR cycle
        }
    }

    // Close file
    fclose(fp);

    return 0;
}
