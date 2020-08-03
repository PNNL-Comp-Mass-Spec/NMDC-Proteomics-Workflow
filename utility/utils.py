import time
import argparse
from datetime import datetime, timezone

def timeit(method):
    '''
    Calculate and logs runtime of a function.
    :param method:
    :return: string: HH:MM:SS
    '''
    def timed(*args, **kw):
        ts = time.time()
        result = method(*args, **kw)
        te = time.time()
        if 'log_time' in kw:
            name = kw.get('log_name', method.__name__.upper())
            kw['log_time'][name] = time.strftime("%H:%M:%S" , time.gmtime((te - ts)))
        else:
            print("{} took {}.".format(method.__name__,time.strftime("%H:%M:%S" , time.gmtime((te - ts))) ))
        return result
    return timed

def str2bool(v):
    '''
    chnages userInput to a yes/no
    :param v: string
    :return: bool
    '''
    if isinstance(v, bool):
       return v
    if v.lower() in ('yes', 'true', 't', 'y', '1'):
        return True
    elif v.lower() in ('no', 'false', 'f', 'n', '0'):
        return False
    else:
        raise argparse.ArgumentTypeError("Boolean value expected. ['yes', 'true', 't', 'y', '1', 'no', 'false', 'f', 'n', '0']" )

def current_local_datetime():
    '''

    :return: current local date and time
    '''
    return datetime.now()

def current_UTC_datetime():
    '''

    :return: current UTC date and time.
    '''
    return datetime.now(timezone.utc)
