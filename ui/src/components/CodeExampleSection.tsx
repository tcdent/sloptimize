import React, { useState, useEffect } from 'react';
import styled from 'styled-components';
import Prism from 'prismjs';
import 'prismjs/components/prism-python';
import 'prismjs/themes/prism-dark.css';
import Section from './Section';

const CodeTabs = styled.div`
  border: 1px solid var(--border);
  border-radius: 4px;
  background-color: var(--background);
  overflow: hidden;
  box-shadow: none;
`;

const TabHeaders = styled.div`
  display: flex;
  background-color: var(--modal-background);
  border-bottom: 1px solid var(--border);

  @media (max-width: 768px) {
    flex-direction: column;
  }
`;

const TabBtn = styled.button<{ $active: boolean }>`
  flex: 1;
  padding: 12px 20px;
  background-color: ${props => props.$active ? 'var(--border)' : 'transparent'};
  color: ${props => props.$active ? 'var(--text-primary)' : 'var(--text-secondary)'};
  border: none;
  font-family: inherit;
  font-size: 14px;
  font-weight: ${props => props.$active ? '700' : '400'};
  cursor: pointer;
  transition: all 0.2s;
  border-right: 1px solid var(--border);

  &:last-child {
    border-right: none;
  }

  &:hover:not([data-active="true"]) {
    background-color: var(--modal-background);
    color: var(--accent);
  }

  @media (max-width: 768px) {
    border-right: none;
    border-bottom: 1px solid var(--border);

    &:last-child {
      border-bottom: none;
    }
  }
`;

const TabContent = styled.div<{ $active: boolean }>`
  display: ${props => props.$active ? 'block' : 'none'};
  padding: 0;
`;

const Code = styled.pre`
  padding: 20px;
  margin: 0;
  color: var(--text-primary);
  background-color: transparent;
  font-family: inherit;
  font-size: 14px;
  overflow-x: auto;
  line-height: 1.4;

  /* Override Prism.js styles for our color scheme */
  .token.keyword { color: var(--accent); }
  .token.string { color: var(--title); }
  .token.function { color: var(--accent); }
  .token.operator { color: var(--text-primary); }
  .token.punctuation { color: var(--text-primary); }
  .token.comment { color: #666; }
  .token.number { color: var(--title); }
  .token.builtin { color: var(--accent); }
  .token.decorator { color: var(--title); }

  /* Diff highlighting */
  .deleted {
    color: #ff6b6b;
    background-color: rgba(255, 107, 107, 0.1);
  }

  .inserted {
    color: var(--accent);
    background-color: rgba(93, 211, 158, 0.1);
  }
`;

type TabType = 'original' | 'diff' | 'optimized';

