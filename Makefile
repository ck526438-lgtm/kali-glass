# Kali Glass — tâches courantes
#   make test       tests + lint
#   make deb        construit dist/kali-glass_<version>_all.deb
#   make install    installe dans $(PREFIX) (sudo make install)
#   make wallpapers régénère les fonds 4K

PREFIX  ?= /usr
DESTDIR ?=
VERSION := $(shell grep -m1 '^VERSION' bin/kali-glass | cut -d'"' -f2)
DATA    := $(DESTDIR)$(PREFIX)/share/kali-glass

.PHONY: all test lint deb install uninstall wallpapers live preview clean version

all: test

version:
	@echo $(VERSION)

lint:
	python3 -m ruff check .
	shellcheck install.sh uninstall.sh packaging/build-deb.sh
	shellcheck -s bash completions/kali-glass.bash

test: lint
	python3 -m pytest -q

deb:
	bash packaging/build-deb.sh

install:
	install -d $(DATA)
	cp -r wallpapers config $(DATA)/
	install -Dm755 bin/kali-glass                         $(DESTDIR)$(PREFIX)/bin/kali-glass
	install -Dm755 apps/glass-center/glass-center         $(DESTDIR)$(PREFIX)/bin/glass-center
	install -Dm755 bin/kali-glass-live                    $(DESTDIR)$(PREFIX)/bin/kali-glass-live
	install -Dm644 apps/glass-center/glass-center.desktop $(DESTDIR)$(PREFIX)/share/applications/glass-center.desktop
	install -Dm644 apps/glass-center/glass-center.svg     $(DESTDIR)$(PREFIX)/share/icons/hicolor/scalable/apps/glass-center.svg
	install -Dm644 apps/glass-center/io.github.ck526438.GlassCenter.metainfo.xml \
		$(DESTDIR)$(PREFIX)/share/metainfo/io.github.ck526438.GlassCenter.metainfo.xml
	install -Dm644 man/kali-glass.1   $(DESTDIR)$(PREFIX)/share/man/man1/kali-glass.1
	install -Dm644 man/glass-center.1 $(DESTDIR)$(PREFIX)/share/man/man1/glass-center.1
	install -Dm644 completions/kali-glass.bash $(DESTDIR)$(PREFIX)/share/bash-completion/completions/kali-glass
	install -d $(DESTDIR)$(PREFIX)/share/backgrounds/kali-glass
	cp wallpapers/*.jpg $(DESTDIR)$(PREFIX)/share/backgrounds/kali-glass/

uninstall:
	rm -rf $(DATA) $(DESTDIR)$(PREFIX)/share/backgrounds/kali-glass
	rm -f $(DESTDIR)$(PREFIX)/bin/kali-glass $(DESTDIR)$(PREFIX)/bin/glass-center $(DESTDIR)$(PREFIX)/bin/kali-glass-live \
	      $(DESTDIR)$(PREFIX)/share/applications/glass-center.desktop \
	      $(DESTDIR)$(PREFIX)/share/icons/hicolor/scalable/apps/glass-center.svg \
	      $(DESTDIR)$(PREFIX)/share/metainfo/io.github.ck526438.GlassCenter.metainfo.xml \
	      $(DESTDIR)$(PREFIX)/share/man/man1/kali-glass.1 $(DESTDIR)$(PREFIX)/share/man/man1/glass-center.1 \
	      $(DESTDIR)$(PREFIX)/share/bash-completion/completions/kali-glass

wallpapers:
	python3 tools/generate_wallpapers.py wallpapers 3840 2160
	for f in wallpapers/*.png; do [ -e "$$f" ] && convert "$$f" -quality 93 "$${f%.png}.jpg" && rm "$$f"; done; true

live:
	python3 tools/generate_live.py --out dist/live --size 3840x2160

preview:
	python3 tools/make_preview.py

clean:
	rm -rf build dist .pytest_cache .ruff_cache tests/__pycache__
