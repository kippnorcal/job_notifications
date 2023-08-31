from dataclasses import dataclass, field
import logging
from types import FunctionType

from .helpers import join_args, join_kwargs

logger = logging.getLogger(__name__)


@dataclass
class HandledException:
    func: FunctionType
    exception: Exception
    call_args: field(default_factory=list)  # type: ignore
    call_kwargs: field(default_factory=dict)  # type: ignore

    def _join_kwargs(self):
        if self.call_kwargs:
            return ', '.join([f"{k}={v}" for k, v in self.call_kwargs.items()])
        else:
            return "None"

    def _join_args(self):
        if self.call_args:
            return ', '.join([str(x) for x in self.call_args])
        else:
            return "None"

    def to_log(self):
        return f"{self.exception.__class__.__name__} raised on {self.func.__name__} " \
               f"function in {self.func.__module__} module" \
               f"\nArgs: {join_args(self.call_args)}" \
               f"\nKwargs: {join_kwargs(self.call_kwargs)}"

    def __str__(self):
        return f"{self.exception.__class__.__name__} raised on {self.func.__name__} " \
               f"function in {self.func.__module__} module"
