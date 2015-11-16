"""
Filter for GwtS recordings. Checks to make sure all commands are correct and
splits commands into different files.
    - List with timestamps of only 9X commands.
    - List with timestamps of only 55 commands.
    - List with timestamps of both 9X and 55 commands.
    - List with no timestamps of only unique 9X commands, omitting delays and some 0C codes.
    - List with no timestamps of only unique 55 commands.
    - List of commands that didn't pass 55 or 9X CRC, likely from transmission errors or collisions.

Version: 2015-09-22

Use:
    python Filter.py input_file_name #of_timestamp_pieces

Example:
    python Filter.py 2015-08-30.txt 2

    Where 2015-08-30.txt is the name of the file to be processed and 2 is the number
    of pieces where time codes occur (in this case it's 2, 2015-08-30 15:34:20.250)
    before the actual commands occur.


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
import sys

import GwtSUtils


def split_input(file, time_code_len):
    """
    Splits file input into three lists, the 9x commands, the 55 commands, and a list of error commands.
    :param file String Filename
    :param time_code_len Number of timestamp blocks before the actual code.
    :return: [][]String Three lists of strings that contain the 9X commands, and the 55 commands, and a list of error
    commands.
    """
    command9 = list()
    command5 = list()
    recording_errors = list()
    with open(file, 'r') as file_input:
        for file_line in file_input:
            file_line = file_line.rstrip().split()
            if not check_command(file_line[time_code_len:]):
                recording_errors.append(file_line)
                continue
            if file_line[time_code_len][0] == '9':
                command9.append(file_line)
            if file_line[time_code_len][0] == '5':
                command5.append(file_line)
    return command9, command5, recording_errors


def check_command(command):
    """ Checks 9X and 55 commands to make sure they're correct.
    :param command []String 9X or 55 command
    :return Boolean True if it's a correct command and False if not.
    """
    if len(command) < 5:
        return False
    if command[0][0] == '9':
        calculated_command = GwtSUtils.int_array_to_hex_str(GwtSUtils.encode9x(' '.join(command[1:-1])))
    elif command[0][0] == '5':
        calculated_command = GwtSUtils.int_array_to_hex_str(GwtSUtils.encode55(' '.join(command[2:-1])))
    else:
        return False
    if calculated_command == ' '.join(command):
        return True
    return False


def remove_repeats55(commands, time_stamp_len):
    """ Removes repeat of 55 commands in a list.
    :param commands []String List of 55 commands
    :return []String List of 55 commands with repeats removed.
    """
    return set(command for command in [' '.join(command[time_stamp_len:]) for command in commands])


def remove_repeats9x(commands, time_stamp_len):
    """ Removes repeat of 9X commands in a list. Also removes repeats of commands with different delays.
    :param commands []String List of 9X commands
    :return []String List of 9X commands with repeats removed.
    """
    has_delays = set()
    return_set = set()
    for line_9x in [command for command in [' '.join(command[time_stamp_len:]) for command in commands]]:
        if line_9x[3] == 'F' or line_9x[3:5] == '20':
            has_delays.add(line_9x[5:-3])
        elif line_9x[3:5] == '0C':
            has_delays.add(line_9x[9:-3])
        else:
            return_set.add(line_9x)
    for line_9x in has_delays:
        return_set.add(encode9x(line_9x))
    return return_set


def encode9x(command):
    """ Encodes a 9X command with correct 9X length code and CRC.
    :param command String 9X command without
    :return String Encoded 9X command
    """
    return GwtSUtils.int_array_to_hex_str(GwtSUtils.encode9x(command))


def save_list(command_list, type_of_command, file_name, file_name_tail_to_remove=4):
    with open(file_name[:-file_name_tail_to_remove] + '_' + type_of_command + '.txt', 'w') as output:
        for line in sorted(command_list):
            if type(line) is str:
                output.write(line + '\n')
            else:
                output.write(' '.join(line) + '\n')


def main(file_name, time_code_len):
    commands9, commands55, errors = split_input(file_name, time_code_len)
    save_list(commands9 + commands55, '9X_And_55', file_name)
    save_list(commands9, '9X', file_name)
    save_list(commands55, '55', file_name)
    commands55 = remove_repeats55(commands55, time_code_len)
    save_list(commands55, '55_No_Repeats', file_name)
    commands9 = remove_repeats9x(commands9, time_code_len)
    save_list(commands9, '9X_No_Repeats', file_name)
    save_list(errors, 'Errors', file_name)
    # Uncomment below to show lines that didn't pass any kind of CRC in order of how frequent they appeared.
    # I typically keep it low (around 10) to pick up any possible commands we're not scanning for normally
    # but are broadcast multiple times but it's usually just command collisions and transmission errors.
    '''
    from collections import Counter
    num_of_items_to_show = 10
    for item in Counter([' '.join(item[1:]) for item in errors]).most_common(num_of_items_to_show):
        print(item)
    '''

if __name__ == '__main__':
    main(sys.argv[1], int(sys.argv[2]))
