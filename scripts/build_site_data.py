#!/usr/bin/env python3
"""Build deterministic, file://-compatible portal data from the skill catalog.

Only Python's standard library is used. The generated JavaScript is data-only:
no functions, network requests, third-party packages, or build-time runtime.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
SKILLS_ROOT = ROOT / "skills"
OUTPUT = ROOT / "docs" / "data" / "skills_data.js"
ID_PATTERN = re.compile(r"^[a-z0-9-]+$")
PLACEHOLDER_PATTERN = re.compile(
    r"\{\{\s*([a-zA-Z0-9_-]+)(?::(plus|underscore))?\s*\}\}"
)


class BuildError(ValueError):
    """A catalog validation error with an actionable path."""


def read_utf8(path: Path, *, reject_bom: bool = True) -> str:
    raw = path.read_bytes()
    if reject_bom and raw.startswith(b"\xef\xbb\xbf"):
        raise BuildError(f"UTF-8 BOM is not allowed: {path.relative_to(ROOT)}")
    try:
        return raw.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise BuildError(f"Invalid UTF-8: {path.relative_to(ROOT)}: {exc}") from exc


def load_json(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(read_utf8(path))
    except json.JSONDecodeError as exc:
        raise BuildError(f"Invalid JSON: {path.relative_to(ROOT)}: {exc}") from exc
    if not isinstance(value, dict):
        raise BuildError(f"JSON root must be an object: {path.relative_to(ROOT)}")
    return value


def parse_scalar(value: str) -> str:
    value = value.strip()
    if len(value) >= 2 and value[0] == value[-1] == "'":
        return value[1:-1].replace("''", "'")
    if len(value) >= 2 and value[0] == value[-1] == '"':
        try:
            return json.loads(value)
        except json.JSONDecodeError:
            return value[1:-1]
    return value


def parse_frontmatter(path: Path) -> dict[str, str]:
    """Parse the small YAML subset used by skill frontmatter (no PyYAML)."""
    text = read_utf8(path)
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        raise BuildError(f"Missing YAML frontmatter: {path.relative_to(ROOT)}")
    try:
        end = next(i for i in range(1, len(lines)) if lines[i].strip() == "---")
    except StopIteration as exc:
        raise BuildError(f"Unclosed YAML frontmatter: {path.relative_to(ROOT)}") from exc

    result: dict[str, str] = {}
    index = 1
    while index < end:
        line = lines[index]
        match = re.match(r"^([A-Za-z0-9_-]+):\s*(.*)$", line)
        if not match:
            index += 1
            continue
        key, value = match.group(1), match.group(2).strip()
        if value in {">", ">-", ">+", "|", "|-", "|+"}:
            continuation: list[str] = []
            index += 1
            while index < end and (not lines[index] or lines[index][0].isspace()):
                continuation.append(lines[index].strip())
                index += 1
            separator = "\n" if value.startswith("|") else " "
            result[key] = separator.join(part for part in continuation if part).strip()
            continue
        result[key] = parse_scalar(value)
        index += 1

    for required in ("name", "description"):
        if not result.get(required):
            raise BuildError(
                f"Frontmatter '{required}' is required: {path.relative_to(ROOT)}"
            )
    return result


def chinese_alias(description: str, fallback: str) -> str:
    match = re.search(r"【([^】]+)】", description)
    return match.group(1).strip() if match else fallback


def validate_id(value: str, path: Path) -> None:
    if not ID_PATTERN.fullmatch(value):
        raise BuildError(
            f"Directory name must match ^[a-z0-9-]+$: {path.relative_to(ROOT)}"
        )


def fallback_meta(skill_id: str, frontmatter: dict[str, str]) -> dict[str, Any]:
    description = frontmatter["description"]
    alias = chinese_alias(description, skill_id)
    return {
        "name": skill_id,
        "alias": alias,
        "stage": None,
        "stageName": "独立 Skill",
        "tagline": description,
        "description": description,
        "audience": "需要按该 SKILL.md 完成专项任务的用户。",
        "inputs": ["用户提供的任务说明与相关材料"],
        "outputs": ["按 SKILL.md 约定生成的结果"],
        "tags": ["独立 Skill"],
        "inputArtifact": "任务说明与相关材料",
        "action": description,
        "outputArtifact": "按 SKILL.md 约定生成的结果",
        "handoffLabel": "独立 Skill 产物",
        "next": None,
        "nextText": "",
        "why": [
            {
                "pain": "任务要求散落：需要在对话中反复补充约束。",
                "benefit": "以 SKILL.md 固定任务输入、步骤与交付边界。",
            },
            {
                "pain": "执行过程难复用：每次重新组织流程，操作顺序容易漂移。",
                "benefit": "复用仓库内确定的流程、脚本与知识库。",
            },
            {
                "pain": "结果结构不统一：同类任务的输出格式随对话变化。",
                "benefit": "按技能约定生成可检查、可接续的产物。",
            },
        ],
        "phases": [
            {
                "name": "Phase 0",
                "title": "按技能说明执行",
                "text": "读取 SKILL.md，核对输入与依赖，按说明执行并生成约定产物。",
            }
        ],
        "promptFields": [
            {
                "key": "task",
                "label": "任务说明",
                "type": "text",
                "default": "",
                "placeholder": "例如：请描述任务目标、输入路径与预期产出",
            }
        ],
        "promptTemplate": (
            f"请使用 ${skill_id} 完成以下任务。\n"
            "任务说明：{{task}}\n\n"
            "请严格遵循该 Skill 的 SKILL.md，先核对输入与依赖，再执行流程并生成约定产物。"
        ),
        "preview": {
            "title": f"{skill_id} / 预期产物",
            "headers": ["项目", "内容"],
            "rows": [
                ["输入", "任务说明与相关材料"],
                ["输出", "按 SKILL.md 约定生成的结果"],
            ],
        },
    }


def file_kind(relative_path: str) -> str:
    if relative_path == "SKILL.md":
        return "skill"
    if relative_path == "USER_USE.md":
        return "user"
    if relative_path.startswith("scripts/") and relative_path.endswith(".py"):
        return "script"
    if relative_path.startswith("references/") and relative_path.endswith(".md"):
        return "reference"
    if relative_path.startswith("examples/") and relative_path.endswith(".md"):
        return "example"
    return "file"


def inventory_files(
    skill_dir: Path, meta: dict[str, Any]
) -> list[dict[str, str]]:
    descriptions = meta.get("fileDescriptions", [])
    if not isinstance(descriptions, list):
        raise BuildError(f"fileDescriptions must be an array: {skill_dir}")

    description_map: dict[str, str] = {}
    ordered_paths: list[str] = []
    for item in descriptions:
        if not isinstance(item, dict) or not isinstance(item.get("path"), str):
            raise BuildError(f"Invalid fileDescriptions entry: {skill_dir}")
        relative = item["path"].replace("\\", "/")
        candidate = skill_dir / Path(relative)
        if relative.startswith("/") or ".." in Path(relative).parts:
            raise BuildError(f"Unsafe file path '{relative}': {skill_dir}")
        if not candidate.is_file():
            raise BuildError(
                f"Declared file does not exist: {candidate.relative_to(ROOT)}"
            )
        if relative not in description_map:
            ordered_paths.append(relative)
        description_map[relative] = item.get("desc") or "技能文件"

    scanned: set[str] = set()
    for candidate in skill_dir.rglob("*"):
        if not candidate.is_file() or "__pycache__" in candidate.parts:
            continue
        relative = candidate.relative_to(skill_dir).as_posix()
        if file_kind(relative) != "file":
            scanned.add(relative)

    for relative in sorted(scanned):
        if relative not in description_map:
            ordered_paths.append(relative)
            description_map[relative] = {
                "skill": "技能触发、边界与执行规程",
                "user": "安装与使用说明",
                "script": "技能自动化脚本",
                "reference": "技能知识库",
                "example": "结构示例",
            }.get(file_kind(relative), "技能文件")

    return [
        {
            "path": relative,
            "kind": file_kind(relative),
            "desc": description_map[relative],
        }
        for relative in ordered_paths
    ]


def validate_prompt(meta: dict[str, Any], skill_dir: Path) -> None:
    template = meta.get("promptTemplate")
    fields = meta.get("promptFields")
    if not isinstance(template, str) or not template.strip():
        raise BuildError(f"promptTemplate is required: {skill_dir}")
    if not isinstance(fields, list) or not fields:
        raise BuildError(f"promptFields must be a non-empty array: {skill_dir}")
    keys: set[str] = set()
    for field in fields:
        if not isinstance(field, dict) or not isinstance(field.get("key"), str):
            raise BuildError(f"Invalid prompt field: {skill_dir}")
        if field.get("type") not in {"checkboxes", "select", "text", "number"}:
            raise BuildError(f"Unsupported prompt field type: {skill_dir}: {field}")
        keys.add(field["key"])

    computed = meta.get("promptComputed", {})
    if not isinstance(computed, dict):
        raise BuildError(f"promptComputed must be an object: {skill_dir}")
    for key, rule in computed.items():
        if (
            not isinstance(rule, dict)
            or rule.get("field") not in keys
            or not isinstance(rule.get("cases"), dict)
            or not isinstance(rule.get("default"), str)
            or not all(isinstance(value, str) for value in rule["cases"].values())
        ):
            raise BuildError(f"Invalid computed prompt value '{key}': {skill_dir}")
    keys.update(computed)

    for match in PLACEHOLDER_PATTERN.finditer(template):
        if match.group(1) not in keys:
            raise BuildError(
                f"Unknown prompt placeholder '{match.group(1)}': {skill_dir}"
            )
    if PLACEHOLDER_PATTERN.sub("", template).find("{{") >= 0:
        raise BuildError(f"Malformed prompt placeholder: {skill_dir}")


def build_skill(
    skill_dir: Path, category: dict[str, Any], seen_ids: dict[str, Path]
) -> dict[str, Any]:
    skill_id = skill_dir.name
    validate_id(skill_id, skill_dir)
    if skill_id in seen_ids:
        raise BuildError(
            f"Duplicate skill id '{skill_id}': {seen_ids[skill_id]} and {skill_dir}"
        )
    seen_ids[skill_id] = skill_dir

    skill_md = skill_dir / "SKILL.md"
    frontmatter = parse_frontmatter(skill_md)
    if frontmatter["name"] != skill_id:
        raise BuildError(
            f"Frontmatter name '{frontmatter['name']}' != directory '{skill_id}': "
            f"{skill_md.relative_to(ROOT)}"
        )

    meta_path = skill_dir / "skill.meta.json"
    meta = load_json(meta_path) if meta_path.is_file() else fallback_meta(skill_id, frontmatter)
    if meta.get("name") != skill_id:
        raise BuildError(f"Metadata name must equal '{skill_id}': {meta_path}")
    validate_prompt(meta, skill_dir)
    files = inventory_files(skill_dir, meta)

    skill = {key: value for key, value in meta.items() if key != "fileDescriptions"}
    skill.pop("name", None)
    skill.update(
        {
            "id": skill_id,
            "category": category["id"],
            "categoryName": category["name"],
            "repoPath": f"skills/{category['id']}/{skill_id}",
            "scriptCount": sum(file["kind"] == "script" for file in files),
            "files": files,
            "install": {
                "windows": f".\\scripts\\install_skills.ps1 -Skill {skill_id}",
                "bash": f"./scripts/install_skills.sh --skill {skill_id}",
            },
        }
    )
    return skill


def site_data() -> dict[str, Any]:
    return {
        "scenarios": [
            {
                "icon": "radar",
                "title": "不知道读什么，怕错过跨域新机会",
                "description": "顶会与跨域论文太分散，想先得到有评分、有证据、能去重的阅读短名单。",
                "skill": "cross-domain-paper-radar-codex",
                "keyword": "论文雷达",
            },
            {
                "icon": "lightbulb",
                "title": "只有一个模糊想法，不知道能否投稿",
                "description": "需要先查新、判断 Track A/B，再决定完整蓝图还是收敛方案。",
                "skill": "hsi-msi-idea-scout-codex",
                "keyword": "选题与查新",
            },
            {
                "icon": "book",
                "title": "论文读了不少，却难以横向比较",
                "description": "退化模型、数据集、指标与 Agent 循环散落在不同笔记里。",
                "skill": "hsi-agent-paper-reader-codex",
                "keyword": "论文精读",
            },
            {
                "icon": "wrench",
                "title": "论文机制有了，代码仓库接不进去",
                "description": "需要核对张量形状、退化公式、显存瓶颈与 Agent 工具接口。",
                "skill": "hsi-repo-surgeon-codex",
                "keyword": "仓库诊断",
            },
            {
                "icon": "chart",
                "title": "PSNR 上升，SAM 却变差",
                "description": "总分掩盖了逐波段、逐像元误差，需要从物理成因定位问题。",
                "skill": "hsi-exp-diagnostician-codex",
                "keyword": "实验诊断",
            },
            {
                "icon": "shield",
                "title": "投稿前想先挨一次严格审稿",
                "description": "需要遥感物理、CV 方法论、Agent 系统三视角独立挑错。",
                "skill": "hsi-agent-reviewer-codex",
                "keyword": "三视角审稿",
            },
        ],
        "faqs": [
            {
                "q": "安装后怎样触发某个 Skill？",
                "a": "安装到 ~/.codex/skills 后重启 Codex，在对话中使用 $<skill-id>，或直接描述对应任务。可用 scripts/install_skills.ps1 -List 或 scripts/install_skills.sh --list 查看当前目录。",
            },
            {
                "q": "新增 Skill 后必须手工修改网站数据吗？",
                "a": "不需要。运行 python scripts/build_site_data.py 即可重新扫描二级目录。新 Skill 即使尚未编写 skill.meta.json，也会从 SKILL.md frontmatter 生成默认卡片与基础 Prompt；补充元数据后可获得完整中文介绍、工作流和结构化预览。",
            },
            {
                "q": "所有脚本都零外部依赖吗？",
                "a": "核心检索、查新、台账与仓库扫描脚本仅使用 Python 标准库。hsi-exp-diagnostician-codex 的指标与出图脚本按需使用 numpy/matplotlib；网页本身零外部运行依赖、零 CDN。",
            },
            {
                "q": "本地双击 HTML 会出现 CORS 错误吗？",
                "a": "不会。构建器把分类、Skill 与站点配置直接挂载到 window.CATEGORIES_DATA、window.SKILLS_DATA 与 window.SITE_DATA，前端不 fetch 本地 JSON，因此 file:// 与 GitHub Pages 使用同一份数据。",
            },
            {
                "q": "新分类会自动进入科研闭环吗？",
                "a": "只有 category.json 中 hasWorkflow=true 且包含带 stage 的 Skill 才进入专题工作流。多个闭环分类会显示切换 Tab；独立 Skill 保留普通卡片与详情，不强行赋予上下游关系。",
            },
        ],
        "globalInstall": {
            "title": "一次性安装整个分类，或全部目录化 Skill",
            "description": "安装脚本把 skills/<category>/<skill-id> 扁平复制到 Codex Skills 第一层，排除 __pycache__ 与 *.pyc；重复安装会刷新同名目标目录。",
            "windows": ".\\scripts\\install_skills.ps1 -All",
            "bash": "./scripts/install_skills.sh --all",
            "note": "核心检索、查新、台账与仓库扫描脚本零外部 Python 依赖；指标出图脚本按需安装 numpy/matplotlib。安装后重启 Codex。",
        },
        "networkConfig": {
            "title": "让检索类 Skill 可以联网",
            "description": "雷达扫描、Idea 查新与论文 Metadata 补全需要联网。请在 Codex 配置中显式开启网络访问。",
            "windowsPath": "%USERPROFILE%\\.codex\\config.toml",
            "unixPath": "~/.codex/config.toml",
            "toml": "[sandbox_workspace_write]\nnetwork_access = true",
            "note": "若日志出现 <urlopen error [Errno 11001] getaddrinfo failed>，请检查此配置与 DNS；修改后重启 Codex。",
        },
    }


def build_catalog(root: Path = ROOT) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    """Build from an arbitrary root; the optional root also enables isolated tests."""
    global ROOT
    original_root = ROOT
    ROOT = root.resolve()
    try:
        skills_root = ROOT / "skills"
        if not skills_root.is_dir():
            raise BuildError(f"Missing skills directory: {skills_root}")
        categories: list[dict[str, Any]] = []
        skills: list[dict[str, Any]] = []
        seen_ids: dict[str, Path] = {}

        for category_dir in sorted(path for path in skills_root.iterdir() if path.is_dir()):
            validate_id(category_dir.name, category_dir)
            category_path = category_dir / "category.json"
            category = (
                load_json(category_path)
                if category_path.is_file()
                else {
                    "id": category_dir.name,
                    "name": category_dir.name,
                    "description": "独立 Skill 分类",
                    "hasWorkflow": False,
                    "order": 99,
                    "accent": "slate",
                }
            )
            if category.get("id") != category_dir.name:
                raise BuildError(f"Category id must match directory: {category_path}")
            category.setdefault("name", category_dir.name)
            category.setdefault("description", "独立 Skill 分类")
            category.setdefault("hasWorkflow", False)
            category.setdefault("order", 99)
            category.setdefault("accent", "slate")

            category_skills = [
                build_skill(skill_dir, category, seen_ids)
                for skill_dir in sorted(path for path in category_dir.iterdir() if path.is_dir())
                if (skill_dir / "SKILL.md").is_file()
            ]
            category_skills.sort(
                key=lambda skill: (
                    skill.get("stage") is None,
                    skill.get("stage") if skill.get("stage") is not None else 999,
                    skill["id"],
                )
            )
            category["skillCount"] = len(category_skills)
            categories.append(category)
            skills.extend(category_skills)

        categories.sort(key=lambda category: (category["order"], category["id"]))
        category_order = {category["id"]: index for index, category in enumerate(categories)}
        skills.sort(
            key=lambda skill: (
                category_order[skill["category"]],
                skill.get("stage") is None,
                skill.get("stage") if skill.get("stage") is not None else 999,
                skill["id"],
            )
        )
        return categories, skills
    finally:
        ROOT = original_root


def render_javascript(categories: list[dict[str, Any]], skills: list[dict[str, Any]]) -> str:
    def serialize(value: Any) -> str:
        return json.dumps(value, ensure_ascii=False, indent=2)

    return (
        "/* AUTO-GENERATED by scripts/build_site_data.py. DO NOT EDIT. */\n"
        "/* Sources: skills/<category>/<skill-id>/SKILL.md + category.json + skill.meta.json */\n"
        '(function () {\n  "use strict";\n\n'
        f"  window.CATEGORIES_DATA = {serialize(categories)};\n\n"
        f"  window.SKILLS_DATA = {serialize(skills)};\n\n"
        f"  window.SITE_DATA = {serialize(site_data())};\n"
        "})();\n"
    )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--check", action="store_true", help="validate and fail if generated output is stale"
    )
    args = parser.parse_args()
    try:
        categories, skills = build_catalog()
        generated = render_javascript(categories, skills)
        if args.check:
            if not OUTPUT.is_file() or read_utf8(OUTPUT) != generated:
                raise BuildError(
                    "docs/data/skills_data.js is stale; run python scripts/build_site_data.py"
                )
            print(
                f"Check passed: {len(categories)} categories, {len(skills)} skills, "
                f"{sum(skill['scriptCount'] for skill in skills)} scripts; output is current."
            )
        else:
            OUTPUT.parent.mkdir(parents=True, exist_ok=True)
            OUTPUT.write_text(generated, encoding="utf-8", newline="\n")
            print(
                f"Generated {OUTPUT.relative_to(ROOT)}: {len(categories)} categories, "
                f"{len(skills)} skills, {sum(skill['scriptCount'] for skill in skills)} scripts."
            )
        return 0
    except (BuildError, OSError) as exc:
        print(f"Build failed: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
