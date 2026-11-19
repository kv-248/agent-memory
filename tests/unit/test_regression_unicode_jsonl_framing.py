import json

import pytest
from agent_memory.adapters import muse_session, transcript
from agent_memory.core import sessions
from agent_memory.core.pending import Pending


@pytest.mark.parametrize("separator", ["\u2028", "\u2029", "\u0085"])
def test_jsonl_values_keep_unicode_line_separators(store, separator):
    text = "before" + separator + "after"
    pointer = store.archive.append_session("unicode", [{"role": "user", "text": text}])
    assert sessions.count(sessions.session_path(store.layout, "unicode")) == 1
    assert [message.text for message in sessions.resolve(store.layout, pointer)] == [text]
    pending = Pending(store.layout)
    spec = {"body": text, "abstract": "Unicode fixture"}
    pending.append("unicode", [spec])
    assert pending.drain("unicode") == [spec]


@pytest.mark.parametrize("separator", ["\u2028", "\u2029", "\u0085"])
def test_executor_operations_and_verdicts_keep_unicode_separators(store, separator):
    import json

    from agent_memory.core import agentic, reasoning, reconcile

    text = "before" + separator + "after"
    spec = {"op": "new", "type": "decision", "abstract": text}
    rendered = json.dumps(spec, ensure_ascii=False)
    assert reconcile.parse_operations(rendered) == ([spec], [])
    assert agentic._split(rendered) == ([], [rendered])
    verdict = json.dumps(
        {"proposal": "fixture", "verdict": "reject", "text": text}, ensure_ascii=False
    )
    assert reasoning.parse(verdict)[0].text == text


@pytest.mark.parametrize("separator", ["\u2028", "\u2029", "\u0085"])
def test_a_host_transcript_record_keeps_unicode_line_separators(tmp_path, separator):
    text = "before" + separator + "after"
    record = json.dumps(
        {"type": "user", "message": {"role": "user", "content": text}},
        ensure_ascii=False,
    )
    following = json.dumps({"role": "assistant", "content": "done"})
    path = tmp_path / "transcript.jsonl"
    path.write_text(record + "\r\n" + following + "\n", encoding="utf-8")

    assert transcript.items(path) == [f"user: {text}", "assistant: done"]


@pytest.mark.parametrize("separator", ["\u2028", "\u2029", "\u0085"])
def test_a_muse_transcript_record_keeps_unicode_line_separators(tmp_path, separator):
    text = "before" + separator + "after"
    record = json.dumps(
        {
            "payload": {
                "kind": "run",
                "event": {"kind": "started", "prompt": text},
            }
        },
        ensure_ascii=False,
    )
    following = json.dumps(
        {
            "payload": {
                "kind": "run",
                "event": {
                    "kind": "assistant_message_committed",
                    "text": "done",
                },
            }
        }
    )
    path = tmp_path / "session.jsonl"
    path.write_text(record + "\n" + following + "\n", encoding="utf-8")

    assert muse_session.items(path) == [f"user: {text}", "assistant: done"]
