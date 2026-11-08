"""The injected index is a portable link list, not a dump of absolute paths."""

import pathlib

from agent_memory.core.config import Config
from agent_memory.core.memory_md import render
from agent_memory.core.record import MemoryRecord


def _record(path: pathlib.PurePath) -> MemoryRecord:
    return MemoryRecord(
        name="queue-timeout",
        abstract="The queue timeout is 30 seconds",
        type="fact",
        author="tester",
        created="2026-01-01T00:00:00Z",
        updated="2026-01-01T00:00:00Z",
        path=path,
    )


def test_windows_store_links_are_store_relative_posix_paths():
    root = pathlib.PureWindowsPath(r"C:\store")
    rendered = render(
        [_record(root / "fact" / "general" / "queue-timeout.md")],
        Config(),
        str(root),
    )

    assert "](fact/general/queue-timeout.md)" in rendered
    assert "\\" not in rendered


def test_a_directory_whose_name_prefixes_the_store_is_not_rewritten():
    root = pathlib.PureWindowsPath(r"C:\store")
    outside = pathlib.PureWindowsPath(r"C:\store2\fact\general\queue-timeout.md")
    rendered = render([_record(outside)], Config(), str(root))

    assert str(outside) in rendered


def test_a_posix_store_link_stays_relative(store):
    written = store.record(
        abstract="The queue timeout is 30 seconds",
        type="fact",
        name="queue-timeout",
    )
    relative = written.path.relative_to(store.root).as_posix()
    rendered = store.layout.memory_index.read_text(encoding="utf-8")

    assert f"]({relative})" in rendered
    assert str(store.root) not in rendered
