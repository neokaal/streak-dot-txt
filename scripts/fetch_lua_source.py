"""Backward compatibility wrapper for fetch_sources.py."""

from scripts.fetch_sources import fetch_and_verify_sources

if __name__ == "__main__":
    fetch_and_verify_sources()
