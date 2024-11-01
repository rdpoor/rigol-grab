"""
DHO924-grab.py: capture Rigol DHO924 Oscilloscope display as a .png file

rdpoor@gmail.com - October 2024
"""

import argparse
import os
import platform
import subprocess
import sys
import pyvisa

import pyvisa

# DHO924_VID_PID = f'0x{DHO924_VID:04x}::0x{DHO924_PID:04x}'.upper()
# resource_manager = pyvisa.ResourceManager()
# resources = resource_manager.list_resources()
# candidates = [r for r in resources if DHO924_VID_PID in r.upper()]
# if len(candidates) == 0:
#     print(f'Could not find DHO924 - is it connected via USB?')
# elif len(candidates) > 1:
#     print(f'Found {len(candidates)} DHO924s: TODO: User selection')
# else:
#     # found exactly one
#     print(f'Found {candidates[0]}, type={type(candidates[0])}')

class Dho924:

    VID = 0x1AB1
    PID = 0x044C

    def __init__(self, options):
        self.options = options
        self.resource_manager = pyvisa.ResourceManager()

    def error_quit(self, message):
        sys.exit(f'{message}: ...quitting')

    def verbose_print(self, *args):
        if (self.options.verbose):
            print(*args, flush=True)

    def find_instrument_name(self, target_name):
        """
        Return a string, suitable for passing to resource_mgr.open_resource(),
        or None if no Rigol DHO924 can be found on the USB bus.
        """
        resources = self.resource_manager.list_resources()
        candidates = [r for r in resources if target_name in r.upper()]
        if len(candidates) == 0:
            print(f'Could not find DHO924 - is it connected via USB?')
            return None
        elif len(candidates) > 1:
            print(f'Found multiple DHO924s.  Please select one with the --name argument')
            for c in candidates:
                print(f'    {c}')
            return None
        else:
            # found exactly one
            return candidates[0]

    def open_instrument(self, instrument_name):
        if instrument_name is None:
            error_out(f'No valid instrument found, quitting')
        else:
            instrument = self.resource_manager.open_resource(
                instrument_name,
                write_termination='\n',
                read_termination='\n')
            return instrument

    def grab_screen(self, instrument, filename):
        buf = instrument.query_binary_values(
            ':DISP:DATA? PNG',
            datatype='B')
        with open(filename, 'wb') as f:
            self.verbose_print(
                f'Captured screen, writing {len(buf)} bytes to {filename}')
            f.write(bytearray(buf))

    def grab(self):
        """
        If target name is given, search for target_name as a substring of the
        full instrument_name.  Otherwise, use VID::PID as the target_name

        For example, if the Utility screen on your scope lists:
           HostName    RIGOL_DHO9A2544014
        you can pass 'DHO9A2544014' as the target string.

        """
        if self.options.name is None:
            target_name = f'0x{self.VID:04x}::0x{self.PID:04x}'.upper()
        else:
            target_name = self.options.name.upper()
        self.verbose_print(f'Searching for instrument with {target_name} in name')

        instrument_name = self.find_instrument_name(target_name)
        if instrument_name is None:
            self.error_quit(f'Cannot find DHO924 matching {target_name}')
        self.verbose_print(f'Opening instrument {instrument_name}')

        instrument = self.open_instrument(instrument_name)
        if instrument is None:
            self.error_quit(f'Cannot open instrument named {instrument_name}')

        if self.options.filename is None:
            filename = 'rigol.png'
        else:
            filename = self.options.filename
        self.verbose_print(f'Writing screen capture to {filename}')

        try:
            # Allow up to 10 seconds to complete read
            instrument.timeout = 10000
            self.grab_screen(instrument, filename)
            self.verbose_print(f'Successfully captured screen to {filename}')
        finally:
            # Assure that the instrument is always closed
            instrument.close()

        if self.options.auto_view:
            self.view_file(filename)

    @classmethod
    def view_file(cls, filename):
        """
        Open filename with the native system viewer
        """
        if platform.system() == 'Darwin':       # macOS
            subprocess.call(('open', filename))
        elif platform.system() == 'Windows':    # Windows
            os.startfile(filename)
        else:                                   # linux variants
            subprocess.call(('xdg-open', filename))

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Rigol DHO924 Screen Grabber')
    parser.add_argument('-n', '--name', default=None,
                        help='instrument serial number')
    parser.add_argument('-f', '--filename', default='rigol.png',
                        help='name of output file')
    parser.add_argument('-a', '--auto_view', action='store_true',
                        help='automatically view output file')
    parser.add_argument('-v', '--verbose', action='store_true',
                        help='print additional output')
    # parser.add_argument('-p', '--port',
    #                     help='instrument IP address')
    opts = parser.parse_args()

    Dho924(opts).grab()
