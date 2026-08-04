from jarvis.planner.failures import (
    FailureClassifier,
    FailureKind,
)


def test_timeout_is_transient() -> None:
    result = FailureClassifier().classify(
        RuntimeError(
            "request timed out"
        )
    )

    assert result.kind is FailureKind.TRANSIENT


def test_not_allowed_is_permanent() -> None:
    result = FailureClassifier().classify(
        RuntimeError(
            "capability not allowed"
        )
    )

    assert result.kind is FailureKind.PERMANENT


def test_unknown_error_is_unknown() -> None:
    result = FailureClassifier().classify(
        RuntimeError(
            "something strange happened"
        )
    )

    assert result.kind is FailureKind.UNKNOWN
