"""Run the test questions against the assistant pipeline (mock or real model).

    python session4/activity8_assistant/run_eval.py

'answer' cases pass when the generated SQL runs and returns rows.
'refuse' cases pass when the model refuses or the SQL guard blocks the query.
Exit code is 1 if any case fails, so you can run this in CI.
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from llm_client import backend_name, question_to_sql  # noqa: E402
from tools import UnsafeQuery, run_sql  # noqa: E402


def check(case: dict) -> tuple[bool, str]:
    sql = question_to_sql(case["question"])
    refused = sql.upper().startswith("REFUSE")
    if case["expect"] == "refuse":
        if refused:
            return True, "refused by the model"
        try:
            run_sql(sql)
        except UnsafeQuery:
            return True, "blocked by the SQL guard"
        except Exception as e:
            return False, f"unexpected error: {e}"
        return False, "ran a query it should have refused"
    if refused:
        return False, "refused a valid question"
    try:
        df = run_sql(sql)
    except Exception as e:
        return False, f"query failed: {e}"
    return (len(df) > 0), f"{len(df)} row(s)"


if __name__ == "__main__":
    cases = json.loads((Path(__file__).parent / "eval_questions.json").read_text())
    print(f"Backend: {backend_name()}\n")
    failures = 0
    for case in cases:
        ok, detail = check(case)
        failures += not ok
        print(f"[{'PASS' if ok else 'FAIL'}] {case['question']}  ->  {detail}")
    print(f"\n{len(cases) - failures}/{len(cases)} passed")
    sys.exit(1 if failures else 0)
