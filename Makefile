# declare the phony targets
.PHONY: clean dist desktop-app desktop-dist

dist:
	@echo "Building binary in dist folder using pyinstaller"
	pyinstaller --name=streakdottxt --noconfirm streakdottxt.py

desktop-dist:
	.env/bin/python desktop/package_release.py

desktop-app:
	.env/bin/python desktop/package_release.py --bundles app

clean:
	@echo "Cleaning up the dist folder"
	rm -rf dist/
