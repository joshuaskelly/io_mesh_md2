import sys
import time
from contextlib import contextmanager


class PerformanceMonitor:
    """Simple class for timing addon performance. Adapted from the official
    Blender FBX addon.

    Example:
        pmon = PerformanceMonitor('Demo')
        pmon.push_scope('Starting')

        with pmon.scope():
            for i in range(4):
                pmon.progress('Doing work:', i, 4)

        pmon.pop_scope('Finished')

    """

    def __init__(self, identifier=''):
        self.level = -1
        self.reference_time = []
        self.identifier = identifier

    def push_scope(self, message=''):
        self.level += 1
        self.reference_time.append(time.process_time())
        self.log(message)

    def pop_scope(self, message=''):
        if not self.reference_time:
            self.log(message)

            return

        reference_time = self.reference_time[self.level]
        delta = time.process_time() - reference_time if reference_time else 0
        print(f'{"   " * (self.level)}Done ({delta} sec)\n')

        self.log(message)

        del self.reference_time[self.level]
        self.level -= 1

    @contextmanager
    def scope(self, message=''):
        self.push_scope(message)
        yield
        self.pop_scope()

    def progress(self, message='', current=None, maximum=None):
        p = ''

        if current:
            p = f' {current + 1}'

        if maximum:
            p = f' {current + 1} of {maximum}'

        if current + 1 == maximum:
            p += '\n'

        sys.stdout.write(f'\r{"   " * self.level}[{self.identifier}] {message}{p}')
        sys.stdout.flush()

    def log(self, message=''):
        if message:
            print(f'{"   " * self.level}[{self.identifier}] {message}')

    def __del__(self):
        while self.level >= 0:
            self.pop_scope()
