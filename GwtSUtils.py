"""
GwtS Utilities for calculating 9X commands, 55 commands, IR timings, and sequencing of commands.


Version: 2015-09-06

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.

"""

# Delays seem to vary. Commonly only up to FB but some go up to FF. I think it
# might have something to do with command length and avoiding collisions but
# I'm keeping it to a safe FB for now. Switch to the larger set if you'd like.
#delays = ("FF", "FE", "FD", "FC", "FB", "FA", "F9", "F8", "F7", "F6", "F5", "F4", "F3", "F2", "F1", "20")
delays = ("FB", "FA", "F9", "F8", "F7", "F6", "F5", "F4", "F3", "F2", "F1", "20")

def encode9x(values):
    """ Encodes a command with the appropriate 9X length code and CRC
    :param values: int[] Commands in decimal format OR str[] commands in hex format OR a single str of commands in hex
    :return: int[] 9x encoded commands in decimal format
    """
    if type(values) is str:
        values = values.split()  # Split user input into str[]
    if type(values) is list:
        try:
            if type(values[0]) is str:
                values = [int(value, 16) for value in values]  # Convert str[] with hex values to int[]
        except:
            pass
    values.insert(0, len(values) + 143)
    values.append(crc_9x(values))
    return values


def crc_9x(values):
    """ Calculate CRC for 9X commands
    :param values: int[] Commands, with accompanying 9x length code, written in decimal format.
    :return: int[] CRC value for 9X commands
    """
    crc = 0
    for value in values:
        crc ^= value
        for num in range(8):
            crc = (crc >> 1 ^ 0x8C if crc & 1 else crc >> 1)
    return crc


def encode55(values):
    ''' Encodes a command with 55 AA code and CRC.
    :param values: int[] Commands in decimal format
    :return: int[] 55 encoded commands in decimal format
    '''
    values = [int(value, 16) for value in values.split()]
    values.append(crc55(values))
    return [0x55, 0xAA] + values


def crc55(values):
    ''' Calculates CRC for 55 commands
    :param values: int[] command without 55 AA
    :return: int[] CRC value for 55 commands
    '''
    return sum(values) % 256


def encode_ir(values, message_width=417):
    """ Encodes a complete command into IR compatible on/off time lengths.
    :param values: int[] Command to be encoded for IR
    :param message_width: int Optional variable to change the message width.
    :return: int[] Encoded array of values for IR transmission.
    """
    return_list = []
    for value in values:
        # Commands always have initial on start bit
        high = False
        return_list.append(message_width)
        # Cycle through bits for on/off bits and add/flip as needed.
        for count in range(8):
            if value >> count & 1 == high:
                return_list[-1] += message_width
            else:
                return_list.append(message_width)
                high = not high
        # End with off bit
        if high:
            return_list[-1] += message_width
        else:
            return_list.append(message_width)
    return return_list


def int_array_to_hex_str(values):
    """ Converts int[] to hex string
    :param values: int[] Values to convert to hex string
    :return: String of converted values
    """
    return ' '.join([hex(value).upper()[2:].zfill(2) for value in values])


def ir_fancy_format(values):
    """ Formats IR on/off lengths nicely
    :param values: int[] of on/off IR lengths
    :return: String of nicely formatted IR lengths.
    """
    return '{'+', '.join(str(value) for value in values)+'}'


def generate_delays(command):
    """ Generates timing and calculates delays of a command for a show.
    :param command: str[] of time offset and commands
    :return: dict() of using their timings as keys and the 9x encoded commands as content.
    """
    delay_dict = dict()
    for index, delay in enumerate(delays):
        # Calculate time advances
        time = (int(command[0])-(len(delays)-index)*100)
        if time < 0:  # If the time advance goes before 0 (start of show), omit it.
                continue
        # Put together delay code and command
        command_list = [delay]
        command_list.extend(command[1:])
        # Add to dict the timing and encode the command for 9x with appropriate delays.
        delay_dict[hex(time)[2:].upper().zfill(8)] = [hex(value)[2:].upper().zfill(2) for value in encode9x(command_list)]
    return delay_dict
