#!/usr/bin/env python3
"""Package tracked-intent source using an allowlist, with no credentials or OS metadata."""
import argparse
import hashlib
import json
from pathlib import Path
import posixpath
import re
import zipfile

ROOT = Path(__file__).resolve().parents[1]
VERSION = "0.10.2"
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
                 "evaluations/reports/2026-11-05-source-audit.md", "evaluations/reports/2026-11-05-source-audit.en.md",
                 "research/global-public-data.md", "research/global-public-data.en.md",
                 "research/china-public-sources.md", "research/china-public-sources.en.md",
                 "research/china-public-sources-2026-11-05.json", "research/china-public-index-probes-2026-11-05.json",
                 "references/source-status.md", "references/source-status.en.md",
                 "evaluations/reports/2026-11-05-source-status.json",
                 "scripts/benchmark.py", "evaluations/agent-search-cases.json", "evaluations/agent-search-cases.en.json",
                 "evaluations/reports/2026-11-08-agent-search.md", "evaluations/reports/2026-11-08-agent-search.en.md",
                 "evaluations/reports/2026-11-08-agent-search.data.json",
                 "evaluations/agent-search-cases-v2.json", "evaluations/agent-search-cases-v2.en.json",
                 "evaluations/agent-search-cases-v3.json", "evaluations/agent-search-cases-v3.en.json",
                 "evaluations/reports/2026-11-09-agent-search.md", "evaluations/reports/2026-11-09-agent-search.en.md",
                 "evaluations/reports/2026-11-09-agent-search.data.json",
                 "evaluations/reports/2026-11-09-public-source-check.json",
                 "evaluations/reports/2026-11-09-100-question-baseline.md",
                 "evaluations/reports/2026-11-09-100-question-baseline.en.md",
                 "evaluations/reports/2026-11-09-100-question-baseline.data.json",
                 "evaluations/reports/2026-11-09-exa-outage.md", "evaluations/reports/2026-11-09-exa-outage.en.md",
                 "evaluations/reports/2026-11-09-exa-outage.data.json",
                 "evaluations/reports/2026-11-10-parallel-no-exa.md", "evaluations/reports/2026-11-10-parallel-no-exa.en.md",
                 "evaluations/reports/2026-11-10-parallel-no-exa.data.json"]
RUNTIME_FILES += ['scripts/documentation_search.py', 'references/documentation.md', 'references/documentation.en.md',
                  'evaluations/reports/2026-11-16-keyless-search.md', 'evaluations/reports/2026-11-16-keyless-search.en.md',
                  'evaluations/reports/2026-11-16-keyless-search.data.json']
RUNTIME_FILES += ['scripts/native_search.py', 'references/china-site-search.md', 'references/china-site-search.en.md',
                  'evaluations/reports/2026-11-16-native-search.md', 'evaluations/reports/2026-11-16-native-search.en.md',
                  'evaluations/reports/2026-11-16-native-search.data.json']
SOURCE_EXTRA = ["tests/test_native_search.py", "tests/test_keyless_search.py", "evaluations/build_source_status.py", "evaluations/check_sources.py", "tests/test_source_status.py", ".gitignore",
                ".github/workflows/source-check.yml",
                ".github/workflows/test.yml", ".github/workflows/release.yml",
                "scripts/build_release.py", "scripts/prepare_release.py",
                "tests/test_search.py", "tests/test_release.py", "tests/test_providers.py",
                "tests/test_evaluation.py", "tests/test_routing.py", "scripts/evaluate.py", "evaluations/queries.json",
                "evaluations/README.md"]
RUNTIME_FILES += ['scripts/industry_search.py', 'references/industry-search.md', 'references/industry-search.en.md',
                  'evaluations/energy-procurement-cases.json',
                  'evaluations/reports/2026-11-16-energy-procurement.md',
                  'evaluations/reports/2026-11-16-energy-procurement.en.md',
                  'evaluations/reports/2026-11-16-energy-procurement.data.json']
SOURCE_EXTRA += ['tests/test_industry_search.py']


RUNTIME_FILES += ["README.en.md", "SKILL.en.md", "INSTALL.en.md", "TODO.en.md",
                  "CONTRIBUTING.en.md", "CHANGELOG.en.md", "VALIDATION.en.md",
                  "PUBLISHING.en.md", "MARKETPLACE.en.md", "references/setup.en.md",
                  "references/providers.en.md", "references/output.en.md",
                  "references/search-services.en.md"]
