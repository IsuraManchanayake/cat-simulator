from datetime import datetime
import io

from .enums import LogMethod


class Logger:
    method = LogMethod.console
    file = 'simulation.log'
    # simulation = None

    @staticmethod
    def setup(method, file='simulation.log'):
        Logger.method = method
        # Logger.simulation = simulation
        Logger.file = file

        # Erase content
        open(Logger.file, 'w')

    @staticmethod
    def log(*args, **kwargs):
        now = datetime.now()

        sout = io.StringIO()
        print(now.strftime('%Y-%m-%d %H:%M:%S.%f'), ': ', *args, file=sout, sep='', **kwargs)
        s = sout.getvalue()
        sout.close()

        if Logger.method == LogMethod.console:
            print(s, end='')
        elif Logger.method == LogMethod.file and Logger.file is not None:
            with open(Logger.file, 'a') as outf:
                outf.write(s)

    @staticmethod
    def sep():
        Logger.log('------------')