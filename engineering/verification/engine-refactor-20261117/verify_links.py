"""Check local Markdown links in the task evidence and changed owner documents."""
import json
from pathlib import Path
import re
from urllib.parse import unquote, urlsplit

ROOT = Path(__file__).resolve().parents[3]
EVIDENCE = Path(__file__).resolve().parent


def main():
    paths = [*EVIDENCE.rglob("*.md"), ROOT / "engineering/docs/architecture/technical-architecture.md",
             ROOT / "engineering/docs/architecture/ui-ux-reference.md", ROOT / "engineering/docs/development/testing.md"]
    checked, missing = [], []
    for path in paths:
        lines, fence = [], None
        for line in path.read_text(encoding="utf-8").splitlines():
            mark = re.match(r"^\s*(`{3,}|~{3,})", line)
            if mark:
                token = mark[1]
                if fence is None:
                    fence = token
                elif token[0] == fence[0] and len(token) >= len(fence):
                    fence = None
                continue
            if fence is None:
                lines.append(line)
        text = re.sub(r"`[^`\n]+`", "", "\n".join(lines))
        for target in re.findall(r"!?\[[^\]]*\]\(([^)]+)\)", text):
            target = target.strip().strip("<>")
            if target.startswith("#") or urlsplit(target).scheme:
                continue
            local = unquote(target.split("#", 1)[0])
            resolved = (path.parent / local).resolve()
            row = dict(source=str(path.relative_to(ROOT)), target=target)
            checked.append(row)
            if not resolved.exists():
                missing.append(row)
    result = dict(status="FAIL" if missing else "PASS", checked=len(checked), missing=missing)
    (EVIDENCE / "link-verification.json").write_text(json.dumps(result, indent=2), encoding="utf-8")
    print(json.dumps(result))
    assert not missing


if __name__ == "__main__":
    main()
