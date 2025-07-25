# Reviewer PR Analysis System

## Project Setup

### Prerequisites
- Docker & Docker Compose (for containerized setup)

### **Build and start all services:**
- Add openai secret key in docker-compose.yml placeholder
- ```bash
   docker-compose up --build
   ``` 
   while in the root directory.
   This will start FastAPI, Celery worker, Redis, and PostgreSQL.
---

## API Documentation
See the "API Interface Design" section below for detailed request/response examples for all endpoints.
---

## Running Tests

1. **Install test dependencies:**
    Run following commands in sequencial manner
   ```bash
   pip install virtualenv
   virtualenv venv
   source venv/bin/activate
   pip install -r pr_review_app/requirements.txt
   pip install -r celery_worker/requirements.txt
   ```
2. **Run all tests:**
   ```bash
   pytest
   ```

---

# Technical Design Document

## Functional Requirements

### API Endpoints:
- **POST** `/analyze-pr`: Accepts GitHub PR details (repo URL, PR number, GitHub token (optional)) and triggers an asynchronous analysis task
- **GET** `/status/<task_id>`: Returns status of task queued by analyze-pr (`pending`, `processing`, `completed`, `failed`).
- **GET** `/results/<task_id>`: Retrieves the completed analysis results for a given task ID in a structured format.
- **GET** `/pr-review-status`: Accepts GitHub PR details (repo URL, PR number, GitHub token (optional)) and returns status & result of task corresponding to this PR.

### Task Handling:
- Use Celery to handle tasks asynchronously, ensuring that the main API thread is not blocked.
- Implement task state tracking with statuses like `PENDING`, `PROCESSING`, `COMPLETED`, and `FAILED`.
- Handle task errors gracefully, providing meaningful error messages and status codes.

### AI Code Analysis Agent:
- **Code Style:** Identify formatting and PEP-8 (or language-specific) style violations.
- **Potential Bugs:** Highlight sections of code with potential logic or runtime issues.
- **Performance Improvements:** Suggest code optimizations.
- **Best Practices:** Ensure adherence to coding best practices.

### GitHub Integration:
- Fetch code diffs and files for the given pull request using the GitHub API and an optional user-provided token for authentication.

### Storage and Results:
- Use Redis as broker for Celery
- Store task results in PostgreSQL.
- Ensure results are retrievable through the `GET /results/<task_id>` endpoint.


## Non-Functional Requirements

### Performance:
- Ensure low latency for API endpoints, except for the actual analysis task, which is asynchronous.
- Optimize Celery task execution by configuring worker concurrency.

### Scalability:
- Support concurrent task processing with Celery workers.
- Ensure horizontal scalability to handle multiple simultaneous pull request analyses (keeping celery_app and tasks decoupled from app).

### Reliability:
- Implement robust error handling to ensure that failures (e.g., API rate limits or task crashes) are logged and communicated clearly.
- Retry failed tasks using Celery’s retry mechanism.

### Maintainability:
- Use structured logging for debugging and monitoring.
- Write clear documentation for API usage, deployment, and maintenance.

### Testing:
- Use pytest to write comprehensive unit and integration tests.
- Mock external services (e.g., GitHub API) during testing.

### Deployment:
- Provide Docker configuration for easy deployment.

## Known Constraints

### Precision:
- LLM-based evaluation instead of compiler/test suite based.

### Long PRs:
- Might be slow and inaccurate for large PRs due to context window and lack of Knowledge Map-based retrieval and context stitching functions.


## Future Scope

### Multi-Platform Support:
- Extend the system to support other version control platforms, such as Bitbucket and GitLab (strategy or adapter Design pattern).
- Abstract the GitHub-specific features (e.g., fetching PR details) to make the system platform agnostic.

### User/Organization Management:
- Support user creation and authentication.
- Configurability for repository-level or account-level keys per user.

### Prompt Management:
- Moving prompts to DB or other prompt management tools.

### Gateway:
- Using gateways (PortKey) to better monitor the cost, performance, and guardrails.

### Multi-LLM Routing:
- User can choose themselves or we can decide based on PR length, etc.

### Advanced Code Analysis:
- Add support for static analysis tools like linters for deeper insights.

### Customizable Analysis:
- Allow users to configure which types of analysis (style, bug, performance) should be performed.
- Templates for user-specific coding standards.

### Live Updates:
- Webhooks to provide live updates to developers when the analysis is completed.
- Adding comments directly to PR instead of storing to DB.

### Caching and Optimization:
- Caching strategies based on PR diffs, so that the same PR is not analyzed multiple times.

### Analytics Dashboard:
- A dashboard to visualize metrics like number of PRs analyzed, common issues detected, average time taken for analysis.

## Design Considerations

### System Architecture
- Decoupled services
- **FastAPI Service:** Handles API requests and user management.
- **Celery Worker Service:** Processes code analysis tasks asynchronously.
- **Redis:** Stores task statuses and results.
- **AI Agent Service:** Interacts with the chosen AI framework using LangChain as orchestrator.

