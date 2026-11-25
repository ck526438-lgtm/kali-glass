"""Tests de bout en bout de la CLI kali-glass (sans bureau : xfconf est simulé)."""
import json
import os
import subprocess
import sys
import importlib.util
from importlib.machinery import SourceFileLoader
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
CLI = ROOT / "bin" / "kali-glass"
MOCK = ROOT / "tests" / "mock"

ORIGINAL = {
    "xfce4-panel:/panels": ["1"],
    "xfce4-panel:/plugins/plugin-1": "whiskermenu",
    "xfce4-panel:/panels/panel-1/size": "24",
    "xfce4-panel:/panels/panel-1/position": "p=6;x=0;y=0",
    "xfce4-panel:/panels/panel-1/background-rgba": ["0.1", "0.1", "0.1", "1.0"],
    "xsettings:/Net/ThemeName": "Kali-Dark",
    "xfce4-desktop:/backdrop/screen0/monitorVirtual1/workspace0/last-image": "/usr/share/backgrounds/kali/kali.png",
}


@pytest.fixture
def env(tmp_path):
    home = tmp_path / "home"
    home.mkdir()
    db = tmp_path / "xfconf.json"
    db.write_text(json.dumps(ORIGINAL))
    e = {k: v for k, v in os.environ.items() if k not in ("DISPLAY", "WAYLAND_DISPLAY")}
    e.update(HOME=str(home), XFCONF_MOCK_DB=str(db), PATH=f"{MOCK}:{os.environ['PATH']}",
             KALI_GLASS_ALLOW_ROOT="1", KALI_GLASS_DOCK="xfce", NO_COLOR="1")

    class Env:
        pass
    x = Env()
    x.home, x.db, x.env = home, db, e

    def run(*args, check=True):
        r = subprocess.run([sys.executable, str(CLI), *args], env=e, text=True,
                           stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        if check:
            assert r.returncode == 0, r.stdout
        return r
    x.run = run
    x.xf = lambda: json.loads(db.read_text())
    x.state = lambda: json.loads((home / ".config/kali-glass/state.json").read_text())
    return x


def load_module():
    loader = SourceFileLoader("kali_glass", str(CLI))
    spec = importlib.util.spec_from_loader("kali_glass", loader)
    mod = importlib.util.module_from_spec(spec)
    loader.exec_module(mod)
    return mod


def test_version_and_help(env):
    assert "1." in env.run("--version").stdout
    assert "doctor" in env.run("--help").stdout


def test_list_wallpapers(env):
    out = env.run("list").stdout
    for name in ("aurora", "dragon", "light", "midnight", "ocean", "sunset"):
        assert name in out


def test_apply_sets_glass_desktop(env):
    env.run("apply", "--no-themes")
    xf = env.xf()
    assert xf["xfce4-desktop:/backdrop/screen0/monitorVirtual1/workspace0/last-image"].endswith("kali-glass-aurora.jpg")
    assert xf["xfce4-panel:/panels/panel-1/size"] == "28"
    assert xf["xfce4-panel:/panels/panel-1/background-rgba"][-1] == "0.35"
    assert xf["xfwm4:/general/button_layout"] == "CHM|"
    assert env.state()["settings"]["applied"] is True
    assert '@import url("kali-glass.css");' in (env.home / ".config/gtk-3.0/gtk.css").read_text()


def test_restore_returns_exact_original(env):
    env.run("apply", "--no-themes")
    env.run("wallpaper", "sunset")
    env.run("panel-opacity", "60")
    env.run("restore")
    assert env.xf() == ORIGINAL
    assert "kali-glass.css" not in (env.home / ".config/gtk-3.0/gtk.css").read_text()


def test_xfce_dock_fallback_add_and_remove(env):
    env.run("apply", "--no-themes")
    xf = env.xf()
    assert xf["xfce4-panel:/panels"] == ["1", "2"]
    assert xf["xfce4-panel:/panels/panel-2/position"] == "p=10;x=0;y=0"
    # la barre du haut ne doit pas toucher au dock
    env.run("panel-opacity", "10")
    assert env.xf()["xfce4-panel:/panels/panel-2/background-rgba"][-1] == "0.18"
    env.run("dock", "off")
    xf = env.xf()
    assert xf["xfce4-panel:/panels"] == ["1"]
    assert not any(k.startswith("xfce4-panel:/panels/panel-2") for k in xf)


def test_mode_uses_installed_whitesur(env):
    (env.home / ".themes/WhiteSur-Light/gtk-3.0").mkdir(parents=True)
    env.run("mode", "light")
    assert env.xf()["xsettings:/Net/ThemeName"] == "WhiteSur-Light"
    assert env.xf()["xfwm4:/general/theme"] == "WhiteSur-Light"


def test_custom_wallpaper_path(env, tmp_path):
    img = tmp_path / "photo.jpg"
    img.write_bytes(b"\xff\xd8fake")
    env.run("wallpaper", str(img))
    assert env.xf()["xfce4-desktop:/backdrop/screen0/monitorVirtual1/workspace0/last-image"] == str(img)


@pytest.mark.parametrize("args", [("blur", "50"), ("blur", "-1"), ("panel-opacity", "150"),
                                  ("wallpaper", "nexistepas"), ("mode", "bleu")])
def test_invalid_input_is_rejected(env, args):
    r = env.run(*args, check=False)
    assert r.returncode != 0


def test_dynamic_schedule():
    m = load_module()
    assert m.dynamic_pick(3) == "midnight"
    assert m.dynamic_pick(8) == "light"
    assert m.dynamic_pick(14) == "ocean"
    assert m.dynamic_pick(18) == "sunset"
    assert m.dynamic_pick(21) == "aurora"
    assert m.dynamic_pick(23) == "midnight"


def test_picom_config_strength_and_disable(tmp_path, monkeypatch):
    m = load_module()
    monkeypatch.setattr(m, "HOME", tmp_path)
    monkeypatch.setattr(m, "have", lambda c: c == "picom")
    monkeypatch.setattr(m, "restart_picom", lambda: None)
    monkeypatch.setattr(m, "AUTOSTART", tmp_path / "autostart")
    monkeypatch.setattr(m, "picom_conf_path", lambda: tmp_path / "picom.conf")
    st = {"backup": {}, "settings": {}}
    m.setup_picom(st, 12)
    assert "strength = 12;" in (tmp_path / "picom.conf").read_text()
    m.setup_picom(st, 0)
    assert 'method = "none"' in (tmp_path / "picom.conf").read_text()
    assert (tmp_path / "autostart" / "kali-glass-picom.desktop").exists()
