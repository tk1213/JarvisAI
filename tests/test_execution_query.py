import pytest

from jarvis.planner.execution_query import ExecutionQuery


def test_query_normalizes_values() -> None:
    query = ExecutionQuery(
        limit=5,
        status=" COMPLETED ",
        capability=" system.ping ",
    )

    assert query.limit == 5
    assert query.status == "completed"
    assert query.capability == "system.ping"


@pytest.mark.parametrize(
    ("kwargs", "message"),
    [
        (
            {
                "limit": 0,
            },
            "at least 1",
        ),
        (
            {
                "status": " ",
            },
            "status cannot be empty",
        ),
        (
            {
                "capability": " ",
            },
            "capability cannot be empty",
        ),
    ],
)
def test_query_rejects_invalid_values(
    kwargs: dict,
    message: str,
) -> None:
    with pytest.raises(
        ValueError,
        match=message,
    ):
        ExecutionQuery(
            **kwargs
        )
