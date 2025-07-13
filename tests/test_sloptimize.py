"""
Unit tests for sloptimize function
"""

import os

# Set up provider before any imports
provider = os.getenv("LLM_PROVIDER", "openai")
os.environ["LLM_PROVIDER"] = provider

from sloptimize import sloptimize
from sloptimize.utils import print_sloptimize_result


def setup_module():
    """Print LLM provider and model info for all tests"""
    from sloptimize.environment import LLM_PROVIDER, OPENAI_MODEL, GROK_MODEL

    print(f"\n🤖 Running tests with LLM provider: {LLM_PROVIDER}")
    if LLM_PROVIDER == "openai":
        print(f"📝 Using OpenAI model: {OPENAI_MODEL}")
    elif LLM_PROVIDER == "grok":
        print(f"📝 Using Grok model: {GROK_MODEL}")
    print()


def test_sloptimize_basic_function():
    """Test sloptimize with a basic Python function"""
    input_code = """
def calculate_sum(numbers):
    total = 0
    for number in numbers:
        total = total + number
    return total
"""

    result = sloptimize(input_code)

    print_sloptimize_result(result)


def test_pydantic_type_basic():
    code = '''
    class LLMOptimizationResponse(BaseModel):
    """Structured response from LLM code optimization"""

    score: float
    optimized_code: str
    metrics: OptimizationMetrics
    recommendations: List[str]
    considerations: str
    '''
    result = sloptimize(code)

    print_sloptimize_result(result)


def test_function_with_paths():
    code = '''
def _get_system_prompt() -> str:
    """Load system prompt from PROMPT.md"""
    prompt_path = os.path.join(os.path.dirname(__file__), "PROMPT.md")
    with open(prompt_path, "r") as f:
        return f.read()
    '''
    result = sloptimize(code)

    print_sloptimize_result(result)


def test_function_print_json():
    code = '''
def print_json(data: Any, title: str = None) -> None:
    """
    Print generic JSON data with syntax highlighting

    Args:
        data: Data to print (can be dict, BaseModel, or JSON string)
        title: Optional title to display above the JSON
    """
    # Convert data to JSON string
    if isinstance(data, BaseModel):
        json_str = data.model_dump_json(indent=2)
    elif isinstance(data, dict):
        json_str = json.dumps(data, indent=2)
    elif isinstance(data, str):
        # Assume it's already JSON, try to reformat it
        try:
            parsed = json.loads(data)
            json_str = json.dumps(parsed, indent=2)
        except json.JSONDecodeError:
            json_str = data
    else:
        json_str = json.dumps(data, indent=2, default=str)

    # Create syntax highlighted JSON
    syntax = Syntax(json_str, "json", theme="monokai", line_numbers=False)

    if title:
        console.print(f"\n[bold cyan]{title}[/bold cyan]")

    console.print(syntax)
    '''
    result = sloptimize(code)

    print_sloptimize_result(result)


def test_file_worker():
    code = '''
    import time
import threading
import uuid
from typing import Optional

from jockey.deploy import DeploymentConfig, build_and_deploy_with_events
from jockey.backend.event import BaseEvent
from jockey.log import logger
from jockey.environment import WORKER_POLL_INTERVAL
from jockey.worker import queue


class Worker:
    """Background worker that processes deployment jobs from Redis queue."""

    running: bool = False
    worker_threads: dict[str, threading.Thread]
    worker_id: str

    def __init__(self):
        """Initialize the deployment worker."""
        self.worker_threads = {}
        self.worker_id = str(uuid.uuid4())

    def start(self) -> None:
        """Start the worker polling loop."""
        self.running = True
        logger.info("Starting deployment worker")

        while self.running:
            try:
                if job_data := self._get_next_job():
                    self._process_job(job_data)

                self._cleanup_threads()
                time.sleep(WORKER_POLL_INTERVAL)

            except Exception as e:
                logger.error(f"Worker error: {e}")
                time.sleep(WORKER_POLL_INTERVAL)

    def stop(self) -> None:
        """Stop the worker and wait for active deployments to complete."""
        logger.info("Stopping deployment worker")
        self.running = False

        # Wait for active deployments to complete
        for thread in self.worker_threads.values():
            if thread.is_alive():
                thread.join(timeout=30)  # 30 second timeout

    def _get_next_job(self) -> Optional[queue.JobData]:
        """Get the next deployment job from the queue using atomic dequeue.

        Returns:
            Job data dictionary or None if queue is empty
        """
        job_data = queue.claim_next_available_job()
        if job_data:
            return job_data
        return None

    def _process_job(self, job_data: queue.JobData) -> None:
        """Process a deployment job by starting it in a background thread.

        Args:
            job_data: Job data containing deployment configuration
        """
        job_id = job_data["job_id"]
        project_id = job_data["project_id"]

        # Don't start duplicate jobs
        if job_id in self.worker_threads and self.worker_threads[job_id].is_alive():
            logger.warning(f"Job {job_id} already running")
            return

        logger.info(f"Starting deployment job {job_id} for project {project_id}")
        thread = threading.Thread(
            target=self._run_job,
            args=(job_data,),
            daemon=True,
            name=f"deploy-{job_id}",
        )
        thread.start()
        self.worker_threads[job_id] = thread

    def _run_job(self, job_data: queue.JobData) -> None:
        """Run a deployment job and store events in Redis.

        Args:
            job_data: Job data containing deployment configuration
        """
        job_id = job_data["job_id"]
        project_id = job_data["project_id"]

        try:
            config = DeploymentConfig(**job_data["config"])
            logger.info(f"Processing deployment for {config.app_name} in {config.namespace}")

            # Process all events from the deployment
            for event in build_and_deploy_with_events(config):
                if isinstance(event, BaseEvent):
                    queue.store_event(job_id=job_id, event=event)

        except Exception:
            logger.error(f"Deployment job {job_id} failed", exc_info=True)
            # note this will not store an event in redis; revisit this if we want to track failures
        finally:
            self._cleanup_job(job_id)

    def _cleanup_job(self, job_id: str) -> None:
        """Clean up job state after completion.

        Args:
            job_id: Job identifier
        """
        try:
            if job_id in self.worker_threads:
                del self.worker_threads[job_id]
                logger.debug(f"Cleaned up job {job_id}")
        except Exception as e:
            logger.error(f"Error cleaning up job {job_id}: {e}")

    def _cleanup_threads(self) -> None:
        """Clean up completed deployment threads."""
        for job_id in self.get_running_jobs():
            logger.debug(f"Removing completed job {job_id} thread")
            del self.worker_threads[job_id]

    def get_running_jobs(self) -> list[str]:
        """Get currently active deployment jobs.

        Returns:
            List of job IDs that are currently running
        """
        return [job_id for job_id, thread in self.worker_threads.items() if thread.is_alive()]


if __name__ == "__main__":
    """Run the deployment worker as a standalone process."""
    import signal
    import sys

    worker = Worker()

    def signal_handler(signum, frame):
        print("\nReceived shutdown signal, stopping worker...")
        worker.stop()
        sys.exit(0)

    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    try:
        worker.start()
    except KeyboardInterrupt:
        worker.stop()
'''
    result = sloptimize(code)

    print_sloptimize_result(result)


