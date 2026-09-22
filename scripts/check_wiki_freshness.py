#!/usr/bin/env python3
"""위키 concept 페이지가 원 문서보다 낡았는지 검사한다.

이 저장소에서 사실의 SSOT 는 `docs/` 이고, `ai-workflow/wiki/concepts/` 는 그것을
개념 축으로 재색인한 계층이다 (wiki/SCHEMA.md §7). 원 문서가 바뀌었는데 재색인이
따라가지 않으면 위키는 조용히 거짓이 된다 — 이 스크립트가 그 상태를 잡는다.

대응 관계의 출처는 각 concept 페이지 frontmatter 의 `last_ingested_from` 이다.
별도 매핑 파일을 두지 않는다. 매핑이 두 곳에 있으면 그 둘이 갈린다.

모드
  (기본)     git 이력 비교. 원 문서의 마지막 커밋이 concept 페이지의 마지막 커밋보다
             나중이면 stale. 저장소 전체 감사용.
  --staged   staged 된 원 문서의 concept 페이지도 함께 staged 됐는지 검사. pre-commit 용.
  --paths    주어진 경로를 "방금 바뀐 것"으로 보고 재ingest 대상을 보고. 에디터 훅용.
  --hook     stdin 의 Claude Code PostToolUse JSON 에서 편집 경로를 뽑아 --paths 와
             같은 검사를 하고, 결과를 hook 출력 JSON 으로 낸다. 항상 0 으로 끝난다 —
             편집을 막는 것이 목적이 아니라 재색인이 남았음을 알리는 것이 목적이다.

종료 코드: 0 = 통과, 1 = 낡은 페이지 있음, 2 = 실행 오류
"""
from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path

WIKI_CONCEPTS = Path("ai-workflow/wiki/concepts")
# 조사 문서가 아니라 워크플로우 산출물이므로 "재색인 누락" 판정에서 뺀다.
NOT_RESEARCH = {"docs/PROJECT_PROFILE.md"}


def repo_root() -> Path:
    out = subprocess.run(
        ["git", "rev-parse", "--show-toplevel"],
        capture_output=True, text=True, check=True,
    )
    return Path(out.stdout.strip())


def load_mapping(root: Path) -> dict[str, list[str]]:
    """concept 페이지 → 그 페이지가 선언한 원 문서 목록."""
    mapping: dict[str, list[str]] = {}
    concepts_dir = root / WIKI_CONCEPTS
    if not concepts_dir.is_dir():
        return mapping
    for page in sorted(concepts_dir.glob("*.md")):
        text = page.read_text(encoding="utf-8")
        fm = re.match(r"^---\n(.*?)\n---", text, re.S)
        if not fm:
            continue
        m = re.search(r"^last_ingested_from:\s*(.+)$", fm.group(1), re.M)
        if not m:
            continue
        sources = [s.strip() for s in m.group(1).split("+")]
        rel = str(page.relative_to(root))
        mapping[rel] = [s for s in sources if s]
    return mapping


def last_commit_epoch(root: Path, path: str) -> int | None:
    out = subprocess.run(
        ["git", "log", "-1", "--format=%ct", "--", path],
        cwd=root, capture_output=True, text=True,
    )
    val = out.stdout.strip()
    return int(val) if val else None


def staged_paths(root: Path) -> set[str]:
    out = subprocess.run(
        ["git", "diff", "--cached", "--name-only", "--diff-filter=ACMR"],
        cwd=root, capture_output=True, text=True, check=True,
    )
    return {line.strip() for line in out.stdout.splitlines() if line.strip()}


def invert(mapping: dict[str, list[str]]) -> dict[str, list[str]]:
    """원 문서 → 그것을 ingest 한 concept 페이지 목록."""
    rev: dict[str, list[str]] = {}
    for page, sources in mapping.items():
        for src in sources:
            rev.setdefault(src, []).append(page)
    return rev


def check_history(root: Path, mapping: dict[str, list[str]]) -> list[dict]:
    """git 이력 기준: 원 문서가 concept 페이지보다 나중에 커밋됐으면 stale."""
    stale = []
    for page, sources in sorted(mapping.items()):
        page_t = last_commit_epoch(root, page)
        if page_t is None:
            continue  # 아직 커밋되지 않은 새 페이지 — 비교 대상이 없다
        newer = []
        for src in sources:
            if not (root / src).exists():
                newer.append({"source": src, "reason": "원 문서가 사라졌다"})
                continue
            src_t = last_commit_epoch(root, src)
            if src_t is not None and src_t > page_t:
                newer.append({"source": src, "reason": "원 문서가 더 나중에 커밋됐다"})
        if newer:
            stale.append({"page": page, "sources": newer})
    return stale


def check_staged(root: Path, mapping: dict[str, list[str]]) -> list[dict]:
    """pre-commit 기준: staged 된 원 문서의 concept 페이지도 함께 staged 됐는가."""
    staged = staged_paths(root)
    rev = invert(mapping)
    stale = []
    for src in sorted(staged & rev.keys()):
        missing = [p for p in rev[src] if p not in staged]
        if missing:
            stale.append({"source": src, "pages": missing})
    return stale


