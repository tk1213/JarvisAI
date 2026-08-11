from jarvis.ai.responses_contracts import (
    ResponsesFunctionCall,
    ResponsesTextResult,
    ResponsesTurnResult,
)


def test_responses_text_result_completed_property() -> None:
    result = ResponsesTextResult(
        response_id="resp_123",
        model="gpt-5.5",
        status="completed",
        output_text="Hello",
    )

    assert result.completed is True


def test_turn_result_detects_tool_output_requirement() -> None:
    result = ResponsesTurnResult(
        response_id="resp_123",
        model="gpt-5.5",
        status="completed",
        output_text="",
        function_calls=(
            ResponsesFunctionCall(
                name="system_ping",
                arguments="{}",
                call_id="call_123",
            ),
        ),
    )

    assert result.requires_tool_output is True


def test_function_call_normalizes_name() -> None:
    call = ResponsesFunctionCall(
        name=" system_ping ",
        arguments="{}",
    )

    assert call.name == "system_ping"



def test_responses_turn_result_detects_function_call() -> None:
    from jarvis.ai.responses_contracts import (
        ResponsesFunctionCall,
        ResponsesTurnResult,
    )

    result = ResponsesTurnResult(
        response_id="resp_123",
        model="gpt-5.5",
        status="completed",
        output_text="",
        function_calls=(
            ResponsesFunctionCall(
                name="system_ping",
                arguments="{}",
                call_id="call_123",
            ),
        ),
    )

    assert result.requires_tool_output is True
