import json
from typing import Dict, Any, List
from collections import defaultdict
import logging
from shared.models.payloads import Issue,ErrorResult, FileResult, AnalysisResults, Summary, ErrorCode, ReviewFactor
from shared.exceptions.agent_exceptions import AgentOutputParseException

logger = logging.getLogger(__name__)

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


def parse_pr_analysis_result_for_complicated_agent_raw_result(raw_results: List[Dict[str, Any]], factors: List[str]) -> AnalysisResults:
    all_files: Dict[str, List[Issue]] = {}
    errors: List[ErrorResult] = []

    try:
        for result in raw_results:
            if isinstance(result, dict) and "error_code" in result:
                errors.append(ErrorResult(**result))
                continue

            all_files.setdefault(result.get("file", "unknown_file"), []).extend(Issue(**issue) for issue in result.get("issues",[]))
    except Exception as e:
        logger.error(f"event: review, msg: error=Failed to parse review result for all factors: {raw_results}",
                     exc_info=e)
        raise AgentOutputParseException(f"Failed to parse result. Error {str(e)}")

    file_results = []
    for filename, issues in all_files.items():
        seen_lines = set()
        deduped_issues = []
        for issue in sorted(issues, key=lambda issue: issue.line):
            if issue.line not in seen_lines:
                deduped_issues.append(issue)
                seen_lines.add(issue.line)
        file_results.append(FileResult(name=filename, issues=deduped_issues))

    summary = Summary(
        total_files=len(file_results),
        total_issues=sum(len(f.issues) for f in file_results),
        critical_issues=sum(
            1 for f in file_results for i in f.issues if i.type.lower() == "critical"
        )
    )

    return AnalysisResults(
        files=file_results,
        summary=summary,
        errors=errors
    )