### Flow
1. User submits a PR analysis request via `POST /analyze-pr`.
2. The FastAPI service creates a Celery task and returns a `task_id`.
3. The Celery worker:
    - Fetches code from the GitHub API
    - Analyzes the code using the AI agent
    - Stores the results in Redis
4. User can check the task status (`GET /status/<task_id>`) and retrieve results (`GET /results/<task_id>`) or `/pr-review-status`.

### AI Agent Design
- Modular design:
  - **Code Fetcher:** Fetches code/diffs from GitHub.
  - **Prompt Manager:** Decoupled prompts (currently in a JSON file).
  - **Analyzer:** Runs AI-based analysis.
  - **Result Formatter (Optional):** Formats results into the expected JSON structure.

### Error Handling
- **2 Types of Errors:**
  - **Retryable (2 times):**
    - 502 Service Unavailable
    - 422 Too Many Requests
    - Timeouts
  - **Non-Retryable:**
    - Invalid repository URLs
    - Insufficient permissions
    - Other LLM Failures
- Create DLQ for erroring requests.

## Database Design

### 1. Task
**Attributes:**
- `task_id`: A unique identifier for the task (UUID).
- `platformType`: Enum (`GITHUB`, `GITLAB`, `BITBUCKET`)
- `repo_url`: The URL of the GitHub repository (string).
- `pr_number`: The pull request number (integer).
- `status`: The current status of the task (enum: `PENDING`, `PROCESSING`, `COMPLETED`, `FAILED`).
- `created_at`: The timestamp when the task was created (datetime).
- `updated_at`: The timestamp when the task was last updated (datetime).

**Relationships:**
- A Task has a one-to-one relationship with a TaskResult.

**Indexes:**
- Index on `repo_url` and `pr_number` for faster lookup of tasks by repository and pull request.
- Unique constraint on the combination of `repo_url` and `pr_number` to ensure only one task is active per PR.

**Future Changes:**
- Can become polymorphic if different fields are needed for different platformTypes.

### 2. TaskResult
**Attributes:**
- `task_id`: A unique identifier for the task (UUID). This serves as a foreign key referencing the Task schema.
- `results`: A structured JSON document containing analysis results (JSON object).

**Relationships:**
- A TaskResult belongs to exactly one Task.


## API Interface Design

### 1. POST `/analyze-pr`
Triggers an analysis task for the given pull request.

#### Request:
Param: 
```cached: boolean```
Body:
```json
{
  "platformType": "GITHUB",
  "repo_url": "https://github.com/user/repo",
  "pr_number": 123,
  "token": "optional_token"
}
```
This request will be polymorphic in future. If cached == true, this will return latest task_id of completed task for given PR.
Note that if any request is under process or pending, it will not be queued again and task_id of older task will be returned.

#### Response (Success):
```json
{
  "task_id": "abc123",
  "status": "QUEUED"
}
```

#### Response (Failure):
```json
{
  "error": "Invalid repository URL",
  "status_code": 400
}
```

---

### 2. GET `/status/<task_id>`
Fetches the status of a specific task.

#### Response (Success):
```json
{
  "task_id": "abc123",
  "status": "PROCESSING"
}
```

#### Response (Failure):
```json
{
  "error": "Task not found",
  "status_code": 404
}
```

---

### 3. GET `/results/<task_id>`
Retrieves the results of a completed analysis task.

#### Response (Success):
```json
{
  "task_id": "abc123",
  "status": "COMPLETED",
  "results": {
    "files": [
      {
        "name": "main.py",
        "issues": [
          {
            "type": "style",
            "line": 15,
            "description": "Line too long",
            "suggestion": "Break line into multiple lines"
          },
          {
            "type": "bug",
            "line": 23,
            "description": "Potential null pointer",
            "suggestion": "Add null check"
          }
        ]
      }
    ],
    "summary": {
      "total_files": 1,
      "total_issues": 2,
      "critical_issues": 1
    }
  }
}
```

#### Response (Failure):
```json
{
  "error": "Task not found or not completed",
  "status_code": 404
}
```

---

### 4. GET `/pr-review-status`
Fetches the status and results of a latest pull request analysis task if it exists.

#### Request:
```json
{
  "platformType": "GITHUB",
  "repo_url": "https://github.com/user/repo",
  "pr_number": 123,
  "github_token": "optional_token"
}
```
This request will be polymorphic in future.

#### Response (Success):
```json
{
  "task_id": "abc123",
  "status": "completed",
  "results": {
    "files": [
      {
        "name": "main.py",
        "issues": [
          {
            "type": "style",
            "line": 15,
            "description": "Line too long",
            "suggestion": "Break line into multiple lines"
          }
        ]
      }
    ],
    "summary": {
      "total_files": 1,
      "total_issues": 1,
      "critical_issues": 0
    }
  }
}
```

#### Response (Failure):
```json
{
  "error": "No analysis task found for the given PR",
  "status_code": 404
}
```