"""Actions, mainly to be executed in measurement Loops."""
import time

from qcodes.utils.deferred_operations import is_function
from qcodes.utils.threading import thread_map


_NO_SNAPSHOT = {'type': None, 'description': 'Action without snapshot'}


def _actions_snapshot(actions, update):
    """Make a list of snapshots from a list of actions."""
    snapshot = []
    for action in actions:
        if hasattr(action, 'snapshot'):
            snapshot.append(action.snapshot(update=update))
        else:
            snapshot.append(_NO_SNAPSHOT)
    return snapshot


class Task:

    """
    A predefined task to be executed within a measurement Loop.

    This form is for a simple task that does not measure any data,
    and does not depend on the state of the loop when it is called.

    The first argument should be a callable, to which any subsequent
    args and kwargs (which are evaluated before the loop starts) are passed.

    kwargs passed when the Task is called are ignored,
    but are accepted for compatibility with other things happening in a Loop.
    """

    def __init__(self, func, *args, **kwargs):
        self.func = func
        self.args = args
        self.kwargs = kwargs

    def __call__(self, **ignore_kwargs):
        self.func(*self.args, **self.kwargs)

    def snapshot(self, update=False):
        return {'type': 'Task', 'func': repr(self.func)}


class Wait:

    """
    A simple class to tell a Loop to wait <delay> seconds.

    This is transformed into a Task within the Loop, such that
    it can do other things (monitor, check for halt) during the delay.

    But for use outside of a Loop, it is also callable (then it just sleeps)
    """

    def __init__(self, delay):
        if not delay >= 0:
            raise ValueError('delay must be > 0, not {}'.format(repr(delay)))
        self.delay = delay

    def __call__(self):
        if self.delay:
            time.sleep(self.delay)

    def snapshot(self, update=False):
        return {'type': 'Wait', 'delay': self.delay}


class _Measure:

    """
    A callable collection of parameters to measure.

    This should not be constructed manually, only by an ActiveLoop.
    """

    def __init__(self, params_indices, data_set, use_threads):
        self.use_threads = use_threads and len(params_indices) > 1
        # the applicable DataSet.store function
        self.store = data_set.store

        # for performance, pre-calculate which params return data for
        # multiple arrays, and the name mappings
        self.getters = []
        self.param_ids = []
        self.composite = []
        for param, action_indices in params_indices:
            self.getters.append(param.get)

            if hasattr(param, 'names'):
                part_ids = []
                for i in range(len(param.names)):
                    param_id = data_set.action_id_map[action_indices + (i,)]
                    part_ids.append(param_id)
                self.param_ids.append(None)
                self.composite.append(part_ids)
            else:
                param_id = data_set.action_id_map[action_indices]
                self.param_ids.append(param_id)
                self.composite.append(False)

    def __call__(self, loop_indices, **ignore_kwargs):
        out_dict = {}
        if self.use_threads:
            out = thread_map(self.getters)
        else:
            out = [g() for g in self.getters]

        for param_out, param_id, composite in zip(out, self.param_ids,
                                                  self.composite):
            if composite:
                for val, part_id in zip(param_out, composite):
                    out_dict[part_id] = val
            else:
                out_dict[param_id] = param_out

        self.store(loop_indices, out_dict)


class _Nest:

    """
    Wrapper to make a callable nested ActiveLoop.

    This should not be constructed manually, only by an ActiveLoop.
    """

    def __init__(self, inner_loop, action_indices):
        self.inner_loop = inner_loop
        self.action_indices = action_indices

    def __call__(self, **kwargs):
        self.inner_loop._run_loop(action_indices=self.action_indices, **kwargs)


class BreakIf:

    """
    Loop action that breaks out of the loop if a condition is truthy.

    condition: a callable taking no arguments.
        Can be a simple function that returns truthy when it's time to quit
        May also be constructed by deferred operations on `Parameter`s, eg:
            BreakIf(gates.chan1 >= 3)
            BreakIf(abs(source.I * source.V) >= source.power_limit.get_latest)
    """

    def __init__(self, condition):
        if not is_function(condition, 0):
            raise TypeError('BreakIf condition must be a callable with '
                            'no arguments')
        self.condition = condition

    def __call__(self, **ignore_kwargs):
        if self.condition():
            raise _QcodesBreak

    def snapshot(self, update=False):
        # TODO: make nice reprs for DeferredOperations
        return {'type': 'BreakIf', 'condition': repr(self.condition)}


class _QcodesBreak(Exception):
    pass