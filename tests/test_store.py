import pytest

from splitsmart.store import Store


@pytest.mark.parametrize("value", ["", "   ", "${SPLITSMART_DB}"])
def test_blank_or_unexpanded_db_env_falls_back_to_default(monkeypatch, tmp_path, value):
    monkeypatch.chdir(tmp_path)
    monkeypatch.setenv("SPLITSMART_DB", value)
    store = Store()
    assert store.path == "splitsmart.db"
    gid = store.create_group("Trip", ["A", "B"])["id"]
    # Data must persist across connections (an empty path would give a throwaway DB).
    assert Store().get_group(gid)["members"] == ["A", "B"]


def test_db_env_is_used_when_set(monkeypatch, tmp_path):
    target = str(tmp_path / "custom.db")
    monkeypatch.setenv("SPLITSMART_DB", target)
    assert Store().path == target
