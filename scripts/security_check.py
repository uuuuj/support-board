#!/usr/bin/env python
"""보안 검사 스크립트.

모든 보안 도구를 실행하고 결과를 요약합니다.
"""

import subprocess
import sys


def run_command(name, command):
    """명령어 실행 및 결과 반환."""
    print(f"\n{'=' * 50}")
    print(f"실행: {name}")
    print('=' * 50)

    try:
        result = subprocess.run(
            command,
            shell=True,
            capture_output=True,
            text=True
        )
        print(result.stdout)
        if result.stderr:
            print(result.stderr)
        return result.returncode == 0
    except Exception as e:
        print(f"에러: {e}")
        return False


def main():
    """메인 함수."""
    results = []

    # 1. Bandit - 보안 취약점 스캔
    success = run_command(
        "Bandit (보안 취약점 스캔)",
        "bandit -r support_board config -c .bandit"
    )
    results.append(("Bandit", success))

    # 2. pip-audit - 의존성 취약점 검사
    success = run_command(
        "pip-audit (의존성 취약점)",
        "pip-audit"
    )
    results.append(("pip-audit", success))

    # 3. Safety - 의존성 취약점 검사 (대안)
    success = run_command(
        "Safety (의존성 취약점)",
        "safety check"
    )
    results.append(("Safety", success))

    # 4. Flake8 - 코드 품질
    success = run_command(
        "Flake8 (코드 품질)",
        "flake8 support_board config"
    )
    results.append(("Flake8", success))

    # 5. detect-secrets - 민감정보 탐지
    success = run_command(
        "detect-secrets (민감정보 탐지)",
        "detect-secrets scan --all-files --exclude-files '\\.env.*' --exclude-files 'node_modules/.*' --exclude-files 'staticfiles/.*'"
    )
    results.append(("detect-secrets", success))

    # 결과 요약
    print(f"\n{'=' * 50}")
    print("보안 검사 결과 요약")
    print('=' * 50)

    all_passed = True
    for name, passed in results:
        status = "PASS" if passed else "FAIL"
        icon = "[PASS]" if passed else "[FAIL]"
        print(f"{icon} {name}")
        if not passed:
            all_passed = False

    print('=' * 50)

    return 0 if all_passed else 1


if __name__ == "__main__":
    sys.exit(main())