def test_class_grok_client():
    code = '''
class GrokClient:
    """Wrapper for xAI Grok interactions using native xAI SDK"""

    def __init__(self, client: Client, model: str):
        self.client = client
        self.model = model

    def __call__(
        self,
        messages: List[Dict[str, str]],
        response_model: Type[T],
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        max_retries: int = 2,
    ) -> T:
        """Complete a chat conversation with structured output using xAI SDK"""
        for attempt in range(max_retries + 1):
            try:
                # Create chat instance
                chat = self.client.chat.create(model=self.model)

                # Add messages to chat
                for message in messages:
                    if message["role"] == "system":
                        chat.append(system(message["content"]))
                    elif message["role"] == "user":
                        chat.append(user(message["content"]))

                # Parse with Pydantic model - returns (response, parsed_object)
                response, parsed_object = chat.parse(response_model)
                return parsed_object

            except (ValidationError, ConnectionError, TimeoutError) as e:
                if attempt == max_retries:
                    logging.error(f"Failed after {max_retries + 1} attempts: {e}")
                    raise

                wait_time = 2 ** attempt
                logging.warning(f"Attempt {attempt + 1} failed: {e}. Retrying in {wait_time}s...")
                time.sleep(wait_time)
    '''
    result = sloptimize(code)
    print_sloptimize_result(result)


def test_nested_loops_inefficient():
    """Test optimization of nested loops that could be improved"""
    code = """
def find_common_elements(list1, list2):
    common = []
    for item1 in list1:
        for item2 in list2:
            if item1 == item2 and item1 not in common:
                common.append(item1)
    return common
    """
    result = sloptimize(code)
    print_sloptimize_result(result)


def test_string_concatenation_inefficient():
    """Test optimization of inefficient string concatenation"""
    code = """
def build_query_string(params):
    query = ""
    for key in params:
        if query != "":
            query = query + "&"
        query = query + str(key) + "=" + str(params[key])
    return query
    """
    result = sloptimize(code)
    print_sloptimize_result(result)


def test_exception_handling_poor():
    """Test improvement of overly broad exception handling"""
    code = """
def process_user_data(data):
    try:
        user_id = int(data["id"])
        email = data["email"].lower().strip()
        age = int(data["age"])

        if age < 0:
            raise ValueError("Age cannot be negative")

        return {"id": user_id, "email": email, "age": age}
    except:
        return None
    """
    result = sloptimize(code)
    print_sloptimize_result(result)


def test_database_query_n_plus_one():
    """Test optimization of N+1 query pattern"""
    code = """
def get_users_with_posts(user_ids):
    users = []
    for user_id in user_ids:
        user = db.query("SELECT * FROM users WHERE id = ?", [user_id])
        posts = db.query("SELECT * FROM posts WHERE user_id = ?", [user_id])
        user["posts"] = posts
        users.append(user)
    return users
    """
    result = sloptimize(code)
    print_sloptimize_result(result)


