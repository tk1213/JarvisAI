from __future__ import annotations

import asyncio

from jarvis.core.application import JarvisApplication
from jarvis.core.container import container


async def main() -> None:
    app = JarvisApplication()

    try:
        await app.start(
            start_background_tasks=False,
        )

        tool_definitions = container.get(
            "tool_definitions"
        )

        definitions = (
            tool_definitions.list_definitions()
        )

        by_name = {
            definition.name: definition
            for definition in definitions
        }

        detail_name = (
            "system_execution_detail"
        )
        diagnostics_name = (
            "system_execution_diagnostics"
        )

        print(
            "Sprint 3.6 Native Execution Observability Tools"
        )
        print(
            "-" * 60
        )
        print(
            f"Native tool count: {len(definitions)}"
        )
        print(
            "Execution detail tool present: "
            f"{detail_name in by_name}"
        )
        print(
            "Execution diagnostics tool present: "
            f"{diagnostics_name in by_name}"
        )

        if detail_name in by_name:
            print(
                "Detail parameters: "
                f"{by_name[detail_name].parameters}"
            )

        if diagnostics_name in by_name:
            print(
                "Diagnostics parameters: "
                f"{by_name[diagnostics_name].parameters}"
            )

        if detail_name not in by_name:
            raise RuntimeError(
                "system_execution_detail is not exposed "
                "on the native read-only tool surface."
            )

        if diagnostics_name not in by_name:
            raise RuntimeError(
                "system_execution_diagnostics is not exposed "
                "on the native read-only tool surface."
            )

        for name in (
            detail_name,
            diagnostics_name,
        ):
            properties = (
                by_name[
                    name
                ].parameters.get(
                    "properties",
                    {},
                )
            )

            if "record_id" not in properties:
                raise RuntimeError(
                    f"{name} is missing record_id."
                )

        print(
            "Native execution observability tool gate: PASS"
        )

    finally:
        await app.shutdown()


if __name__ == "__main__":
    asyncio.run(
        main()
    )
