
def join_kwargs(call_kwargs):
    if call_kwargs:
        return ', '.join([f"{k}={v}" for k, v in call_kwargs.items()])
    else:
        return "None"


def join_args(call_args):
    if call_args:
        return ', '.join([str(x) for x in call_args])
    else:
        return "None"
