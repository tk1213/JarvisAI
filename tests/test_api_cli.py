from __future__ import annotations

import sys
from unittest.mock import patch

from jarvis.cli import create_parser, main


def test_parser_accepts_api_command() -> None:
    args = create_parser().parse_args(
        ["api"]
    )

    assert args.command == "api"


def test_main_runs_api_server(
    monkeypatch,
) -> None:
    monkeypatch.setattr(
        sys,
        "argv",
        [
            "jarvis",
            "api",
        ],
    )

    with patch(
        "jarvis.cli.run_api_server",
    ) as run_api_server:
        main()

    run_api_server.assert_called_once_with()