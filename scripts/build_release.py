#!/usr/bin/env python3
"""Package tracked-intent source using an allowlist, with no credentials or OS metadata."""
import argparse
import hashlib
from pathlib import Path
import zipfile

ROOT = Path(__file__).resolve().parents[1]
VERSION = "0.9.1"
RUNTIME_FILES = ["SKILL.md", "README.md", "INSTALL.zh-CN.md", "LICENSE", "agents/openai.yaml",
                 "scripts/xcoze_search.py", "scripts/setup.command", "references/setup.md",
                 "references/providers.md", "references/output.md", "VALIDATION.md",
                 "MARKETPLACE.zh-CN.md", "PUBLISHING.zh-CN.md", "TODO.md",
                 "CONTRIBUTING.md", "CHANGELOG.md", "references/search-services.md",
                 "scripts/search_common.py", "scripts/search_providers.py", "scripts/public_providers.py",
                 "scripts/search_routing.py", "scripts/search_quality.py", "scripts/public_access.py", "scripts/browser_search.py",
                 "scripts/public_trends.py", "scripts/content_sources.py", "references/feeds.md", "references/feeds.en.md",
                 "references/open-sources.md", "references/open-sources.en.md", "references/routing.md", "references/routing.en.md",
                 "references/sources.md", "references/sources.en.md",
                 "evaluations/reports/2026-11-05-source-audit.md", "evaluations/reports/2026-11-05-source-audit.en.md"]
SOURCE_EXTRA = [".gitignore",
                ".github/workflows/test.yml", ".github/workflows/release.yml",
                "scripts/build_release.py", "scripts/prepare_release.py",
                "tests/test_search.py", "tests/test_release.py", "tests/test_providers.py",
                "tests/test_evaluation.py", "tests/test_routing.py", "scripts/evaluate.py", "evaluations/queries.json",
                "evaluations/README.md"]


RUNTIME_FILES += ["README.en.md", "SKILL.en.md", "INSTALL.en.md", "TODO.en.md",
                  "CONTRIBUTING.en.md", "CHANGELOG.en.md", "VALIDATION.en.md",
                  "PUBLISHING.en.md", "MARKETPLACE.en.md", "references/setup.en.md",
                  "references/providers.en.md", "references/output.en.md",
                  "references/search-services.en.md"]
SOURCE_EXTRA += ["evaluations/README.en.md", "scripts/benchmark.py", "tests/test_benchmark.py",
                 "evaluations/smart-cases.json", "evaluations/smart-holdout.json",
                 "evaluations/reports/2026-11-03.md", "evaluations/reports/2026-11-03.en.md",
                 "evaluations/reports/2026-11-03.data.json", "tests/test_open_sources.py",
                 "evaluations/open-source-cases.json", "evaluations/reports/2026-11-03-open-sources.md",
                 "evaluations/reports/2026-11-03-open-sources.en.md", "evaluations/reports/2026-11-03-open-sources.data.json", "scripts/evaluate_fallback.py",
                 "tests/test_browser_fallback.py", "scripts/evaluate_browser.py",
                 "evaluations/reports/2026-11-03-browser.md", "evaluations/reports/2026-11-03-browser.en.md",
                 "evaluations/reports/2026-11-03-browser.data.json",
                 "evaluations/browser-comparison-cases.json", "evaluations/browser-comparison-scoped.json", "evaluations/browser-comparison-short.json",
                 "evaluations/reports/2026-11-03-comparison.md", "evaluations/reports/2026-11-03-comparison.en.md",
                 "evaluations/reports/2026-11-03-comparison.data.json", "evaluations/reports/2026-11-03-fallback.md",
                 "evaluations/reports/2026-11-03-fallback.en.md", "evaluations/reports/2026-11-03-fallback.data.json"]
SOURCE_EXTRA += ["tests/test_trending.py", "evaluations/reports/2026-11-05-public-platforms.md",
                 "evaluations/reports/2026-11-05-public-platforms.en.md", "evaluations/reports/2026-11-05-public-platforms.data.json"]

SOURCE_EXTRA += ["tests/test_content_sources.py", "evaluations/reports/2026-11-05-feeds-community.md",
                 "evaluations/reports/2026-11-05-feeds-community.en.md", "evaluations/reports/2026-11-05-feeds-community.data.json"]

SOURCE_EXTRA += ["tests/test_config_permissions.py", "research/free-sources-2026-11.md", "research/free-sources-2026-11.en.md", "research/free-sources-2026-11.csv", "research/free-sources-2026-11.data.json", "research/free-sources-2026-11.probes.json", "research/source-reference-audit-2026-11-05.json", "research/source-functional-samples-2026-11-05.json"]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()
    target = args.output_dir.resolve()
    target.mkdir(parents=True, exist_ok=True)
    hashes = []
    for kind, names in (("skill", RUNTIME_FILES), ("source", RUNTIME_FILES + SOURCE_EXTRA)):
        archive = target / ("xcoze-search-%s-v%s.zip" % (kind, VERSION))
        with zipfile.ZipFile(archive, "w", compression=zipfile.ZIP_DEFLATED) as stream:
            for name in sorted(names):
                path = ROOT / name
                if path.is_symlink() or not path.is_file():
                    raise SystemExit("Missing or unsafe release source: " + name)
                info = zipfile.ZipInfo("xcoze-search/" + name, date_time=(2026, 10, 24, 0, 0, 0))
                mode = 0o755 if name.endswith(".command") or name == "scripts/xcoze_search.py" else 0o644
                info.create_system = 3
                info.external_attr = (0o100000 | mode) << 16
                info.compress_type = zipfile.ZIP_DEFLATED
                stream.writestr(info, path.read_bytes())
        hashes.append(hashlib.sha256(archive.read_bytes()).hexdigest() + "  " + archive.name)
        print(archive)
    manifest = target / "SHA256SUMS.txt"
    manifest.write_text("\n".join(hashes) + "\n", encoding="utf-8")
    print(manifest)


if __name__ == "__main__":
    main()