def check_paths(root: Path, mapping: dict[str, list[str]], paths: list[str]) -> list[dict]:
    """주어진 경로가 바뀌었을 때 재ingest 가 필요한 페이지."""
    rev = invert(mapping)
    norm = []
    for p in paths:
        pp = Path(p)
        if pp.is_absolute():
            try:
                pp = pp.relative_to(root)
            except ValueError:
                continue
        norm.append(str(pp))
    hits = []
    for src in sorted(set(norm) & rev.keys()):
        hits.append({"source": src, "pages": sorted(rev[src])})
    return hits


def uncovered(root: Path, mapping: dict[str, list[str]]) -> list[str]:
    """어떤 concept 페이지도 ingest 하지 않은 조사 문서."""
    covered = set(invert(mapping).keys())
    docs = {str(p.relative_to(root)) for p in (root / "docs").glob("*.md")}
    return sorted(docs - covered - NOT_RESEARCH)


def run_hook(args) -> int:
    """Claude Code PostToolUse 훅. 편집을 막지 않고 재색인 잔여만 알린다."""
    try:
        payload = json.load(sys.stdin)
    except (json.JSONDecodeError, ValueError):
        return 0
    edited = (payload.get("tool_response") or {}).get("filePath") \
        or (payload.get("tool_input") or {}).get("file_path")
    if not edited:
        return 0
    try:
        root = repo_root()
    except subprocess.CalledProcessError:
        return 0
    mapping = load_mapping(root)
    if not mapping:
        return 0
    hits = check_paths(root, mapping, [edited])
    if not hits:
        return 0
    pages = sorted({p for h in hits for p in h["pages"]})
    src = hits[0]["source"]
    note = (
        f"{src} 를 고쳤다. 이 문서를 ingest 한 concept 페이지가 이제 낡았다: "
        + ", ".join(pages)
        + ". 위키는 docs/ 의 재색인이므로(ai-workflow/wiki/SCHEMA.md §7) 같은 작업 안에서 "
        "해당 페이지를 재ingest 하고 frontmatter 의 updated 를 올린다. "
        "사실이 바뀌지 않은 편집(오타·서식)이면 재색인 없이 넘어가도 된다."
    )
    print(json.dumps({
        "systemMessage": f"위키 재색인 필요: {', '.join(Path(p).stem for p in pages)}",
        "hookSpecificOutput": {
            "hookEventName": "PostToolUse",
            "additionalContext": note,
        },
    }, ensure_ascii=False))
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    g = ap.add_mutually_exclusive_group()
    g.add_argument("--staged", action="store_true",
                   help="staged 된 원 문서 기준 검사 (pre-commit)")
    g.add_argument("--paths", nargs="+", metavar="PATH",
                   help="이 경로들이 바뀐 것으로 보고 검사 (에디터 훅)")
    g.add_argument("--hook", action="store_true",
                   help="stdin 의 PostToolUse JSON 을 읽어 hook 출력 JSON 을 낸다")
    ap.add_argument("--json", action="store_true", help="JSON 으로 출력")
    ap.add_argument("--show-uncovered", action="store_true",
                   help="어떤 concept 페이지도 다루지 않는 문서를 함께 보고")
    args = ap.parse_args()

    if args.hook:
        return run_hook(args)

    try:
        root = repo_root()
    except subprocess.CalledProcessError:
        print("git 저장소가 아니다.", file=sys.stderr)
        return 2

    mapping = load_mapping(root)
    if not mapping:
        # 위키 계층이 없는 저장소에서는 할 일이 없다. 통과로 둔다.
        if args.json:
            print(json.dumps({"mode": "none", "stale": [], "note": "concept 페이지 없음"},
                             ensure_ascii=False))
        return 0

    if args.staged:
        mode, stale = "staged", check_staged(root, mapping)
    elif args.paths:
        mode, stale = "paths", check_paths(root, mapping, args.paths)
    else:
        mode, stale = "history", check_history(root, mapping)

    result = {"mode": mode, "stale": stale, "concept_pages": len(mapping)}
    if args.show_uncovered:
        result["uncovered_docs"] = uncovered(root, mapping)

    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        if not stale:
            print(f"✅ 위키 재색인 최신 (concept {len(mapping)}종, mode={mode})")
        elif mode == "history":
            print(f"⚠️  원 문서보다 낡은 concept 페이지 {len(stale)}건:\n")
            for item in stale:
                print(f"  {item['page']}")
                for s in item["sources"]:
                    print(f"    ← {s['source']} — {s['reason']}")
            print("\n해당 페이지를 재ingest 하고 frontmatter 의 updated 를 올린다.")
        else:
            print(f"⚠️  재ingest 가 필요한 concept 페이지:\n")
            for item in stale:
                print(f"  {item['source']} 를 고쳤다 →")
                for p in item["pages"]:
                    print(f"    {p}")
            if mode == "staged":
                print("\n같은 커밋에 포함시키거나, 의도한 것이면 --no-verify 로 건너뛴다.")
        if args.show_uncovered and result["uncovered_docs"]:
            print(f"\nℹ️  어떤 concept 페이지도 다루지 않는 문서 {len(result['uncovered_docs'])}건:")
            for d in result["uncovered_docs"]:
                print(f"    {d}")

    return 1 if stale else 0


if __name__ == "__main__":
    sys.exit(main())
