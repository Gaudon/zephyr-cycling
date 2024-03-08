# What is "Zephyr"?

The codename Zephyr Cycling project is an attempt to turn a "dumb" hardware switched 120V fan into a smart cycling fan with minimal (albeit invasive) electrical changes. This project will enable compatible fans to connect to a heart rate monitor to auto scale with user effort while remaining in fan speeds/modes supported by your device, while also enabling the user to manually switch the fan through button presses.

## Overview

While the features and functionality are somewhat straight forward, here's a short overview.

[Video Overview: How it Works](https://youtu.be/IWAn6BZootY)

### Can I see it in action?

The production value of these videos is quite low 😂. But here's some initial testing of the unit running for my own purposes. I did complete the first ride using it on March 7th, 2024 and it worked a treat!

[Treadmill Example](https://youtu.be/G-9pirc2J4w)

[Cycling Example](https://youtube.com/shorts/M7jgy0t9K8Y?feature=share)

## How was this built?

### Hardware

This project was built using 2 [Raspberry Pi PicoW](https://www.raspberrypi.com/documentation/microcontrollers/raspberry-pi-pico.html) microcontrollers, a set of 120V relays, buttons and 5mm LEDs.

The components used in this MVP came from a Canadian supplier called [PiShop](https://www.pishop.ca). 

Component | Quantity | Description | Unit Price (CAD) |
|:-:|:-:|:-:|:-:|
[PicoW](https://www.pishop.ca/product/raspberry-pi-pico-wh-pre-soldered-headers/) | 2 | Microcontrollers for the project. | ~$9
[Breadboard Wiring Kit](https://www.pishop.ca/product/breadboard-wiring-kit/) | 1 | Misc length wires for building out the breadboard. | ~$8
[Breadboards](https://www.pishop.ca/product/half-size-400-pin-electronics-diy-breadboard/) | 1 | Breadboards to build the project on. | ~$8
[Component Kit](https://www.pishop.ca/product/component-kit-for-arduino/) | 1 | Misc components (buttons, switches, resistors) for the project. | ~$8
[8 Channel Relay Module](https://www.pishop.ca/product/8-channel-relay-module/) | 1 | Allows the low voltage microcontrollers to drive and direct the flow of higher voltage (120v) load lines to the fan. | ~$10


### Software

This project uses Micropython to implement the 'smart' functionality. It depends on several other incredible projects/works from other developers to help make this possible.

[MicroPython](https://github.com/micropython/micropython) | [MicroDot](https://github.com/miguelgrinberg/microdot) | [CSC_BLE_Bridge](https://github.com/starryalley/CSC_BLE_Bridge) (Debug Tool)

## Future Plans?

I'd love to be able to put some time into learning KiCAD (or similar software) to provision a schematic or PCB to make adapting this project for DIYers a little less cumbersome. I have limited experience in EDA tools but it's on my list of things I'd like to get more familiar with!
