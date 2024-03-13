cmake_minimum_required(VERSION 3.12)

set(PICO_BOARD pico_w)

#Include build functions for Pico SDK
include(pico_sdk_import.cmake)

project(OLED C CXX ASM)
set(CMAKE_C_STANDARD 11)
set(CMAKE_CXX_STANDARD 17)
#create a pico-sdk subdirectory in our project for the libraries
pico_sdk_init()

add_executable(OLED
        oled.c
        )

#Create map/bin/hex/uf2 files
pico_add_extra_outputs(OLED)

#Link to pico_stdlib (gpio, time, etc, functions)
target_link_libraries(OLED
 pico_stdlib
 hardware_i2c
)

