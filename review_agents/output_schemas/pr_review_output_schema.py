REVIEW_OUTPUT_SCHEMA = {
    "title": "CodeReviewResult",
    "description": "A structured code review result for a pull request.",
    "type": "object",
    "properties": {
        "files": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "name": {"type": "string"},
                    "issues": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "type": {"type": "string",
                                         "enum": ["code_style", "bugs", "performance", "best_practices"]},
                                "subtype": {"type": "string"},
                                "line": {"type": "integer"},
                                "description": {"type": "string"},
                                "suggestion": {"type": "string"}
                            },
                            "required": ["type", "line", "description", "suggestion"]
                        }
                    }
                },
                "required": ["name", "issues"]
            }
        },
        "summary": {
            "type": "object",
            "properties": {
                "total_files": {"type": "integer"},
                "total_issues": {"type": "integer"},
                "critical_issues": {"type": "integer"}
            },
            "required": ["total_files", "total_issues", "critical_issues"]
        }
    },
    "required": ["files", "summary"]
}