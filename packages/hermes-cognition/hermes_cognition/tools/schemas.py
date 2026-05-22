"""Tool schemas for Cognition Engine Hermes tools."""

COGNITION_INIT = {
    "name": "cognition_init",
    "description": "Initialize Cognition Engine for the current project (DNA, .cognition/). Run once per repo.",
    "parameters": {
        "type": "object",
        "properties": {
            "project_name": {"type": "string", "description": "Display name for the project"},
            "reinit": {"type": "boolean", "description": "Reset existing DNA", "default": False},
        },
    },
}

COGNITION_PLAN = {
    "name": "cognition_plan",
    "description": "Generate a phased master plan (20-30 phases) from a project goal and save to DNA.",
    "parameters": {
        "type": "object",
        "properties": {
            "goal": {"type": "string", "description": "What you are building"},
            "phases": {"type": "integer", "description": "Target phase count", "default": 24},
        },
        "required": ["goal"],
    },
}

COGNITION_STATUS = {
    "name": "cognition_status",
    "description": "Show phase progress map and project completion from Cognition DNA.",
    "parameters": {
        "type": "object",
        "properties": {
            "detailed": {"type": "boolean", "default": False},
            "phase_id": {"type": "string", "description": "Drill into one phase"},
        },
    },
}

COGNITION_PHASE_UPDATE = {
    "name": "cognition_phase_update",
    "description": "Update phase or sub-task status in DNA (valid state machine transitions).",
    "parameters": {
        "type": "object",
        "properties": {
            "phase_id": {"type": "string"},
            "status": {
                "type": "string",
                "enum": ["not_started", "in_progress", "in_review", "blocked", "completed", "cancelled"],
            },
            "subtask_id": {"type": "string"},
            "subtask_progress": {"type": "integer", "minimum": 0, "maximum": 100},
        },
        "required": ["phase_id", "status"],
    },
}

COGNITION_VALIDATE = {
    "name": "cognition_validate",
    "description": "Run Cognition Shield validation on code before writing files.",
    "parameters": {
        "type": "object",
        "properties": {
            "file_path": {"type": "string"},
            "code": {"type": "string"},
        },
        "required": ["file_path", "code"],
    },
}

COGNITION_INDEX = {
    "name": "cognition_index",
    "description": "Index codebase into truth database and architecture graph.",
    "parameters": {"type": "object", "properties": {}},
}

COGNITION_RECORD_AVOID = {
    "name": "cognition_record_avoid",
    "description": "Record a failure, hallucination, or deprecated pattern in the avoid registry.",
    "parameters": {
        "type": "object",
        "properties": {
            "description": {"type": "string"},
            "category": {
                "type": "string",
                "enum": ["hallucination", "failed_approach", "deprecated_pattern"],
                "default": "failed_approach",
            },
            "file": {"type": "string"},
        },
        "required": ["description"],
    },
}

COGNITION_BUDGET = {
    "name": "cognition_budget",
    "description": "Show session token budget zone and consumption.",
    "parameters": {"type": "object", "properties": {}},
}

COGNITION_IMPACT = {
    "name": "cognition_impact",
    "description": "Estimate impact of adding a feature (phases affected, rework risk).",
    "parameters": {
        "type": "object",
        "properties": {
            "feature_description": {"type": "string"},
        },
        "required": ["feature_description"],
    },
}

COGNITION_DELEGATE = {
    "name": "cognition_delegate",
    "description": (
        "Delegate work to a specialized sub-agent role: architect, backend, frontend, "
        "security, test, docs, or refactor. Uses Hermes delegate_task under the hood."
    ),
    "parameters": {
        "type": "object",
        "properties": {
            "role": {
                "type": "string",
                "enum": ["architect", "backend", "frontend", "security", "test", "docs", "refactor"],
            },
            "goal": {"type": "string"},
            "toolsets": {
                "type": "array",
                "items": {"type": "string"},
                "description": "Optional toolsets for sub-agent",
            },
        },
        "required": ["role", "goal"],
    },
}

COGNITION_GRAPHIFY_INDEX = {
    "name": "cognition_graphify_index",
    "description": (
        "Build or rebuild the Graphify project graph (files, imports, symbols) for "
        "token-optimized navigation and memory retrieval. Run after large refactors."
    ),
    "parameters": {
        "type": "object",
        "properties": {
            "max_files": {"type": "integer", "description": "Max source files to scan", "default": 400},
        },
    },
}

COGNITION_GRAPHIFY_NAVIGATE = {
    "name": "cognition_graphify_navigate",
    "description": (
        "Get a token-budgeted file reading plan for a task using the project graph. "
        "Use before broad read_file/search to avoid wasting tokens on redundant reads."
    ),
    "parameters": {
        "type": "object",
        "properties": {
            "task": {"type": "string", "description": "What you are trying to accomplish"},
            "token_budget": {
                "type": "integer",
                "description": "Max tokens to spend on planned file reads",
                "default": 8000,
            },
        },
        "required": ["task"],
    },
}

COGNITION_GRAPHIFY_STATUS = {
    "name": "cognition_graphify_status",
    "description": "Show Graphify graph stats and most-accessed files (memory retrieval hints).",
    "parameters": {"type": "object", "properties": {}},
}

COGNITION_RECOMMEND_MODEL = {
    "name": "cognition_recommend_model",
    "description": "Recommend best-value model for task complexity using Cognition cost engine.",
    "parameters": {
        "type": "object",
        "properties": {
            "complexity": {"type": "string", "enum": ["LOW", "MEDIUM", "HIGH"], "default": "MEDIUM"},
            "task_description": {"type": "string"},
        },
    },
}
