import json
from typing import Dict, Any, List
from shared.models.payloads import Issue


def parse_review_result(review: Any) -> Dict[str, List[Issue]]:
    """
    Parse the review object returned from LLM into a dictionary
    mapping filenames to lists of Issue objects.

    Args:
        review: Either a JSON string or a dict matching REVIEW_OUTPUT_SCHEMA.

    Returns:
        Dict[str, List[Issue]]: Mapping from filename to list of Issue instances.
    """
    if isinstance(review, str):
        parsed = json.loads(review)
    else:
        parsed = review

    all_files: Dict[str, List[Issue]] = {}

    for file_data in parsed.get("files", []):
        filename = file_data.get("name")
        issues = [Issue(**issue) for issue in file_data.get("issues", [])]
        all_files.setdefault(filename, []).extend(issues)

    return all_files
