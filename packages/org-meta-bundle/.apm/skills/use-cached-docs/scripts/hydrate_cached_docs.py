#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = [
#   "certifi>=2025.0.0",
#   "pyyaml>=6.0.2",
# ]
# ///
"""Hydrate documentation manifests owned by installed agent skills."""

from __future__ import annotations

import argparse
import io
import json
import re
import shutil
import ssl
import tarfile
import tempfile
from collections.abc import Mapping
from dataclasses import dataclass
from pathlib import Path, PurePosixPath
from urllib.parse import quote
import urllib.request

import certifi
import yaml


USER_AGENT = "agent-context-hydrate-cached-docs"
SSL_CONTEXT = ssl.create_default_context(cafile=certifi.where())
IDENTIFIER_PATTERN = re.compile(r"^[a-z0-9][a-z0-9._-]*$")
COMMIT_PATTERN = re.compile(r"^[0-9a-f]{40}$")


@dataclass(frozen=True)
class CachedDocsSource:
    identifier: str
    repository: str
    strategy_type: str
    version: str
    files: tuple[tuple[PurePosixPath, PurePosixPath], ...]
    folders: tuple[tuple[PurePosixPath, PurePosixPath], ...]
    configuration_path: Path


def request_json(url: str) -> dict[str, object]:
    request = urllib.request.Request(
        url,
        headers={"Accept": "application/vnd.github+json", "User-Agent": USER_AGENT},
    )
    with urllib.request.urlopen(request, context=SSL_CONTEXT) as response:
        return json.load(response)


def download(url: str) -> bytes:
    request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(request, context=SSL_CONTEXT) as response:
        return response.read()


def release_source(repository: str, version: str) -> tuple[str, str]:
    if version == "latest":
        url = f"https://api.github.com/repos/{repository}/releases/latest"
    else:
        url = (
            f"https://api.github.com/repos/{repository}/releases/tags/"
            f"{quote(version, safe='')}"
        )

    release = request_json(url)
    if release.get("draft") or release.get("prerelease"):
        raise RuntimeError(f"GitHub release {version!r} for {repository} is not stable")

    tag = release.get("tag_name")
    archive_url = release.get("tarball_url")
    if not isinstance(tag, str) or not isinstance(archive_url, str):
        raise RuntimeError(f"GitHub's release response for {repository} is missing a tag or source archive")
    return tag, archive_url


def required_string(value: object, label: str) -> str:
    if not isinstance(value, str) or not value:
        raise ValueError(f"{label} must be a non-empty string")
    return value


def source_identifier(value: object, label: str) -> str:
    identifier = required_string(value, label)
    if not IDENTIFIER_PATTERN.fullmatch(identifier):
        raise ValueError(f"{label} must contain lowercase letters, digits, dots, underscores, or hyphens")
    return identifier


def relative_folder(value: object, label: str) -> PurePosixPath:
    path = PurePosixPath(required_string(value, label))
    if path.is_absolute() or ".." in path.parts or path == PurePosixPath("."):
        raise ValueError(f"{label} must be a relative path without '..'")
    return path


def configured_paths(
    entry: Mapping[object, object],
    label: str,
    key: str,
) -> tuple[tuple[PurePosixPath, PurePosixPath], ...]:
    configured = entry.get(key, [])
    if not isinstance(configured, list):
        raise ValueError(f"{label}.{key} must be a list")

    paths: list[tuple[PurePosixPath, PurePosixPath]] = []
    destinations: set[PurePosixPath] = set()
    for index, path in enumerate(configured, start=1):
        if not isinstance(path, Mapping):
            raise ValueError(f"{label}.{key}[{index}] must be a mapping")
        source = relative_folder(path.get("source"), f"{label}.{key}[{index}].source")
        destination = relative_folder(
            path.get("destination", source.as_posix()),
            f"{label}.{key}[{index}].destination",
        )
        if destination in destinations:
            raise ValueError(f"{label}.{key} has duplicate destination {destination}")
        destinations.add(destination)
        paths.append((source, destination))
    return tuple(paths)


def load_sources(configuration_path: Path) -> list[CachedDocsSource]:
    with configuration_path.open() as configuration_file:
        configuration = yaml.safe_load(configuration_file)
    if not isinstance(configuration, Mapping):
        raise ValueError(f"{configuration_path} must contain a mapping")

    entries = configuration.get("cached_docs")
    if not isinstance(entries, list) or not entries:
        raise ValueError(f"{configuration_path} must define at least one cached_docs entry")

    sources: list[CachedDocsSource] = []
    for index, entry in enumerate(entries, start=1):
        if not isinstance(entry, Mapping):
            raise ValueError(f"{configuration_path}: cached_docs entry {index} must be a mapping")
        identifier = source_identifier(entry.get("id"), f"{configuration_path}: cached_docs entry {index}.id")
        strategy = entry.get("strategy")
        if not isinstance(strategy, Mapping):
            raise ValueError(f"{configuration_path}: cached_docs entry {identifier}.strategy must be a mapping")
        strategy_type = required_string(strategy.get("type"), f"{configuration_path}: {identifier}.strategy.type")
        if strategy_type not in {"github-release-http", "github-archive-http"}:
            raise ValueError(
                f"{configuration_path}: cached_docs entry {identifier} must use github-release-http or github-archive-http"
            )

        repository = required_string(strategy.get("repository"), f"{configuration_path}: {identifier}.repository")
        version_key = "version" if strategy_type == "github-release-http" else "ref"
        version = required_string(strategy.get(version_key), f"{configuration_path}: {identifier}.{version_key}")
        if strategy_type == "github-archive-http" and not COMMIT_PATTERN.fullmatch(version):
            raise ValueError(f"{configuration_path}: {identifier}.ref must be a 40-character lowercase commit SHA")

        files = configured_paths(entry, f"{configuration_path}: {identifier}", "files")
        folders = configured_paths(entry, f"{configuration_path}: {identifier}", "folders")
        if not files and not folders:
            raise ValueError(f"{configuration_path}: {identifier} must define at least one file or folder")
        destinations = [destination for _source, destination in (*files, *folders)]
        if len(destinations) != len(set(destinations)):
            raise ValueError(f"{configuration_path}: {identifier} has duplicate file or folder destinations")

        sources.append(
            CachedDocsSource(identifier, repository, strategy_type, version, files, folders, configuration_path)
        )
    return sources


