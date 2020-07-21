import time
import argparse
from datetime import datetime, timezone

def timeit(method):
    def timed(*args, **kw):
        ts = time.time()
        result = method(*args, **kw)
        te = time.time()
        if 'log_time' in kw:
            name = kw.get('log_name', method.__name__.upper())
            kw['log_time'][name] = time.strftime("%H:%M:%S" , time.gmtime((te - ts)))
        else:
            # print('%r took  %2.2f ms' % \
            #       (method.__name__, (te - ts) * 1000))
            print("{} took {}.".format(method.__name__,time.strftime("%H:%M:%S" , time.gmtime((te - ts))) ))
        return result
    return timed

def str2bool(v):
    if isinstance(v, bool):
       return v
    if v.lower() in ('yes', 'true', 't', 'y', '1'):
        return True
    elif v.lower() in ('no', 'false', 'f', 'n', '0'):
        return False
    else:
        raise argparse.ArgumentTypeError("Boolean value expected. ['yes', 'true', 't', 'y', '1', 'no', 'false', 'f', 'n', '0']" )

def current_local_datetime():
    return datetime.now()

def current_UTC_datetime():
    return datetime.now(timezone.utc)