const CodeExampleSection: React.FC = () => {
  const [activeTab, setActiveTab] = useState<TabType>('original');

  useEffect(() => {
    Prism.highlightAll();
  }, [activeTab]);

  const originalCode = `import multiprocessing
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
        worker.stop()`;

  const diffCode = `+from typing import Any, Callable, Optional
 import multiprocessing
-import time
 import signal
 import sys
-from typing import Callable, Any, Optional
+import time


 class Worker:
-    def __init__(self, target_function: Callable[[], Any], poll_interval: float = 1.0):
-        self.target_function = target_function
+    """Manages a background process that periodically calls a provided callback function.
+
+    This class creates a separate process to run the callback in a loop, sleeping for the specified
+    poll interval between calls. It handles signals for graceful shutdown and provides methods to
+    start, stop, and check the status of the process.
+
+    Example:
+        def example_function():
+            print(f"Polling at {time.strftime('%Y-%m-%d %H:%M:%S')}")
+
+        worker = Worker(example_function, poll_interval=2.0)
+        worker.start()
+        time.sleep(10)
+        worker.stop()
+    """
+
+    process: Optional[multiprocessing.Process]
+    running: bool
+    target: Callable[[], Any]
+    poll_interval: float
+
+    def __init__(self, target: Callable[[], Any], poll_interval: float = 1.0) -> None:
+        self.target = target
         self.poll_interval = poll_interval
-        self.worker_process: Optional[multiprocessing.Process] = None
+        self.process = None
         self.running = False

-    def _worker_loop(self):
+    def _run_loop(self) -> None:
+        """Internal loop that runs in the worker process, calling the target function periodically."""
         signal.signal(signal.SIGTERM, self._signal_handler)
         signal.signal(signal.SIGINT, self._signal_handler)

         while True:
             try:
-                self.target_function()
+                self.target()
                 time.sleep(self.poll_interval)
             except KeyboardInterrupt:
                 break
             except Exception as e:
-                print(f"Error in worker process: {e}")
+                print(f"Error in process: {e}")
                 time.sleep(self.poll_interval)

-    def _signal_handler(self, signum, frame):
+    def _signal_handler(self, signum: int, frame: Any) -> None:
+        """Handles termination signals by exiting the process."""
         sys.exit(0)

-    def start(self):
+    def start(self) -> None:
+        """Starts the worker process if not already running."""
         if self.running:
             raise RuntimeError("Worker is already running")

-        self.worker_process = multiprocessing.Process(target=self._worker_loop)
-        self.worker_process.start()
+        self.process = multiprocessing.Process(target=self._run_loop)
+        self.process.start()
         self.running = True
-        print(f"Worker process started with PID: {self.worker_process.pid}")
+        print(f"Started process with PID: {self.process.pid}")

-    def stop(self):
-        if not self.running or not self.worker_process:
+    def stop(self) -> None:
+        """Stops the worker process gracefully, forcing termination if necessary."""
+        if not self.running or not self.process:
             return

-        self.worker_process.terminate()
-        self.worker_process.join(timeout=5)
+        self.process.terminate()
+        self.process.join(timeout=5)

-        if self.worker_process.is_alive():
-            self.worker_process.kill()
-            self.worker_process.join()
+        if self.process.is_alive():
+            self.process.kill()
+            self.process.join()

         self.running = False
-        print("Worker process stopped")
+        print("Process stopped")

-    def is_alive(self):
-        return self.running and self.worker_process and self.worker_process.is_alive()
+    def is_alive(self) -> bool:
+        """Checks if the worker process is running and alive."""
+        return self.running and self.process and self.process.is_alive()
-
-
-if __name__ == "__main__":
-
-    def example_function():
-        print(f"Polling at {time.strftime('%Y-%m-%d %H:%M:%S')}")
-
-    worker = Worker(example_function, poll_interval=2.0)
-
-    try:
-        worker.start()
-        time.sleep(10)
-        worker.stop()
-    except KeyboardInterrupt:
-        worker.stop()
`;

  const optimizedCode = `from typing import Any, Callable, Optional
import multiprocessing
import signal
import sys
import time


class Worker:
    """Manages a background process that periodically calls a provided callback function.

    This class creates a separate process to run the callback in a loop, sleeping for the specified
    poll interval between calls. It handles signals for graceful shutdown and provides methods to
    start, stop, and check the status of the process.

    Example:
        def example_function():
            print(f"Polling at {time.strftime('%Y-%m-%d %H:%M:%S')}")

        worker = Worker(example_function, poll_interval=2.0)
        worker.start()
        time.sleep(10)
        worker.stop()
    """

    process: Optional[multiprocessing.Process]
    running: bool
    target: Callable[[], Any]
    poll_interval: float

    def __init__(self, target: Callable[[], Any], poll_interval: float = 1.0) -> None:
        self.target = target
        self.poll_interval = poll_interval
        self.process = None
        self.running = False

    def _run_loop(self) -> None:
        """Internal loop that runs in the worker process, calling the target function periodically."""
        signal.signal(signal.SIGTERM, self._signal_handler)
        signal.signal(signal.SIGINT, self._signal_handler)

        while True:
            try:
                self.target()
                time.sleep(self.poll_interval)
            except KeyboardInterrupt:
                break
            except Exception as e:
                print(f"Error in process: {e}")
                time.sleep(self.poll_interval)

    def _signal_handler(self, signum: int, frame: Any) -> None:
        """Handles termination signals by exiting the process."""
        sys.exit(0)

    def start(self) -> None:
        """Starts the worker process if not already running."""
        if self.running:
            raise RuntimeError("Worker is already running")

        self.process = multiprocessing.Process(target=self._run_loop)
        self.process.start()
        self.running = True
        print(f"Started process with PID: {self.process.pid}")

    def stop(self) -> None:
        """Stops the worker process gracefully, forcing termination if necessary."""
        if not self.running or not self.process:
            return

        self.process.terminate()
        self.process.join(timeout=5)

        if self.process.is_alive():
            self.process.kill()
            self.process.join()

        self.running = False
        print("Process stopped")

    def is_alive(self) -> bool:
        """Checks if the worker process is running and alive."""
        return self.running and self.process and self.process.is_alive()`;

  const formatDiffCode = (code: string) => {
    return code.split('\n').map((line, index) => {
      if (line.startsWith('-')) {
        return <span key={index} className="deleted">{line}</span>;
      } else if (line.startsWith('+')) {
        return <span key={index} className="inserted">{line}</span>;
      }
      return <span key={index}>{line}</span>;
    }).reduce((prev, curr, index) => [prev, '\n', curr] as any);
  };

  const getCode = () => {
    switch (activeTab) {
      case 'original':
        return <code className="language-python">{originalCode}</code>;
      case 'diff':
        return formatDiffCode(diffCode);
      case 'optimized':
        return <code className="language-python">{optimizedCode}</code>;
      default:
        return <code className="language-python">{originalCode}</code>;
    }
  };

  return (
    <Section title="Code Optimization Example">
      <CodeTabs>
        <TabHeaders>
          <TabBtn
            $active={activeTab === 'original'}
            onClick={() => setActiveTab('original')}
          >
            Original
          </TabBtn>
          <TabBtn
            $active={activeTab === 'diff'}
            onClick={() => setActiveTab('diff')}
          >
            Diff
          </TabBtn>
          <TabBtn
            $active={activeTab === 'optimized'}
            onClick={() => setActiveTab('optimized')}
          >
            Optimized
          </TabBtn>
        </TabHeaders>

        <TabContent $active={true}>
          <Code>{getCode()}</Code>
        </TabContent>
      </CodeTabs>
    </Section>
  );
};

export default CodeExampleSection;