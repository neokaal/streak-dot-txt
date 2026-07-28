# declare the phony targets
.PHONY: clean dist desktop-dist

dist:
	@echo "Building binary in dist folder using pyinstaller"
	pyinstaller --name=streakdottxt --noconfirm streakdottxt.py

desktop-dist:
	./desktop/package-release.sh

clean:
	@echo "Cleaning up the dist folder"
	rm -rf dist/
