import importlib.util
import io
import tarfile
import tempfile
import unittest
from pathlib import Path
from pathlib import PurePosixPath
import sys


SCRIPT = Path(__file__).parents[1] / "packages/org-meta-bundle/.apm/skills/use-cached-docs/scripts/hydrate_cached_docs.py"
SPEC = importlib.util.spec_from_file_location("hydrate_cached_docs", SCRIPT)
assert SPEC and SPEC.loader
hydrator = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = hydrator
SPEC.loader.exec_module(hydrator)


class HydrateCachedDocsTests(unittest.TestCase):
    def test_extracts_selected_files_and_folders(self) -> None:
        archive = io.BytesIO()
        with tarfile.open(fileobj=archive, mode="w:gz") as tar:
            for name, content in {
                "repo-abc/README.md": b"readme",
                "repo-abc/docs/guide.md": b"guide",
                "repo-abc/ignored.txt": b"ignored",
            }.items():
                info = tarfile.TarInfo(name)
                info.size = len(content)
                tar.addfile(info, io.BytesIO(content))

        with tempfile.TemporaryDirectory() as temporary_directory:
            destination = Path(temporary_directory)
            files, folders = hydrator.extract_folders(
                archive.getvalue(),
                destination,
                ((PurePosixPath("README.md"), PurePosixPath("README.md")),),
                ((PurePosixPath("docs"), PurePosixPath("docs")),),
            )
            self.assertEqual(files[PurePosixPath("README.md")], 1)
            self.assertEqual(folders[PurePosixPath("docs")], 1)
            self.assertEqual((destination / "README.md").read_text(), "readme")
            self.assertEqual((destination / "docs/guide.md").read_text(), "guide")
            self.assertFalse((destination / "ignored.txt").exists())

    def test_rejects_non_immutable_archive_ref(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            configuration = Path(temporary_directory) / "cached-docs.yml"
            configuration.write_text(
                "cached_docs:\n"
                "  - id: example\n"
                "    strategy:\n"
                "      type: github-archive-http\n"
                "      repository: owner/repository\n"
                "      ref: main\n"
                "    files:\n"
                "      - source: README.md\n"
            )
            with self.assertRaisesRegex(ValueError, "40-character lowercase commit SHA"):
                hydrator.load_sources(configuration)


if __name__ == "__main__":
    unittest.main()
