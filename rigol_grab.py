##
# rigol_grab: save Rigol Oscilloscope display as a .png file

import argparse
import os
import platform
import subprocess
import sys
import pyvisa
import time

class RigolGrab(object):

    VID = 0x1AB1
    PID = 0x04CE

    def __init__(self, verbose=False):
        self._verbose = verbose
        self._rigol = None
        self._resource_manager = pyvisa.ResourceManager()

    def grab(self, filename='rigol.png', auto_view=True):
        # self.rigol().write(':STOP')
        self.verbose_print('Identification: ' + self.rigol().query('*IDN?'))
        buf = self.rigol().query_binary_values(':DISP:DATA? ON,0,PNG', datatype='B')
        with open(filename, 'wb') as f:
            self.verbose_print('Capturing screen to', filename)
            f.write(bytearray(buf))
        if auto_view:
            self.open_file_with_system_viewer(filename)

    def rigol(self):
        '''
        Find and open the instrument with matching VID_PID
        '''
        if self._rigol == None:
            if(opts.port):
                inst = 'TCPIP0::{}::INSTR'
                name = inst.format(opts.port)
            else:
                name = self.find_rigol()
                if name == None: self.err_out("Could not find Rigol. Check USB?")
            self.verbose_print('Opening', name)
            try:
                self._rigol = self._resource_manager.open_resource(name, write_termination='\n', read_termination='\n')
                
                '''
                Following some advice from:
                    https://github.com/pyvisa/pyvisa/issues/481
                this seems to be the maximum chunk size Rigol (reliably?) 
                supports over USB.
                '''
                self._rigol.chunk_size = 64 - 12
            except:
                self.err_out('Could not open oscilloscope')
        return self._rigol

    def find_rigol(self):
        # Note: VISA regular expressions are case insensitive
        visa_match_expression = f'?*::(0x{self.VID:0{4}x}|{self.VID})::(0x{self.PID:0{4}x}|{self.PID})::?*::INSTR'
        names = self._resource_manager.list_resources(visa_match_expression)
        return names[0] if names else None

    def verbose_print(self, *args):
        if (self._verbose): print(*args)

    def err_out(self, message):
        sys.exit(message + '...quitting')

    def close(self):
        self._rigol.close()
        self._resource_manager.close()

    @classmethod
    def open_file_with_system_viewer(cls, filepath):
        if platform.system() == 'Darwin':       # macOS
            subprocess.call(('open', filepath))
        elif platform.system() == 'Windows':    # Windows
            os.startfile(filepath)
        else:                                   # linux variants
            subprocess.call(('xdg-open', filepath))

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Rigol Screen Grabber')
    parser.add_argument('-f', '--filename', default='rigol.png',
                        help='name of output file')
    parser.add_argument('-a', '--auto_view', action='store_true',
                        help='automatically view output file')
    parser.add_argument('-v', '--verbose', action='store_true',
                        help='print additional output')
    parser.add_argument('-p', '--port',
                        help='instrument IP address')
    opts = parser.parse_args()

    grabber = RigolGrab(verbose=opts.verbose)
    grabber.grab(filename=opts.filename, auto_view=opts.auto_view)
    grabber.close()
