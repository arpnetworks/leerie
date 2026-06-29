{
  "preprocess": {
    "path": "orchestrator/leerie.py",
    "sha256": "18dde36ed6fd9a5f3a428d49c883cac35702154d1be408233377cef688f6626e",
    "lines": 15321,
    "bytes": 712534,
    "module_doc": "Leerie \u2014 deterministic task orchestrator for Claude Code."
  },
  "lex": {
    "total_tokens": 82896,
    "token_class_counts": {
      "OP": 30184,
      "NAME": 24189,
      "NL": 7014,
      "NEWLINE": 5882,
      "STRING": 5071,
      "COMMENT": 2727,
      "INDENT": 1871,
      "DEDENT": 1871,
      "FSTRING_MIDDLE": 1632,
      "FSTRING_START": 947,
      "FSTRING_END": 947,
      "NUMBER": 560,
      "ENDMARKER": 1
    },
    "keyword_counts": {
      "if": 1038,
      "in": 673,
      "None": 581,
      "return": 506,
      "for": 501,
      "not": 438,
      "or": 381,
      "def": 298,
      "and": 170,
      "is": 155,
      "await": 152,
      "True": 126,
      "except": 125,
      "continue": 120,
      "else": 119,
      "try": 115,
      "False": 85,
      "async": 81,
      "raise": 54,
      "as": 41,
      "break": 35,
      "pass": 31,
      "elif": 31,
      "import": 25,
      "with": 18
    },
    "top_identifiers": {
      "str": 779,
      "get": 756,
      "dict": 417,
      "st": 379,
      "sid": 296,
      "r": 275,
      "append": 275,
      "list": 266,
      "s": 262,
      "repo_root": 247,
      "data": 190,
      "len": 173,
      "Path": 167,
      "log": 166,
      "e": 154,
      "caps": 147,
      "int": 136,
      "out": 116,
      "args": 112,
      "plans": 110,
      "set": 106,
      "die": 105,
      "self": 103,
      "strip": 99,
      "plan": 97,
      "join": 92,
      "entry": 89,
      "f": 89,
      "parts": 80,
      "p": 79,
      "output": 79,
      "c": 78,
      "line": 77,
      "bool": 72,
      "leerie_dir": 72,
      "models": 69,
      "efforts": 69,
      "name": 65,
      "tag": 65,
      "run_id": 64,
      "is_file": 63,
      "cli_value": 63,
      "v": 62,
      "ValueError": 61,
      "save": 61,
      "w": 60,
      "subtasks": 60,
      "lines": 59,
      "tuple": 58,
      "i": 58,
      "n": 57,
      "json": 56,
      "proc": 56,
      "asyncio": 55,
      "result": 55,
      "issues": 55,
      "isinstance": 54,
      "cwd": 53,
      "dep": 53,
      "text": 52
    },
    "top_operators": {
      "(": 4455,
      ")": 4455,
      ",": 3954,
      ":": 3648,
      ".": 2777,
      "=": 2715,
      "[": 1796,
      "]": 1796,
      "{": 1616,
      "}": 1616,
      "->": 288,
      "/": 204,
      "|": 165,
      "==": 158,
      "!": 129,
      "+": 92,
      "*": 55,
      "!=": 52,
      "-": 46,
      ">": 39,
      "+=": 36,
      "<": 34,
      ">=": 18,
      "<=": 16,
      "**": 9
    },
    "comment_chars": 156745,
    "string_literal_count": 5071,
    "env_vars": [
      "LEERIE_CLARIFY",
      "LEERIE_CONFIDENCE_ROUNDS",
      "LEERIE_DANGEROUSLY_SKIP_PERMISSIONS",
      "LEERIE_EFFORT",
      "LEERIE_EFFORT_",
      "LEERIE_HEAL_DIR",
      "LEERIE_HEAL_MAX_ROUNDS",
      "LEERIE_HEAL_SUCCESS_THRESHOLD",
      "LEERIE_IMPLEMENTER_CONFIDENCE_RETRIES",
      "LEERIE_INSPECT_DIRS",
      "LEERIE_JUDGE_DIR",
      "LEERIE_JUDGMENT_CHECK_ROUNDS",
      "LEERIE_MAX_PARALLEL",
      "LEERIE_MAX_WORKERS",
      "LEERIE_MODEL",
      "LEERIE_MODEL_",
      "LEERIE_MODEL_HEAL",
      "LEERIE_MODEL_JUDGE",
      "LEERIE_MODEL_PR_WRITER",
      "LEERIE_NO_PUSH",
      "LEERIE_PLANNER_CHECK_ROUNDS",
      "LEERIE_PLANNER_SAMPLES",
      "LEERIE_PR_TEMPLATE",
      "LEERIE_RUNTIME",
      "LEERIE_SKIP_BUDGET_CHECK",
      "LEERIE_SKIP_OVERLAP_JUDGE",
      "LEERIE_SOURCE_OF_TRUTH",
      "LEERIE_STATE_DIR",
      "LEERIE_STATE_HOST_DIR",
      "LEERIE_STRICT_CONFORMER",
      "LEERIE_TELEMETRY",
      "LEERIE_TELEMETRY_DIR",
      "LEERIE_VERBOSITY",
      "LEERIE_WORKER_DEBUG",
      "LEERIE_WORKER_MEMORY_MAX"
    ],
    "exit_symbols": [
      "EXIT_BUDGET_INFEASIBLE",
      "EXIT_LOCKED",
      "EXIT_NEEDS_ANSWERS"
    ]
  },
  "ast": {
    "node_class_counts": {
      "Load": 15800,
      "Name": 13583,
      "Constant": 7276,
      "Call": 3693,
      "Store": 2822,
      "Attribute": 2776,
      "Assign": 1788,
      "Expr": 1204,
      "Subscript": 1190,
      "FormattedValue": 1128,
      "If": 914,
      "arg": 699,
      "keyword": 654,
      "Compare": 639,
      "JoinedStr": 636,
      "List": 535,
      "Tuple": 521,
      "BinOp": 515,
      "Return": 506,
      "BoolOp": 485,
      "Dict": 446,
      "Or": 332,
      "For": 331,
      "arguments": 312,
      "UnaryOp": 281,
      "Not": 252,
      "FunctionDef": 225,
      "Div": 204,
      "AnnAssign": 201,
      "comprehension": 167,
      "BitOr": 166,
      "Eq": 158,
      "And": 153,
      "Await": 152,
      "Add": 128,
      "ExceptHandler": 125,
      "Continue": 120,
      "Try": 115,
      "IsNot": 113,
      "In": 99,
      "IfExp": 79,
      "AsyncFunctionDef": 73,
      "NotIn": 73,
      "ListComp": 71,
      "GeneratorExp": 67,
      "Raise": 54,
      "NotEq": 52,
      "Slice": 43,
      "Is": 42,
      "AugAssign": 40,
      "Gt": 39,
      "alias": 35,
      "Break": 35,
      "Lt": 34,
      "Pass": 31,
      "USub": 29,
      "Mult": 23,
      "Starred": 19,
      "Import": 18,
      "withitem": 18,
      "GtE": 18,
      "Sub": 18,
      "LtE": 16,
      "While": 15,
      "SetComp": 15,
      "DictComp": 14,
      "Lambda": 14,
      "Set": 13,
      "With": 13,
      "ClassDef": 8,
      "ImportFrom": 7,
      "Pow": 6,
      "FloorDiv": 5,
      "AsyncWith": 5,
      "BitAnd": 5,
      "AsyncFor": 3,
      "Nonlocal": 3,
      "Global": 2,
      "Delete": 2,
      "Del": 2,
      "Module": 1,
      "Yield": 1,
      "NamedExpr": 1
    },
    "imports": [
      "from __future__ import annotations",
      "argparse",
      "asyncio",
      "contextlib",
      "copy",
      "fcntl",
      "json",
      "os",
      "re",
      "shutil",
      "signal",
      "subprocess",
      "sys",
      "time",
      "uuid",
      "from collections import deque",
      "from collections.abc import Awaitable, Callable, Iterator",
      "from datetime import datetime, timedelta, timezone",
      "from pathlib import Path",
      "from zoneinfo import ZoneInfo, ZoneInfoNotFoundError",
      "from tenacity import AsyncRetrying, RetryCallState, RetryError, retry_if_result, stop_after_delay, wait_exponential_jitter"
    ],
    "constant_count": 147,
    "function_count": 237,
    "class_count": 8
  },
  "constants": [
    {
      "name": "ROOT",
      "lineno": 52,
      "kind": "expr",
      "expr": "Path(__file__).resolve().parent.parent"
    },
    {
      "name": "PROMPTS",
      "lineno": 53,
      "kind": "expr",
      "expr": "ROOT / 'prompts'"
    },
    {
      "name": "SCRIPTS",
      "lineno": 54,
      "kind": "expr",
      "expr": "ROOT / 'scripts'"
    },
    {
      "name": "_PROMPT_INCLUDE_RE",
      "lineno": 72,
      "kind": "expr",
      "expr": "re.compile('\\\\{\\\\{\\\\s*include:\\\\s*(_[a-z0-9_]+\\\\.md)\\\\s*\\\\}\\\\}')"
    },
    {
      "name": "MIN_CLAUDE_CLI",
      "lineno": 91,
      "kind": "tuple",
      "len": 3,
      "values": [
        2,
        1,
        22
      ]
    },
    {
      "name": "DEFAULT_CAPS",
      "lineno": 94,
      "kind": "dict",
      "len": 17,
      "keys": [
        "max_total_workers",
        "max_parallel",
        "subtask_continuations",
        "failed_retries",
        "conformance_rounds",
        "judgment_check_rounds",
        "planner_check_rounds",
        "implementer_confidence_retries",
        "planner_samples",
        "worker_timeout_sec",
        "worker_idle_warn_sec",
        "confidence_rounds",
        "worker_memory_max_bytes",
        "worker_pids_max",
        "auth_retry_max_sec",
        "subtask_call_estimate",
        "budget_safety_margin"
      ]
    },
    {
      "name": "STATE_FIELDS",
      "lineno": 202,
      "kind": "tuple",
      "len": 35,
      "values": [
        "task",
        "started_at",
        "finished_at",
        "waves",
        "completed_waves",
        "subtask_status",
        "blocked",
        "worker_count",
        "telemetry",
        "categories",
        "classifier_questions",
        "answers",
        "needs_source_of_truth",
        "source_of_truth_pref",
        "clarify",
        "dangerously_skip_permissions",
        "skip_overlap_judge",
        "skip_budget_check",
        "strict_conformer",
        "verbosity",
        "inspect_dirs",
        "integrator_warnings",
        "scope_warnings",
        "conformance",
        "provision",
        "external_preconditions",
        "current_phase",
        "dropped_subtasks",
        "conditional_drops",
        "plan_overlap_judge",
        "plan_overlap_applied",
        "no_work_required",
        "no_work_reasons",
        "working_branch",
        "leerie_version"
      ]
    },
    {
      "name": "CATEGORIES",
      "lineno": 273,
      "kind": "list",
      "len": 9,
      "values": [
        "feature-implementation",
        "bug-fixing",
        "refactoring",
        "performance-optimization",
        "testing",
        "dependency-migration",
        "configuration-build",
        "infrastructure",
        "documentation"
      ]
    },
    {
      "name": "CATEGORY_ABBREV",
      "lineno": 282,
      "kind": "dict",
      "len": 9,
      "keys": [
        "feature-implementation",
        "bug-fixing",
        "refactoring",
        "performance-optimization",
        "testing",
        "dependency-migration",
        "configuration-build",
        "infrastructure",
        "documentation"
      ]
    },
    {
      "name": "_PROTECTED_PREFIXES",
      "lineno": 308,
      "kind": "tuple",
      "len": 2,
      "values": [
        ".leerie/",
        ".git/"
      ]
    },
    {
      "name": "_CLAUDE_DELIVERABLE_PREFIXES",
      "lineno": 309,
      "kind": "tuple",
      "len": 3,
      "values": [
        ".claude/agents/",
        ".claude/commands/",
        ".claude/skills/"
      ]
    },
    {
      "name": "_READ_BASE",
      "lineno": 324,
      "kind": "str",
      "value": "Read,Grep,Glob,WebSearch,WebFetch"
    },
    {
      "name": "INSPECT_TOOLS",
      "lineno": 342,
      "kind": "expr",
      "expr": "f'{_READ_BASE},Bash(ls:*),Bash(find:*),Bash(cat:*),Bash(head:*),Bash(tail:*),Bash(wc:*),Bash(grep:*),Bash(rg:*),Bash(file:*),Bash(stat:*),Bash(tree:*),Bash(pwd),Bash(echo:*),Bash(git log:*),Bash(git s"
    },
    {
      "name": "ACT_TOOLS",
      "lineno": 350,
      "kind": "expr",
      "expr": "f'{_READ_BASE},Bash,Write,Edit'"
    },
    {
      "name": "INSPECT_DIRS_ENV",
      "lineno": 359,
      "kind": "str",
      "value": "LEERIE_INSPECT_DIRS"
    },
    {
      "name": "INSPECT_DIRS_FILE",
      "lineno": 360,
      "kind": "str",
      "value": "leerie.toml"
    },
    {
      "name": "EXIT_NEEDS_ANSWERS",
      "lineno": 362,
      "kind": "int",
      "value": 10
    },
    {
      "name": "EXIT_BUDGET_INFEASIBLE",
      "lineno": 373,
      "kind": "int",
      "value": 11
    },
    {
      "name": "EXIT_LOCKED",
      "lineno": 381,
      "kind": "int",
      "value": 75
    },
    {
      "name": "SOURCE_OF_TRUTH_VALUES",
      "lineno": 389,
      "kind": "tuple",
      "len": 3,
      "values": [
        "codebase",
        "research",
        "both"
      ]
    },
    {
      "name": "SOURCE_OF_TRUTH_ENV",
      "lineno": 390,
      "kind": "str",
      "value": "LEERIE_SOURCE_OF_TRUTH"
    },
    {
      "name": "SOURCE_OF_TRUTH_FILE",
      "lineno": 391,
      "kind": "str",
      "value": "leerie.toml"
    },
    {
      "name": "RUNTIME_VALUES",
      "lineno": 396,
      "kind": "tuple",
      "len": 2,
      "values": [
        "local",
        "fly"
      ]
    },
    {
      "name": "RUNTIME_ENV",
      "lineno": 397,
      "kind": "str",
      "value": "LEERIE_RUNTIME"
    },
    {
      "name": "RUNTIME_FILE",
      "lineno": 398,
      "kind": "expr",
      "expr": "SOURCE_OF_TRUTH_FILE"
    },
    {
      "name": "CONFIDENCE_ROUNDS_ENV",
      "lineno": 405,
      "kind": "str",
      "value": "LEERIE_CONFIDENCE_ROUNDS"
    },
    {
      "name": "CONFIDENCE_ROUNDS_FILE",
      "lineno": 406,
      "kind": "expr",
      "expr": "SOURCE_OF_TRUTH_FILE"
    },
    {
      "name": "JUDGMENT_CHECK_ROUNDS_ENV",
      "lineno": 409,
      "kind": "str",
      "value": "LEERIE_JUDGMENT_CHECK_ROUNDS"
    },
    {
      "name": "PLANNER_CHECK_ROUNDS_ENV",
      "lineno": 410,
      "kind": "str",
      "value": "LEERIE_PLANNER_CHECK_ROUNDS"
    },
    {
      "name": "IMPLEMENTER_CONFIDENCE_RETRIES_ENV",
      "lineno": 411,
      "kind": "str",
      "value": "LEERIE_IMPLEMENTER_CONFIDENCE_RETRIES"
    },
    {
      "name": "PLANNER_SAMPLES_ENV",
      "lineno": 412,
      "kind": "str",
      "value": "LEERIE_PLANNER_SAMPLES"
    },
    {
      "name": "MAX_WORKERS_ENV",
      "lineno": 417,
      "kind": "str",
      "value": "LEERIE_MAX_WORKERS"
    },
    {
      "name": "MAX_WORKERS_FILE",
      "lineno": 418,
      "kind": "expr",
      "expr": "SOURCE_OF_TRUTH_FILE"
    },
    {
      "name": "MAX_PARALLEL_ENV",
      "lineno": 423,
      "kind": "str",
      "value": "LEERIE_MAX_PARALLEL"
    },
    {
      "name": "MAX_PARALLEL_FILE",
      "lineno": 424,
      "kind": "expr",
      "expr": "SOURCE_OF_TRUTH_FILE"
    },
    {
      "name": "WORKER_MEMORY_MAX_ENV",
      "lineno": 431,
      "kind": "str",
      "value": "LEERIE_WORKER_MEMORY_MAX"
    },
    {
      "name": "WORKER_MEMORY_MAX_FILE",
      "lineno": 432,
      "kind": "expr",
      "expr": "SOURCE_OF_TRUTH_FILE"
    },
    {
      "name": "NO_PUSH_ENV",
      "lineno": 440,
      "kind": "str",
      "value": "LEERIE_NO_PUSH"
    },
    {
      "name": "NO_PUSH_FILE",
      "lineno": 441,
      "kind": "expr",
      "expr": "SOURCE_OF_TRUTH_FILE"
    },
    {
      "name": "CLARIFY_ENV",
      "lineno": 449,
      "kind": "str",
      "value": "LEERIE_CLARIFY"
    },
    {
      "name": "CLARIFY_FILE",
      "lineno": 450,
      "kind": "expr",
      "expr": "SOURCE_OF_TRUTH_FILE"
    },
    {
      "name": "DANGEROUS_SKIP_PERMS_ENV",
      "lineno": 460,
      "kind": "str",
      "value": "LEERIE_DANGEROUSLY_SKIP_PERMISSIONS"
    },
    {
      "name": "DANGEROUS_SKIP_PERMS_FILE",
      "lineno": 461,
      "kind": "expr",
      "expr": "SOURCE_OF_TRUTH_FILE"
    },
    {
      "name": "SKIP_OVERLAP_JUDGE_ENV",
      "lineno": 470,
      "kind": "str",
      "value": "LEERIE_SKIP_OVERLAP_JUDGE"
    },
    {
      "name": "SKIP_OVERLAP_JUDGE_FILE",
      "lineno": 471,
      "kind": "expr",
      "expr": "SOURCE_OF_TRUTH_FILE"
    },
    {
      "name": "SKIP_BUDGET_CHECK_ENV",
      "lineno": 483,
      "kind": "str",
      "value": "LEERIE_SKIP_BUDGET_CHECK"
    },
    {
      "name": "SKIP_BUDGET_CHECK_FILE",
      "lineno": 484,
      "kind": "expr",
      "expr": "SOURCE_OF_TRUTH_FILE"
    },
    {
      "name": "STRICT_CONFORMER_ENV",
      "lineno": 486,
      "kind": "str",
      "value": "LEERIE_STRICT_CONFORMER"
    },
    {
      "name": "STRICT_CONFORMER_FILE",
      "lineno": 487,
      "kind": "expr",
      "expr": "SOURCE_OF_TRUTH_FILE"
    },
    {
      "name": "PR_TEMPLATE_ENV",
      "lineno": 496,
      "kind": "str",
      "value": "LEERIE_PR_TEMPLATE"
    },
    {
      "name": "PR_TEMPLATE_FILE",
      "lineno": 497,
      "kind": "expr",
      "expr": "SOURCE_OF_TRUTH_FILE"
    },
    {
      "name": "VERBOSITY_VALUES",
      "lineno": 505,
      "kind": "tuple",
      "len": 4,
      "values": [
        "quiet",
        "normal",
        "stream",
        "debug"
      ]
    },
    {
      "name": "VERBOSITY_DEFAULT",
      "lineno": 506,
      "kind": "str",
      "value": "stream"
    },
    {
      "name": "VERBOSITY_ENV",
      "lineno": 507,
      "kind": "str",
      "value": "LEERIE_VERBOSITY"
    },
    {
      "name": "VERBOSITY_FILE",
      "lineno": 508,
      "kind": "expr",
      "expr": "SOURCE_OF_TRUTH_FILE"
    },
    {
      "name": "_TERMINAL_STATUSES",
      "lineno": 511,
      "kind": "expr",
      "expr": "frozenset({'complete', 'failed', 'blocked'})"
    },
    {
      "name": "MODEL_VALUES",
      "lineno": 517,
      "kind": "tuple",
      "len": 3,
      "values": [
        "sonnet",
        "opus",
        "haiku"
      ]
    },
    {
      "name": "MODEL_DEFAULT",
      "lineno": 524,
      "kind": "str",
      "value": "opus"
    },
    {
      "name": "MODEL_DEFAULT_PER_WORKER",
      "lineno": 528,
      "kind": "dict",
      "len": 5,
      "keys": [
        "implementer",
        "conformer",
        "judge",
        "heal",
        "pr_writer"
      ]
    },
    {
      "name": "MODEL_ENV",
      "lineno": 535,
      "kind": "str",
      "value": "LEERIE_MODEL"
    },
    {
      "name": "MODEL_FILE",
      "lineno": 536,
      "kind": "str",
      "value": "leerie.toml"
    },
    {
      "name": "EFFORT_VALUES",
      "lineno": 544,
      "kind": "tuple",
      "len": 5,
      "values": [
        "low",
        "medium",
        "high",
        "xhigh",
        "max"
      ]
    },
    {
      "name": "EFFORT_DEFAULT",
      "lineno": 545,
      "kind": "NoneType",
      "value": null
    },
    {
      "name": "EFFORT_DEFAULT_PER_WORKER",
      "lineno": 546,
      "kind": "dict",
      "len": 7,
      "keys": [
        "classifier",
        "planner",
        "reconciler",
        "plan_overlap_judge",
        "provision",
        "integrator",
        "pr_writer"
      ]
    },
    {
      "name": "EFFORT_ENV",
      "lineno": 555,
      "kind": "str",
      "value": "LEERIE_EFFORT"
    },
    {
      "name": "WORKER_TYPES",
      "lineno": 556,
      "kind": "tuple",
      "len": 8,
      "values": [
        "classifier",
        "planner",
        "reconciler",
        "plan_overlap_judge",
        "provision",
        "implementer",
        "integrator",
        "conformer"
      ]
    },
    {
      "name": "MODEL_JUDGE_ENV",
      "lineno": 561,
      "kind": "str",
      "value": "LEERIE_MODEL_JUDGE"
    },
    {
      "name": "MODEL_HEAL_ENV",
      "lineno": 562,
      "kind": "str",
      "value": "LEERIE_MODEL_HEAL"
    },
    {
      "name": "MODEL_PR_WRITER_ENV",
      "lineno": 563,
      "kind": "str",
      "value": "LEERIE_MODEL_PR_WRITER"
    },
    {
      "name": "TELEMETRY_DEFAULT",
      "lineno": 570,
      "kind": "bool",
      "value": true
    },
    {
      "name": "TELEMETRY_ENV",
      "lineno": 571,
      "kind": "str",
      "value": "LEERIE_TELEMETRY"
    },
    {
      "name": "TELEMETRY_FILE",
      "lineno": 572,
      "kind": "str",
      "value": "leerie.toml"
    },
    {
      "name": "TELEMETRY_SUBDIR_DEFAULT",
      "lineno": 577,
      "kind": "str",
      "value": "events"
    },
    {
      "name": "TELEMETRY_SUBDIR_ENV",
      "lineno": 578,
      "kind": "str",
      "value": "LEERIE_TELEMETRY_DIR"
    },
    {
      "name": "TELEMETRY_SUBDIR_FILE",
      "lineno": 579,
      "kind": "str",
      "value": "leerie.toml"
    },
    {
      "name": "JUDGE_DIR_DEFAULT",
      "lineno": 584,
      "kind": "str",
      "value": "judge-out"
    },
    {
      "name": "JUDGE_DIR_ENV",
      "lineno": 585,
      "kind": "str",
      "value": "LEERIE_JUDGE_DIR"
    },
    {
      "name": "JUDGE_DIR_FILE",
      "lineno": 586,
      "kind": "str",
      "value": "leerie.toml"
    },
    {
      "name": "HEAL_DIR_DEFAULT",
      "lineno": 591,
      "kind": "str",
      "value": "heal-out"
    },
    {
      "name": "HEAL_DIR_ENV",
      "lineno": 592,
      "kind": "str",
      "value": "LEERIE_HEAL_DIR"
    },
    {
      "name": "HEAL_DIR_FILE",
      "lineno": 593,
      "kind": "str",
      "value": "leerie.toml"
    },
    {
      "name": "HEAL_MAX_ROUNDS_DEFAULT",
      "lineno": 598,
      "kind": "int",
      "value": 10
    },
    {
      "name": "HEAL_SUCCESS_THRESHOLD_DEFAULT",
      "lineno": 599,
      "kind": "float",
      "value": 0.9
    },
    {
      "name": "HEAL_PLATEAU_WINDOW_DEFAULT",
      "lineno": 600,
      "kind": "int",
      "value": 3
    },
    {
      "name": "HEAL_PLATEAU_DELTA_DEFAULT",
      "lineno": 601,
      "kind": "float",
      "value": 0.03
    },
    {
      "name": "HEAL_N_REPLAYS_DEFAULT",
      "lineno": 602,
      "kind": "int",
      "value": 5
    },
    {
      "name": "HEAL_MAX_ROUNDS_ENV",
      "lineno": 603,
      "kind": "str",
      "value": "LEERIE_HEAL_MAX_ROUNDS"
    },
    {
      "name": "HEAL_SUCCESS_THRESHOLD_ENV",
      "lineno": 604,
      "kind": "str",
      "value": "LEERIE_HEAL_SUCCESS_THRESHOLD"
    },
    {
      "name": "HEAL_MAX_ROUNDS_FILE",
      "lineno": 605,
      "kind": "str",
      "value": "leerie.toml"
    },
    {
      "name": "HEAL_SUCCESS_THRESHOLD_FILE",
      "lineno": 606,
      "kind": "str",
      "value": "leerie.toml"
    },
    {
      "name": "STATE_DIR_ENV",
      "lineno": 614,
      "kind": "str",
      "value": "LEERIE_STATE_DIR"
    },
    {
      "name": "_CONFORMER_BLT_PROP",
      "lineno": 647,
      "kind": "dict",
      "len": 3,
      "keys": [
        "type",
        "required",
        "properties"
      ]
    },
    {
      "name": "_REQUIRES_ITEM",
      "lineno": 666,
      "kind": "dict",
      "len": 3,
      "keys": [
        "type",
        "required",
        "properties"
      ]
    },
    {
      "name": "SCHEMAS",
      "lineno": 702,
      "kind": "dict",
      "len": 11,
      "keys": [
        "classifier",
        "planner",
        "reconciler",
        "implementer",
        "integrator",
        "judge",
        "conformer",
        "patch_generator",
        "pr_writer",
        "provision",
        "plan_overlap_judge"
      ]
    },
    {
      "name": "_SESSION_LIMIT_PREFIX",
      "lineno": 1369,
      "kind": "expr",
      "expr": "re.compile(\"you've hit your session limit\", re.IGNORECASE)"
    },
    {
      "name": "_SESSION_LIMIT_RESET",
      "lineno": 1371,
      "kind": "expr",
      "expr": "re.compile('resets?\\\\s+(\\\\d{1,2}):(\\\\d{2})\\\\s*([ap]m)\\\\s*\\\\(([^)]+)\\\\)', re.IGNORECASE)"
    },
    {
      "name": "_RATE_LIMIT_ALLOWED_STATUSES",
      "lineno": 1380,
      "kind": "tuple",
      "len": 2,
      "values": [
        "allowed",
        "allowed_warning"
      ]
    },
    {
      "name": "_PROC_TREE_GRACE_SEC",
      "lineno": 1438,
      "kind": "float",
      "value": 2.0
    },
    {
      "name": "_DESCENDANT_POLL_SEC",
      "lineno": 1495,
      "kind": "float",
      "value": 0.5
    },
    {
      "name": "RUN_STATUSES",
      "lineno": 2303,
      "kind": "tuple",
      "len": 11,
      "values": [
        "seed-failed",
        "corrupt-sidecar",
        "in-progress",
        "done",
        "done-pushed-no-pr",
        "done-pushed-pr",
        "push-failed",
        "pr-failed",
        "paused",
        "killed",
        "sync-failed"
      ]
    },
    {
      "name": "TASK_FILE_SUFFIXES",
      "lineno": 2483,
      "kind": "tuple",
      "len": 2,
      "values": [
        ".txt",
        ".md"
      ]
    },
    {
      "name": "_MEMORY_SUFFIX_MULTIPLIER",
      "lineno": 2738,
      "kind": "dict",
      "len": 5,
      "keys": [
        "",
        "K",
        "M",
        "G",
        "T"
      ]
    },
    {
      "name": "_ID_PREFIXES",
      "lineno": 3613,
      "kind": "expr",
      "expr": "frozenset((f'{v}-' for v in CATEGORY_ABBREV.values()))"
    },
    {
      "name": "_VALID_EXTENTS",
      "lineno": 3616,
      "kind": "expr",
      "expr": "frozenset({'in_plan', 'external'})"
    },
    {
      "name": "_MIGRATION_SIGNAL_RE",
      "lineno": 3699,
      "kind": "expr",
      "expr": "re.compile('replac(?:es?|ing)\\\\s+(?:direct\\\\s+)?[`\\'\\\\\"]?([a-zA-Z_][a-zA-Z0-9_.]*)[`\\'\\\\\"]?|migrat(?:es?|ing)\\\\s+from\\\\s+[`\\'\\\\\"]?([a-zA-Z_][a-zA-Z0-9_.]*)[`\\'\\\\\"]?|extract(?:s|ing)\\\\s+[`\\'\\\\\"]?([a-zA"
    },
    {
      "name": "_MIGRATION_SURFACE_THRESHOLD",
      "lineno": 3707,
      "kind": "int",
      "value": 5
    },
    {
      "name": "_GLOB_CHARS",
      "lineno": 4042,
      "kind": "expr",
      "expr": "frozenset('*?[{')"
    },
    {
      "name": "_BRACE_RE",
      "lineno": 4043,
      "kind": "expr",
      "expr": "re.compile('\\\\{([^}]+)\\\\}')"
    },
    {
      "name": "_MAX_COVERAGE_ITEMS",
      "lineno": 4131,
      "kind": "int",
      "value": 50
    },
    {
      "name": "_ENV_TAG_KEYWORDS",
      "lineno": 4325,
      "kind": "expr",
      "expr": "frozenset({'env', 'bootstrap', 'secret', 'config-key', 'credential'})"
    },
    {
      "name": "_PROVISION_ARGV0_ALLOW",
      "lineno": 4454,
      "kind": "expr",
      "expr": "frozenset({'pnpm', 'npm', 'yarn', 'pip', 'pip3', 'uv', 'poetry', 'pipenv', 'go', 'cargo', 'bundle', 'gem', 'mvn', 'gradle', 'gradlew', 'make', 'composer', 'dotnet'})"
    },
    {
      "name": "_PROVISION_SHELL_METACHARS",
      "lineno": 4465,
      "kind": "expr",
      "expr": "frozenset(set('|&;$`><\\n\\r'))"
    },
    {
      "name": "_README_SECTION_RE",
      "lineno": 4662,
      "kind": "expr",
      "expr": "re.compile('(?i)\\\\b(install|getting[\\\\s-]?started|quick[\\\\s-]?start|setup|usage|\\\\brun\\\\b|develop|build(ing)?( from source| instructions)?|compil(e|ing)( from source)?|download|from source|requirement"
    },
    {
      "name": "_HEADER_DECOR_RE",
      "lineno": 4687,
      "kind": "expr",
      "expr": "re.compile('^[^\\\\w]+', flags=re.UNICODE)"
    },
    {
      "name": "_INSTALL_CMD_HINT_RE",
      "lineno": 4692,
      "kind": "expr",
      "expr": "re.compile('\\\\b(pip|pip3|npm|pnpm|yarn|uv|poetry|cargo|brew|apt|apt-get|dnf|yum|pacman|go install|make|bundle install|gem install|mise install)\\\\b')"
    },
    {
      "name": "_README_INTRO_BUDGET",
      "lineno": 4805,
      "kind": "int",
      "value": 1024
    },
    {
      "name": "_README_EXTRACT_BUDGET",
      "lineno": 4806,
      "kind": "int",
      "value": 8192
    },
    {
      "name": "_README_FALLBACK_BUDGET",
      "lineno": 4807,
      "kind": "int",
      "value": 6144
    },
    {
      "name": "_FIXTURE_TOTAL_BUDGET",
      "lineno": 4808,
      "kind": "int",
      "value": 24576
    },
    {
      "name": "_PROVISION_ROOT_MANIFESTS",
      "lineno": 4882,
      "kind": "tuple",
      "len": 9,
      "values": [
        "package.json",
        "pyproject.toml",
        "go.mod",
        "Cargo.toml",
        "Gemfile",
        "Makefile",
        "pom.xml",
        "build.gradle",
        "build.gradle.kts"
      ]
    },
    {
      "name": "_PROVISION_WORKFLOW_PREFERRED_RE",
      "lineno": 4887,
      "kind": "expr",
      "expr": "re.compile('(?i)\\\\b(ci|test|build|release)\\\\b')"
    },
    {
      "name": "_PROVISION_WORKFLOW_SKIP_RE",
      "lineno": 4888,
      "kind": "expr",
      "expr": "re.compile('(?i)\\\\b(codeql|stale|dependabot)\\\\b')"
    },
    {
      "name": "_CHECKPOINT_SECTIONS",
      "lineno": 5044,
      "kind": "list",
      "len": 7,
      "values": [
        "## Frozen success criteria",
        "## Current status",
        "## Files touched",
        "## Decisions made",
        "## Evidence gate status",
        "## Next action",
        "## Open unknowns"
      ]
    },
    {
      "name": "_CHECKPOINT_SECTIONS_ALLOW_NONE",
      "lineno": 5057,
      "kind": "set",
      "len": 2,
      "values": [
        "## Decisions made",
        "## Open unknowns"
      ]
    },
    {
      "name": "_NOISE_TOKENS",
      "lineno": 5065,
      "kind": "set",
      "len": 12,
      "values": [
        "none",
        "n/a",
        "na",
        "tbd",
        "nothing",
        "unknown",
        "todo",
        "pending",
        "\u2014",
        "--",
        "-",
        "?"
      ]
    },
    {
      "name": "_CGROUP_ROOT",
      "lineno": 5833,
      "kind": "expr",
      "expr": "Path('/sys/fs/cgroup')"
    },
    {
      "name": "_CGROUP_DELEGATED_SLICE",
      "lineno": 5834,
      "kind": "expr",
      "expr": "Path('/sys/fs/cgroup/leerie.slice')"
    },
    {
      "name": "_CGROUP_PROBE_RESULT",
      "lineno": 5835,
      "kind": "NoneType",
      "value": null
    },
    {
      "name": "_CGROUP_DETECTED_ROOT",
      "lineno": 5836,
      "kind": "NoneType",
      "value": null
    },
    {
      "name": "_DOCS_ONLY_CATEGORIES",
      "lineno": 7621,
      "kind": "expr",
      "expr": "frozenset({'documentation'})"
    },
    {
      "name": "_GO_MOD_VERSION_RE",
      "lineno": 7698,
      "kind": "expr",
      "expr": "re.compile('^\\\\s*go\\\\s+(\\\\d+(?:\\\\.\\\\d+){0,2})\\\\s*$', re.MULTILINE)"
    },
    {
      "name": "_LEADING_V_RE",
      "lineno": 7753,
      "kind": "expr",
      "expr": "re.compile('^[vV]+')"
    },
    {
      "name": "_IDIOMATIC_VERSION_FILES",
      "lineno": 7764,
      "kind": "tuple",
      "len": 4,
      "values": [
        "('.nvmrc', 'node', lambda s: _LEADING_V_RE.sub('', s))",
        "('.node-version', 'node', lambda s: _LEADING_V_RE.sub('', s))",
        "('.python-version', 'python', lambda s: s)",
        "('.ruby-version', 'ruby', lambda s: s)"
      ]
    },
    {
      "name": "_ASDF_TOOL_ALIASES",
      "lineno": 7779,
      "kind": "dict",
      "len": 2,
      "keys": [
        "nodejs",
        "python3"
      ]
    },
    {
      "name": "_MISE_SIGNAL_FILES",
      "lineno": 8006,
      "kind": "tuple",
      "len": 9,
      "values": [
        "mise.toml",
        ".mise.toml",
        ".tool-versions",
        ".nvmrc",
        ".node-version",
        ".python-version",
        ".ruby-version",
        "rust-toolchain.toml",
        ".go-version"
      ]
    },
    {
      "name": "_RETRYABLE_FAILURE_KINDS",
      "lineno": 12301,
      "kind": "expr",
      "expr": "frozenset({'no_commits', 'dirty_worktree', 'empty_handoff'})"
    },
    {
      "name": "_RULES_FILE_CANDIDATES",
      "lineno": 12351,
      "kind": "tuple",
      "len": 13,
      "values": [
        "CLAUDE.md",
        "AGENTS.md",
        ".agent.md",
        ".cursorrules",
        ".windsurfrules",
        "docs/CLAUDE.md",
        "docs/AGENTS.md",
        "docs/CONVENTIONS.md",
        "docs/STYLE.md",
        "README.md",
        "CONTRIBUTING.md",
        "docs/DESIGN.md",
        "docs/IMPLEMENTATION.md"
      ]
    },
    {
      "name": "_BLT_AXIS_RES",
      "lineno": 12793,
      "kind": "dict",
      "len": 3,
      "keys": [
        "test",
        "build",
        "lint"
      ]
    },
    {
      "name": "_BG_RESULT_PREFIX",
      "lineno": 12817,
      "kind": "str",
      "value": "Command running in background with ID:"
    },
    {
      "name": "_BG_ID_RE",
      "lineno": 12818,
      "kind": "expr",
      "expr": "re.compile('Command running in background with ID:\\\\s*(\\\\w+)')"
    },
    {
      "name": "_PR_TEMPLATE_SINGLE_LOCATIONS",
      "lineno": 13814,
      "kind": "tuple",
      "len": 3,
      "values": [
        ".github/pull_request_template.md",
        "pull_request_template.md",
        "docs/pull_request_template.md"
      ]
    },
    {
      "name": "_PR_TEMPLATE_MULTI_DIRS",
      "lineno": 13822,
      "kind": "tuple",
      "len": 3,
      "values": [
        ".github/PULL_REQUEST_TEMPLATE",
        "PULL_REQUEST_TEMPLATE",
        "docs/PULL_REQUEST_TEMPLATE"
      ]
    },
    {
      "name": "PR_WRITER_COMMIT_LOG_MAX_BYTES",
      "lineno": 13883,
      "kind": "int",
      "value": 80000
    },
    {
      "name": "PR_WRITER_TEMPLATE_MAX_BYTES",
      "lineno": 13884,
      "kind": "int",
      "value": 32000
    },
    {
      "name": "PR_WRITER_DIFF_SAMPLE_MAX_LINES",
      "lineno": 13885,
      "kind": "int",
      "value": 500
    },
    {
      "name": "PR_WRITER_FINAL_CONFORMANCE_MAX_BYTES",
      "lineno": 13891,
      "kind": "int",
      "value": 8000
    },
    {
      "name": "_LEERIE_PREFIX_RE",
      "lineno": 13919,
      "kind": "expr",
      "expr": "re.compile('^leerie:\\\\s*', re.IGNORECASE)"
    }
  ],
  "functions": [
    {
      "name": "_read_version",
      "qualname": "_read_version",
      "async": false,
      "lineno": 57,
      "end_lineno": 66,
      "span": 10,
      "decorators": [],
      "signature": "()",
      "returns": "str",
      "doc": "Single source of truth: `.claude-plugin/plugin.json`'s `version`"
    },
    {
      "name": "load_prompt",
      "qualname": "load_prompt",
      "async": false,
      "lineno": 75,
      "end_lineno": 84,
      "span": 10,
      "decorators": [],
      "signature": "(name: str)",
      "returns": "str",
      "doc": "Read prompts/<name>.md and expand any {{include: _foo.md}}"
    },
    {
      "name": "is_protected_path",
      "qualname": "is_protected_path",
      "async": false,
      "lineno": 314,
      "end_lineno": 322,
      "span": 9,
      "decorators": [],
      "signature": "(path: str)",
      "returns": "bool",
      "doc": "Return True if `path` is a meta-directory the implementer must not"
    },
    {
      "name": "resolve_prompt",
      "qualname": "resolve_prompt",
      "async": false,
      "lineno": 619,
      "end_lineno": 634,
      "span": 16,
      "decorators": [],
      "signature": "(call_type: str)",
      "returns": "tuple[str, str, str]",
      "doc": "Return (source_kind, content, location_hint) for a worker call_type."
    },
    {
      "name": "_confidence_schema",
      "qualname": "_confidence_schema",
      "async": false,
      "lineno": 677,
      "end_lineno": 700,
      "span": 24,
      "decorators": [],
      "signature": "(axes: list[str])",
      "returns": "dict",
      "doc": "Build the \u00a78 confidence sub-schema for the given score axes."
    },
    {
      "name": "now",
      "qualname": "now",
      "async": false,
      "lineno": 1305,
      "end_lineno": 1306,
      "span": 2,
      "decorators": [],
      "signature": "()",
      "returns": "str",
      "doc": null
    },
    {
      "name": "log",
      "qualname": "log",
      "async": false,
      "lineno": 1309,
      "end_lineno": 1312,
      "span": 4,
      "decorators": [],
      "signature": "(msg: str)",
      "returns": "None",
      "doc": null
    },
    {
      "name": "die",
      "qualname": "die",
      "async": false,
      "lineno": 1315,
      "end_lineno": 1317,
      "span": 3,
      "decorators": [],
      "signature": "(msg: str, code: int = 1)",
      "returns": null,
      "doc": null
    },
    {
      "name": "detect_session_limit",
      "qualname": "detect_session_limit",
      "async": false,
      "lineno": 1383,
      "end_lineno": 1422,
      "span": 40,
      "decorators": [],
      "signature": "(text: str)",
      "returns": "RateLimitedExit | None",
      "doc": "Return a RateLimitedExit if `text` matches the Claude Code"
    },
    {
      "name": "_install_signal_handlers",
      "qualname": "_install_signal_handlers",
      "async": false,
      "lineno": 1425,
      "end_lineno": 1435,
      "span": 11,
      "decorators": [],
      "signature": "()",
      "returns": "None",
      "doc": "Install SIGTERM/SIGHUP handlers that raise InterruptedBySignal."
    },
    {
      "name": "_enumerate_descendants",
      "qualname": "_enumerate_descendants",
      "async": false,
      "lineno": 1441,
      "end_lineno": 1480,
      "span": 40,
      "decorators": [],
      "signature": "(root_pid: int)",
      "returns": "set[int]",
      "doc": "Return every PID reachable from `root_pid` via PPID links."
    },
    {
      "name": "_signal_pids",
      "qualname": "_signal_pids",
      "async": false,
      "lineno": 1483,
      "end_lineno": 1492,
      "span": 10,
      "decorators": [],
      "signature": "(pids: set[int], sig: int)",
      "returns": "None",
      "doc": "Best-effort signal delivery to a set of PIDs. Drops ProcessLookupError"
    },
    {
      "name": "_terminate_proc_tree",
      "qualname": "_terminate_proc_tree",
      "async": true,
      "lineno": 1586,
      "end_lineno": 1654,
      "span": 69,
      "decorators": [],
      "signature": "(proc: asyncio.subprocess.Process)",
      "returns": "None",
      "doc": "Terminate a subprocess AND every descendant process, then reap."
    },
    {
      "name": "_cleanup_on_abnormal_exit",
      "qualname": "_cleanup_on_abnormal_exit",
      "async": false,
      "lineno": 1657,
      "end_lineno": 1772,
      "span": 116,
      "decorators": [],
      "signature": "(st: 'State', *, full_purge: bool)",
      "returns": "None",
      "doc": "Clean up after an abnormal exit (signal, exception, WorkerError)."
    },
    {
      "name": "_reset_subtask_worktree",
      "qualname": "_reset_subtask_worktree",
      "async": true,
      "lineno": 1775,
      "end_lineno": 1798,
      "span": 24,
      "decorators": [],
      "signature": "(sid: str, leerie_dir: Path, run_id: str)",
      "returns": "None",
      "doc": "Remove the per-subtask worktree directory and branch so a corrective"
    },
    {
      "name": "_parse_claude_version",
      "qualname": "_parse_claude_version",
      "async": false,
      "lineno": 1801,
      "end_lineno": 1806,
      "span": 6,
      "decorators": [],
      "signature": "(version_output: str | None)",
      "returns": "tuple[int, int, int] | None",
      "doc": "Pull MAJOR.MINOR.PATCH out of `claude --version` output."
    },
    {
      "name": "_check_claude_cli_version",
      "qualname": "_check_claude_cli_version",
      "async": false,
      "lineno": 1809,
      "end_lineno": 1839,
      "span": 31,
      "decorators": [],
      "signature": "()",
      "returns": "None",
      "doc": "die() if `claude` is too old for --json-schema. Without this, a"
    },
    {
      "name": "compute_run_branch",
      "qualname": "compute_run_branch",
      "async": false,
      "lineno": 1853,
      "end_lineno": 1864,
      "span": 12,
      "decorators": [],
      "signature": "(run_id: str)",
      "returns": "str",
      "doc": "The git branch name carrying a run's integrated work."
    },
    {
      "name": "compute_subtask_branch",
      "qualname": "compute_subtask_branch",
      "async": false,
      "lineno": 1867,
      "end_lineno": 1876,
      "span": 10,
      "decorators": [],
      "signature": "(run_id: str, sid: str)",
      "returns": "str",
      "doc": "The git branch name for one subtask's worktree."
    },
    {
      "name": "_validate_run_json",
      "qualname": "_validate_run_json",
      "async": false,
      "lineno": 1881,
      "end_lineno": 1977,
      "span": 97,
      "decorators": [],
      "signature": "(data: dict)",
      "returns": "None",
      "doc": "Enforce the logical invariants on a `run.json` sidecar."
    },
    {
      "name": "_format_run_duration",
      "qualname": "_format_run_duration",
      "async": false,
      "lineno": 1982,
      "end_lineno": 2003,
      "span": 22,
      "decorators": [],
      "signature": "(started_at: str | None, finished_at: str | None)",
      "returns": "str | None",
      "doc": "Return a human-readable elapsed duration like '3m 42s' or '1h 12m'."
    },
    {
      "name": "compose_pr_body",
      "qualname": "compose_pr_body",
      "async": false,
      "lineno": 2006,
      "end_lineno": 2062,
      "span": 57,
      "decorators": [],
      "signature": "(state: dict, run_id: str)",
      "returns": "str",
      "doc": "Generate the deterministic fallback PR body from run state +"
    },
    {
      "name": "_write_run_json",
      "qualname": "_write_run_json",
      "async": false,
      "lineno": 2065,
      "end_lineno": 2090,
      "span": 26,
      "decorators": [],
      "signature": "(run_dir: Path, **fields)",
      "returns": "None",
      "doc": "Merge fields into the run.json sidecar at `run_dir/run.json`,"
    },
    {
      "name": "discover_runs",
      "qualname": "discover_runs",
      "async": false,
      "lineno": 2095,
      "end_lineno": 2182,
      "span": 88,
      "decorators": [],
      "signature": "(leerie_root: Path)",
      "returns": "list[dict]",
      "doc": "Enumerate `<state-root>/runs/*/state.json`, returning one summary"
    },
    {
      "name": "resolve_run_id",
      "qualname": "resolve_run_id",
      "async": false,
      "lineno": 2185,
      "end_lineno": 2219,
      "span": 35,
      "decorators": [],
      "signature": "(leerie_root: Path, cli_run_id: str | None)",
      "returns": "str",
      "doc": "Pick the run_id to operate on. Used by `--resume`."
    },
    {
      "name": "_format_run_for_disambiguation",
      "qualname": "_format_run_for_disambiguation",
      "async": false,
      "lineno": 2222,
      "end_lineno": 2267,
      "span": 46,
      "decorators": [],
      "signature": "(run: dict, leerie_root: Path)",
      "returns": "str",
      "doc": "Build the per-row hint string for `resolve_run_id`'s"
    },
    {
      "name": "_format_age",
      "qualname": "_format_age",
      "async": false,
      "lineno": 2270,
      "end_lineno": 2287,
      "span": 18,
      "decorators": [],
      "signature": "(seconds: float)",
      "returns": "str",
      "doc": "Render a duration in seconds as a short human-friendly age:"
    },
    {
      "name": "_derive_run_status",
      "qualname": "_derive_run_status",
      "async": false,
      "lineno": 2318,
      "end_lineno": 2382,
      "span": 65,
      "decorators": [],
      "signature": "(run_json: dict | None, state_json: dict | None)",
      "returns": "str",
      "doc": "Pure function: derive a run's status from run.json + state.json."
    },
    {
      "name": "_collect_run_rows",
      "qualname": "_collect_run_rows",
      "async": false,
      "lineno": 2385,
      "end_lineno": 2410,
      "span": 26,
      "decorators": [],
      "signature": "(leerie_root: Path)",
      "returns": "list[tuple[str, str, str, str, bool]]",
      "doc": "Build (run_id, started_at, status, branch, is_fly) rows for every"
    },
    {
      "name": "_render_run_table",
      "qualname": "_render_run_table",
      "async": false,
      "lineno": 2413,
      "end_lineno": 2423,
      "span": 11,
      "decorators": [],
      "signature": "(rows: list[tuple[str, str, str, str, bool]])",
      "returns": "None",
      "doc": "Print rows as a columnar table with auto-sized columns."
    },
    {
      "name": "list_runs",
      "qualname": "list_runs",
      "async": false,
      "lineno": 2426,
      "end_lineno": 2460,
      "span": 35,
      "decorators": [],
      "signature": "(leerie_root: Path, status_filter: str | None = None, runtime_filter: str | None = None)",
      "returns": "None",
      "doc": "Render a sortable columnar table of runs to stdout. Used by"
    },
    {
      "name": "_read_toml_key",
      "qualname": "_read_toml_key",
      "async": false,
      "lineno": 2464,
      "end_lineno": 2480,
      "span": 17,
      "decorators": [],
      "signature": "(path: Path, key: str)",
      "returns": "str | None",
      "doc": "Read a single `key = value` from a flat leerie.toml. Returns"
    },
    {
      "name": "resolve_task_argument",
      "qualname": "resolve_task_argument",
      "async": false,
      "lineno": 2486,
      "end_lineno": 2512,
      "span": 27,
      "decorators": [],
      "signature": "(raw: str)",
      "returns": "str",
      "doc": "Resolve the positional `task` argument to the task string."
    },
    {
      "name": "resolve_leerie_root",
      "qualname": "resolve_leerie_root",
      "async": false,
      "lineno": 2515,
      "end_lineno": 2530,
      "span": 16,
      "decorators": [],
      "signature": "(repo_root: Path)",
      "returns": "Path",
      "doc": "Resolve the leerie state root directory."
    },
    {
      "name": "_resolve_enum_pref",
      "qualname": "_resolve_enum_pref",
      "async": false,
      "lineno": 2533,
      "end_lineno": 2552,
      "span": 20,
      "decorators": [],
      "signature": "(repo_root: Path, cli_value: str | None, *, env_var: str, file_key: str, file_name: str, allowed: frozenset[str] | tuple[str, ...], default: str)",
      "returns": "str",
      "doc": "Shared resolution for enum-valued prefs. CLI > env > file > default."
    },
    {
      "name": "resolve_source_of_truth",
      "qualname": "resolve_source_of_truth",
      "async": false,
      "lineno": 2555,
      "end_lineno": 2567,
      "span": 13,
      "decorators": [],
      "signature": "(repo_root: Path, cli_value: str | None = None)",
      "returns": "str",
      "doc": "Resolve the source-of-truth preference. Order:"
    },
    {
      "name": "resolve_runtime",
      "qualname": "resolve_runtime",
      "async": false,
      "lineno": 2570,
      "end_lineno": 2581,
      "span": 12,
      "decorators": [],
      "signature": "(repo_root: Path, cli_value: str | None = None)",
      "returns": "str",
      "doc": "Resolve the runtime mode. Order:"
    },
    {
      "name": "_resolve_str_pref",
      "qualname": "_resolve_str_pref",
      "async": false,
      "lineno": 2584,
      "end_lineno": 2598,
      "span": 15,
      "decorators": [],
      "signature": "(repo_root: Path, cli_value: str | None, *, env_var: str, file_key: str, file_name: str, default: str | None)",
      "returns": "str | None",
      "doc": "Shared resolution for unvalidated string prefs. CLI > env > file >"
    },
    {
      "name": "resolve_pr_template",
      "qualname": "resolve_pr_template",
      "async": false,
      "lineno": 2601,
      "end_lineno": 2613,
      "span": 13,
      "decorators": [],
      "signature": "(repo_root: Path, cli_value: str | None = None)",
      "returns": "str | None",
      "doc": "Resolve the --pr-template selector. Order:"
    },
    {
      "name": "_resolve_positive_int_pref",
      "qualname": "_resolve_positive_int_pref",
      "async": false,
      "lineno": 2616,
      "end_lineno": 2642,
      "span": 27,
      "decorators": [],
      "signature": "(repo_root: Path, cli_value: int | None, *, env_var: str, file_key: str, file_name: str, default: int)",
      "returns": "int",
      "doc": "Shared resolution for positive-int prefs. CLI > env > file > default."
    },
    {
      "name": "resolve_confidence_rounds",
      "qualname": "resolve_confidence_rounds",
      "async": false,
      "lineno": 2645,
      "end_lineno": 2657,
      "span": 13,
      "decorators": [],
      "signature": "(repo_root: Path, cli_value: int | None = None)",
      "returns": "int",
      "doc": "Resolve the confidence-rounds cap. Order:"
    },
    {
      "name": "resolve_max_workers",
      "qualname": "resolve_max_workers",
      "async": false,
      "lineno": 2660,
      "end_lineno": 2672,
      "span": 13,
      "decorators": [],
      "signature": "(repo_root: Path, cli_value: int | None = None)",
      "returns": "int",
      "doc": "Resolve the max-workers cap. Order:"
    },
    {
      "name": "resolve_max_parallel",
      "qualname": "resolve_max_parallel",
      "async": false,
      "lineno": 2675,
      "end_lineno": 2687,
      "span": 13,
      "decorators": [],
      "signature": "(repo_root: Path, cli_value: int | None = None)",
      "returns": "int",
      "doc": "Resolve the max-parallel cap. Order:"
    },
    {
      "name": "resolve_judgment_check_rounds",
      "qualname": "resolve_judgment_check_rounds",
      "async": false,
      "lineno": 2690,
      "end_lineno": 2699,
      "span": 10,
      "decorators": [],
      "signature": "(repo_root: Path, cli_value: int | None = None)",
      "returns": "int",
      "doc": "Resolve the judgment-check-rounds cap (CRITIC-pattern re-invocations"
    },
    {
      "name": "resolve_planner_check_rounds",
      "qualname": "resolve_planner_check_rounds",
      "async": false,
      "lineno": 2702,
      "end_lineno": 2711,
      "span": 10,
      "decorators": [],
      "signature": "(repo_root: Path, cli_value: int | None = None)",
      "returns": "int",
      "doc": "Resolve the planner-check-rounds cap (CRITIC-pattern re-invocations"
    },
    {
      "name": "resolve_implementer_confidence_retries",
      "qualname": "resolve_implementer_confidence_retries",
      "async": false,
      "lineno": 2714,
      "end_lineno": 2724,
      "span": 11,
      "decorators": [],
      "signature": "(repo_root: Path, cli_value: int | None = None)",
      "returns": "int",
      "doc": "Resolve the implementer-confidence-retries cap (separate from"
    },
    {
      "name": "resolve_planner_samples",
      "qualname": "resolve_planner_samples",
      "async": false,
      "lineno": 2727,
      "end_lineno": 2735,
      "span": 9,
      "decorators": [],
      "signature": "(repo_root: Path, cli_value: int | None = None)",
      "returns": "int",
      "doc": "Resolve the planner-samples cap (multi-sample; 1 disables)."
    },
    {
      "name": "_parse_memory_size",
      "qualname": "_parse_memory_size",
      "async": false,
      "lineno": 2743,
      "end_lineno": 2767,
      "span": 25,
      "decorators": [],
      "signature": "(value: str, context: str)",
      "returns": "int",
      "doc": "Parse a memory size string like \"4G\", \"512M\", \"1024\" into bytes."
    },
    {
      "name": "_auto_worker_memory_max",
      "qualname": "_auto_worker_memory_max",
      "async": false,
      "lineno": 2770,
      "end_lineno": 2795,
      "span": 26,
      "decorators": [],
      "signature": "(max_parallel: int)",
      "returns": "int",
      "doc": "Auto-derive a per-worker memory cap from /proc/meminfo."
    },
    {
      "name": "resolve_worker_memory_max",
      "qualname": "resolve_worker_memory_max",
      "async": false,
      "lineno": 2798,
      "end_lineno": 2818,
      "span": 21,
      "decorators": [],
      "signature": "(repo_root: Path, max_parallel: int, cli_value: str | None = None)",
      "returns": "int",
      "doc": "Resolve the per-worker cgroup memory cap (bytes). Order:"
    },
    {
      "name": "resolve_inspect_dirs",
      "qualname": "resolve_inspect_dirs",
      "async": false,
      "lineno": 2821,
      "end_lineno": 2859,
      "span": 39,
      "decorators": [],
      "signature": "(repo_root: Path, cli_values: list[str] | None = None)",
      "returns": "list[str]",
      "doc": "Resolve the extra inspection directories for classifier/planner/"
    },
    {
      "name": "_parse_bool_envtoml",
      "qualname": "_parse_bool_envtoml",
      "async": false,
      "lineno": 2862,
      "end_lineno": 2874,
      "span": 13,
      "decorators": [],
      "signature": "(value: str)",
      "returns": "bool | None",
      "doc": "Parse a boolean from an env var or TOML scalar. Returns True/False"
    },
    {
      "name": "_resolve_bool_pref",
      "qualname": "_resolve_bool_pref",
      "async": false,
      "lineno": 2877,
      "end_lineno": 2904,
      "span": 28,
      "decorators": [],
      "signature": "(repo_root: Path, cli_value: bool, *, env_var: str, file_key: str, file_name: str)",
      "returns": "bool",
      "doc": "Shared resolution for `store_true` CLI flags that also have an"
    },
    {
      "name": "resolve_no_push",
      "qualname": "resolve_no_push",
      "async": false,
      "lineno": 2907,
      "end_lineno": 2914,
      "span": 8,
      "decorators": [],
      "signature": "(repo_root: Path, cli_value: bool)",
      "returns": "bool",
      "doc": "Resolve the --no-push preference. Order:"
    },
    {
      "name": "push_will_happen",
      "qualname": "push_will_happen",
      "async": false,
      "lineno": 2917,
      "end_lineno": 2941,
      "span": 25,
      "decorators": [],
      "signature": "(no_push: bool, host_no_push: bool | None)",
      "returns": "bool",
      "doc": "Whether the host will push after this orchestrator exits."
    },
    {
      "name": "resolve_clarify",
      "qualname": "resolve_clarify",
      "async": false,
      "lineno": 2944,
      "end_lineno": 2951,
      "span": 8,
      "decorators": [],
      "signature": "(repo_root: Path, cli_value: bool)",
      "returns": "bool",
      "doc": "Resolve the --clarify preference. Order:"
    },
    {
      "name": "resolve_dangerously_skip_permissions",
      "qualname": "resolve_dangerously_skip_permissions",
      "async": false,
      "lineno": 2954,
      "end_lineno": 2973,
      "span": 20,
      "decorators": [],
      "signature": "(repo_root: Path, cli_value: bool)",
      "returns": "bool",
      "doc": "Resolve the --dangerously-skip-permissions preference. Order:"
    },
    {
      "name": "resolve_skip_overlap_judge",
      "qualname": "resolve_skip_overlap_judge",
      "async": false,
      "lineno": 2976,
      "end_lineno": 2993,
      "span": 18,
      "decorators": [],
      "signature": "(repo_root: Path, cli_value: bool)",
      "returns": "bool",
      "doc": "Resolve the --skip-overlap-judge preference. Order:"
    },
    {
      "name": "resolve_skip_budget_check",
      "qualname": "resolve_skip_budget_check",
      "async": false,
      "lineno": 2996,
      "end_lineno": 3015,
      "span": 20,
      "decorators": [],
      "signature": "(repo_root: Path, cli_value: bool)",
      "returns": "bool",
      "doc": "Resolve the --skip-budget-check preference. Order:"
    },
    {
      "name": "resolve_strict_conformer",
      "qualname": "resolve_strict_conformer",
      "async": false,
      "lineno": 3018,
      "end_lineno": 3032,
      "span": 15,
      "decorators": [],
      "signature": "(repo_root: Path, cli_value: bool)",
      "returns": "bool",
      "doc": "Resolve the --strict-conformer preference. Order:"
    },
    {
      "name": "_positive_int",
      "qualname": "_positive_int",
      "async": false,
      "lineno": 3035,
      "end_lineno": 3044,
      "span": 10,
      "decorators": [],
      "signature": "(s: str)",
      "returns": "int",
      "doc": "argparse `type=` helper. Rejects non-positive integers with the"
    },
    {
      "name": "resolve_verbosity",
      "qualname": "resolve_verbosity",
      "async": false,
      "lineno": 3047,
      "end_lineno": 3066,
      "span": 20,
      "decorators": [],
      "signature": "(repo_root: Path, cli_value: str | None = None)",
      "returns": "str",
      "doc": "Resolve the verbosity level. Order:"
    },
    {
      "name": "verbosity_from_shortcuts",
      "qualname": "verbosity_from_shortcuts",
      "async": false,
      "lineno": 3069,
      "end_lineno": 3087,
      "span": 19,
      "decorators": [],
      "signature": "(verbose: int, quiet: int)",
      "returns": "str | None",
      "doc": "Map argparse -v/-vv/-q/-qq counts to a verbosity level."
    },
    {
      "name": "resolve_models",
      "qualname": "resolve_models",
      "async": false,
      "lineno": 3090,
      "end_lineno": 3163,
      "span": 74,
      "decorators": [],
      "signature": "(repo_root: Path, args)",
      "returns": "dict[str, str]",
      "doc": "Resolve the model alias for each worker type. Per-worker"
    },
    {
      "name": "resolve_efforts",
      "qualname": "resolve_efforts",
      "async": false,
      "lineno": 3166,
      "end_lineno": 3224,
      "span": 59,
      "decorators": [],
      "signature": "(repo_root: Path, args)",
      "returns": "dict[str, str | None]",
      "doc": "Resolve the --effort value for each worker type. Mirrors"
    },
    {
      "name": "resolve_telemetry_enabled",
      "qualname": "resolve_telemetry_enabled",
      "async": false,
      "lineno": 3227,
      "end_lineno": 3256,
      "span": 30,
      "decorators": [],
      "signature": "(repo_root: Path, cli_value: bool | None = None)",
      "returns": "bool",
      "doc": "Resolve the telemetry enabled/disabled preference. Order:"
    },
    {
      "name": "resolve_telemetry_subdir",
      "qualname": "resolve_telemetry_subdir",
      "async": false,
      "lineno": 3259,
      "end_lineno": 3269,
      "span": 11,
      "decorators": [],
      "signature": "(repo_root: Path, cli_value: str | None = None)",
      "returns": "str",
      "doc": "Resolve the telemetry event subdirectory name. Order:"
    },
    {
      "name": "resolve_judge_dir",
      "qualname": "resolve_judge_dir",
      "async": false,
      "lineno": 3272,
      "end_lineno": 3281,
      "span": 10,
      "decorators": [],
      "signature": "(repo_root: Path, cli_value: str | None = None)",
      "returns": "str",
      "doc": "Resolve the judge output directory name. Order:"
    },
    {
      "name": "resolve_heal_dir",
      "qualname": "resolve_heal_dir",
      "async": false,
      "lineno": 3284,
      "end_lineno": 3293,
      "span": 10,
      "decorators": [],
      "signature": "(repo_root: Path, cli_value: str | None = None)",
      "returns": "str",
      "doc": "Resolve the heal output directory name. Order:"
    },
    {
      "name": "resolve_heal_max_rounds",
      "qualname": "resolve_heal_max_rounds",
      "async": false,
      "lineno": 3296,
      "end_lineno": 3305,
      "span": 10,
      "decorators": [],
      "signature": "(repo_root: Path, cli_value: int | None = None)",
      "returns": "int",
      "doc": "Resolve the heal-loop max-iterations cap. Order:"
    },
    {
      "name": "resolve_heal_success_threshold",
      "qualname": "resolve_heal_success_threshold",
      "async": false,
      "lineno": 3308,
      "end_lineno": 3335,
      "span": 28,
      "decorators": [],
      "signature": "(repo_root: Path, cli_value: float | None = None)",
      "returns": "float",
      "doc": "Resolve the heal-loop success pass-rate threshold. Order:"
    },
    {
      "name": "run_proc",
      "qualname": "run_proc",
      "async": true,
      "lineno": 3338,
      "end_lineno": 3382,
      "span": 45,
      "decorators": [],
      "signature": "(cmd: list[str], *, cwd: str | None = None, timeout: float | None = None)",
      "returns": "subprocess.CompletedProcess",
      "doc": "Async equivalent of `subprocess.run(cmd, capture_output=True, text=True)`."
    },
    {
      "name": "run_streaming",
      "qualname": "run_streaming",
      "async": true,
      "lineno": 3385,
      "end_lineno": 3508,
      "span": 124,
      "decorators": [],
      "signature": "(cmd: list[str], *, cwd: str | None = None, env: dict[str, str] | None = None, timeout: float | None = None, log_path: Path | None = None, label: str | None = None, verbosity: str = 'stream', line_prefix: str = '  | ', tail_lines: int = 40)",
      "returns": "tuple[int, str]",
      "doc": "Run a subprocess with stdout+stderr streamed live, persisted to a"
    },
    {
      "name": "gather_or_cancel",
      "qualname": "gather_or_cancel",
      "async": true,
      "lineno": 3511,
      "end_lineno": 3532,
      "span": 22,
      "decorators": [],
      "signature": "(*aws)",
      "returns": null,
      "doc": "Like asyncio.gather, but on the first exception cancel every other"
    },
    {
      "name": "run_script",
      "qualname": "run_script",
      "async": true,
      "lineno": 3535,
      "end_lineno": 3537,
      "span": 3,
      "decorators": [],
      "signature": "(name: str, *args: str)",
      "returns": "subprocess.CompletedProcess",
      "doc": "Run one of the bundled git worktree scripts in the target repo."
    },
    {
      "name": "preflight",
      "qualname": "preflight",
      "async": true,
      "lineno": 3550,
      "end_lineno": 3610,
      "span": 61,
      "decorators": [],
      "signature": "(leerie_dir: Path, verbosity: str = VERBOSITY_DEFAULT, skip_smoke: bool = False, no_push: bool = False)",
      "returns": "None",
      "doc": "Hard checks before any LLM work. Fails fast rather than wasting workers."
    },
    {
      "name": "_confidence_issues",
      "qualname": "_confidence_issues",
      "async": false,
      "lineno": 3625,
      "end_lineno": 3643,
      "span": 19,
      "decorators": [],
      "signature": "(conf: dict, axes: list[str], threshold: float = 9.0)",
      "returns": "list[str]",
      "doc": "Return one LOW_CONFIDENCE issue per axis below *threshold*."
    },
    {
      "name": "check_classifier_output",
      "qualname": "check_classifier_output",
      "async": false,
      "lineno": 3646,
      "end_lineno": 3692,
      "span": 47,
      "decorators": [],
      "signature": "(result: dict, repo_root: Path)",
      "returns": "list[str]",
      "doc": "Thin mechanical checks on the classifier's category selection."
    },
    {
      "name": "_grep_old_pattern",
      "qualname": "_grep_old_pattern",
      "async": false,
      "lineno": 3710,
      "end_lineno": 3732,
      "span": 23,
      "decorators": [],
      "signature": "(pattern: str, repo_root: Path)",
      "returns": "set[str]",
      "doc": "Grep *repo_root* for *pattern*, return set of relative file paths."
    },
    {
      "name": "_check_migration_surface",
      "qualname": "_check_migration_surface",
      "async": false,
      "lineno": 3735,
      "end_lineno": 3763,
      "span": 29,
      "decorators": [],
      "signature": "(subtasks: list[dict], repo_root: Path)",
      "returns": "list[str]",
      "doc": "UNCOVERED_MIGRATION_SURFACE check (DESIGN \u00a75)."
    },
    {
      "name": "check_planner_output",
      "qualname": "check_planner_output",
      "async": false,
      "lineno": 3766,
      "end_lineno": 3860,
      "span": 95,
      "decorators": [],
      "signature": "(result: dict, repo_root: Path, domain: str)",
      "returns": "list[str]",
      "doc": "Rich mechanical checks on a single planner domain's output."
    },
    {
      "name": "check_reconciler_output",
      "qualname": "check_reconciler_output",
      "async": false,
      "lineno": 3863,
      "end_lineno": 3894,
      "span": 32,
      "decorators": [],
      "signature": "(output: dict, plans: list[dict])",
      "returns": "list[str]",
      "doc": "Mechanical checks on the reconciler's output beyond the existing"
    },
    {
      "name": "check_overlap_judge_output",
      "qualname": "check_overlap_judge_output",
      "async": false,
      "lineno": 3897,
      "end_lineno": 3958,
      "span": 62,
      "decorators": [],
      "signature": "(output: dict, plans: list[dict], repo_root: Path)",
      "returns": "list[str]",
      "doc": "Mechanical checks on the overlap judge's collision list."
    },
    {
      "name": "check_provision_output",
      "qualname": "check_provision_output",
      "async": false,
      "lineno": 3961,
      "end_lineno": 4000,
      "span": 40,
      "decorators": [],
      "signature": "(result: dict, repo_root: Path)",
      "returns": "list[str]",
      "doc": "Mechanical checks on the provision LLM fallback's recipe."
    },
    {
      "name": "check_integrator_output",
      "qualname": "check_integrator_output",
      "async": false,
      "lineno": 4003,
      "end_lineno": 4006,
      "span": 4,
      "decorators": [],
      "signature": "(result: dict)",
      "returns": "list[str]",
      "doc": "Confidence gate for the integrator."
    },
    {
      "name": "check_implementer_output",
      "qualname": "check_implementer_output",
      "async": false,
      "lineno": 4009,
      "end_lineno": 4031,
      "span": 23,
      "decorators": [],
      "signature": "(result: dict, subtask: dict, actual_files: set[str])",
      "returns": "list[str]",
      "doc": "Mechanical checks on an implementer's complete result."
    },
    {
      "name": "_expand_braces",
      "qualname": "_expand_braces",
      "async": false,
      "lineno": 4046,
      "end_lineno": 4059,
      "span": 14,
      "decorators": [],
      "signature": "(pattern: str)",
      "returns": "list[str]",
      "doc": "Expand shell-style ``{a,b}`` brace groups into multiple patterns."
    },
    {
      "name": "glob_task_references",
      "qualname": "glob_task_references",
      "async": false,
      "lineno": 4062,
      "end_lineno": 4091,
      "span": 30,
      "decorators": [],
      "signature": "(task: str, repo_root: Path)",
      "returns": "list[Path]",
      "doc": "Find file references in the task string via glob expansion."
    },
    {
      "name": "extract_task_file_structure",
      "qualname": "extract_task_file_structure",
      "async": false,
      "lineno": 4094,
      "end_lineno": 4128,
      "span": 35,
      "decorators": [],
      "signature": "(task: str, repo_root: Path)",
      "returns": "list[str] | None",
      "doc": "Extract structural elements from files referenced in the task."
    },
    {
      "name": "check_task_file_coverage",
      "qualname": "check_task_file_coverage",
      "async": false,
      "lineno": 4134,
      "end_lineno": 4165,
      "span": 32,
      "decorators": [],
      "signature": "(extracted: list[str], subtasks: list[dict])",
      "returns": "list[str]",
      "doc": "Check which extracted items are NOT referenced by any subtask."
    },
    {
      "name": "_format_task_file_structure",
      "qualname": "_format_task_file_structure",
      "async": false,
      "lineno": 4168,
      "end_lineno": 4179,
      "span": 12,
      "decorators": [],
      "signature": "(items: list[str])",
      "returns": "str",
      "doc": "Format extracted structure as an external coverage reference"
    },
    {
      "name": "validate_plan",
      "qualname": "validate_plan",
      "async": false,
      "lineno": 4182,
      "end_lineno": 4288,
      "span": 107,
      "decorators": [],
      "signature": "(subtasks: dict)",
      "returns": "None",
      "doc": "Structural validation of the merged plan \u2014 pure Python set operations."
    },
    {
      "name": "warn_cross_planner_file_overlap",
      "qualname": "warn_cross_planner_file_overlap",
      "async": false,
      "lineno": 4291,
      "end_lineno": 4322,
      "span": 32,
      "decorators": [],
      "signature": "(plans: list[dict])",
      "returns": "None",
      "doc": "Log a warning when subtasks from different planner outputs both list"
    },
    {
      "name": "warn_layer_gaps",
      "qualname": "warn_layer_gaps",
      "async": false,
      "lineno": 4329,
      "end_lineno": 4367,
      "span": 39,
      "decorators": [],
      "signature": "(plans: list[dict])",
      "returns": "None",
      "doc": "Advisory cross-domain layer-gap warnings (DESIGN \u00a75)."
    },
    {
      "name": "_resolves_under",
      "qualname": "_resolves_under",
      "async": false,
      "lineno": 4370,
      "end_lineno": 4382,
      "span": 13,
      "decorators": [],
      "signature": "(path_str: str, root: Path)",
      "returns": "bool",
      "doc": "True iff `path_str` (relative or absolute) resolves under `root`."
    },
    {
      "name": "filter_offtree_subtasks",
      "qualname": "filter_offtree_subtasks",
      "async": false,
      "lineno": 4385,
      "end_lineno": 4442,
      "span": 58,
      "decorators": [],
      "signature": "(plans: list[dict], repo_root: Path, inspect_dirs: list[str], st: 'State')",
      "returns": "None",
      "doc": "Mutate `plans` in place: drop any subtask whose `files_likely_touched`"
    },
    {
      "name": "_lockfile_table_entries",
      "qualname": "_lockfile_table_entries",
      "async": false,
      "lineno": 4468,
      "end_lineno": 4581,
      "span": 114,
      "decorators": [],
      "signature": "(repo_root: Path)",
      "returns": "list[dict]",
      "doc": "The deterministic lockfile \u2192 install-command table. Returns a list of"
    },
    {
      "name": "detect_recipe_from_lockfiles",
      "qualname": "detect_recipe_from_lockfiles",
      "async": false,
      "lineno": 4584,
      "end_lineno": 4589,
      "span": 6,
      "decorators": [],
      "signature": "(repo_root: Path)",
      "returns": "list[dict]",
      "doc": "Public entry point for the deterministic detection layer. Returns"
    },
    {
      "name": "validate_provision_recipe",
      "qualname": "validate_provision_recipe",
      "async": false,
      "lineno": 4592,
      "end_lineno": 4653,
      "span": 62,
      "decorators": [],
      "signature": "(recipe: list[dict])",
      "returns": "None",
      "doc": "Mechanically bound the provision recipe. Raises ValueError on any"
    },
    {
      "name": "_split_readme_headers",
      "qualname": "_split_readme_headers",
      "async": false,
      "lineno": 4698,
      "end_lineno": 4747,
      "span": 50,
      "decorators": [],
      "signature": "(text: str)",
      "returns": "list[tuple[int, str, str]]",
      "doc": "Return [(line_index, header_text, body_until_next_header), ...] for"
    },
    {
      "name": "_is_install_section",
      "qualname": "_is_install_section",
      "async": false,
      "lineno": 4750,
      "end_lineno": 4757,
      "span": 8,
      "decorators": [],
      "signature": "(header: str)",
      "returns": "bool",
      "doc": "True if a header (after decoration-strip) matches the section"
    },
    {
      "name": "_slice_code_fences_with_install_hints",
      "qualname": "_slice_code_fences_with_install_hints",
      "async": false,
      "lineno": 4760,
      "end_lineno": 4799,
      "span": 40,
      "decorators": [],
      "signature": "(text: str, ctx_lines: int = 10)",
      "returns": "str",
      "doc": "Fallback layer: scan for fenced code blocks containing recognized"
    },
    {
      "name": "extract_readme_sections",
      "qualname": "extract_readme_sections",
      "async": false,
      "lineno": 4811,
      "end_lineno": 4868,
      "span": 58,
      "decorators": [],
      "signature": "(text: str)",
      "returns": "str",
      "doc": "Extract the install/setup-relevant slice of a README."
    },
    {
      "name": "_read_file_safely",
      "qualname": "_read_file_safely",
      "async": false,
      "lineno": 4871,
      "end_lineno": 4878,
      "span": 8,
      "decorators": [],
      "signature": "(path: Path, budget: int)",
      "returns": "str",
      "doc": "Read a file with a byte ceiling, swallowing missing-file and"
    },
    {
      "name": "_sample_workspace_manifests",
      "qualname": "_sample_workspace_manifests",
      "async": false,
      "lineno": 4891,
      "end_lineno": 4928,
      "span": 38,
      "decorators": [],
      "signature": "(repo_root: Path, pkg_json_text: str, per_file_budget: int, max_files: int)",
      "returns": "list[tuple[str, str]]",
      "doc": "For a monorepo whose root package.json declares `workspaces`,"
    },
    {
      "name": "gather_provision_fixtures",
      "qualname": "gather_provision_fixtures",
      "async": false,
      "lineno": 4931,
      "end_lineno": 5039,
      "span": 109,
      "decorators": [],
      "signature": "(repo_root: Path)",
      "returns": "dict",
      "doc": "Assemble the LLM-fallback worker's input set. Returns a dict with"
    },
    {
      "name": "_split_checkpoint_sections",
      "qualname": "_split_checkpoint_sections",
      "async": false,
      "lineno": 5072,
      "end_lineno": 5088,
      "span": 17,
      "decorators": [],
      "signature": "(content: str)",
      "returns": "dict[str, list[str]]",
      "doc": "Split a checkpoint file by `## ` headers into {header: lines}."
    },
    {
      "name": "validate_checkpoint",
      "qualname": "validate_checkpoint",
      "async": false,
      "lineno": 5091,
      "end_lineno": 5140,
      "span": 50,
      "decorators": [],
      "signature": "(path: str, worktree_root: Path | None = None)",
      "returns": "str | None",
      "doc": "Return an error description if the checkpoint is structurally incomplete,"
    },
    {
      "name": "_normalize_for_noise",
      "qualname": "_normalize_for_noise",
      "async": false,
      "lineno": 5143,
      "end_lineno": 5155,
      "span": 13,
      "decorators": [],
      "signature": "(line: str)",
      "returns": "str",
      "doc": "Reduce a checkpoint line to its comparison key for `_NOISE_TOKENS`."
    },
    {
      "name": "_strip_bullet",
      "qualname": "_strip_bullet",
      "async": false,
      "lineno": 5158,
      "end_lineno": 5172,
      "span": 15,
      "decorators": [],
      "signature": "(line: str)",
      "returns": "str",
      "doc": "Strip leading markdown bullet markers (`-`, `*`, `1.`) before noise"
    },
    {
      "name": "_parse_touched_file_line",
      "qualname": "_parse_touched_file_line",
      "async": false,
      "lineno": 5175,
      "end_lineno": 5195,
      "span": 21,
      "decorators": [],
      "signature": "(line: str)",
      "returns": "tuple[str | None, bool]",
      "doc": "Extract a file path from a `## Files touched` line and detect the"
    },
    {
      "name": "validate_result",
      "qualname": "validate_result",
      "async": false,
      "lineno": 5200,
      "end_lineno": 5268,
      "span": 69,
      "decorators": [],
      "signature": "(result: dict)",
      "returns": "tuple[str, str] | None",
      "doc": "Cross-field invariant checks that JSON Schema cannot express."
    },
    {
      "name": "check_diff_scope",
      "qualname": "check_diff_scope",
      "async": true,
      "lineno": 5273,
      "end_lineno": 5316,
      "span": 44,
      "decorators": [],
      "signature": "(sid: str, worktree: str, subtask: dict, st: State)",
      "returns": "str | None",
      "doc": "Check the implementer's diff for violations."
    },
    {
      "name": "check_merge_committed",
      "qualname": "check_merge_committed",
      "async": true,
      "lineno": 5321,
      "end_lineno": 5344,
      "span": 24,
      "decorators": [],
      "signature": "(staging: Path)",
      "returns": "str | None",
      "doc": "Return an error if the staging worktree is still mid-merge."
    },
    {
      "name": "check_integrator_commit",
      "qualname": "check_integrator_commit",
      "async": true,
      "lineno": 5347,
      "end_lineno": 5360,
      "span": 14,
      "decorators": [],
      "signature": "(staging: Path)",
      "returns": "str | None",
      "doc": "Return an error if the integrator's merge commit touched .leerie/ files."
    },
    {
      "name": "check_branch_has_commits",
      "qualname": "check_branch_has_commits",
      "async": true,
      "lineno": 5365,
      "end_lineno": 5390,
      "span": 26,
      "decorators": [],
      "signature": "(sid: str, worktree: str, parent_branch: str)",
      "returns": "tuple[str, str] | None",
      "doc": "Return `(failure_kind, message)` if the implementer's subtask"
    },
    {
      "name": "scan_conflict_markers",
      "qualname": "scan_conflict_markers",
      "async": true,
      "lineno": 5395,
      "end_lineno": 5413,
      "span": 19,
      "decorators": [],
      "signature": "(staging: Path)",
      "returns": "str | None",
      "doc": "Return error if unresolved conflict markers remain in the staging tree."
    },
    {
      "name": "validate_resume_state",
      "qualname": "validate_resume_state",
      "async": false,
      "lineno": 5418,
      "end_lineno": 5443,
      "span": 26,
      "decorators": [],
      "signature": "(data: dict)",
      "returns": "None",
      "doc": "Assert the structure of a loaded state.json before resuming. A corrupt"
    },
    {
      "name": "_is_auth_or_quota_failure",
      "qualname": "_is_auth_or_quota_failure",
      "async": false,
      "lineno": 5453,
      "end_lineno": 5470,
      "span": 18,
      "decorators": [],
      "signature": "(envelope: dict)",
      "returns": "bool",
      "doc": "True if the `claude -p` envelope looks like a 401/429/auth-message"
    },
    {
      "name": "_extract_tool_result_text",
      "qualname": "_extract_tool_result_text",
      "async": false,
      "lineno": 5473,
      "end_lineno": 5486,
      "span": 14,
      "decorators": [],
      "signature": "(block: dict)",
      "returns": "str",
      "doc": "Tool-result `content` is either a string or a list of content"
    },
    {
      "name": "_tag_each_line",
      "qualname": "_tag_each_line",
      "async": false,
      "lineno": 5489,
      "end_lineno": 5524,
      "span": 36,
      "decorators": [],
      "signature": "(prefix: str, content: str)",
      "returns": "str",
      "doc": "Prefix the first non-empty line of `content` with `prefix`;"
    },
    {
      "name": "_summarize_tool_use",
      "qualname": "_summarize_tool_use",
      "async": false,
      "lineno": 5527,
      "end_lineno": 5566,
      "span": 40,
      "decorators": [],
      "signature": "(sid: str, block: dict, verbosity: str)",
      "returns": "str",
      "doc": "Map one `tool_use` content block to a one-line inline summary."
    },
    {
      "name": "_summarize_stream_event",
      "qualname": "_summarize_stream_event",
      "async": false,
      "lineno": 5569,
      "end_lineno": 5723,
      "span": 155,
      "decorators": [],
      "signature": "(sid: str, event: dict, verbosity: str)",
      "returns": "str | None",
      "doc": "Return the one-line inline-log summary for one stream event, or"
    },
    {
      "name": "_format_progress_prefix",
      "qualname": "_format_progress_prefix",
      "async": false,
      "lineno": 5726,
      "end_lineno": 5749,
      "span": 24,
      "decorators": [],
      "signature": "(prog: tuple[int, int, int, int, int] | None)",
      "returns": "str",
      "doc": "Render the activity prefix from a `_get_progress` tuple, or \"\" when"
    },
    {
      "name": "_get_progress",
      "qualname": "_get_progress",
      "async": false,
      "lineno": 5752,
      "end_lineno": 5795,
      "span": 44,
      "decorators": [],
      "signature": "(st: 'State')",
      "returns": "tuple[int, int, int, int, int] | None",
      "doc": "Return (running, in_conformer, done, wave_idx, wave_total) for the"
    },
    {
      "name": "_detect_cgroup_root",
      "qualname": "_detect_cgroup_root",
      "async": false,
      "lineno": 5839,
      "end_lineno": 5856,
      "span": 18,
      "decorators": [],
      "signature": "()",
      "returns": "Path",
      "doc": "Pick the cgroup root for worker subtrees. Prefer the delegated"
    },
    {
      "name": "_cgroup_probe",
      "qualname": "_cgroup_probe",
      "async": false,
      "lineno": 5859,
      "end_lineno": 5904,
      "span": 46,
      "decorators": [],
      "signature": "()",
      "returns": "bool",
      "doc": "Once-per-run probe: can we create cgroups under the detected"
    },
    {
      "name": "_cgroup_create",
      "qualname": "_cgroup_create",
      "async": false,
      "lineno": 5907,
      "end_lineno": 5931,
      "span": 25,
      "decorators": [],
      "signature": "(sid: str, memory_max_bytes: int, pids_max: int)",
      "returns": "Path | None",
      "doc": "Create a child cgroup for a worker and set its caps. Returns the"
    },
    {
      "name": "_cgroup_enroll",
      "qualname": "_cgroup_enroll",
      "async": false,
      "lineno": 5934,
      "end_lineno": 5945,
      "span": 12,
      "decorators": [],
      "signature": "(cgroup_path: Path, pid: int)",
      "returns": "bool",
      "doc": "Move `pid` into the cgroup. Called immediately after the worker"
    },
    {
      "name": "_cgroup_destroy",
      "qualname": "_cgroup_destroy",
      "async": false,
      "lineno": 5948,
      "end_lineno": 5961,
      "span": 14,
      "decorators": [],
      "signature": "(cgroup_path: Path | None)",
      "returns": "None",
      "doc": "Tear down the worker's cgroup. Best-effort:"
    },
    {
      "name": "_invoke",
      "qualname": "_invoke",
      "async": true,
      "lineno": 5964,
      "end_lineno": 6303,
      "span": 340,
      "decorators": [],
      "signature": "(cmd: list[str], cwd: str, timeout: int, sid: str, leerie_dir: Path, verbosity: str, progress: Callable[[], tuple[int, int, int, int] | None] | None = None, idle_warn_sec: float | None = None, worker_memory_max_bytes: int | None = None, worker_pids_max: int | None = None)",
      "returns": "dict",
      "doc": "Run a `claude -p` command, streaming events as they arrive."
    },
    {
      "name": "_capture_call",
      "qualname": "_capture_call",
      "async": false,
      "lineno": 6306,
      "end_lineno": 6316,
      "span": 11,
      "decorators": [],
      "signature": "(run_dir: Path, record: dict)",
      "returns": "None",
      "doc": "Append one NDJSON record to calls.ndjson with fsync-per-line durability."
    },
    {
      "name": "_collect_memory_sample",
      "qualname": "_collect_memory_sample",
      "async": false,
      "lineno": 6319,
      "end_lineno": 6368,
      "span": 50,
      "decorators": [],
      "signature": "(st: 'State')",
      "returns": "dict",
      "doc": "Snapshot orchestrator RSS / current phase / worker count / open FDs /"
    },
    {
      "name": "_memory_sampler",
      "qualname": "_memory_sampler",
      "async": true,
      "lineno": 6371,
      "end_lineno": 6413,
      "span": 43,
      "decorators": [],
      "signature": "(st: 'State', interval_sec: float = 30.0)",
      "returns": "None",
      "doc": "Periodic orchestrator-memory sample for leak detection."
    },
    {
      "name": "claude_p",
      "qualname": "claude_p",
      "async": true,
      "lineno": 6416,
      "end_lineno": 6663,
      "span": 248,
      "decorators": [],
      "signature": "(user_prompt: str, system_prompt: str, *, schema_key: str, cwd: str, allowed_tools: str, max_turns: int, autonomous: bool, caps: dict, st: 'State', model: str, sid: str, add_dirs: list[str] | None = None, effort: str | None = None, _suppress_capture: bool = False)",
      "returns": "dict",
      "doc": "Run one headless Claude Code worker and return its validated"
    },
    {
      "name": "replay_capture",
      "qualname": "replay_capture",
      "async": true,
      "lineno": 6666,
      "end_lineno": 6730,
      "span": 65,
      "decorators": [],
      "signature": "(record: dict, *, override_system_prompt: str | None = None, cwd: str | None = None)",
      "returns": "tuple[dict, dict]",
      "doc": "Replay one captured call from a calls.ndjson record."
    },
    {
      "name": "_accumulate_telemetry",
      "qualname": "_accumulate_telemetry",
      "async": false,
      "lineno": 6733,
      "end_lineno": 6743,
      "span": 11,
      "decorators": [],
      "signature": "(data: dict, envelope: dict)",
      "returns": "None",
      "doc": "Accumulate run-weight signals from a worker envelope into `data`."
    },
    {
      "name": "judge_capture",
      "qualname": "judge_capture",
      "async": true,
      "lineno": 6931,
      "end_lineno": 6979,
      "span": 49,
      "decorators": [],
      "signature": "(record: dict, models: dict[str, str], efforts: dict[str, str | None], caps: dict, st: 'State')",
      "returns": "dict",
      "doc": "Run a judge worker against one captured call record."
    },
    {
      "name": "phase_judge",
      "qualname": "phase_judge",
      "async": true,
      "lineno": 6982,
      "end_lineno": 7050,
      "span": 69,
      "decorators": [],
      "signature": "(run_dir: Path, judge_out_dir: Path, caps: dict, st: 'State', models: dict[str, str], efforts: dict[str, str | None], judge_call_types: list[str] | None = None)",
      "returns": "dict",
      "doc": "Judge all captured call records in run_dir/calls.ndjson."
    },
    {
      "name": "heal_baseline",
      "qualname": "heal_baseline",
      "async": true,
      "lineno": 7105,
      "end_lineno": 7184,
      "span": 80,
      "decorators": [],
      "signature": "(call_type: str, failing_records: list[dict], n: int, heal_dir: Path, caps: dict, st: 'State', models: dict[str, str], efforts: dict[str, str | None])",
      "returns": "HealState",
      "doc": "Run n unpatched replays per failing capture to establish a noise-floor."
    },
    {
      "name": "heal_apply_patch",
      "qualname": "heal_apply_patch",
      "async": false,
      "lineno": 7187,
      "end_lineno": 7210,
      "span": 24,
      "decorators": [],
      "signature": "(call_type: str, iter_n: int, patch_text: str, anchor_match: str, heal_dir: Path, failing_records: list[dict])",
      "returns": "list[Path]",
      "doc": "Materialise per-sample patched prompts under iter-<N>/patched-prompts/."
    },
    {
      "name": "heal_replay_patched",
      "qualname": "heal_replay_patched",
      "async": true,
      "lineno": 7213,
      "end_lineno": 7312,
      "span": 100,
      "decorators": [],
      "signature": "(call_type: str, iter_n: int, n: int, heal_dir: Path, caps: dict, st: 'State', models: dict[str, str], efforts: dict[str, str | None])",
      "returns": "HealState",
      "doc": "Run n patched replays per failing capture and append an iteration record."
    },
    {
      "name": "check_convergence",
      "qualname": "check_convergence",
      "async": false,
      "lineno": 7315,
      "end_lineno": 7375,
      "span": 61,
      "decorators": [],
      "signature": "(state: HealState, config: dict)",
      "returns": "str",
      "doc": "Evaluate whether the heal loop has converged."
    },
    {
      "name": "write_heal_report",
      "qualname": "write_heal_report",
      "async": false,
      "lineno": 7378,
      "end_lineno": 7430,
      "span": 53,
      "decorators": [],
      "signature": "(call_type: str, state: HealState, best_patch_text: str = '')",
      "returns": "Path",
      "doc": "Render a markdown heal report to <heal_dir>/<call_type>/healing-<call_type>.md."
    },
    {
      "name": "request_patch",
      "qualname": "request_patch",
      "async": true,
      "lineno": 7433,
      "end_lineno": 7520,
      "span": 88,
      "decorators": [],
      "signature": "(state: HealState, iter_n: int, st: 'State', caps: dict, models: dict[str, str], efforts: dict[str, str | None])",
      "returns": "tuple[str, str]",
      "doc": "Invoke the patch-generator worker to propose a minimal prompt edit."
    },
    {
      "name": "phase_heal",
      "qualname": "phase_heal",
      "async": true,
      "lineno": 7523,
      "end_lineno": 7608,
      "span": 86,
      "decorators": [],
      "signature": "(call_type: str, failing_records: list[dict], heal_dir: Path, caps: dict, st: 'State', models: dict[str, str], efforts: dict[str, str | None], request_patch_fn = None, n: int = HEAL_N_REPLAYS_DEFAULT, config: dict | None = None)",
      "returns": "str",
      "doc": "Drive the full heal loop for one call_type."
    },
    {
      "name": "run_setup_hook",
      "qualname": "run_setup_hook",
      "async": true,
      "lineno": 7624,
      "end_lineno": 7693,
      "span": 70,
      "decorators": [],
      "signature": "(repo_root: Path, log_dir: Path, st: 'State')",
      "returns": "None",
      "doc": "Execute `<repo>/.leerie-setup.sh` if present. Idempotent via"
    },
    {
      "name": "_existing_mise_toml_path",
      "qualname": "_existing_mise_toml_path",
      "async": false,
      "lineno": 7701,
      "end_lineno": 7713,
      "span": 13,
      "decorators": [],
      "signature": "(repo_root: Path)",
      "returns": "Path | None",
      "doc": "Return the path to whichever of `mise.toml` or `.mise.toml`"
    },
    {
      "name": "_go_already_pinned",
      "qualname": "_go_already_pinned",
      "async": false,
      "lineno": 7716,
      "end_lineno": 7748,
      "span": 33,
      "decorators": [],
      "signature": "(repo_root: Path)",
      "returns": "bool",
      "doc": "Return True if the repo already specifies a Go version mise would"
    },
    {
      "name": "_existing_mise_toml_tool_keys",
      "qualname": "_existing_mise_toml_tool_keys",
      "async": false,
      "lineno": 7785,
      "end_lineno": 7807,
      "span": 23,
      "decorators": [],
      "signature": "(text: str | None)",
      "returns": "set[str]",
      "doc": "Return the set of tool keys pinned by a `[tools]` section in the"
    },
    {
      "name": "_read_idiomatic_pins",
      "qualname": "_read_idiomatic_pins",
      "async": false,
      "lineno": 7810,
      "end_lineno": 7870,
      "span": 61,
      "decorators": [],
      "signature": "(repo_root: Path, already_pinned: set[str])",
      "returns": "list[tuple[str, str]]",
      "doc": "Return [(tool, version), ...] for every idiomatic version file in"
    },
    {
      "name": "synth_mise_go_override",
      "qualname": "synth_mise_go_override",
      "async": false,
      "lineno": 7873,
      "end_lineno": 7999,
      "span": 127,
      "decorators": [],
      "signature": "(repo_root: Path, run_dir: Path)",
      "returns": "Path | None",
      "doc": "If `go.mod` exists and no other Go pin is in place, write a mise"
    },
    {
      "name": "_repo_has_version_signal",
      "qualname": "_repo_has_version_signal",
      "async": false,
      "lineno": 8017,
      "end_lineno": 8028,
      "span": 12,
      "decorators": [],
      "signature": "(repo_root: Path, override_file: Path | None)",
      "returns": "bool",
      "doc": "Return True if the repo declares any runtime version pin mise"
    },
    {
      "name": "run_mise_install",
      "qualname": "run_mise_install",
      "async": true,
      "lineno": 8031,
      "end_lineno": 8118,
      "span": 88,
      "decorators": [],
      "signature": "(repo_root: Path, log_dir: Path, st: 'State', override_file: Path | None = None)",
      "returns": "None",
      "doc": "Invoke `mise install` at the repo root. If `override_file` is"
    },
    {
      "name": "phase_classify",
      "qualname": "phase_classify",
      "async": true,
      "lineno": 8124,
      "end_lineno": 8177,
      "span": 54,
      "decorators": [],
      "signature": "(task: str, st: State, caps: dict, clarify: bool, models: dict[str, str], efforts: dict[str, str | None])",
      "returns": "dict",
      "doc": "Phase 1 (classify), which also produces the Clarify sub-step's"
    },
    {
      "name": "gather_answers",
      "qualname": "gather_answers",
      "async": false,
      "lineno": 8180,
      "end_lineno": 8225,
      "span": 46,
      "decorators": [],
      "signature": "(st: State, supplied: dict | None)",
      "returns": "dict",
      "doc": "Collect clarification answers \u2014 from --answers, from the resolved"
    },
    {
      "name": "absorb_supplied_answers",
      "qualname": "absorb_supplied_answers",
      "async": false,
      "lineno": 8228,
      "end_lineno": 8290,
      "span": 63,
      "decorators": [],
      "signature": "(args, st: State, leerie_dir: Path)",
      "returns": "None",
      "doc": "Merge --answers FILE into st.data['answers'] and propagate the"
    },
    {
      "name": "surface_clarification",
      "qualname": "surface_clarification",
      "async": false,
      "lineno": 8293,
      "end_lineno": 8338,
      "span": 46,
      "decorators": [],
      "signature": "(sid: str, question: dict, checkpoint_path: str, st: State)",
      "returns": "bool",
      "doc": "Surface a mid-execution clarification question to the user"
    },
    {
      "name": "_format_provision_user_prompt",
      "qualname": "_format_provision_user_prompt",
      "async": false,
      "lineno": 8341,
      "end_lineno": 8369,
      "span": 29,
      "decorators": [],
      "signature": "(fixtures: dict, task: str)",
      "returns": "str",
      "doc": "Compose the LLM-fallback user prompt from the assembled fixture"
    },
    {
      "name": "phase_provision",
      "qualname": "phase_provision",
      "async": true,
      "lineno": 8372,
      "end_lineno": 8523,
      "span": 152,
      "decorators": [],
      "signature": "(repo_root: Path, st: State, caps: dict, models: dict[str, str], efforts: dict[str, str | None])",
      "returns": "None",
      "doc": "Phase 1\u00bd: per-repo dependency *detection*."
    },
    {
      "name": "_select_best_planner_sample",
      "qualname": "_select_best_planner_sample",
      "async": false,
      "lineno": 8526,
      "end_lineno": 8548,
      "span": 23,
      "decorators": [],
      "signature": "(samples: list[dict], repo_root: Path, domain: str)",
      "returns": "dict",
      "doc": "Mechanically select the best planner sample for a domain."
    },
    {
      "name": "phase_plan",
      "qualname": "phase_plan",
      "async": true,
      "lineno": 8551,
      "end_lineno": 8689,
      "span": 139,
      "decorators": [],
      "signature": "(task: str, st: State, caps: dict, models: dict[str, str], efforts: dict[str, str | None])",
      "returns": "list[dict]",
      "doc": "Phase 2: one planner per category, run in parallel (bounded by"
    },
    {
      "name": "_promote_external_collisions",
      "qualname": "_promote_external_collisions",
      "async": false,
      "lineno": 8692,
      "end_lineno": 8716,
      "span": 25,
      "decorators": [],
      "signature": "(plans: list[dict])",
      "returns": "int",
      "doc": "In-place: for every `requires` entry with `extent: external` whose"
    },
    {
      "name": "_collect_external_preconditions",
      "qualname": "_collect_external_preconditions",
      "async": false,
      "lineno": 8719,
      "end_lineno": 8749,
      "span": 31,
      "decorators": [],
      "signature": "(plans: list[dict])",
      "returns": "list[dict]",
      "doc": "Walk plans and return the deduped list of planner-declared"
    },
    {
      "name": "_compute_unresolved_requires",
      "qualname": "_compute_unresolved_requires",
      "async": false,
      "lineno": 8752,
      "end_lineno": 8791,
      "span": 40,
      "decorators": [],
      "signature": "(plans: list[dict])",
      "returns": "list[dict]",
      "doc": "Pure-Python lookup: every (sid, tag, domain) where a subtask"
    },
    {
      "name": "_find_oversized_added_subtasks",
      "qualname": "_find_oversized_added_subtasks",
      "async": false,
      "lineno": 8794,
      "end_lineno": 8813,
      "span": 20,
      "decorators": [],
      "signature": "(plans: list[dict])",
      "returns": "list[dict]",
      "doc": "Pure-Python lookup: every reconciler-added subtask (carrying"
    },
    {
      "name": "_apply_reconciler_output",
      "qualname": "_apply_reconciler_output",
      "async": false,
      "lineno": 8816,
      "end_lineno": 9209,
      "span": 394,
      "decorators": [],
      "signature": "(plans: list[dict], output: dict, attempt_1_renames: list[dict] | None = None)",
      "returns": "list[dict]",
      "doc": "Mutate `plans` per the reconciler's output. On success, returns"
    },
    {
      "name": "phase_reconcile",
      "qualname": "phase_reconcile",
      "async": true,
      "lineno": 9212,
      "end_lineno": 9788,
      "span": 577,
      "decorators": [],
      "signature": "(plans: list[dict], task: str, st: State, caps: dict, models: dict[str, str], efforts: dict[str, str | None])",
      "returns": "list[dict]",
      "doc": "Phase 2\u00bd: reconcile cross-domain capability-tag drift between"
    },
    {
      "name": "_tarjan_sccs",
      "qualname": "_tarjan_sccs",
      "async": false,
      "lineno": 9791,
      "end_lineno": 9859,
      "span": 69,
      "decorators": [],
      "signature": "(nodes: set[str], succ: dict[str, set[str]])",
      "returns": "list[list[str]]",
      "doc": "Tarjan's strongly-connected-components algorithm."
    },
    {
      "name": "_attribute_cycle_edges",
      "qualname": "_attribute_cycle_edges",
      "async": false,
      "lineno": 9862,
      "end_lineno": 9925,
      "span": 64,
      "decorators": [],
      "signature": "(scc: list[str], succ: dict[str, set[str]], edge_sources: dict[tuple[str, str], str], output: dict, subtasks: dict[str, dict])",
      "returns": "list[dict]",
      "doc": "For each edge inside an SCC, attribute it back to the reconciler"
    },
    {
      "name": "_format_cycle_diagnostic",
      "qualname": "_format_cycle_diagnostic",
      "async": false,
      "lineno": 9928,
      "end_lineno": 9968,
      "span": 41,
      "decorators": [],
      "signature": "(sccs: list[list[str]], succ: dict[str, set[str]], edge_sources: dict[tuple[str, str], str], output: dict, subtasks: dict[str, dict])",
      "returns": "str",
      "doc": "Render an SCC list + edge attributions into the multi-line"
    },
    {
      "name": "_shared_files_in_scc",
      "qualname": "_shared_files_in_scc",
      "async": false,
      "lineno": 9971,
      "end_lineno": 9986,
      "span": 16,
      "decorators": [],
      "signature": "(scc: list[str], subtasks: dict[str, dict])",
      "returns": "list[str]",
      "doc": "Files that appear in `files_likely_touched` of \u2265 2 SCC members."
    },
    {
      "name": "_original_tag_for_rename_edge",
      "qualname": "_original_tag_for_rename_edge",
      "async": false,
      "lineno": 9989,
      "end_lineno": 10019,
      "span": 31,
      "decorators": [],
      "signature": "(edge: dict, output: dict)",
      "returns": "str",
      "doc": "Given a cycle-edge dict (from `_attribute_cycle_edges`) and the"
    },
    {
      "name": "_recommend_cycle_resolution",
      "qualname": "_recommend_cycle_resolution",
      "async": false,
      "lineno": 10022,
      "end_lineno": 10217,
      "span": 196,
      "decorators": [],
      "signature": "(scc: list[str], succ: dict[str, set[str]], edge_sources: dict[tuple[str, str], str], subtasks: dict[str, dict], output: dict, pre_providers: dict[str, list[str]])",
      "returns": "dict",
      "doc": "Deterministic recommendation for breaking one SCC."
    },
    {
      "name": "_format_recommendation",
      "qualname": "_format_recommendation",
      "async": false,
      "lineno": 10220,
      "end_lineno": 10240,
      "span": 21,
      "decorators": [],
      "signature": "(rec: dict)",
      "returns": "str",
      "doc": "Render a recommendation dict (from `_recommend_cycle_resolution`)"
    },
    {
      "name": "_format_must_include",
      "qualname": "_format_must_include",
      "async": false,
      "lineno": 10243,
      "end_lineno": 10280,
      "span": 38,
      "decorators": [],
      "signature": "(scc: list[str], edges: list[dict], output: dict)",
      "returns": "list[str]",
      "doc": "For one SCC, list the bounded set of legal cycle-breaking"
    },
    {
      "name": "_build_cycle_retry_prompt",
      "qualname": "_build_cycle_retry_prompt",
      "async": false,
      "lineno": 10283,
      "end_lineno": 10371,
      "span": 89,
      "decorators": [],
      "signature": "(sccs: list[list[str]], succ: dict[str, set[str]], edge_sources: dict[tuple[str, str], str], output: dict, subtasks: dict[str, dict], recommendations: list[dict], original_user_prompt: str)",
      "returns": "str",
      "doc": "Build the retry prompt sent to the reconciler when the"
    },
    {
      "name": "_build_size_retry_prompt",
      "qualname": "_build_size_retry_prompt",
      "async": false,
      "lineno": 10374,
      "end_lineno": 10442,
      "span": 69,
      "decorators": [],
      "signature": "(oversized: list[dict], original_user_prompt: str)",
      "returns": "str",
      "doc": "Build the retry prompt sent to the reconciler when the size gate"
    },
    {
      "name": "_matches_recommendation",
      "qualname": "_matches_recommendation",
      "async": false,
      "lineno": 10445,
      "end_lineno": 10459,
      "span": 15,
      "decorators": [],
      "signature": "(option_str: str, rec: dict)",
      "returns": "bool",
      "doc": "Whether a must-include option string matches the recommendation"
    },
    {
      "name": "_validate_must_include",
      "qualname": "_validate_must_include",
      "async": false,
      "lineno": 10462,
      "end_lineno": 10504,
      "span": 43,
      "decorators": [],
      "signature": "(output: dict, sccs: list[list[str]])",
      "returns": "list[str]",
      "doc": "For each SCC, check that the reconciler's revised output includes"
    },
    {
      "name": "_tag_jaccard",
      "qualname": "_tag_jaccard",
      "async": false,
      "lineno": 10507,
      "end_lineno": 10524,
      "span": 18,
      "decorators": [],
      "signature": "(a: str, b: str)",
      "returns": "float",
      "doc": "Token-set Jaccard similarity over hyphen-split tokens."
    },
    {
      "name": "_recommend_unresolved_resolution",
      "qualname": "_recommend_unresolved_resolution",
      "async": false,
      "lineno": 10527,
      "end_lineno": 10624,
      "span": 98,
      "decorators": [],
      "signature": "(consumer_sid: str, unresolved_tag: str, providers: dict[str, list[str]], output: dict)",
      "returns": "dict | None",
      "doc": "Deterministic recommendation for resolving one unresolved"
    },
    {
      "name": "_build_unresolved_retry_prompt",
      "qualname": "_build_unresolved_retry_prompt",
      "async": false,
      "lineno": 10627,
      "end_lineno": 10780,
      "span": 154,
      "decorators": [],
      "signature": "(unresolved: list[dict], providers: dict[str, list[str]], recommendations: dict[tuple[str, str], dict | None], output: dict, original_user_prompt: str)",
      "returns": "str",
      "doc": "Build the retry prompt sent to the reconciler when the"
    },
    {
      "name": "_validate_unresolved_must_include",
      "qualname": "_validate_unresolved_must_include",
      "async": false,
      "lineno": 10783,
      "end_lineno": 10915,
      "span": 133,
      "decorators": [],
      "signature": "(output: dict, unresolved: list[dict], attempt_1_output: dict | None)",
      "returns": "list[str]",
      "doc": "For each unresolved (sid, tag), check the reconciler's revised"
    },
    {
      "name": "_compute_overlap_anchors",
      "qualname": "_compute_overlap_anchors",
      "async": false,
      "lineno": 10945,
      "end_lineno": 10967,
      "span": 23,
      "decorators": [],
      "signature": "(collisions: list[dict])",
      "returns": "set[str]",
      "doc": "An *anchor* is a sid that appears in two or more non-"
    },
    {
      "name": "_validate_overlap_judge_output",
      "qualname": "_validate_overlap_judge_output",
      "async": false,
      "lineno": 10970,
      "end_lineno": 11067,
      "span": 98,
      "decorators": [],
      "signature": "(output: dict, subtasks_by_id: dict[str, dict])",
      "returns": "None",
      "doc": "Apply the merge-feasibility backstop and structural sanity checks"
    },
    {
      "name": "_apply_overlap_drop",
      "qualname": "_apply_overlap_drop",
      "async": false,
      "lineno": 11070,
      "end_lineno": 11176,
      "span": 107,
      "decorators": [],
      "signature": "(plans: list[dict], dropped_sid: str, surviving_sid: str)",
      "returns": "None",
      "doc": "Remove `dropped_sid` from its plan, union its `provides` tags"
    },
    {
      "name": "_apply_overlap_merge",
      "qualname": "_apply_overlap_merge",
      "async": false,
      "lineno": 11179,
      "end_lineno": 11371,
      "span": 193,
      "decorators": [],
      "signature": "(plans: list[dict], a_sid: str, b_sid: str, artifact: str, merge_feasibility: str, survivor_hint: str | None = None)",
      "returns": "str",
      "doc": "Collapse `a_sid` and `b_sid` into one subtask. Returns the"
    },
    {
      "name": "_apply_overlap_collisions",
      "qualname": "_apply_overlap_collisions",
      "async": false,
      "lineno": 11374,
      "end_lineno": 11527,
      "span": 154,
      "decorators": [],
      "signature": "(plans: list[dict], collisions: list[dict])",
      "returns": "list[dict]",
      "doc": "Apply a validated list of overlap-judge collisions to `plans`"
    },
    {
      "name": "phase_overlap_judge",
      "qualname": "phase_overlap_judge",
      "async": true,
      "lineno": 11530,
      "end_lineno": 11740,
      "span": 211,
      "decorators": [],
      "signature": "(plans: list[dict], task: str, st: State, caps: dict, models: dict[str, str], efforts: dict[str, str | None])",
      "returns": "list[dict]",
      "doc": "Phase 2\u00be: detect cross-planner surface-overlap collisions"
    },
    {
      "name": "_build_predecessor_graph",
      "qualname": "_build_predecessor_graph",
      "async": false,
      "lineno": 11743,
      "end_lineno": 11794,
      "span": 52,
      "decorators": [],
      "signature": "(subtasks: dict[str, dict])",
      "returns": "tuple[dict[str, set[str]], dict[str, list[str]], dict[tuple[str, str], str]]",
      "doc": "Build the predecessor graph from a merged subtasks dict."
    },
    {
      "name": "detect_no_work",
      "qualname": "detect_no_work",
      "async": false,
      "lineno": 11797,
      "end_lineno": 11825,
      "span": 29,
      "decorators": [],
      "signature": "(plans: list[dict])",
      "returns": "dict[str, str] | None",
      "doc": "Return a `{domain: basis}` map iff *every* plan satisfies"
    },
    {
      "name": "_finish_no_work_run",
      "qualname": "_finish_no_work_run",
      "async": false,
      "lineno": 11828,
      "end_lineno": 11870,
      "span": 43,
      "decorators": [],
      "signature": "(st: State, no_work_map: dict[str, str])",
      "returns": "None",
      "doc": "Terminal-state handler for the cleared-but-empty case"
    },
    {
      "name": "schedule",
      "qualname": "schedule",
      "async": false,
      "lineno": 11873,
      "end_lineno": 11922,
      "span": 50,
      "decorators": [],
      "signature": "(plans: list[dict])",
      "returns": "tuple[dict, list[list[str]]]",
      "doc": "Phase 3 (pure Python): merge plans, resolve intra- and cross-domain"
    },
    {
      "name": "check_budget_feasibility",
      "qualname": "check_budget_feasibility",
      "async": false,
      "lineno": 11925,
      "end_lineno": 11986,
      "span": 62,
      "decorators": [],
      "signature": "(st: State, caps: dict, subtasks: dict, waves: list[list[str]])",
      "returns": "None",
      "doc": "Phase 3 pure-Python gate (DESIGN \u00a713 *Budget feasibility \u2014 fail"
    },
    {
      "name": "_write_subtask_artifacts",
      "qualname": "_write_subtask_artifacts",
      "async": false,
      "lineno": 11989,
      "end_lineno": 12010,
      "span": 22,
      "decorators": [],
      "signature": "(leerie_dir: Path, sid: str, artifacts: list)",
      "returns": "None",
      "doc": "Persist a subtask's `artifacts` result field to"
    },
    {
      "name": "_read_upstream_artifacts",
      "qualname": "_read_upstream_artifacts",
      "async": false,
      "lineno": 12013,
      "end_lineno": 12033,
      "span": 21,
      "decorators": [],
      "signature": "(leerie_dir: Path, predecessor_ids: list[str])",
      "returns": "list[dict]",
      "doc": "Read the artifacts files for `predecessor_ids` and return them"
    },
    {
      "name": "_format_upstream_artifacts_for_sid",
      "qualname": "_format_upstream_artifacts_for_sid",
      "async": false,
      "lineno": 12036,
      "end_lineno": 12065,
      "span": 30,
      "decorators": [],
      "signature": "(leerie_dir: Path, sid: str)",
      "returns": "str | None",
      "doc": "End-to-end helper: load the persisted plan, recompute the"
    },
    {
      "name": "_format_upstream_artifacts_section",
      "qualname": "_format_upstream_artifacts_section",
      "async": false,
      "lineno": 12068,
      "end_lineno": 12095,
      "span": 28,
      "decorators": [],
      "signature": "(payloads: list[dict])",
      "returns": "str | None",
      "doc": "Render upstream artifact payloads as a prompt section, or None"
    },
    {
      "name": "write_plan",
      "qualname": "write_plan",
      "async": false,
      "lineno": 12098,
      "end_lineno": 12123,
      "span": 26,
      "decorators": [],
      "signature": "(leerie_dir: Path, task: str, st: State, subtasks: dict, waves: list[list[str]])",
      "returns": "None",
      "doc": "Persist the merged plan and per-subtask spec files the implementers read."
    },
    {
      "name": "_format_provision_recipe_section",
      "qualname": "_format_provision_recipe_section",
      "async": false,
      "lineno": 12126,
      "end_lineno": 12179,
      "span": 54,
      "decorators": [],
      "signature": "(recipe: list[dict], *, audience: str)",
      "returns": "str | None",
      "doc": "Render the persisted provision recipe as a prompt section, or"
    },
    {
      "name": "run_implementer",
      "qualname": "run_implementer",
      "async": true,
      "lineno": 12182,
      "end_lineno": 12290,
      "span": 109,
      "decorators": [],
      "signature": "(sid: str, leerie_dir: Path, caps: dict, st: State, models: dict[str, str], efforts: dict[str, str | None], continuation: bool = False, note: str = '')",
      "returns": "dict",
      "doc": "Spawn one implementer for one subtask in its own worktree. Handles"
    },
    {
      "name": "_retryable_failure",
      "qualname": "_retryable_failure",
      "async": false,
      "lineno": 12320,
      "end_lineno": 12334,
      "span": 15,
      "decorators": [],
      "signature": "(kind: str)",
      "returns": "bool",
      "doc": "The retry policy, in one place. Dispatches on a structured"
    },
    {
      "name": "discover_rules_files",
      "qualname": "discover_rules_files",
      "async": false,
      "lineno": 12361,
      "end_lineno": 12373,
      "span": 13,
      "decorators": [],
      "signature": "(repo_root: Path)",
      "returns": "list[Path]",
      "doc": "Return existing rule-file paths from `_RULES_FILE_CANDIDATES`, in"
    },
    {
      "name": "_is_rails_repo",
      "qualname": "_is_rails_repo",
      "async": false,
      "lineno": 12376,
      "end_lineno": 12381,
      "span": 6,
      "decorators": [],
      "signature": "(repo_root: Path)",
      "returns": "bool",
      "doc": "True when the repo is a Rails application. Requires both a"
    },
    {
      "name": "_infer_build_lint_test",
      "qualname": "_infer_build_lint_test",
      "async": false,
      "lineno": 12384,
      "end_lineno": 12448,
      "span": 65,
      "decorators": [],
      "signature": "(repo_root: Path)",
      "returns": "dict[str, str]",
      "doc": "Best-effort guess at the repo's build / lint / test commands. Returns"
    },
    {
      "name": "validate_conformance_result",
      "qualname": "validate_conformance_result",
      "async": false,
      "lineno": 12451,
      "end_lineno": 12504,
      "span": 54,
      "decorators": [],
      "signature": "(result: dict, worktree: str)",
      "returns": "str | None",
      "doc": "Cross-field invariants for the conformer's structured output."
    },
    {
      "name": "_branch_head_sha",
      "qualname": "_branch_head_sha",
      "async": true,
      "lineno": 12507,
      "end_lineno": 12513,
      "span": 7,
      "decorators": [],
      "signature": "(worktree: str)",
      "returns": "str",
      "doc": "HEAD sha in the worktree, or empty string on failure. Used as the"
    },
    {
      "name": "_protected_paths_since",
      "qualname": "_protected_paths_since",
      "async": true,
      "lineno": 12516,
      "end_lineno": 12537,
      "span": 22,
      "decorators": [],
      "signature": "(worktree: str, before_sha: str)",
      "returns": "list[str]",
      "doc": "Return the list of protected paths the diff `before_sha..HEAD`"
    },
    {
      "name": "rollback_conformer_commits",
      "qualname": "rollback_conformer_commits",
      "async": true,
      "lineno": 12540,
      "end_lineno": 12551,
      "span": 12,
      "decorators": [],
      "signature": "(worktree: str, before_sha: str)",
      "returns": "None",
      "doc": "Hard-reset the subtask branch back to `before_sha`. Used when the"
    },
    {
      "name": "_uncommitted_paths",
      "qualname": "_uncommitted_paths",
      "async": true,
      "lineno": 12554,
      "end_lineno": 12568,
      "span": 15,
      "decorators": [],
      "signature": "(worktree: str)",
      "returns": "list[str]",
      "doc": "Return tracked-file paths with uncommitted changes in the worktree,"
    },
    {
      "name": "_unprefixed_conformer_commits",
      "qualname": "_unprefixed_conformer_commits",
      "async": true,
      "lineno": 12571,
      "end_lineno": 12593,
      "span": 23,
      "decorators": [],
      "signature": "(worktree: str, before_sha: str, prefix: str = 'conformer:')",
      "returns": "list[str]",
      "doc": "Return subject lines of commits between before_sha..HEAD whose"
    },
    {
      "name": "run_conformer",
      "qualname": "run_conformer",
      "async": true,
      "lineno": 12596,
      "end_lineno": 12662,
      "span": 67,
      "decorators": [],
      "signature": "(sid: str, leerie_dir: Path, worktree: str, caps: dict, st: State, models: dict[str, str], efforts: dict[str, str | None], rules_files: list[Path], blt_commands: dict[str, str], diff_base: str, extra_feedback: str | None = None)",
      "returns": "dict | None",
      "doc": "Spawn one conformer for one subtask in its existing worktree."
    },
    {
      "name": "_summarize_residuals",
      "qualname": "_summarize_residuals",
      "async": false,
      "lineno": 12665,
      "end_lineno": 12678,
      "span": 14,
      "decorators": [],
      "signature": "(conf_res: dict)",
      "returns": "list[str]",
      "doc": "One advisory string per residual / failing build-lint-test axis."
    },
    {
      "name": "_confidence_axes_clear",
      "qualname": "_confidence_axes_clear",
      "async": false,
      "lineno": 12681,
      "end_lineno": 12692,
      "span": 12,
      "decorators": [],
      "signature": "(conf: dict, axes: list[str], threshold: float = 9.0)",
      "returns": "bool",
      "doc": "True when every named axis in *conf* is a number >= *threshold*."
    },
    {
      "name": "_format_check_feedback",
      "qualname": "_format_check_feedback",
      "async": false,
      "lineno": 12695,
      "end_lineno": 12715,
      "span": 21,
      "decorators": [],
      "signature": "(issues: list[str], rnd: int, max_rounds: int)",
      "returns": "str",
      "doc": "Format a structured feedback block for a re-invocation."
    },
    {
      "name": "_run_checked_loop",
      "qualname": "_run_checked_loop",
      "async": true,
      "lineno": 12718,
      "end_lineno": 12771,
      "span": 54,
      "decorators": [],
      "signature": "(*, invoke: Callable[..., Awaitable[dict]], check: Callable[[dict], list[str]], name: str, max_rounds: int, make_feedback_prompt: Callable[[str], Awaitable[dict]] | None = None)",
      "returns": "tuple[dict | None, list[str]]",
      "doc": "Generic mechanical-feedback retry loop (CRITIC pattern)."
    },
    {
      "name": "_conformance_clean",
      "qualname": "_conformance_clean",
      "async": false,
      "lineno": 12774,
      "end_lineno": 12784,
      "span": 11,
      "decorators": [],
      "signature": "(conf_res: dict)",
      "returns": "bool",
      "doc": "True when the conformer reports no residuals and every axis is"
    },
    {
      "name": "_iter_log_tool_use",
      "qualname": "_iter_log_tool_use",
      "async": false,
      "lineno": 12821,
      "end_lineno": 12875,
      "span": 55,
      "decorators": [],
      "signature": "(log_path: Path)",
      "returns": "Iterator[tuple[str, dict, str]]",
      "doc": "Yield each Bash/BashOutput/KillBash/Read `tool_use` block from a"
    },
    {
      "name": "_count_bash_axis_invocations",
      "qualname": "_count_bash_axis_invocations",
      "async": false,
      "lineno": 12878,
      "end_lineno": 12889,
      "span": 12,
      "decorators": [],
      "signature": "(log_path: Path, axis_re: re.Pattern[str])",
      "returns": "int",
      "doc": "Count distinct Bash `tool_use` invocations in `log_path` whose"
    },
    {
      "name": "_count_orphaned_bg_axis",
      "qualname": "_count_orphaned_bg_axis",
      "async": false,
      "lineno": 12892,
      "end_lineno": 12953,
      "span": 62,
      "decorators": [],
      "signature": "(log_path: Path, axis_re: re.Pattern[str])",
      "returns": "list[str]",
      "doc": "Return the bash_ids of BLT commands matching `axis_re` that"
    },
    {
      "name": "_emit_bash_axis_warnings",
      "qualname": "_emit_bash_axis_warnings",
      "async": false,
      "lineno": 12956,
      "end_lineno": 12981,
      "span": 26,
      "decorators": [],
      "signature": "(log_path: Path, round_label: str, warnings: list[str])",
      "returns": "None",
      "doc": "Helper called once per conformer round: append advisory warnings"
    },
    {
      "name": "_run_conformance_phase",
      "qualname": "_run_conformance_phase",
      "async": true,
      "lineno": 12984,
      "end_lineno": 13093,
      "span": 110,
      "decorators": [],
      "signature": "(sid: str, leerie_dir: Path, worktree: str, subtask: dict, caps: dict, st: State, models: dict[str, str], efforts: dict[str, str | None])",
      "returns": "tuple[dict | None, list[str], str | None]",
      "doc": "Drive the orchestrator-level conformer loop for one subtask."
    },
    {
      "name": "run_final_conformance",
      "qualname": "run_final_conformance",
      "async": true,
      "lineno": 13096,
      "end_lineno": 13288,
      "span": 193,
      "decorators": [],
      "signature": "(leerie_dir: Path, st: State, caps: dict, models: dict[str, str], efforts: dict[str, str | None])",
      "returns": "None",
      "doc": "Whole-tree conformance pass on the integrated staging worktree"
    },
    {
      "name": "settle_subtask",
      "qualname": "settle_subtask",
      "async": true,
      "lineno": 13291,
      "end_lineno": 13580,
      "span": 290,
      "decorators": [],
      "signature": "(sid: str, leerie_dir: Path, caps: dict, st: State, models: dict[str, str], efforts: dict[str, str | None])",
      "returns": "dict",
      "doc": "Drive one subtask to a terminal state."
    },
    {
      "name": "integrate_wave",
      "qualname": "integrate_wave",
      "async": true,
      "lineno": 13583,
      "end_lineno": 13696,
      "span": 114,
      "decorators": [],
      "signature": "(wave: list[str], results: dict[str, dict], leerie_dir: Path, caps: dict, st: State, models: dict[str, str], efforts: dict[str, str | None])",
      "returns": "list[str]",
      "doc": "Merge each completed subtask branch into staging (git merge, not"
    },
    {
      "name": "phase_execute",
      "qualname": "phase_execute",
      "async": true,
      "lineno": 13699,
      "end_lineno": 13792,
      "span": 94,
      "decorators": [],
      "signature": "(leerie_dir: Path, st: State, caps: dict, models: dict[str, str], efforts: dict[str, str | None])",
      "returns": "None",
      "doc": "Phases 4-5: create staging, then run waves sequentially; within a wave,"
    },
    {
      "name": "find_pr_template",
      "qualname": "find_pr_template",
      "async": false,
      "lineno": 13829,
      "end_lineno": 13874,
      "span": 46,
      "decorators": [],
      "signature": "(repo_root: Path, override: str | None = None)",
      "returns": "tuple[Path, str] | None",
      "doc": "Locate the PR template the worker should fill out, or None when"
    },
    {
      "name": "_cap_text",
      "qualname": "_cap_text",
      "async": false,
      "lineno": 13894,
      "end_lineno": 13913,
      "span": 20,
      "decorators": [],
      "signature": "(s: str, max_bytes: int, label: str)",
      "returns": "tuple[str, bool]",
      "doc": "Return (capped_text, was_truncated). Cap `s` at `max_bytes` of"
    },
    {
      "name": "_strip_leerie_prefix",
      "qualname": "_strip_leerie_prefix",
      "async": false,
      "lineno": 13922,
      "end_lineno": 13932,
      "span": 11,
      "decorators": [],
      "signature": "(title: str)",
      "returns": "str",
      "doc": "Strip a leading `leerie:` from a worker-emitted PR title so the"
    },
    {
      "name": "_truncate_diff_sample",
      "qualname": "_truncate_diff_sample",
      "async": false,
      "lineno": 13935,
      "end_lineno": 13949,
      "span": 15,
      "decorators": [],
      "signature": "(diff_text: str, max_lines: int)",
      "returns": "tuple[str, bool]",
      "doc": "Return (truncated_text, was_truncated). Splits on newlines and"
    },
    {
      "name": "_final_conformance_payload",
      "qualname": "_final_conformance_payload",
      "async": false,
      "lineno": 13952,
      "end_lineno": 14008,
      "span": 57,
      "decorators": [],
      "signature": "(st: 'State')",
      "returns": "dict | None",
      "doc": "Compact view of the final-tree conformer pass for the pr_writer"
    },
    {
      "name": "_compose_pr_via_llm",
      "qualname": "_compose_pr_via_llm",
      "async": true,
      "lineno": 14011,
      "end_lineno": 14191,
      "span": 181,
      "decorators": [],
      "signature": "(st: 'State', caps: dict, models: dict[str, str], efforts: dict[str, str | None], repo_root: Path, pr_template_override: str | None)",
      "returns": "None",
      "doc": "Run the pr_writer worker and persist its title/body to run.json."
    },
    {
      "name": "phase_finalize",
      "qualname": "phase_finalize",
      "async": true,
      "lineno": 14194,
      "end_lineno": 14298,
      "span": 105,
      "decorators": [],
      "signature": "(leerie_dir: Path, st: State, no_push: bool, no_verify: bool, caps: dict | None = None, models: dict[str, str] | None = None, efforts: dict[str, str | None] | None = None, pr_template_override: str | None = None, host_no_push: bool | None = None)",
      "returns": "None",
      "doc": "Phase 6: verify the run branch and record finalize state."
    },
    {
      "name": "orchestrate",
      "qualname": "orchestrate",
      "async": true,
      "lineno": 14304,
      "end_lineno": 14322,
      "span": 19,
      "decorators": [],
      "signature": "(args, caps: dict, leerie_dir: Path, st: State, sot_pref: str, verbosity: str, models: dict[str, str], efforts: dict[str, str | None])",
      "returns": "None",
      "doc": "The async portion of a run: every phase that spawns a `claude -p`"
    },
    {
      "name": "_run_phases",
      "qualname": "_run_phases",
      "async": true,
      "lineno": 14325,
      "end_lineno": 14542,
      "span": 218,
      "decorators": [],
      "signature": "(args, caps: dict, leerie_dir: Path, st: State, sot_pref: str, verbosity: str, models: dict[str, str], efforts: dict[str, str | None])",
      "returns": "None",
      "doc": "The phase sequence of one run. Split out from `orchestrate()`"
    },
    {
      "name": "main",
      "qualname": "main",
      "async": false,
      "lineno": 14545,
      "end_lineno": 15317,
      "span": 773,
      "decorators": [],
      "signature": "()",
      "returns": "None",
      "doc": null
    }
  ],
  "classes": [
    {
      "name": "InterruptedBySignal",
      "bases": [
        "BaseException"
      ],
      "lineno": 1320,
      "end_lineno": 1332,
      "span": 13,
      "doc": "Raised by signal handlers (SIGTERM, SIGHUP) installed in main().",
      "methods": []
    },
    {
      "name": "RateLimitedExit",
      "bases": [
        "BaseException"
      ],
      "lineno": 1335,
      "end_lineno": 1356,
      "span": 22,
      "doc": "Raised when claude -p reports the Claude Code subscription",
      "methods": [
        {
          "name": "__init__",
          "qualname": "RateLimitedExit.__init__",
          "async": false,
          "lineno": 1353,
          "end_lineno": 1356,
          "span": 4,
          "decorators": [],
          "signature": "(self, reset_at: datetime | None, raw_message: str)",
          "returns": null,
          "doc": null
        }
      ]
    },
    {
      "name": "_DescendantTracker",
      "bases": [],
      "lineno": 1498,
      "end_lineno": 1583,
      "span": 86,
      "doc": "Background poller that accumulates every PID ever observed as a",
      "methods": [
        {
          "name": "__init__",
          "qualname": "_DescendantTracker.__init__",
          "async": false,
          "lineno": 1527,
          "end_lineno": 1531,
          "span": 5,
          "decorators": [],
          "signature": "(self, leader_pid: int)",
          "returns": null,
          "doc": null
        },
        {
          "name": "start",
          "qualname": "_DescendantTracker.start",
          "async": false,
          "lineno": 1533,
          "end_lineno": 1536,
          "span": 4,
          "decorators": [],
          "signature": "(self)",
          "returns": "None",
          "doc": "Spawn the polling task on the current event loop."
        },
        {
          "name": "_poll_loop",
          "qualname": "_DescendantTracker._poll_loop",
          "async": true,
          "lineno": 1538,
          "end_lineno": 1560,
          "span": 23,
          "decorators": [],
          "signature": "(self)",
          "returns": "None",
          "doc": null
        },
        {
          "name": "stop_and_reap",
          "qualname": "_DescendantTracker.stop_and_reap",
          "async": true,
          "lineno": 1562,
          "end_lineno": 1583,
          "span": 22,
          "decorators": [],
          "signature": "(self)",
          "returns": "int",
          "doc": "Stop polling, SIGKILL every accumulated PID, return the"
        }
      ]
    },
    {
      "name": "WorkerError",
      "bases": [
        "RuntimeError"
      ],
      "lineno": 5449,
      "end_lineno": 5450,
      "span": 2,
      "doc": null,
      "methods": []
    },
    {
      "name": "_ReplayState",
      "bases": [],
      "lineno": 6746,
      "end_lineno": 6774,
      "span": 29,
      "doc": "Minimal State-alike for replay_capture: no persistent writes.",
      "methods": [
        {
          "name": "__init__",
          "qualname": "_ReplayState.__init__",
          "async": false,
          "lineno": 6755,
          "end_lineno": 6764,
          "span": 10,
          "decorators": [],
          "signature": "(self, run_dir: Path, state_path: Path)",
          "returns": "None",
          "doc": null
        },
        {
          "name": "save",
          "qualname": "_ReplayState.save",
          "async": false,
          "lineno": 6766,
          "end_lineno": 6767,
          "span": 2,
          "decorators": [],
          "signature": "(self)",
          "returns": "None",
          "doc": null
        },
        {
          "name": "bump_workers",
          "qualname": "_ReplayState.bump_workers",
          "async": false,
          "lineno": 6769,
          "end_lineno": 6770,
          "span": 2,
          "decorators": [],
          "signature": "(self, caps: dict)",
          "returns": "None",
          "doc": null
        },
        {
          "name": "add_telemetry",
          "qualname": "_ReplayState.add_telemetry",
          "async": false,
          "lineno": 6772,
          "end_lineno": 6774,
          "span": 3,
          "decorators": [],
          "signature": "(self, envelope: dict)",
          "returns": "None",
          "doc": null
        }
      ]
    },
    {
      "name": "StateLockedError",
      "bases": [
        "Exception"
      ],
      "lineno": 6777,
      "end_lineno": 6789,
      "span": 13,
      "doc": "Raised when State.__init__ cannot acquire the per-run-directory",
      "methods": [
        {
          "name": "__init__",
          "qualname": "StateLockedError.__init__",
          "async": false,
          "lineno": 6787,
          "end_lineno": 6789,
          "span": 3,
          "decorators": [],
          "signature": "(self, run_dir: Path)",
          "returns": null,
          "doc": null
        }
      ]
    },
    {
      "name": "State",
      "bases": [],
      "lineno": 6795,
      "end_lineno": 6924,
      "span": 130,
      "doc": "In-memory run state with atomic on-disk persistence.",
      "methods": [
        {
          "name": "__init__",
          "qualname": "State.__init__",
          "async": false,
          "lineno": 6824,
          "end_lineno": 6844,
          "span": 21,
          "decorators": [],
          "signature": "(self, leerie_root: Path, run_id: str, repo_root: Path | None = None)",
          "returns": null,
          "doc": null
        },
        {
          "name": "_acquire_lock",
          "qualname": "State._acquire_lock",
          "async": false,
          "lineno": 6846,
          "end_lineno": 6860,
          "span": 15,
          "decorators": [],
          "signature": "(self)",
          "returns": "None",
          "doc": "Open run_dir for flock and acquire EX|NB. Raises"
        },
        {
          "name": "release_lock",
          "qualname": "State.release_lock",
          "async": false,
          "lineno": 6862,
          "end_lineno": 6877,
          "span": 16,
          "decorators": [],
          "signature": "(self)",
          "returns": "None",
          "doc": "Explicit release. Idempotent. The kernel also releases on"
        },
        {
          "name": "__del__",
          "qualname": "State.__del__",
          "async": false,
          "lineno": 6879,
          "end_lineno": 6890,
          "span": 12,
          "decorators": [],
          "signature": "(self)",
          "returns": "None",
          "doc": null
        },
        {
          "name": "load",
          "qualname": "State.load",
          "async": false,
          "lineno": 6892,
          "end_lineno": 6896,
          "span": 5,
          "decorators": [],
          "signature": "(self)",
          "returns": "bool",
          "doc": null
        },
        {
          "name": "save",
          "qualname": "State.save",
          "async": false,
          "lineno": 6898,
          "end_lineno": 6907,
          "span": 10,
          "decorators": [],
          "signature": "(self)",
          "returns": "None",
          "doc": "Atomic write via temp-file rename."
        },
        {
          "name": "bump_workers",
          "qualname": "State.bump_workers",
          "async": false,
          "lineno": 6909,
          "end_lineno": 6917,
          "span": 9,
          "decorators": [],
          "signature": "(self, caps: dict)",
          "returns": "None",
          "doc": null
        },
        {
          "name": "add_telemetry",
          "qualname": "State.add_telemetry",
          "async": false,
          "lineno": 6919,
          "end_lineno": 6924,
          "span": 6,
          "decorators": [],
          "signature": "(self, envelope: dict)",
          "returns": "None",
          "doc": "Accumulate run-weight signals from a worker envelope. On a"
        }
      ]
    },
    {
      "name": "HealState",
      "bases": [],
      "lineno": 7057,
      "end_lineno": 7102,
      "span": 46,
      "doc": "Persistent state for one heal-loop run scoped to a single call_type.",
      "methods": [
        {
          "name": "__init__",
          "qualname": "HealState.__init__",
          "async": false,
          "lineno": 7070,
          "end_lineno": 7078,
          "span": 9,
          "decorators": [],
          "signature": "(self, heal_dir: Path, call_type: str)",
          "returns": "None",
          "doc": null
        },
        {
          "name": "save",
          "qualname": "HealState.save",
          "async": false,
          "lineno": 7080,
          "end_lineno": 7091,
          "span": 12,
          "decorators": [],
          "signature": "(self)",
          "returns": "None",
          "doc": "Atomic write via temp-file rename."
        },
        {
          "name": "load",
          "qualname": "HealState.load",
          "async": false,
          "lineno": 7093,
          "end_lineno": 7102,
          "span": 10,
          "decorators": [],
          "signature": "(self)",
          "returns": "bool",
          "doc": "Load state from disk. Returns True if file existed and was loaded."
        }
      ]
    }
  ],
  "callgraph": {
    "fan_in_top": {
      "log": 42,
      "die": 34,
      "run_proc": 18,
      "claude_p": 13,
      "load_prompt": 12,
      "now": 11,
      "_read_toml_key": 10,
      "compute_run_branch": 8,
      "_resolve_positive_int_pref": 8,
      "_resolve_bool_pref": 6,
      "_confidence_issues": 6,
      "_run_checked_loop": 6,
      "gather_or_cancel": 5,
      "_write_run_json": 5,
      "_resolve_str_pref": 4,
      "is_protected_path": 4,
      "_build_predecessor_graph": 4,
      "run_script": 4,
      "_format_check_feedback": 4,
      "_enumerate_descendants": 3,
      "_resolve_enum_pref": 3,
      "_terminate_proc_tree": 3,
      "judge_capture": 3,
      "_attribute_cycle_edges": 3,
      "_shared_files_in_scc": 3,
      "_format_provision_recipe_section": 3,
      "_signal_pids": 2,
      "_format_run_duration": 2,
      "_validate_run_json": 2,
      "discover_runs": 2,
      "_derive_run_status": 2,
      "_parse_bool_envtoml": 2,
      "_invoke": 2,
      "_expand_braces": 2,
      "_read_file_safely": 2,
      "_strip_bullet": 2,
      "_detect_cgroup_root": 2,
      "_accumulate_telemetry": 2,
      "replay_capture": 2,
      "run_streaming": 2
    },
    "fan_out_top": {
      "main": 41,
      "_run_phases": 29,
      "phase_reconcile": 21,
      "run_final_conformance": 17,
      "settle_subtask": 16,
      "_run_conformance_phase": 14,
      "phase_provision": 13,
      "phase_plan": 11,
      "phase_overlap_judge": 11,
      "integrate_wave": 11,
      "_compose_pr_via_llm": 11,
      "phase_finalize": 9,
      "_invoke": 8,
      "phase_execute": 8,
      "phase_heal": 7,
      "claude_p": 6,
      "phase_classify": 6,
      "preflight": 5,
      "_build_cycle_retry_prompt": 5,
      "run_implementer": 5,
      "check_diff_scope": 4,
      "_summarize_stream_event": 4,
      "heal_baseline": 4,
      "heal_replay_patched": 4,
      "synth_mise_go_override": 4,
      "run_mise_install": 4,
      "_apply_overlap_collisions": 4,
      "run_conformer": 4,
      "resolve_run_id": 3,
      "_format_run_for_disambiguation": 3,
      "_collect_run_rows": 3,
      "resolve_worker_memory_max": 3,
      "_resolve_bool_pref": 3,
      "resolve_telemetry_enabled": 3,
      "check_planner_output": 3,
      "validate_plan": 3,
      "extract_readme_sections": 3,
      "gather_provision_fixtures": 3,
      "validate_checkpoint": 3,
      "_cgroup_create": 3
    },
    "edges": {
      "_read_version": [],
      "load_prompt": [],
      "is_protected_path": [],
      "resolve_prompt": [],
      "_confidence_schema": [],
      "now": [
        "now"
      ],
      "log": [
        "now"
      ],
      "die": [],
      "RateLimitedExit.__init__": [],
      "detect_session_limit": [
        "now"
      ],
      "_install_signal_handlers": [],
      "_enumerate_descendants": [],
      "_signal_pids": [],
      "_DescendantTracker.__init__": [],
      "_DescendantTracker.start": [],
      "_DescendantTracker._poll_loop": [
        "_enumerate_descendants"
      ],
      "_DescendantTracker.stop_and_reap": [
        "_enumerate_descendants",
        "_signal_pids"
      ],
      "_terminate_proc_tree": [
        "_enumerate_descendants",
        "_signal_pids"
      ],
      "_cleanup_on_abnormal_exit": [
        "log"
      ],
      "_reset_subtask_worktree": [
        "run_proc"
      ],
      "_parse_claude_version": [],
      "_check_claude_cli_version": [
        "die",
        "_parse_claude_version"
      ],
      "compute_run_branch": [],
      "compute_subtask_branch": [],
      "_validate_run_json": [],
      "_format_run_duration": [],
      "compose_pr_body": [
        "_format_run_duration"
      ],
      "_write_run_json": [
        "_validate_run_json"
      ],
      "discover_runs": [
        "log"
      ],
      "resolve_run_id": [
        "discover_runs",
        "die",
        "_format_run_for_disambiguation"
      ],
      "_format_run_for_disambiguation": [
        "_derive_run_status",
        "_format_age",
        "now"
      ],
      "_format_age": [],
      "_derive_run_status": [
        "_validate_run_json"
      ],
      "_collect_run_rows": [
        "discover_runs",
        "_derive_run_status",
        "compute_run_branch"
      ],
      "_render_run_table": [],
      "list_runs": [
        "_collect_run_rows",
        "_render_run_table"
      ],
      "_read_toml_key": [],
      "resolve_task_argument": [
        "die"
      ],
      "resolve_leerie_root": [],
      "_resolve_enum_pref": [
        "die",
        "_read_toml_key"
      ],
      "resolve_source_of_truth": [
        "_resolve_enum_pref"
      ],
      "resolve_runtime": [
        "_resolve_enum_pref"
      ],
      "_resolve_str_pref": [
        "_read_toml_key"
      ],
      "resolve_pr_template": [
        "_resolve_str_pref"
      ],
      "_resolve_positive_int_pref": [
        "die",
        "_read_toml_key"
      ],
      "resolve_confidence_rounds": [
        "_resolve_positive_int_pref"
      ],
      "resolve_max_workers": [
        "_resolve_positive_int_pref"
      ],
      "resolve_max_parallel": [
        "_resolve_positive_int_pref"
      ],
      "resolve_judgment_check_rounds": [
        "_resolve_positive_int_pref"
      ],
      "resolve_planner_check_rounds": [
        "_resolve_positive_int_pref"
      ],
      "resolve_implementer_confidence_retries": [
        "_resolve_positive_int_pref"
      ],
      "resolve_planner_samples": [
        "_resolve_positive_int_pref"
      ],
      "_parse_memory_size": [
        "die"
      ],
      "_auto_worker_memory_max": [],
      "resolve_worker_memory_max": [
        "_parse_memory_size",
        "_read_toml_key",
        "_auto_worker_memory_max"
      ],
      "resolve_inspect_dirs": [
        "_read_toml_key"
      ],
      "_parse_bool_envtoml": [],
      "_resolve_bool_pref": [
        "_parse_bool_envtoml",
        "die",
        "_read_toml_key"
      ],
      "resolve_no_push": [
        "_resolve_bool_pref"
      ],
      "push_will_happen": [],
      "resolve_clarify": [
        "_resolve_bool_pref"
      ],
      "resolve_dangerously_skip_permissions": [
        "_resolve_bool_pref"
      ],
      "resolve_skip_overlap_judge": [
        "_resolve_bool_pref"
      ],
      "resolve_skip_budget_check": [
        "_resolve_bool_pref"
      ],
      "resolve_strict_conformer": [
        "_resolve_bool_pref"
      ],
      "_positive_int": [],
      "resolve_verbosity": [
        "_resolve_enum_pref"
      ],
      "verbosity_from_shortcuts": [],
      "resolve_models": [
        "die",
        "_read_toml_key"
      ],
      "resolve_efforts": [
        "die",
        "_read_toml_key"
      ],
      "resolve_telemetry_enabled": [
        "_parse_bool_envtoml",
        "die",
        "_read_toml_key"
      ],
      "resolve_telemetry_subdir": [
        "_resolve_str_pref"
      ],
      "resolve_judge_dir": [
        "_resolve_str_pref"
      ],
      "resolve_heal_dir": [
        "_resolve_str_pref"
      ],
      "resolve_heal_max_rounds": [
        "_resolve_positive_int_pref"
      ],
      "resolve_heal_success_threshold": [
        "die",
        "_read_toml_key"
      ],
      "run_proc": [
        "_terminate_proc_tree"
      ],
      "run_streaming": [
        "log",
        "_terminate_proc_tree"
      ],
      "gather_or_cancel": [],
      "run_script": [
        "run_proc"
      ],
      "preflight": [
        "run_proc",
        "die",
        "_check_claude_cli_version",
        "log",
        "_invoke"
      ],
      "_confidence_issues": [],
      "check_classifier_output": [
        "_confidence_issues"
      ],
      "_grep_old_pattern": [],
      "_check_migration_surface": [
        "_grep_old_pattern"
      ],
      "check_planner_output": [
        "is_protected_path",
        "_check_migration_surface",
        "_confidence_issues"
      ],
      "check_reconciler_output": [
        "_confidence_issues"
      ],
      "check_overlap_judge_output": [
        "_confidence_issues"
      ],
      "check_provision_output": [
        "_confidence_issues"
      ],
      "check_integrator_output": [
        "_confidence_issues"
      ],
      "check_implementer_output": [],
      "_expand_braces": [
        "_expand_braces"
      ],
      "glob_task_references": [
        "_expand_braces"
      ],
      "extract_task_file_structure": [
        "glob_task_references"
      ],
      "check_task_file_coverage": [],
      "_format_task_file_structure": [],
      "validate_plan": [
        "is_protected_path",
        "die",
        "log"
      ],
      "warn_cross_planner_file_overlap": [
        "log"
      ],
      "warn_layer_gaps": [
        "log"
      ],
      "_resolves_under": [],
      "filter_offtree_subtasks": [
        "_resolves_under",
        "log"
      ],
      "_lockfile_table_entries": [],
      "detect_recipe_from_lockfiles": [
        "_lockfile_table_entries"
      ],
      "validate_provision_recipe": [],
      "_split_readme_headers": [],
      "_is_install_section": [],
      "_slice_code_fences_with_install_hints": [],
      "extract_readme_sections": [
        "_split_readme_headers",
        "_is_install_section",
        "_slice_code_fences_with_install_hints"
      ],
      "_read_file_safely": [],
      "_sample_workspace_manifests": [
        "_read_file_safely"
      ],
      "gather_provision_fixtures": [
        "_read_file_safely",
        "extract_readme_sections",
        "_sample_workspace_manifests"
      ],
      "_split_checkpoint_sections": [],
      "validate_checkpoint": [
        "_split_checkpoint_sections",
        "_normalize_for_noise",
        "_parse_touched_file_line"
      ],
      "_normalize_for_noise": [
        "_strip_bullet"
      ],
      "_strip_bullet": [],
      "_parse_touched_file_line": [
        "_strip_bullet"
      ],
      "validate_result": [],
      "check_diff_scope": [
        "compute_run_branch",
        "run_proc",
        "is_protected_path",
        "log"
      ],
      "check_merge_committed": [
        "run_proc"
      ],
      "check_integrator_commit": [
        "run_proc"
      ],
      "check_branch_has_commits": [
        "run_proc"
      ],
      "scan_conflict_markers": [
        "run_proc"
      ],
      "validate_resume_state": [
        "die"
      ],
      "_is_auth_or_quota_failure": [],
      "_extract_tool_result_text": [],
      "_tag_each_line": [],
      "_summarize_tool_use": [],
      "_summarize_stream_event": [
        "detect_session_limit",
        "_summarize_tool_use",
        "_extract_tool_result_text",
        "_tag_each_line"
      ],
      "_format_progress_prefix": [],
      "_get_progress": [],
      "_detect_cgroup_root": [],
      "_cgroup_probe": [
        "_detect_cgroup_root",
        "log"
      ],
      "_cgroup_create": [
        "_cgroup_probe",
        "_detect_cgroup_root",
        "log"
      ],
      "_cgroup_enroll": [
        "log"
      ],
      "_cgroup_destroy": [],
      "_invoke": [
        "log",
        "_cgroup_create",
        "_cgroup_enroll",
        "now",
        "_summarize_stream_event",
        "_format_progress_prefix",
        "_terminate_proc_tree",
        "_cgroup_destroy"
      ],
      "_capture_call": [],
      "_collect_memory_sample": [
        "now"
      ],
      "_memory_sampler": [
        "_collect_memory_sample"
      ],
      "claude_p": [
        "_invoke",
        "_get_progress",
        "_capture_call",
        "now",
        "log",
        "_is_auth_or_quota_failure"
      ],
      "replay_capture": [
        "claude_p"
      ],
      "_accumulate_telemetry": [],
      "_ReplayState.__init__": [],
      "_ReplayState.save": [],
      "_ReplayState.bump_workers": [],
      "_ReplayState.add_telemetry": [
        "_accumulate_telemetry"
      ],
      "StateLockedError.__init__": [],
      "State.__init__": [],
      "State._acquire_lock": [],
      "State.release_lock": [],
      "State.__del__": [],
      "State.load": [],
      "State.save": [],
      "State.bump_workers": [],
      "State.add_telemetry": [
        "_accumulate_telemetry"
      ],
      "judge_capture": [
        "load_prompt",
        "claude_p"
      ],
      "phase_judge": [
        "log",
        "judge_capture",
        "gather_or_cancel"
      ],
      "HealState.__init__": [],
      "HealState.save": [],
      "HealState.load": [],
      "heal_baseline": [
        "replay_capture",
        "judge_capture",
        "gather_or_cancel",
        "log"
      ],
      "heal_apply_patch": [
        "log"
      ],
      "heal_replay_patched": [
        "replay_capture",
        "judge_capture",
        "log",
        "gather_or_cancel"
      ],
      "check_convergence": [],
      "write_heal_report": [
        "log"
      ],
      "request_patch": [
        "resolve_prompt",
        "load_prompt",
        "claude_p"
      ],
      "phase_heal": [
        "log",
        "heal_baseline",
        "request_patch",
        "heal_apply_patch",
        "heal_replay_patched",
        "check_convergence",
        "write_heal_report"
      ],
      "run_setup_hook": [
        "die",
        "log",
        "run_streaming"
      ],
      "_existing_mise_toml_path": [],
      "_go_already_pinned": [
        "_existing_mise_toml_path"
      ],
      "_existing_mise_toml_tool_keys": [],
      "_read_idiomatic_pins": [],
      "synth_mise_go_override": [
        "_go_already_pinned",
        "_existing_mise_toml_path",
        "_existing_mise_toml_tool_keys",
        "_read_idiomatic_pins"
      ],
      "_repo_has_version_signal": [],
      "run_mise_install": [
        "_repo_has_version_signal",
        "log",
        "run_streaming",
        "die"
      ],
      "phase_classify": [
        "log",
        "load_prompt",
        "claude_p",
        "_run_checked_loop",
        "check_classifier_output",
        "die"
      ],
      "gather_answers": [
        "die",
        "log"
      ],
      "absorb_supplied_answers": [
        "die"
      ],
      "surface_clarification": [
        "log"
      ],
      "_format_provision_user_prompt": [],
      "phase_provision": [
        "log",
        "run_setup_hook",
        "synth_mise_go_override",
        "run_mise_install",
        "detect_recipe_from_lockfiles",
        "gather_provision_fixtures",
        "load_prompt",
        "_format_provision_user_prompt",
        "claude_p",
        "_run_checked_loop",
        "check_provision_output",
        "die",
        "validate_provision_recipe"
      ],
      "_select_best_planner_sample": [
        "check_planner_output",
        "log"
      ],
      "phase_plan": [
        "log",
        "load_prompt",
        "extract_task_file_structure",
        "_format_task_file_structure",
        "claude_p",
        "check_planner_output",
        "check_task_file_coverage",
        "_run_checked_loop",
        "die",
        "gather_or_cancel",
        "_select_best_planner_sample"
      ],
      "_promote_external_collisions": [],
      "_collect_external_preconditions": [],
      "_compute_unresolved_requires": [],
      "_find_oversized_added_subtasks": [],
      "_apply_reconciler_output": [
        "die"
      ],
      "phase_reconcile": [
        "die",
        "_promote_external_collisions",
        "log",
        "_collect_external_preconditions",
        "_compute_unresolved_requires",
        "load_prompt",
        "claude_p",
        "_run_checked_loop",
        "check_reconciler_output",
        "_apply_reconciler_output",
        "_find_oversized_added_subtasks",
        "_build_size_retry_prompt",
        "_build_predecessor_graph",
        "_tarjan_sccs",
        "_format_cycle_diagnostic",
        "_recommend_cycle_resolution",
        "_build_cycle_retry_prompt",
        "_validate_must_include",
        "_recommend_unresolved_resolution",
        "_build_unresolved_retry_prompt",
        "_validate_unresolved_must_include"
      ],
      "_tarjan_sccs": [],
      "_attribute_cycle_edges": [],
      "_format_cycle_diagnostic": [
        "_attribute_cycle_edges",
        "_shared_files_in_scc"
      ],
      "_shared_files_in_scc": [],
      "_original_tag_for_rename_edge": [],
      "_recommend_cycle_resolution": [
        "_attribute_cycle_edges",
        "_original_tag_for_rename_edge",
        "_shared_files_in_scc"
      ],
      "_format_recommendation": [],
      "_format_must_include": [
        "_original_tag_for_rename_edge"
      ],
      "_build_cycle_retry_prompt": [
        "_attribute_cycle_edges",
        "_shared_files_in_scc",
        "_format_recommendation",
        "_format_must_include",
        "_matches_recommendation"
      ],
      "_build_size_retry_prompt": [],
      "_matches_recommendation": [],
      "_validate_must_include": [],
      "_tag_jaccard": [],
      "_recommend_unresolved_resolution": [
        "_tag_jaccard"
      ],
      "_build_unresolved_retry_prompt": [
        "_tag_jaccard"
      ],
      "_validate_unresolved_must_include": [],
      "_compute_overlap_anchors": [],
      "_validate_overlap_judge_output": [
        "die",
        "_compute_overlap_anchors"
      ],
      "_apply_overlap_drop": [],
      "_apply_overlap_merge": [
        "die"
      ],
      "_apply_overlap_collisions": [
        "_compute_overlap_anchors",
        "log",
        "_apply_overlap_merge",
        "_apply_overlap_drop"
      ],
      "phase_overlap_judge": [
        "log",
        "load_prompt",
        "claude_p",
        "_run_checked_loop",
        "check_overlap_judge_output",
        "die",
        "_validate_overlap_judge_output",
        "_apply_overlap_collisions",
        "_build_predecessor_graph",
        "_tarjan_sccs",
        "_format_cycle_diagnostic"
      ],
      "_build_predecessor_graph": [],
      "detect_no_work": [],
      "_finish_no_work_run": [
        "log",
        "now",
        "_write_run_json"
      ],
      "schedule": [
        "log",
        "die",
        "_build_predecessor_graph"
      ],
      "check_budget_feasibility": [
        "die"
      ],
      "_write_subtask_artifacts": [],
      "_read_upstream_artifacts": [],
      "_format_upstream_artifacts_for_sid": [
        "_build_predecessor_graph",
        "_read_upstream_artifacts",
        "_format_upstream_artifacts_section"
      ],
      "_format_upstream_artifacts_section": [],
      "write_plan": [],
      "_format_provision_recipe_section": [],
      "run_implementer": [
        "load_prompt",
        "run_script",
        "_format_provision_recipe_section",
        "_format_upstream_artifacts_for_sid",
        "claude_p"
      ],
      "_retryable_failure": [],
      "discover_rules_files": [],
      "_is_rails_repo": [],
      "_infer_build_lint_test": [
        "_is_rails_repo"
      ],
      "validate_conformance_result": [],
      "_branch_head_sha": [
        "run_proc"
      ],
      "_protected_paths_since": [
        "run_proc",
        "is_protected_path"
      ],
      "rollback_conformer_commits": [
        "run_proc"
      ],
      "_uncommitted_paths": [
        "run_proc"
      ],
      "_unprefixed_conformer_commits": [
        "run_proc"
      ],
      "run_conformer": [
        "load_prompt",
        "_format_provision_recipe_section",
        "claude_p",
        "log"
      ],
      "_summarize_residuals": [],
      "_confidence_axes_clear": [],
      "_format_check_feedback": [],
      "_run_checked_loop": [
        "_format_check_feedback"
      ],
      "_conformance_clean": [],
      "_iter_log_tool_use": [],
      "_count_bash_axis_invocations": [
        "_iter_log_tool_use"
      ],
      "_count_orphaned_bg_axis": [
        "_iter_log_tool_use"
      ],
      "_emit_bash_axis_warnings": [
        "_count_bash_axis_invocations",
        "_count_orphaned_bg_axis"
      ],
      "_run_conformance_phase": [
        "discover_rules_files",
        "_infer_build_lint_test",
        "compute_run_branch",
        "_branch_head_sha",
        "run_conformer",
        "validate_conformance_result",
        "check_diff_scope",
        "_uncommitted_paths",
        "rollback_conformer_commits",
        "_unprefixed_conformer_commits",
        "_emit_bash_axis_warnings",
        "_format_check_feedback",
        "_conformance_clean",
        "_summarize_residuals"
      ],
      "run_final_conformance": [
        "log",
        "discover_rules_files",
        "_infer_build_lint_test",
        "load_prompt",
        "_branch_head_sha",
        "_format_provision_recipe_section",
        "claude_p",
        "validate_conformance_result",
        "_protected_paths_since",
        "_uncommitted_paths",
        "rollback_conformer_commits",
        "_unprefixed_conformer_commits",
        "_emit_bash_axis_warnings",
        "_format_check_feedback",
        "_conformance_clean",
        "_summarize_residuals",
        "die"
      ],
      "settle_subtask": [
        "_retryable_failure",
        "log",
        "_reset_subtask_worktree",
        "run_implementer",
        "validate_result",
        "_confidence_axes_clear",
        "compute_run_branch",
        "run_proc",
        "check_implementer_output",
        "_format_check_feedback",
        "check_branch_has_commits",
        "check_diff_scope",
        "_write_subtask_artifacts",
        "_run_conformance_phase",
        "validate_checkpoint",
        "surface_clarification"
      ],
      "integrate_wave": [
        "run_script",
        "die",
        "log",
        "load_prompt",
        "claude_p",
        "_run_checked_loop",
        "check_integrator_output",
        "run_proc",
        "check_merge_committed",
        "compute_run_branch",
        "check_integrator_commit"
      ],
      "phase_execute": [
        "log",
        "run_script",
        "die",
        "run_proc",
        "settle_subtask",
        "gather_or_cancel",
        "integrate_wave",
        "scan_conflict_markers"
      ],
      "find_pr_template": [],
      "_cap_text": [],
      "_strip_leerie_prefix": [],
      "_truncate_diff_sample": [],
      "_final_conformance_payload": [],
      "_compose_pr_via_llm": [
        "find_pr_template",
        "_cap_text",
        "log",
        "compute_run_branch",
        "_truncate_diff_sample",
        "_format_run_duration",
        "_final_conformance_payload",
        "load_prompt",
        "claude_p",
        "_strip_leerie_prefix",
        "_write_run_json"
      ],
      "phase_finalize": [
        "log",
        "run_script",
        "die",
        "run_proc",
        "now",
        "push_will_happen",
        "_write_run_json",
        "_compose_pr_via_llm",
        "compute_run_branch"
      ],
      "orchestrate": [
        "_memory_sampler",
        "_run_phases"
      ],
      "_run_phases": [
        "die",
        "validate_resume_state",
        "log",
        "_read_version",
        "absorb_supplied_answers",
        "resolve_task_argument",
        "now",
        "preflight",
        "phase_classify",
        "run_proc",
        "_write_run_json",
        "compute_run_branch",
        "phase_provision",
        "gather_answers",
        "phase_plan",
        "phase_reconcile",
        "detect_no_work",
        "_finish_no_work_run",
        "phase_overlap_judge",
        "warn_cross_planner_file_overlap",
        "warn_layer_gaps",
        "filter_offtree_subtasks",
        "schedule",
        "check_budget_feasibility",
        "validate_plan",
        "write_plan",
        "phase_execute",
        "run_final_conformance",
        "phase_finalize"
      ],
      "main": [
        "_read_version",
        "resolve_leerie_root",
        "list_runs",
        "die",
        "resolve_max_workers",
        "resolve_max_parallel",
        "resolve_confidence_rounds",
        "resolve_judgment_check_rounds",
        "resolve_planner_check_rounds",
        "resolve_implementer_confidence_retries",
        "resolve_planner_samples",
        "resolve_worker_memory_max",
        "verbosity_from_shortcuts",
        "resolve_verbosity",
        "resolve_run_id",
        "log",
        "resolve_source_of_truth",
        "resolve_runtime",
        "resolve_models",
        "resolve_efforts",
        "resolve_no_push",
        "resolve_clarify",
        "resolve_dangerously_skip_permissions",
        "resolve_skip_overlap_judge",
        "resolve_skip_budget_check",
        "resolve_strict_conformer",
        "resolve_pr_template",
        "resolve_inspect_dirs",
        "resolve_telemetry_enabled",
        "resolve_telemetry_subdir",
        "resolve_judge_dir",
        "resolve_heal_dir",
        "resolve_heal_max_rounds",
        "resolve_heal_success_threshold",
        "phase_judge",
        "phase_heal",
        "_install_signal_handlers",
        "orchestrate",
        "_cleanup_on_abnormal_exit",
        "now",
        "_write_run_json"
      ]
    },
    "ordered_calls": {
      "_read_version": [],
      "load_prompt": [],
      "is_protected_path": [],
      "resolve_prompt": [],
      "_confidence_schema": [],
      "now": [
        "now"
      ],
      "log": [
        "now"
      ],
      "die": [],
      "RateLimitedExit.__init__": [],
      "detect_session_limit": [
        "now"
      ],
      "_install_signal_handlers": [],
      "_enumerate_descendants": [],
      "_signal_pids": [],
      "_DescendantTracker.__init__": [],
      "_DescendantTracker.start": [],
      "_DescendantTracker._poll_loop": [
        "_enumerate_descendants"
      ],
      "_DescendantTracker.stop_and_reap": [
        "_enumerate_descendants",
        "_signal_pids"
      ],
      "_terminate_proc_tree": [
        "_enumerate_descendants",
        "_signal_pids",
        "_enumerate_descendants",
        "_signal_pids"
      ],
      "_cleanup_on_abnormal_exit": [
        "log",
        "log",
        "log",
        "log",
        "log"
      ],
      "_reset_subtask_worktree": [
        "run_proc",
        "run_proc",
        "run_proc"
      ],
      "_parse_claude_version": [],
      "_check_claude_cli_version": [
        "die",
        "_parse_claude_version",
        "die"
      ],
      "compute_run_branch": [],
      "compute_subtask_branch": [],
      "_validate_run_json": [],
      "_format_run_duration": [],
      "compose_pr_body": [
        "_format_run_duration"
      ],
      "_write_run_json": [
        "_validate_run_json"
      ],
      "discover_runs": [
        "log",
        "log",
        "log",
        "log"
      ],
      "resolve_run_id": [
        "discover_runs",
        "die",
        "die",
        "_format_run_for_disambiguation",
        "die"
      ],
      "_format_run_for_disambiguation": [
        "_derive_run_status",
        "_format_age",
        "now"
      ],
      "_format_age": [],
      "_derive_run_status": [
        "_validate_run_json"
      ],
      "_collect_run_rows": [
        "discover_runs",
        "_derive_run_status",
        "compute_run_branch"
      ],
      "_render_run_table": [],
      "list_runs": [
        "_collect_run_rows",
        "_render_run_table"
      ],
      "_read_toml_key": [],
      "resolve_task_argument": [
        "die"
      ],
      "resolve_leerie_root": [],
      "_resolve_enum_pref": [
        "die",
        "_read_toml_key",
        "die"
      ],
      "resolve_source_of_truth": [
        "_resolve_enum_pref"
      ],
      "resolve_runtime": [
        "_resolve_enum_pref"
      ],
      "_resolve_str_pref": [
        "_read_toml_key"
      ],
      "resolve_pr_template": [
        "_resolve_str_pref"
      ],
      "_resolve_positive_int_pref": [
        "die",
        "die",
        "_read_toml_key",
        "die",
        "die"
      ],
      "resolve_confidence_rounds": [
        "_resolve_positive_int_pref"
      ],
      "resolve_max_workers": [
        "_resolve_positive_int_pref"
      ],
      "resolve_max_parallel": [
        "_resolve_positive_int_pref"
      ],
      "resolve_judgment_check_rounds": [
        "_resolve_positive_int_pref"
      ],
      "resolve_planner_check_rounds": [
        "_resolve_positive_int_pref"
      ],
      "resolve_implementer_confidence_retries": [
        "_resolve_positive_int_pref"
      ],
      "resolve_planner_samples": [
        "_resolve_positive_int_pref"
      ],
      "_parse_memory_size": [
        "die",
        "die",
        "die"
      ],
      "_auto_worker_memory_max": [],
      "resolve_worker_memory_max": [
        "_parse_memory_size",
        "_parse_memory_size",
        "_read_toml_key",
        "_parse_memory_size",
        "_auto_worker_memory_max"
      ],
      "resolve_inspect_dirs": [
        "_read_toml_key"
      ],
      "_parse_bool_envtoml": [],
      "_resolve_bool_pref": [
        "_parse_bool_envtoml",
        "die",
        "_read_toml_key",
        "_parse_bool_envtoml",
        "die"
      ],
      "resolve_no_push": [
        "_resolve_bool_pref"
      ],
      "push_will_happen": [],
      "resolve_clarify": [
        "_resolve_bool_pref"
      ],
      "resolve_dangerously_skip_permissions": [
        "_resolve_bool_pref"
      ],
      "resolve_skip_overlap_judge": [
        "_resolve_bool_pref"
      ],
      "resolve_skip_budget_check": [
        "_resolve_bool_pref"
      ],
      "resolve_strict_conformer": [
        "_resolve_bool_pref"
      ],
      "_positive_int": [],
      "resolve_verbosity": [
        "_resolve_enum_pref"
      ],
      "verbosity_from_shortcuts": [],
      "resolve_models": [
        "die",
        "_read_toml_key",
        "die"
      ],
      "resolve_efforts": [
        "die",
        "_read_toml_key",
        "die"
      ],
      "resolve_telemetry_enabled": [
        "_parse_bool_envtoml",
        "die",
        "_read_toml_key",
        "_parse_bool_envtoml",
        "die"
      ],
      "resolve_telemetry_subdir": [
        "_resolve_str_pref"
      ],
      "resolve_judge_dir": [
        "_resolve_str_pref"
      ],
      "resolve_heal_dir": [
        "_resolve_str_pref"
      ],
      "resolve_heal_max_rounds": [
        "_resolve_positive_int_pref"
      ],
      "resolve_heal_success_threshold": [
        "die",
        "die",
        "_read_toml_key",
        "die",
        "die"
      ],
      "run_proc": [
        "_terminate_proc_tree",
        "_terminate_proc_tree"
      ],
      "run_streaming": [
        "log",
        "_terminate_proc_tree",
        "_terminate_proc_tree"
      ],
      "gather_or_cancel": [],
      "run_script": [
        "run_proc"
      ],
      "preflight": [
        "run_proc",
        "die",
        "run_proc",
        "die",
        "_check_claude_cli_version",
        "log",
        "_invoke",
        "die",
        "die",
        "die",
        "log"
      ],
      "_confidence_issues": [],
      "check_classifier_output": [
        "_confidence_issues"
      ],
      "_grep_old_pattern": [],
      "_check_migration_surface": [
        "_grep_old_pattern"
      ],
      "check_planner_output": [
        "is_protected_path",
        "_check_migration_surface",
        "_confidence_issues"
      ],
      "check_reconciler_output": [
        "_confidence_issues"
      ],
      "check_overlap_judge_output": [
        "_confidence_issues"
      ],
      "check_provision_output": [
        "_confidence_issues"
      ],
      "check_integrator_output": [
        "_confidence_issues"
      ],
      "check_implementer_output": [],
      "_expand_braces": [
        "_expand_braces"
      ],
      "glob_task_references": [
        "_expand_braces"
      ],
      "extract_task_file_structure": [
        "glob_task_references"
      ],
      "check_task_file_coverage": [],
      "_format_task_file_structure": [],
      "validate_plan": [
        "is_protected_path",
        "die",
        "log"
      ],
      "warn_cross_planner_file_overlap": [
        "log",
        "log"
      ],
      "warn_layer_gaps": [
        "log",
        "log"
      ],
      "_resolves_under": [],
      "filter_offtree_subtasks": [
        "_resolves_under",
        "_resolves_under",
        "log",
        "log"
      ],
      "_lockfile_table_entries": [],
      "detect_recipe_from_lockfiles": [
        "_lockfile_table_entries"
      ],
      "validate_provision_recipe": [],
      "_split_readme_headers": [],
      "_is_install_section": [],
      "_slice_code_fences_with_install_hints": [],
      "extract_readme_sections": [
        "_split_readme_headers",
        "_is_install_section",
        "_slice_code_fences_with_install_hints"
      ],
      "_read_file_safely": [],
      "_sample_workspace_manifests": [
        "_read_file_safely"
      ],
      "gather_provision_fixtures": [
        "_read_file_safely",
        "extract_readme_sections",
        "_read_file_safely",
        "_sample_workspace_manifests",
        "_read_file_safely",
        "_read_file_safely"
      ],
      "_split_checkpoint_sections": [],
      "validate_checkpoint": [
        "_split_checkpoint_sections",
        "_normalize_for_noise",
        "_parse_touched_file_line"
      ],
      "_normalize_for_noise": [
        "_strip_bullet"
      ],
      "_strip_bullet": [],
      "_parse_touched_file_line": [
        "_strip_bullet"
      ],
      "validate_result": [],
      "check_diff_scope": [
        "compute_run_branch",
        "run_proc",
        "is_protected_path",
        "log"
      ],
      "check_merge_committed": [
        "run_proc",
        "run_proc"
      ],
      "check_integrator_commit": [
        "run_proc"
      ],
      "check_branch_has_commits": [
        "run_proc"
      ],
      "scan_conflict_markers": [
        "run_proc"
      ],
      "validate_resume_state": [
        "die",
        "die",
        "die",
        "die"
      ],
      "_is_auth_or_quota_failure": [],
      "_extract_tool_result_text": [],
      "_tag_each_line": [],
      "_summarize_tool_use": [],
      "_summarize_stream_event": [
        "detect_session_limit",
        "_summarize_tool_use",
        "_extract_tool_result_text",
        "_tag_each_line",
        "_tag_each_line"
      ],
      "_format_progress_prefix": [],
      "_get_progress": [],
      "_detect_cgroup_root": [],
      "_cgroup_probe": [
        "_detect_cgroup_root",
        "log"
      ],
      "_cgroup_create": [
        "_cgroup_probe",
        "_detect_cgroup_root",
        "log"
      ],
      "_cgroup_enroll": [
        "log"
      ],
      "_cgroup_destroy": [],
      "_invoke": [
        "log",
        "_cgroup_create",
        "_cgroup_enroll",
        "now",
        "now",
        "_summarize_stream_event",
        "_format_progress_prefix",
        "log",
        "now",
        "log",
        "log",
        "_terminate_proc_tree",
        "_terminate_proc_tree",
        "_cgroup_destroy",
        "log"
      ],
      "_capture_call": [],
      "_collect_memory_sample": [
        "now"
      ],
      "_memory_sampler": [
        "_collect_memory_sample",
        "_collect_memory_sample"
      ],
      "claude_p": [
        "_invoke",
        "_get_progress",
        "_capture_call",
        "now",
        "log",
        "log",
        "_is_auth_or_quota_failure",
        "log",
        "_is_auth_or_quota_failure"
      ],
      "replay_capture": [
        "claude_p"
      ],
      "_accumulate_telemetry": [],
      "_ReplayState.__init__": [],
      "_ReplayState.save": [],
      "_ReplayState.bump_workers": [],
      "_ReplayState.add_telemetry": [
        "_accumulate_telemetry"
      ],
      "StateLockedError.__init__": [],
      "State.__init__": [],
      "State._acquire_lock": [],
      "State.release_lock": [],
      "State.__del__": [],
      "State.load": [],
      "State.save": [],
      "State.bump_workers": [],
      "State.add_telemetry": [
        "_accumulate_telemetry"
      ],
      "judge_capture": [
        "load_prompt",
        "claude_p"
      ],
      "phase_judge": [
        "log",
        "log",
        "log",
        "log",
        "judge_capture",
        "log",
        "gather_or_cancel",
        "log"
      ],
      "HealState.__init__": [],
      "HealState.save": [],
      "HealState.load": [],
      "heal_baseline": [
        "replay_capture",
        "judge_capture",
        "gather_or_cancel",
        "log"
      ],
      "heal_apply_patch": [
        "log"
      ],
      "heal_replay_patched": [
        "replay_capture",
        "judge_capture",
        "log",
        "gather_or_cancel",
        "log"
      ],
      "check_convergence": [],
      "write_heal_report": [
        "log"
      ],
      "request_patch": [
        "resolve_prompt",
        "load_prompt",
        "claude_p"
      ],
      "phase_heal": [
        "log",
        "heal_baseline",
        "request_patch",
        "heal_apply_patch",
        "heal_replay_patched",
        "check_convergence",
        "log",
        "write_heal_report",
        "log"
      ],
      "run_setup_hook": [
        "die",
        "log",
        "run_streaming",
        "die",
        "die"
      ],
      "_existing_mise_toml_path": [],
      "_go_already_pinned": [
        "_existing_mise_toml_path"
      ],
      "_existing_mise_toml_tool_keys": [],
      "_read_idiomatic_pins": [],
      "synth_mise_go_override": [
        "_go_already_pinned",
        "_existing_mise_toml_path",
        "_existing_mise_toml_tool_keys",
        "_read_idiomatic_pins"
      ],
      "_repo_has_version_signal": [],
      "run_mise_install": [
        "_repo_has_version_signal",
        "log",
        "run_streaming",
        "die",
        "die",
        "log"
      ],
      "phase_classify": [
        "log",
        "load_prompt",
        "claude_p",
        "_run_checked_loop",
        "check_classifier_output",
        "die",
        "log",
        "die",
        "log"
      ],
      "gather_answers": [
        "die",
        "log"
      ],
      "absorb_supplied_answers": [
        "die",
        "die",
        "die",
        "die"
      ],
      "surface_clarification": [
        "log"
      ],
      "_format_provision_user_prompt": [],
      "phase_provision": [
        "log",
        "log",
        "run_setup_hook",
        "synth_mise_go_override",
        "log",
        "run_mise_install",
        "log",
        "detect_recipe_from_lockfiles",
        "log",
        "log",
        "gather_provision_fixtures",
        "load_prompt",
        "_format_provision_user_prompt",
        "claude_p",
        "_run_checked_loop",
        "check_provision_output",
        "die",
        "log",
        "validate_provision_recipe",
        "die",
        "log"
      ],
      "_select_best_planner_sample": [
        "check_planner_output",
        "log"
      ],
      "phase_plan": [
        "log",
        "load_prompt",
        "extract_task_file_structure",
        "_format_task_file_structure",
        "log",
        "claude_p",
        "check_planner_output",
        "check_task_file_coverage",
        "_run_checked_loop",
        "log",
        "die",
        "log",
        "gather_or_cancel",
        "log",
        "gather_or_cancel",
        "die",
        "_select_best_planner_sample",
        "log",
        "log"
      ],
      "_promote_external_collisions": [],
      "_collect_external_preconditions": [],
      "_compute_unresolved_requires": [],
      "_find_oversized_added_subtasks": [],
      "_apply_reconciler_output": [
        "die",
        "die",
        "die",
        "die",
        "die",
        "die"
      ],
      "phase_reconcile": [
        "die",
        "_promote_external_collisions",
        "log",
        "_collect_external_preconditions",
        "log",
        "_compute_unresolved_requires",
        "log",
        "load_prompt",
        "claude_p",
        "die",
        "_run_checked_loop",
        "check_reconciler_output",
        "die",
        "log",
        "_apply_reconciler_output",
        "_find_oversized_added_subtasks",
        "log",
        "_build_size_retry_prompt",
        "log",
        "check_reconciler_output",
        "log",
        "_apply_reconciler_output",
        "_find_oversized_added_subtasks",
        "die",
        "_build_predecessor_graph",
        "_tarjan_sccs",
        "_format_cycle_diagnostic",
        "log",
        "_recommend_cycle_resolution",
        "_build_cycle_retry_prompt",
        "log",
        "_validate_must_include",
        "die",
        "check_reconciler_output",
        "log",
        "_apply_reconciler_output",
        "_build_predecessor_graph",
        "_tarjan_sccs",
        "_format_cycle_diagnostic",
        "die",
        "_promote_external_collisions",
        "log",
        "_collect_external_preconditions",
        "log",
        "_compute_unresolved_requires",
        "log",
        "_recommend_unresolved_resolution",
        "log",
        "_build_unresolved_retry_prompt",
        "log",
        "_validate_unresolved_must_include",
        "die",
        "check_reconciler_output",
        "log",
        "_apply_reconciler_output",
        "_promote_external_collisions",
        "_collect_external_preconditions",
        "_build_predecessor_graph",
        "_tarjan_sccs",
        "_format_cycle_diagnostic",
        "die",
        "_compute_unresolved_requires",
        "die",
        "log"
      ],
      "_tarjan_sccs": [],
      "_attribute_cycle_edges": [],
      "_format_cycle_diagnostic": [
        "_attribute_cycle_edges",
        "_shared_files_in_scc"
      ],
      "_shared_files_in_scc": [],
      "_original_tag_for_rename_edge": [],
      "_recommend_cycle_resolution": [
        "_attribute_cycle_edges",
        "_original_tag_for_rename_edge",
        "_shared_files_in_scc",
        "_original_tag_for_rename_edge"
      ],
      "_format_recommendation": [],
      "_format_must_include": [
        "_original_tag_for_rename_edge"
      ],
      "_build_cycle_retry_prompt": [
        "_attribute_cycle_edges",
        "_shared_files_in_scc",
        "_format_recommendation",
        "_format_must_include",
        "_matches_recommendation"
      ],
      "_build_size_retry_prompt": [],
      "_matches_recommendation": [],
      "_validate_must_include": [],
      "_tag_jaccard": [],
      "_recommend_unresolved_resolution": [
        "_tag_jaccard"
      ],
      "_build_unresolved_retry_prompt": [
        "_tag_jaccard"
      ],
      "_validate_unresolved_must_include": [],
      "_compute_overlap_anchors": [],
      "_validate_overlap_judge_output": [
        "die",
        "die",
        "die",
        "die",
        "die",
        "die",
        "_compute_overlap_anchors",
        "die",
        "die"
      ],
      "_apply_overlap_drop": [],
      "_apply_overlap_merge": [
        "die",
        "die"
      ],
      "_apply_overlap_collisions": [
        "_compute_overlap_anchors",
        "log",
        "_apply_overlap_merge",
        "log",
        "_apply_overlap_drop",
        "log",
        "_apply_overlap_drop",
        "log"
      ],
      "phase_overlap_judge": [
        "log",
        "log",
        "log",
        "log",
        "load_prompt",
        "claude_p",
        "_run_checked_loop",
        "check_overlap_judge_output",
        "die",
        "log",
        "log",
        "_validate_overlap_judge_output",
        "die",
        "_apply_overlap_collisions",
        "_build_predecessor_graph",
        "_tarjan_sccs",
        "_format_cycle_diagnostic",
        "die",
        "log"
      ],
      "_build_predecessor_graph": [],
      "detect_no_work": [],
      "_finish_no_work_run": [
        "log",
        "log",
        "now",
        "_write_run_json",
        "log",
        "log"
      ],
      "schedule": [
        "log",
        "die",
        "die",
        "log",
        "_build_predecessor_graph",
        "die",
        "log"
      ],
      "check_budget_feasibility": [
        "die"
      ],
      "_write_subtask_artifacts": [],
      "_read_upstream_artifacts": [],
      "_format_upstream_artifacts_for_sid": [
        "_build_predecessor_graph",
        "_read_upstream_artifacts",
        "_format_upstream_artifacts_section"
      ],
      "_format_upstream_artifacts_section": [],
      "write_plan": [],
      "_format_provision_recipe_section": [],
      "run_implementer": [
        "load_prompt",
        "run_script",
        "_format_provision_recipe_section",
        "_format_upstream_artifacts_for_sid",
        "claude_p"
      ],
      "_retryable_failure": [],
      "discover_rules_files": [],
      "_is_rails_repo": [],
      "_infer_build_lint_test": [
        "_is_rails_repo"
      ],
      "validate_conformance_result": [],
      "_branch_head_sha": [
        "run_proc"
      ],
      "_protected_paths_since": [
        "run_proc",
        "is_protected_path"
      ],
      "rollback_conformer_commits": [
        "run_proc"
      ],
      "_uncommitted_paths": [
        "run_proc"
      ],
      "_unprefixed_conformer_commits": [
        "run_proc"
      ],
      "run_conformer": [
        "load_prompt",
        "_format_provision_recipe_section",
        "claude_p",
        "log",
        "log"
      ],
      "_summarize_residuals": [],
      "_confidence_axes_clear": [],
      "_format_check_feedback": [],
      "_run_checked_loop": [
        "_format_check_feedback"
      ],
      "_conformance_clean": [],
      "_iter_log_tool_use": [],
      "_count_bash_axis_invocations": [
        "_iter_log_tool_use"
      ],
      "_count_orphaned_bg_axis": [
        "_iter_log_tool_use"
      ],
      "_emit_bash_axis_warnings": [
        "_count_bash_axis_invocations",
        "_count_orphaned_bg_axis"
      ],
      "_run_conformance_phase": [
        "discover_rules_files",
        "_infer_build_lint_test",
        "compute_run_branch",
        "_branch_head_sha",
        "run_conformer",
        "validate_conformance_result",
        "check_diff_scope",
        "_uncommitted_paths",
        "rollback_conformer_commits",
        "_uncommitted_paths",
        "_unprefixed_conformer_commits",
        "_emit_bash_axis_warnings",
        "_format_check_feedback",
        "_conformance_clean",
        "_summarize_residuals",
        "_conformance_clean",
        "_summarize_residuals"
      ],
      "run_final_conformance": [
        "log",
        "log",
        "log",
        "log",
        "discover_rules_files",
        "_infer_build_lint_test",
        "load_prompt",
        "_branch_head_sha",
        "_format_provision_recipe_section",
        "claude_p",
        "validate_conformance_result",
        "_protected_paths_since",
        "_uncommitted_paths",
        "rollback_conformer_commits",
        "_uncommitted_paths",
        "_unprefixed_conformer_commits",
        "_emit_bash_axis_warnings",
        "_format_check_feedback",
        "_conformance_clean",
        "_summarize_residuals",
        "_conformance_clean",
        "log",
        "die"
      ],
      "settle_subtask": [
        "_retryable_failure",
        "log",
        "log",
        "_reset_subtask_worktree",
        "run_implementer",
        "validate_result",
        "log",
        "_confidence_axes_clear",
        "log",
        "compute_run_branch",
        "run_proc",
        "check_implementer_output",
        "log",
        "_format_check_feedback",
        "check_branch_has_commits",
        "compute_run_branch",
        "log",
        "run_proc",
        "check_diff_scope",
        "_write_subtask_artifacts",
        "_run_conformance_phase",
        "log",
        "validate_checkpoint",
        "log",
        "validate_checkpoint",
        "log",
        "surface_clarification"
      ],
      "integrate_wave": [
        "run_script",
        "die",
        "log",
        "load_prompt",
        "claude_p",
        "_run_checked_loop",
        "check_integrator_output",
        "run_proc",
        "die",
        "log",
        "check_merge_committed",
        "run_proc",
        "die",
        "compute_run_branch",
        "check_integrator_commit",
        "log",
        "log",
        "run_proc",
        "die",
        "compute_run_branch"
      ],
      "phase_execute": [
        "log",
        "run_script",
        "die",
        "run_proc",
        "settle_subtask",
        "log",
        "log",
        "log",
        "log",
        "gather_or_cancel",
        "integrate_wave",
        "scan_conflict_markers",
        "die",
        "log",
        "die"
      ],
      "find_pr_template": [],
      "_cap_text": [],
      "_strip_leerie_prefix": [],
      "_truncate_diff_sample": [],
      "_final_conformance_payload": [],
      "_compose_pr_via_llm": [
        "find_pr_template",
        "_cap_text",
        "log",
        "log",
        "compute_run_branch",
        "_cap_text",
        "_truncate_diff_sample",
        "_format_run_duration",
        "_final_conformance_payload",
        "load_prompt",
        "log",
        "claude_p",
        "_strip_leerie_prefix",
        "log",
        "_write_run_json",
        "log",
        "log"
      ],
      "phase_finalize": [
        "log",
        "run_script",
        "die",
        "run_script",
        "run_proc",
        "die",
        "now",
        "push_will_happen",
        "_write_run_json",
        "_compose_pr_via_llm",
        "log",
        "compute_run_branch",
        "log",
        "compute_run_branch",
        "log",
        "compute_run_branch",
        "log"
      ],
      "orchestrate": [
        "_memory_sampler",
        "_run_phases"
      ],
      "_run_phases": [
        "die",
        "validate_resume_state",
        "log",
        "log",
        "log",
        "log",
        "die",
        "die",
        "_read_version",
        "absorb_supplied_answers",
        "die",
        "resolve_task_argument",
        "now",
        "_read_version",
        "preflight",
        "phase_classify",
        "log",
        "run_proc",
        "_write_run_json",
        "compute_run_branch",
        "phase_provision",
        "gather_answers",
        "phase_plan",
        "phase_reconcile",
        "detect_no_work",
        "_finish_no_work_run",
        "phase_overlap_judge",
        "warn_cross_planner_file_overlap",
        "warn_layer_gaps",
        "filter_offtree_subtasks",
        "schedule",
        "check_budget_feasibility",
        "validate_plan",
        "write_plan",
        "phase_execute",
        "run_final_conformance",
        "log",
        "phase_finalize"
      ],
      "main": [
        "_read_version",
        "resolve_leerie_root",
        "list_runs",
        "die",
        "resolve_max_workers",
        "resolve_max_parallel",
        "resolve_confidence_rounds",
        "resolve_judgment_check_rounds",
        "resolve_planner_check_rounds",
        "resolve_implementer_confidence_retries",
        "resolve_planner_samples",
        "resolve_worker_memory_max",
        "verbosity_from_shortcuts",
        "resolve_verbosity",
        "resolve_leerie_root",
        "resolve_run_id",
        "die",
        "log",
        "resolve_source_of_truth",
        "resolve_runtime",
        "resolve_models",
        "log",
        "resolve_efforts",
        "log",
        "resolve_no_push",
        "resolve_clarify",
        "resolve_dangerously_skip_permissions",
        "log",
        "resolve_skip_overlap_judge",
        "resolve_skip_budget_check",
        "resolve_strict_conformer",
        "resolve_pr_template",
        "resolve_inspect_dirs",
        "resolve_telemetry_enabled",
        "resolve_telemetry_subdir",
        "resolve_judge_dir",
        "resolve_heal_dir",
        "resolve_heal_max_rounds",
        "resolve_heal_success_threshold",
        "resolve_run_id",
        "log",
        "die",
        "phase_judge",
        "log",
        "phase_judge",
        "die",
        "log",
        "log",
        "phase_heal",
        "_install_signal_handlers",
        "orchestrate",
        "log",
        "_cleanup_on_abnormal_exit",
        "log",
        "now",
        "log",
        "log",
        "log",
        "log",
        "log",
        "log",
        "now",
        "_write_run_json",
        "log",
        "_cleanup_on_abnormal_exit",
        "log",
        "die"
      ]
    }
  }
}
