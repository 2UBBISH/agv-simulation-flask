from datetime import datetime

__OLD_PRINT = print
__IS_DEBUG = True


def print(arg):
    if __IS_DEBUG is True:
        __OLD_PRINT( "[%s]: %s" % (datetime.now(), str(arg)))
    else:
        # do nothing
        pass