SOURCE_EXTRA += ["evaluations/README.en.md", "tests/test_benchmark.py",
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
RUNTIME_FILES += ['scripts/native_reader.py','scripts/research_evidence.py','scripts/research_workflow.py',
                  'scripts/manage_skill.py','scripts/source_health.py','references/source-health.json',
                  'references/research.md','references/research.en.md',
                  'references/agent-workflows.md','references/agent-workflows.en.md']
SOURCE_EXTRA += ['tests/test_research.py','tests/test_manage_skill.py','tests/test_source_health.py',
                 'evaluations/research-cases.json','evaluations/evaluate_research.py',
                 'evaluations/reports/2026-11-22-research.md','evaluations/reports/2026-11-22-research.en.md',
                 'evaluations/reports/2026-11-22-research.data.json']
SOURCE_EXTRA += ['tests/test_answer_review.py','evaluations/review_research.py',
                 'evaluations/research-cases-v2.json','evaluations/research-answer-reviews.json',
                 'evaluations/reports/2026-11-22-answer-support.data.json',
                 'evaluations/reports/2026-11-22-answer-support.md',
                 'evaluations/reports/2026-11-22-answer-support.en.md']
SOURCE_EXTRA += ['tests/test_followups.py','evaluations/research-followup-reviews.json',
                 'evaluations/reports/2026-11-22-followups.data.json',
                 'evaluations/reports/2026-11-22-followups.md','evaluations/reports/2026-11-22-followups.en.md']
FULL_FILES = sorted(set(RUNTIME_FILES + SOURCE_EXTRA))
# Historical evaluations and raw research belong to the source archive, not normal installation.
RUNTIME_FILES = [p for p in RUNTIME_FILES if not p.startswith(('evaluations/','research/')) and p!='scripts/benchmark.py']


def package_bytes(name, included, *, runtime=False):
    path=ROOT/name
    if path.is_symlink() or not path.is_file(): raise ValueError('Missing or unsafe release source: '+name)
    data=path.read_bytes()
    if runtime and name.endswith('.md'):
        def rewrite(match):
            target=match[1]
            if re.match(r'[a-z]+:',target) or target.startswith('#'): return match[0]
            relative,sep,anchor=target.partition('#')
            resolved=posixpath.normpath(posixpath.join(posixpath.dirname(name),relative))
            if resolved in FULL_FILES and resolved not in included:
                return '](https://github.com/wjason/xcoze-search/blob/v'+VERSION+'/'+resolved+('#'+anchor if sep else '')+')'
            return match[0]
        data=re.sub(r'\]\(([^)]+)\)',rewrite,data.decode('utf-8')).encode('utf-8')
    return data


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()
    target = args.output_dir.resolve()
    target.mkdir(parents=True, exist_ok=True)
    hashes = []
    for kind, names in (("skill", RUNTIME_FILES), ("source", FULL_FILES)):
        archive = target / ("xcoze-search-%s-v%s.zip" % (kind, VERSION))
        files={}
        with zipfile.ZipFile(archive, "w", compression=zipfile.ZIP_DEFLATED) as stream:
            for name in sorted(set(names)):
                path = ROOT / name
                if path.is_symlink() or not path.is_file():
                    raise SystemExit("Missing or unsafe release source: " + name)
                info = zipfile.ZipInfo("xcoze-search/" + name, date_time=(2026, 10, 24, 0, 0, 0))
                mode = 0o755 if name.endswith(".command") or name == "scripts/xcoze_search.py" else 0o644
                info.create_system = 3
                info.external_attr = (0o100000 | mode) << 16
                info.compress_type = zipfile.ZIP_DEFLATED
                data=package_bytes(name,set(names),runtime=kind=='skill')
                stream.writestr(info, data); files[name]=hashlib.sha256(data).hexdigest()
            info=zipfile.ZipInfo('xcoze-search/manifest.json',date_time=(2026,10,24,0,0,0))
            info.create_system=3;info.external_attr=(0o100000|0o644)<<16;info.compress_type=zipfile.ZIP_DEFLATED
            stream.writestr(info,json.dumps({'schema_version':1,'version':VERSION,
                'package':kind,'files':files},ensure_ascii=False,sort_keys=True,indent=2)+'\n')
        hashes.append(hashlib.sha256(archive.read_bytes()).hexdigest() + "  " + archive.name)
        print(archive)
    manifest = target / "SHA256SUMS.txt"
    manifest.write_text("\n".join(hashes) + "\n", encoding="utf-8")
    print(manifest)


if __name__ == "__main__":
    main()
