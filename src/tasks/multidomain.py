# src/tasks/multidomain.py
from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Any, List
import random
import time


@dataclass
class MultiDomainConfig:
    serial_start: int = 100
    serial_step: int = 7
    serial_n: int = 5

    digit_span_len: int = 6

    trail_n: int = 6  # will generate 1..N and A..(A+N-1)
    seed: int | None = None


def _normalize(text: str) -> str:
    return "".join(ch for ch in text.strip().lower() if ch.isalnum())


def run_multidomain_task(
    participant_id: str,
    config: MultiDomainConfig = MultiDomainConfig(),
    *,
    input_fn=input,
    print_fn=print
) -> Dict[str, Any]:
    rng = random.Random(config.seed)
    start_time = time.perf_counter()

    print_fn("\n=== Multi-domain Screening ===")
    total_points = 0
    max_points = 0
    raw: Dict[str, Any] = {}

    # 1) Serial subtraction
    print_fn("\nPart 1: Serial subtraction")
    print_fn(f"Start at {config.serial_start} and subtract {config.serial_step} each time.")
    current = config.serial_start
    serial_answers = []
    for i in range(config.serial_n):
        ans = input_fn(f"Step {i+1}: {current} - {config.serial_step} = ").strip()
        serial_answers.append(ans)
        current -= config.serial_step

    # score
    correct_serial = 0
    expected = []
    cur = config.serial_start
    for _ in range(config.serial_n):
        cur -= config.serial_step
        expected.append(cur)

    for given, exp in zip(serial_answers, expected):
        try:
            if int(given) == exp:
                correct_serial += 1
        except ValueError:
            pass

    max_points += config.serial_n
    total_points += correct_serial
    raw["serial"] = {"answers": serial_answers, "expected": expected, "correct": correct_serial}

    # 2) Digit span (forward)
    print_fn("\nPart 2: Digit span (forward)")
    digits = [str(rng.randint(0, 9)) for _ in range(config.digit_span_len)]
    print_fn("Memorize these digits:")
    print_fn(" ".join(digits))
    time.sleep(3.0)
    print_fn("\n" * 20)
    typed = input_fn("Type the digits in the same order (no spaces needed): ")
    typed_norm = _normalize(typed)
    expected_norm = "".join(digits)

    digit_correct = 1 if typed_norm == expected_norm else 0
    max_points += 1
    total_points += digit_correct
    raw["digit_span"] = {"digits": digits, "typed": typed, "correct": digit_correct}

    # 3) Trail-making lite (alternating sequence)
    # True Trails is visuomotor; here we approximate executive switching as a sequence rule.
    print_fn("\nPart 3: Alternating sequence (executive switching)")
    nums = list(range(1, config.trail_n + 1))
    letters = [chr(ord("a") + i) for i in range(config.trail_n)]
    expected_seq = []
    for n, L in zip(nums, letters):
        expected_seq.append(str(n))
        expected_seq.append(L)

    print_fn("Type the alternating sequence like: 1 a 2 b 3 c ...")
    typed = input_fn("Your sequence: ")
    typed_tokens = _normalize(typed).replace(" ", "")
    expected_tokens = "".join(expected_seq)

    # score as proportion correct by position (leniency)
    # compare token-by-token (characters) is messy; use token list comparison instead:
    typed_list = [t for t in typed.strip().lower().replace(",", " ").split() if t]
    # allow without spaces: if they typed "1a2b3c"
    if len(typed_list) <= 2:
        # fallback: split characters into tokens like ["1","a","2","b",...]
        typed_list = list(_normalize(typed))

    pos_correct = 0
    for i in range(min(len(typed_list), len(expected_seq))):
        if typed_list[i] == expected_seq[i]:
            pos_correct += 1

    max_points += len(expected_seq)
    total_points += pos_correct
    raw["trail"] = {
        "expected_seq": expected_seq,
        "typed_tokens": typed_list,
        "pos_correct": pos_correct
    }

    elapsed = time.perf_counter() - start_time

    return {
        "task": "multidomain_screen",
        "participant_id": participant_id,
        "score": total_points,
        "max_score": max_points,
        "metrics": {
            "percent": (total_points / max_points) if max_points else None,
            "elapsed_seconds": elapsed
        },
        "raw": raw
    }
