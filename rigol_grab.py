##
# rigol_grab: save Rigol Oscilloscope display as a .png file

import argparse
import os
import platform
import subprocess
import sys
import visa

class RigolGrab(object):

    VID_PID = '0x1AB1::0x04CE'

    def __init__(self, verbose=False):
        self._verbose = verbose
        self._rigol = None
        self._resource_manager = visa.ResourceManager()

    def grab(self, filename='rigol.png', auto_open=True):
        # self.rigol().write(':STOP')
        buf = self.rigol().query_binary_values(':DISP:DATA? ON,0,PNG', datatype='B')
        with open(filename, 'wb') as f:
            f.write(bytearray(buf))
        if auto_open:
            self.open_file_with_system_viewer(filename)

    def rigol(self):
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
            except:
                self.err_out('Could not open oscilloscope')
        return self._rigol

    def verbose_print(self, *args):
        if (self._verbose): print(*args)

    def err_out(self, message):
        sys.exit(message + '...quitting')

    def find_rigol(self):
        resource_names = self._resource_manager.list_resources()
        self.verbose_print('Found', resource_names)
        for name in resource_names:
            if self.VID_PID in name: return name
        return None

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

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Rigol Screen Grabber")
    parser.add_argument('-f', '--filename', default='rigol.png',
                        help='name of output file')
    parser.add_argument('-a', '--auto_open', action='store_true',
                        help='automatically open output file')
    parser.add_argument('-v', '--verbose', action='store_true',
                        help='print additional output')
    parser.add_argument('-p', '--port',
                        help='instrument IP address')
    opts = parser.parse_args()

    grabber = RigolGrab(verbose=opts.verbose)
    grabber.grab(filename=opts.filename, auto_open=opts.auto_open)
    grabber.close()
