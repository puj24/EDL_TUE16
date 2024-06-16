#include <stdio.h>
#include <math.h>
#include "pico/stdlib.h"
#include "hardware/gpio.h"
#include "hardware/adc.h"
#include "hardware/pwm.h"
#include "hardware/clocks.h"
#include "time.h"
#include "constants.h"


float integral_error = 0.0;
float prev_error = 0.0;
float prev_time = 0.0;
float pid_output;

float ideal_temp, current_temp;
float curr_sec;


float read_temperature(){
    float T = adc_read()*3.3f/(1<<12);
    T = T * 100;
    return T;
}

void print_time(unsigned long seconds){
    unsigned long minutes = seconds / 60;
    unsigned long hours = minutes / 60;

    printf("Time:%lu:%lu:%lu, ", hours, (minutes%60), (seconds%60));
}

float absolute(float value){
    if(value < 0){
        value = -value;
    }
    return value;
}

void peltier_control(float duty_cycle) {

    duty_cycle = fminf(fmaxf(duty_cycle, -1.0), 1.0);
    printf("Duty_cycle:%0.2f\n", duty_cycle);

    int pwm_value = absolute(duty_cycle) * PWM_RANGE;

    if(duty_cycle >= 0){
        pwm_set_gpio_level(PELTIER_PIN1, pwm_value);
        pwm_set_gpio_level(PELTIER_PIN2, PWM_RANGE - pwm_value);
    }
    else{
        pwm_set_gpio_level(PELTIER_PIN1, PWM_RANGE - pwm_value);
        pwm_set_gpio_level(PELTIER_PIN2, pwm_value);
    }
   
}

void pid(float current_setpoint, float current_temp, int mode) {

    float current_time = (float)time_us_64() / 1000000.0;
    float dt = current_time - prev_time;
    
    float error = current_setpoint - current_temp;
    integral_error += error * dt;
    float diff_error = (error - prev_error) / dt;

    if(mode == 0){
        pid_output = KP * error + KI * integral_error + KD * diff_error;
        pid_output = pid_output/ KP;
    }
    else{
        pid_output = KP_cool * error + KI_cool * integral_error + KD_cool * diff_error;
        pid_output = pid_output/ (KP_cool*5);
    }

    printf("error:%0.2f, diff_error:%0.2f, i_error:%0.2f, pid_output:%0.2f, ", error, diff_error, integral_error, pid_output);

    prev_error = error;
    prev_time = current_time;

}

void ramp_control(float current_setpoint, int mode){

    if(current_setpoint > current_temp){
        if((current_setpoint - current_temp) > 1){
            pid_output = 1;
            prev_error = current_setpoint - current_temp;
            prev_time = (float)time_us_64() / 1000000.0;
        }
        else{
            pid(current_setpoint, current_temp, mode);
        }
    }
    else{
        if((current_temp - current_setpoint) > 5){
            pid_output = 0;
            prev_error = current_setpoint - current_temp;
            prev_time = (float)time_us_64() / 1000000.0;
        }
        else{
            pid(current_setpoint, current_temp, mode);
        }
    }

    peltier_control(pid_output);
}

void maintain_const_temperature(float current_setpoint, float duration, int mode){
    float prev_sec =  (float)time_us_64() / 1000000.0;
    curr_sec =  (float)time_us_64() / 1000000.0;

    while((curr_sec - prev_sec) < duration){
        current_temp = read_temperature();

        print_time(curr_sec);
        printf("Ideal:%0.2f, Setpoint:%0.2f, Temperature:%0.2f, ", ideal_temp, current_setpoint, current_temp);

        pid(current_setpoint, current_temp, mode);
        peltier_control(pid_output);

        curr_sec =  (float)time_us_64() / 1000000.0;
        sleep_ms(10);
    }
    integral_error = 0.0;
}


int main() {
    stdio_init_all();
    adc_init();

    adc_gpio_init(TEMPERATURE_SENSOR_PIN);
    adc_select_input(1);        // Select ADC input 0 (GPIO26)
   
    gpio_set_function(PELTIER_PIN1, GPIO_FUNC_PWM);
    gpio_set_function(PELTIER_PIN2, GPIO_FUNC_PWM);

    pwm_config config = pwm_get_default_config();
    pwm_config_set_clkdiv(&config, 4.f); // "resolution"

    uint slice_num = pwm_gpio_to_slice_num(PELTIER_PIN1);
    pwm_init(slice_num, &config, true);
    slice_num = pwm_gpio_to_slice_num(PELTIER_PIN2); 
    pwm_init(slice_num, &config, true);

    float current_setpoint = SETPOINT_1;
    float prev_setpoint = read_temperature();   // initial temperature
    float mode = 0;     // heating or cooling mode
    float stage = 1;
    curr_sec = (float)time_us_64() / 1000000.0;

    // Main loop
    while (1) {

        float global_sec = (float)time_us_64() / 1000000.0;
        print_time(global_sec);

        if(mode == 0){
            ideal_temp = prev_setpoint + (global_sec - curr_sec)*RAMP_RATE;
            if(ideal_temp > current_setpoint) ideal_temp = current_setpoint;
        }
        else{
            ideal_temp = prev_setpoint - (global_sec - curr_sec)*RAMP_RATE;
            if(ideal_temp < current_setpoint) ideal_temp = current_setpoint;
        }

        current_temp = read_temperature();

        printf("Ideal:%0.2f, Setpoint:%0.2f, Temperature:%0.2f, ", ideal_temp, current_setpoint, current_temp);
    
        ramp_control(current_setpoint, mode);

        //stage control
        if ((stage == 1)&& (current_temp > SETPOINT_1 - marginal_temp_error)){
            maintain_const_temperature(SETPOINT_1, CONST_S1, mode);
            prev_setpoint = SETPOINT_1;
            current_setpoint = SETPOINT_2;
            stage++;    mode = 1;       // next stage - cooling
        }
        else if((stage == 2) && (current_temp < SETPOINT_2 + marginal_temp_error)){
            maintain_const_temperature(SETPOINT_2, CONST_S2, mode);
            prev_setpoint = SETPOINT_2;
            current_setpoint = SETPOINT_3;
            stage++;    mode = 0;       // next stage - heating
        }
        else if((stage == 3) && (current_temp > SETPOINT_3 - marginal_temp_error)){
            maintain_const_temperature(SETPOINT_3, CONST_S3, mode);
            prev_setpoint = SETPOINT_3;
            current_setpoint = SETPOINT_1;
            stage = 1;  mode = 0;       // next stage - heating
        }

        sleep_ms(SAMPLE_INTERVAL_MS);
    }

    return 0;
}
