"""
Main sloptimize functionality
"""

import os
from typing import Dict, Any, List, Optional
import pydantic
import weave

from .environment import LLM_PROVIDER
from .llm import openai_client, grok_client

if LLM_PROVIDER == "openai":
    client = openai_client
elif LLM_PROVIDER == "grok":
    client = grok_client
else:
    raise ValueError(
        f"Invalid LLM_PROVIDER: {LLM_PROVIDER}. Must be 'openai' or 'grok'"
    )


# schemas for interaction with the LLM
class LLMOptimizationResponse(pydantic.BaseModel):
    """Structured response from LLM code optimization"""

    class Metrics(pydantic.BaseModel):
        """Metrics from code optimization analysis"""

        complexity_improvement: Optional[str] = pydantic.Field(
            None, description="How much complexity was improved"
        )
        readability_score: Optional[str] = pydantic.Field(
            None, description="How much readability was improved"
        )
        performance_gain: Optional[str] = pydantic.Field(
            None, description="How much performance was improved"
        )

    optimized_code: str = pydantic.Field(
        ...,
        description=(
            "The optimized version of the input code that the client can use to directly replace the original"
        ),
    )
    metrics: Metrics
    score: float = pydantic.Field(
        ..., description="How much impact your optimization had"
    )
    integration_considerations: list[str] = pydantic.Field(
        [],
        description=(
            "Considerations for integrating the optimized code into the existing codebase."
            "Indicate if imports need to be added or removed."
            "Indicate if the method signature was altered and how."
        ),
    )


# return types from this module
class OptimizationAssessment(pydantic.BaseModel):
    """Internal assessment type for optimization results"""

    score: Optional[float]
    metrics: Optional[Dict[str, Any]]
    recommendations: Optional[List[str]]


class SloptimizeResult(pydantic.BaseModel):
    """Internal result type for sloptimize operations"""

    source_code: str
    assessment: OptimizationAssessment
    integration_considerations: List[str]


def _get_system_prompt() -> str:
    """Load system prompt from PROMPT.md"""
    prompt_path = os.path.join(os.path.dirname(__file__), "PROMPT.md")
    with open(prompt_path, "r") as f:
        return f.read()


@weave.op()
def sloptimize(code: str) -> SloptimizeResult:
    """
    Analyze and optimize the provided code

    Args:
        code: Source code to analyze and optimize

    Returns:
        SloptimizeResult with optimized code, assessment, and considerations
    """
    # Prepare messages for LLM
    messages = [
        {
            "role": "system",
            "content": _get_system_prompt(),
        },
        {
            "role": "user",
            "content": code,
        },
    ]

    # Get structured LLM response
    completion = client(messages, LLMOptimizationResponse, temperature=0.3)

    # Convert LLM response to internal format
    assessment = OptimizationAssessment(
        score=completion.score,
        metrics=completion.metrics.model_dump(),
        recommendations=None,  # No longer in LLM response
    )

    return SloptimizeResult(
        source_code=completion.optimized_code,
        assessment=assessment,
        integration_considerations=completion.integration_considerations,
    )


weave.init("sloptimize")
