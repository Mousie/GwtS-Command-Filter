# GwtS Recording Filter

Filter for GwtS recordings. Checks to make sure all commands are correct and
splits commands into different files.

    - List with timestamps of only 9X commands.
    - List with timestamps of only 55 commands.
    - List with timestamps of both 9X and 55 commands.
    - List with no timestamps of only unique 9X commands, ommiting delays and some 0C codes.
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