def discover_configuration_paths(workspace_root: Path) -> list[Path]:
    own_configuration = Path(__file__).resolve().parents[1] / "cached-docs.yml"
    installed_configurations = workspace_root.glob(".agents/skills/*/cached-docs.yml")
    configurations = [own_configuration, *installed_configurations]
    unique_configurations = {path.resolve() for path in configurations if path.is_file()}
    return sorted(unique_configurations)


def discover_sources(workspace_root: Path) -> list[CachedDocsSource]:
    sources_by_id: dict[str, CachedDocsSource] = {}
    for configuration_path in discover_configuration_paths(workspace_root):
        for source in load_sources(configuration_path):
            existing = sources_by_id.get(source.identifier)
            if existing:
                raise ValueError(
                    f"Duplicate cached docs ID {source.identifier!r} in "
                    f"{existing.configuration_path} and {source.configuration_path}"
                )
            sources_by_id[source.identifier] = source
    if not sources_by_id:
        raise ValueError("No cached-docs.yml files were found beside installed skills")
    return list(sources_by_id.values())


def source_archive(source: CachedDocsSource) -> tuple[str, str]:
    if source.strategy_type == "github-release-http":
        return release_source(source.repository, source.version)
    return source.version, f"https://api.github.com/repos/{source.repository}/tarball/{source.version}"


def extract_folders(
    archive: bytes,
    destination: Path,
    files: tuple[tuple[PurePosixPath, PurePosixPath], ...],
    folders: tuple[tuple[PurePosixPath, PurePosixPath], ...],
) -> tuple[dict[PurePosixPath, int], dict[PurePosixPath, int]]:
    files_written = {source: 0 for source, _ in files}
    folders_written = {source: 0 for source, _ in folders}
    with tarfile.open(fileobj=io.BytesIO(archive), mode="r:gz") as tar:
        for member in tar:
            if not member.isfile():
                continue

            archive_path = PurePosixPath(member.name)
            relative_path = archive_path.parts[1:]
            if not relative_path:
                continue
            archive_relative = PurePosixPath(*relative_path)
            for source_file, destination_file in files:
                if archive_relative != source_file:
                    continue
                target = destination / Path(*destination_file.parts)
                target.parent.mkdir(parents=True, exist_ok=True)
                archive_file = tar.extractfile(member)
                if archive_file is None:
                    raise RuntimeError(f"Could not extract {member.name}")
                with archive_file, target.open("wb") as output:
                    shutil.copyfileobj(archive_file, output)
                files_written[source_file] += 1
                break
            else:
                for source_folder, destination_folder in folders:
                    source_parts = source_folder.parts
                    if relative_path[: len(source_parts)] != source_parts:
                        continue
                    remaining_path = relative_path[len(source_parts) :]
                    if not remaining_path:
                        continue
                    target = destination / Path(*destination_folder.parts, *remaining_path)
                    target.parent.mkdir(parents=True, exist_ok=True)
                    archive_file = tar.extractfile(member)
                    if archive_file is None:
                        raise RuntimeError(f"Could not extract {member.name}")
                    with archive_file, target.open("wb") as output:
                        shutil.copyfileobj(archive_file, output)
                    folders_written[source_folder] += 1
                    break
    return files_written, folders_written


def hydrate(source: CachedDocsSource, cache_root: Path, dry_run: bool) -> None:
    tag, source_url = source_archive(source)
    destination = cache_root / "tool-docs" / source.identifier / tag
    if dry_run:
        print(f"Would hydrate {source.repository} {tag} into {destination}")
        return

    archive = download(source_url)
    destination.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(dir=destination.parent, prefix=f".{source.identifier}-{tag}-") as temporary_dir:
        temporary_destination = Path(temporary_dir)
        files_written, folders_written = extract_folders(
            archive, temporary_destination, source.files, source.folders
        )
        missing_files = [file for file, count in files_written.items() if not count]
        missing_folders = [folder for folder, count in folders_written.items() if not count]
        if missing_files or missing_folders:
            missing = ", ".join(
                [*(file.as_posix() for file in missing_files), *(folder.as_posix() for folder in missing_folders)]
            )
            raise RuntimeError(f"{source.repository} {tag} did not contain configured paths: {missing}")

        if destination.exists():
            shutil.rmtree(destination)
        shutil.move(str(temporary_destination), destination)

    print(
        f"Hydrated {sum(files_written.values()) + sum(folders_written.values())} files "
        f"from {source.repository} {tag} into {destination}"
    )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dry-run", action="store_true", help="Resolve releases without downloading or writing files.")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    workspace_root = Path.cwd()
    cache_root = workspace_root / ".agent-cache"
    for source in discover_sources(workspace_root):
        hydrate(source, cache_root, args.dry_run)


if __name__ == "__main__":
    main()
