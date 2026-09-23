"""Validated descriptions for learner-program execution."""

from pynivo.core.execution.output_buffer import OutputBuffer, OutputChunk
from pynivo.core.execution.request import ExecutionRequest, ExecutionRequestError

__all__ = ["ExecutionRequest", "ExecutionRequestError", "OutputBuffer", "OutputChunk"]