def test_memory_inefficient_list_processing():
    """Test optimization of memory-inefficient list processing"""
    code = """
def process_large_dataset(filename):
    with open(filename, 'r') as f:
        lines = f.readlines()

    processed = []
    for line in lines:
        if line.strip():
            parts = line.split(',')
            if len(parts) >= 3:
                processed.append({
                    'name': parts[0].strip(),
                    'value': float(parts[1]),
                    'category': parts[2].strip()
                })

    return processed
    """
    result = sloptimize(code)
    print_sloptimize_result(result)


def test_regex_compilation_in_loop():
    """Test optimization of regex compilation inside loops"""
    code = """
import re

def validate_emails(email_list):
    valid_emails = []
    for email in email_list:
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if re.match(pattern, email):
            valid_emails.append(email)
    return valid_emails
    """
    result = sloptimize(code)
    print_sloptimize_result(result)


def test_django_orm_inefficient():
    """Test optimization of inefficient Django ORM usage"""
    code = """
def get_article_data(article_ids):
    articles = []
    for article_id in article_ids:
        article = Article.objects.get(id=article_id)
        author = article.author
        category = article.category
        comment_count = article.comments.count()

        articles.append({
            'title': article.title,
            'author': author.name,
            'category': category.name,
            'comment_count': comment_count
        })

    return articles
    """
    result = sloptimize(code)
    print_sloptimize_result(result)


def test_async_function_inefficient():
    """Test optimization of inefficient async function"""
    code = """
import asyncio
import aiohttp

async def fetch_user_profiles(user_ids):
    profiles = []
    async with aiohttp.ClientSession() as session:
        for user_id in user_ids:
            async with session.get(f'/api/users/{user_id}') as response:
                profile = await response.json()
                profiles.append(profile)
    return profiles
    """
    result = sloptimize(code)
    print_sloptimize_result(result)


def test_dict_comprehension_opportunity():
    """Test code that could benefit from dict comprehension"""
    code = """
def transform_config(raw_config):
    config = {}
    for key in raw_config:
        if isinstance(raw_config[key], str):
            config[key.upper()] = raw_config[key].strip()
        elif isinstance(raw_config[key], (int, float)):
            config[key.upper()] = raw_config[key]
    return config
    """
    result = sloptimize(code)
    print_sloptimize_result(result)


def test_enum_if_statements():
    """Test optimization of if/elif statements over enum values"""
    code = """
def process_request(request_status, request_data):
    if request_status == Status.PENDING:
        return {"message": "Request is pending review", "next_action": "wait"}
    elif request_status == Status.APPROVED:
        return {"message": "Request approved, processing...", "next_action": "execute"}
    elif request_status == Status.REJECTED:
        return {"message": "Request rejected", "next_action": "revise"}
    elif request_status == Status.CANCELLED:
        return {"message": "Request cancelled", "next_action": "none"}
    else:
        return {"message": "Unknown status", "next_action": "error"}
    """
    result = sloptimize(code)
    print_sloptimize_result(result)


def test_another_worker():
    # fmt: off
    code = '''
import multiprocessing
import time
import signal
import sys
from typing import Callable, Any, Optional


class Worker:
    """A class that implements a worker process which accepts a callback function."""
    def __init__(self, target_function: Callable[[], Any], poll_interval: float = 1.0):
        self.target_function = target_function
        self.poll_interval = poll_interval
        self.worker_process: Optional[multiprocessing.Process] = None
        self.running = False

    def _worker_loop(self):
        signal.signal(signal.SIGTERM, self._signal_handler)
        signal.signal(signal.SIGINT, self._signal_handler)

        while True:
            try:
            # Call target function.
                self.target_function()
                time.sleep(self.poll_interval)
            except KeyboardInterrupt:
                break
            except Exception as e:
                # Handle exceptions in worker process.
                print(f"Error in worker process: {e}")
                time.sleep(self.poll_interval)

    def _signal_handler(self, signum, frame):
        sys.exit(0)

    def start(self):
        if self.running:
            raise RuntimeError("Worker is already running")

        # Start the worker process.
        self.worker_process = multiprocessing.Process(target=self._worker_loop)
        self.worker_process.start()
        self.running = True
        print(f"Worker process started with PID: {self.worker_process.pid}")

    def stop(self):
        if not self.running or not self.worker_process:
            return

        # Terminate the worker process gracefully.
        self.worker_process.terminate()
        self.worker_process.join(timeout=5)

        if self.worker_process.is_alive():
            self.worker_process.kill()
            self.worker_process.join()

        self.running = False
        print("Worker process stopped")

    def is_alive(self):
        return self.running and self.worker_process and self.worker_process.is_alive()


if __name__ == "__main__":
    def example_function():
        print(f"Polling at {time.strftime('%Y-%m-%d %H:%M:%S')}")

    worker = Worker(example_function, poll_interval=2.0)

    try:
        worker.start()
        time.sleep(10)
        worker.stop()
    except KeyboardInterrupt:
        worker.stop()
    '''
    result = sloptimize(code)
    print_sloptimize_result(result)
    # write the result to a temp file:
    with open("temp.py", "w") as f:
        f.write(result.source_code)
