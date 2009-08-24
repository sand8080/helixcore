
#Client code must inirialize this variable with allowed transitions list
ALLOWED_TRANSITIONS = [
#    ('table1', 'table2'), ...
]

############################
import threading
import traceback

class Lock(object):
    def __init__(self, table, args):
        self.trace_lst = traceback.extract_stack()
        self.table = table
        self.fn_args = args

context = threading.local()
#context.locks = []

class TransitionNotAllowedError(Exception):
    def __init__(self):
        Exception.__init__(self,
            'Possible deadlock while attempting to lock table %s: lock transition not allowed' %
            context.locks[-1].table
        )
        self.locks = context.locks

    def __str__(self):
        msg = self.message + "\n\tLocks chain: %s\n" % ', '.join([lock.table for lock in self.locks])
        for lock in self.locks:
            msg += self._format_lock(lock)
        return msg

    def _format_lock(self, lock):
        msg = "\t------------\n"
        msg += "\ttable: %s\n" % lock.table
        msg += "\ttrace: \n"
        for entry in traceback.format_list(lock.trace_lst):
            msg += "\t\t%s\n" % entry
        if lock.fn_args:
            msg += "\tcaller args: %s\n" % lock.fn_args
        return msg

#context will be cleared on transaction end
def clear_context():
    context.locks = []

def handle_lock(table, *args):
    lock = Lock(table, args)
    if not hasattr(context, 'locks'):
        context.locks = []

    context.locks.append(lock)

    if len(context.locks) == 1:
        return

    transition = (context.locks[-2].table, context.locks[-1].table)

    if not transition in ALLOWED_TRANSITIONS:
        raise TransitionNotAllowedError()
