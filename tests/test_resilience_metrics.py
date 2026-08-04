from jarvis.planner.resilience_metrics import ResilienceMetrics


def test_metrics_snapshot_is_independent() -> None:
    metrics = ResilienceMetrics()

    metrics.plans_started = 1
    metrics.increment_capability_failure(
        "system.ping"
    )

    snapshot = metrics.snapshot()

    metrics.plans_started = 2
    metrics.increment_capability_failure(
        "system.ping"
    )

    assert snapshot.plans_started == 1
    assert snapshot.capability_failures == {
        "system.ping": 1,
    }


def test_capability_failure_rejects_empty_name() -> None:
    metrics = ResilienceMetrics()

    try:
        metrics.increment_capability_failure(
            " "
        )
    except ValueError as exc:
        assert "empty" in str(exc)
    else:
        raise AssertionError(
            "Expected ValueError."
        )
