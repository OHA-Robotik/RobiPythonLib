# Robi State Report Communication Protocol (RSRCP) Version 1.0.0

## Introduction

The Robi State Report Communication Protocol (RSRCP) is a simple protocol to communicate the state of a Robi robot to
a connected device.

## Protocol

The protocol is a read-only protocol, meaning that the connected device can only read the state of the robot and no
data can be sent to the robot.

### Data communicated at connection (Handshake)

When a connection is established, the robot sends the following information:

- An 8-bit SOP (Start of Packet) byte with the value `0x7E`.
- The version of the protocol as an 8-bit unsigned integer.
- Milliseconds delta time (MSDT): The time interval between every sent state in milliseconds as a 16-bit unsigned
  integer.
- An 8-bit EOP (End of Packet) byte with the value `0x7F`.

#### Version

The following versions are defined:

| Version | Byte Representation |
|---------|---------------------|
| 1.0.0   | 0x1                 |

### Data communicated with every sent state (Frame)

A frame communicates the following status information:

- Voltages
- Motor states
- Gyroscope state
- Accelerometer state
- Laser sensor state
- Infrared sensors state
- Poti state
- Button states
- LED states
- Piezo state
- LCD display state

Additionally, the following information is communicated:

- Frame ID: A 24-bit unsigned integer that is incremented with every sent frame.
- Enabled feature set (EFS): Which features are enabled. This means that the robot can be configured to only send the
  state of a subset of the above-mentioned information.

#### Frame ID

The frame ID is a 24-bit unsigned integer that is incremented with every sent frame.

#### Enabled Feature Set (EFS)

The enabled feature set is communicated as an 16-bit unsigned integer. Each bit represents a feature:

| Bit Position | Feature                |
|--------------|------------------------|
| 0 (MSB)      | Voltages               |
| 1            | Motor States           |
| 2            | Gyroscope State        |
| 3            | Accelerometer State    |
| 4            | Laser Sensor State     |
| 5            | Infrared Sensors State |
| 6            | Poti State             |
| 7            | Button States          |
| 8            | LED States             |
| 9            | Piezo State            |
| 10           | LCD State              |

A 0 means that the feature is disabled and a 1 means that the feature is enabled.
If a feature is disabled, the corresponding state is not communicated. All bits of the feature will not be present in
the frame.

#### Voltages

[Yet to be defined]

#### Motor States

The state of a single motor is communicated as a 16-bit signed fixed-point number.  
Minimum value: -300.0  
Maximum value: 300.0  
The value represents the speed of the motor in rad/s. Negative values represent reverse rotation.  
First comes the left motor and then the right motor.

```python
import struct

def encode_fixed_point(value):
    if not -300 <= value <= 300:
        raise ValueError("Value out of range!")
    fixed_value = int(value * 100)  # Scale and convert to integer
    return struct.pack('>h', fixed_value)  # Store as 2 bytes (big-endian signed short)

def decode_fixed_point(byte_data):
    fixed_value = struct.unpack('>h', byte_data)[0]  # Retrieve 2-byte signed int
    return fixed_value / 100  # Convert back to float
```

#### Gyroscope State

[Yet to be defined]

#### Accelerometer State

[Yet to be defined]

#### Laser Sensor State

[Yet to be defined]

#### Infrared Sensors State

[Yet to be defined]

#### Poti State

The state of the poti is communicated 8-bit unsigned integer.  
0 represents the poti in the lowest position and 255 represents the poti in the highest position.
Turning the poti clockwise increases the value and turning the poti counterclockwise decreases the value.

#### Button States

A single button state is represented by a single bit. The bit is set to 1 if the button is pressed and 0 if the button
is not pressed.

The state of all buttons is represented by an 8-bit value:

| Bit Position | Represented Button |
|--------------|--------------------|
| 0 (MSB)      | Center Button      |
| 1            | Left Button        |
| 2            | Right Button       |
| 3            | Top Button         |
| 4            | Bottom Button      |
| 5            | (Unused)           |
| 6            | (Unused)           |
| 7 (LSB)      | (Unused)           |

#### LED States

The state of a single LED is represented by a single bit. The bit is set to 1 if the LED is on and 0 if the LED is off.

The state of all LEDs is represented by an 8-bit value:

| Bit Position | Represented LED       |
|--------------|-----------------------|
| 0 (MSB)      | Front left blinker    |
| 1            | Front left headlight  |
| 2            | Front right headlight |
| 3            | Front right blinker   |
| 4            | Back right blinker    |
| 5            | Back right taillight  |
| 6            | Back left taillight   |
| 7 (LSB)      | Back left blinker     |

#### Piezo State

The state of the piezo consists of two values:
A leading bit that is set to 1 if the piezo is audible and 0 if the piezo is silent.
This is followed by a 15-bit value that represents the frequency of the piezo in Hertz.

0: The piezo is vibrating at 0 Hz and is therefore silent.  
20000: The piezo is vibrating at 20 kHz.

#### LCD State

[Yet to be defined]

### Frame Message Format

A frame consists of the all the above-mentioned states and information. The frame is structured as follows:

- First comes the SOP byte.
- After that, the frame ID is placed.  
- Next follows the EFS value.  
- After that, the frame is filled with the states of the enabled features in the order they are defined above.  
- At the end of the frame, an 8-bit EOP (End of Packet) byte with the value `0x7F` is placed.

Note: If a feature is disabled, all bits of the feature will not be present in the frame.

## Changelog

- 2025-02-22: Version 1.0.0 released.
