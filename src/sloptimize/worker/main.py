"""
Background worker for processing repositories with sloptimize
"""

import sys
import asyncio
import tempfile
import shutil
from pathlib import Path
from typing import List
import traceback

from ..database import Database, JobStatus
from ..main import sloptimize


class RepositoryProcessor:
    """Handles repository checkout and file processing"""

    def __init__(self, job_id: str, repo_url: str):
        self.job_id = job_id
        self.repo_url = repo_url
        self.db = Database()
        self.temp_dir = None

        # File extensions to process
        self.supported_extensions = {
            ".py",
        }

    async def process(self):
        """Main processing function"""
        try:
            self.db.update_job_status(self.job_id, JobStatus.PROCESSING)

            # Clone repository
            await self._clone_repository()

            # Find all code files
            code_files = self._find_code_files()

            if not code_files:
                self.db.update_job_status(
                    self.job_id, JobStatus.COMPLETED, "No supported code files found"
                )
                return

            # Update progress
            self.db.update_job_progress(self.job_id, len(code_files), 0)

            # Process files concurrently
            await self._process_files_async(code_files)

            self.db.update_job_status(self.job_id, JobStatus.COMPLETED)

        except Exception as e:
            error_msg = f"Processing failed: {str(e)}\n{traceback.format_exc()}"
            self.db.update_job_status(self.job_id, JobStatus.FAILED, error_msg)
        finally:
            # Cleanup
            if self.temp_dir and self.temp_dir.exists():
                shutil.rmtree(self.temp_dir)

    async def _clone_repository(self):
        """Clone the repository to a temporary directory"""
        self.temp_dir = Path(tempfile.mkdtemp())

        process = await asyncio.create_subprocess_exec(
            "git",
            "clone",
            "--depth",
            "1",
            self.repo_url,
            str(self.temp_dir),
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )

        stdout, stderr = await process.communicate()

        if process.returncode != 0:
            raise Exception(f"Git clone failed: {stderr.decode()}")

    def _find_code_files(self) -> List[Path]:
        """Find all supported code files in the repository"""
        code_files = []

        for file_path in self.temp_dir.rglob("*"):
            if (
                file_path.is_file()
                and file_path.suffix.lower() in self.supported_extensions
                and not self._should_ignore_file(file_path)
            ):
                code_files.append(file_path)

        return code_files

    def _should_ignore_file(self, file_path: Path) -> bool:
        """Check if file should be ignored (e.g., in node_modules, .git, etc.)"""
        ignore_dirs = {
            ".git",
            "node_modules",
            "__pycache__",
            ".pytest_cache",
            "venv",
            ".venv",
            "env",
            ".env",
            "build",
            "dist",
            ".idea",
            ".vscode",
            "target",
            "bin",
            "obj",
        }

        # Check if any parent directory is in ignore list
        for parent in file_path.parents:
            if parent.name in ignore_dirs:
                return True

        # Check file size (skip very large files > 1MB)
        try:
            if file_path.stat().st_size > 1024 * 1024:
                return True
        except:
            return True

        return False

    async def _process_files_async(self, code_files: List[Path]):
        """Process code files asynchronously with concurrency limit"""
        semaphore = asyncio.Semaphore(5)  # Limit concurrent processing

        async def process_single_file(file_path: Path):
            async with semaphore:
                await self._process_single_file(file_path)

        # Create tasks for all files
        tasks = [process_single_file(file_path) for file_path in code_files]

        # Process with progress updates
        completed = 0
        for task in asyncio.as_completed(tasks):
            try:
                await task
                completed += 1
                self.db.update_job_progress(self.job_id, len(code_files), completed)
            except Exception as e:
                print(f"Error processing file: {e}")
                completed += 1
                self.db.update_job_progress(self.job_id, len(code_files), completed)

    async def _process_single_file(self, file_path: Path):
        """Process a single file with sloptimize."""
        try:
            # Read file content
            original_code = file_path.read_text(encoding="utf-8", errors="ignore")

            # Skip empty files or very small files
            if len(original_code.strip()) < 50:
                return

            # Run sloptimize in executor to avoid blocking
            loop = asyncio.get_event_loop()
            result = await loop.run_in_executor(None, sloptimize, original_code)

            # Get relative path from repo root
            relative_path = file_path.relative_to(self.temp_dir)

            # Save result to database
            self.db.save_file_result(
                job_id=self.job_id,
                file_path=str(relative_path),
                original_code=original_code,
                optimized_code=result.source_code,
                score=result.assessment.score or 0.0,
                metrics=result.assessment.metrics or {},
                integration_considerations=result.integration_considerations,
            )

        except Exception as e:
            print(f"Error processing {file_path}: {e}")


async def main():
    """Entry point for worker process"""
    if len(sys.argv) != 3:
        print("Usage: python -m sloptimize.worker.main <job_id> <repo_url>")
        sys.exit(1)

    job_id = sys.argv[1]
    repo_url = sys.argv[2]

    processor = RepositoryProcessor(job_id, repo_url)
    await processor.process()


if __name__ == "__main__":
    asyncio.run(main())
