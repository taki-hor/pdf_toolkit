"""
快速測試腳本 - 驗證 PDF Toolkit 主要功能。

會根據當前環境判斷必要依賴與測試檔案是否就緒，
若缺少依賴則將對應測試標記為「略過」，避免誤判失敗。
"""

from __future__ import annotations

import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from shutil import which
from typing import Iterable, Mapping, Sequence


@dataclass(frozen=True)
class TestCase:
    label: str
    command: str
    requires: Sequence[str] = ()
    needs_input_pdf: bool = True


DEPENDENCY_GROUPS: Mapping[str, Sequence[str]] = {
    "fitz": ("fitz",),
    "pikepdf": ("pikepdf",),
}

TEST_CASES: Sequence[TestCase] = (
    TestCase("查詢資訊", "python pdf_toolkit.py info test.pdf", requires=("fitz",)),
    TestCase(
        "合併 PDF",
        "python pdf_toolkit.py merge test.pdf test.pdf -o test_output/merged.pdf",
        requires=("fitz",),
    ),
    TestCase(
        "拆分單頁",
        "python pdf_toolkit.py split test.pdf -d test_output/split_single/",
        requires=("fitz",),
    ),
    TestCase(
        "拆分範圍",
        'python pdf_toolkit.py split test.pdf -d test_output/split_range/ -p "1-3,5-6"',
        requires=("fitz",),
    ),
    TestCase(
        "刪除頁面",
        'python pdf_toolkit.py delete test.pdf -p "1,3,5" -o test_output/deleted.pdf',
        requires=("fitz",),
    ),
    TestCase(
        "旋轉頁面",
        'python pdf_toolkit.py rotate test.pdf -p "1-3" -a 90 -o test_output/rotated.pdf',
        requires=("fitz",),
    ),
    TestCase(
        "添加水印",
        'python pdf_toolkit.py watermark test.pdf -t "DRAFT" -o test_output/watermarked.pdf',
        requires=("fitz",),
    ),
    TestCase(
        "壓縮優化",
        "python pdf_toolkit.py optimize test.pdf -o test_output/optimized.pdf",
        requires=("pikepdf",),
    ),
)


def command_available(executable: str) -> bool:
    """Return True if the given executable is discoverable on PATH."""
    return which(executable) is not None


def check_dependencies() -> dict[str, bool]:
    """Detect whether required third-party packages are importable."""
    availability: dict[str, bool] = {}
    for name in DEPENDENCY_GROUPS:
        availability[name] = all(_importable(mod) for mod in DEPENDENCY_GROUPS[name])
    return availability


def _importable(module_name: str) -> bool:
    try:
        __import__(module_name)
    except ImportError:
        return False
    return True


def ensure_fixture_directory() -> None:
    Path("test_output").mkdir(parents=True, exist_ok=True)


def run_command(label: str, command: str) -> bool:
    """Execute a shell command and stream the output."""
    print("\n" + "=" * 72)
    print(f"[執行] {label}: {command}")
    print("=" * 72)
    result = subprocess.run(command, shell=True, text=True)
    if result.returncode != 0:
        print(f"✗ 指令失敗（代碼 {result.returncode}）")
        return False
    print("✓ 指令執行成功")
    return True


def summarize(passed: int, failed: int, skipped: int) -> None:
    total = passed + failed + skipped
    print("\n測試結束")
    print(f"總計：{total}，通過：{passed}，失敗：{failed}，略過：{skipped}")


def missing_dependencies(requirements: Iterable[str], availability: Mapping[str, bool]) -> Sequence[str]:
    return [dep for dep in requirements if not availability.get(dep, False)]


def main() -> int:
    """Run the quick test suite."""
    ensure_fixture_directory()
    dependency_status = check_dependencies()

    if not command_available("python"):
        print("❗ 找不到 python 指令，請確認環境設定。")
        return 1

    if not Path("test.pdf").exists():
        print("⚠ 找不到測試檔案 test.pdf，將略過需要此檔案的測試。")

    print("快速測試開始")

    passed = 0
    failed = 0
    skipped = 0

    for case in TEST_CASES:
        print(f"\n>>> 測試項目：{case.label}")

        missing = missing_dependencies(case.requires, dependency_status)
        if missing:
            print(f"⚠ 略過：缺少依賴 {', '.join(missing)}")
            skipped += 1
            continue

        if case.needs_input_pdf and not Path("test.pdf").exists():
            print("⚠ 略過：需要 test.pdf 才能執行此測試。")
            skipped += 1
            continue

        if run_command(case.label, case.command):
            passed += 1
        else:
            failed += 1

    summarize(passed, failed, skipped)
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
