"""
StxScript File Watcher
Provides file watching and auto-rebuild functionality for development
"""

import os
import sys
import time
import threading
from pathlib import Path
from typing import Set, List, Optional, Callable, Dict, Any
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler, FileSystemEvent
import fnmatch

from .transpiler import StxScriptTranspiler
from .error_handler import create_helpful_error_message


class StxScriptWatcher(FileSystemEventHandler):
    """File system event handler for StxScript files"""

    def __init__(self,
                 output_dir: Optional[Path] = None,
                 ignore_patterns: List[str] = None,
                 verbose: bool = False,
                 on_change: Optional[Callable] = None):
        super().__init__()
        self.output_dir = output_dir
        self.ignore_patterns = ignore_patterns or [
            "*.clar",
            "node_modules/*",
            ".git/*",
            "*.pyc",
            "__pycache__/*",
            ".stxscript/*"
        ]
        self.verbose = verbose
        self.on_change = on_change
        self.transpiler = StxScriptTranspiler()
        self.last_build_time = 0
        self.build_lock = threading.Lock()
        self.pending_files: Set[Path] = set()
        self.build_timer: Optional[threading.Timer] = None

    def on_any_event(self, event: FileSystemEvent) -> None:
        """Handle any file system event"""
        if event.is_directory:
            return

        file_path = Path(event.src_path)

        # Check if file should be ignored
        if self._should_ignore(file_path):
            return

        # Only process StxScript files
        if not file_path.suffix == '.stx':
            return

        if self.verbose:
            print(f"📝 Detected change: {file_path}")

        # Add to pending files and schedule build
        with self.build_lock:
            self.pending_files.add(file_path)
            self._schedule_build()

    def _should_ignore(self, file_path: Path) -> bool:
        """Check if file matches ignore patterns"""
        file_str = str(file_path)

        for pattern in self.ignore_patterns:
            if fnmatch.fnmatch(file_str, pattern) or fnmatch.fnmatch(file_path.name, pattern):
                return True

        return False

    def _schedule_build(self) -> None:
        """Schedule a build with debouncing"""
        # Cancel existing timer
        if self.build_timer is not None:
            self.build_timer.cancel()

        # Schedule new build after delay
        self.build_timer = threading.Timer(0.5, self._execute_build)
        self.build_timer.start()

    def _execute_build(self) -> None:
        """Execute build for pending files"""
        with self.build_lock:
            if not self.pending_files:
                return

            files_to_build = list(self.pending_files)
            self.pending_files.clear()

        start_time = time.time()
        success_count = 0
        error_count = 0

        if self.verbose:
            print(f"🔄 Building {len(files_to_build)} files...")

        for file_path in files_to_build:
            try:
                self._build_file(file_path)
                success_count += 1
                if self.verbose:
                    print(f"✅ {file_path}")

            except Exception as e:
                error_count += 1
                error_message = create_helpful_error_message(e, file_path.read_text())
                print(f"❌ {file_path}:")
                print(error_message)

        build_time = time.time() - start_time
        print(f"🏁 Build complete: {success_count} succeeded, {error_count} failed ({build_time:.2f}s)")

        # Call custom change handler
        if self.on_change:
            self.on_change(files_to_build, success_count, error_count)

        self.last_build_time = time.time()

    def _build_file(self, file_path: Path) -> None:
        """Build a single StxScript file"""
        # Read source code
        source_code = file_path.read_text(encoding='utf-8')

        # Transpile
        result = self.transpiler.transpile_with_error_handling(source_code)

        if not result.get("success", True):
            raise Exception(result["error"])

        clarity_code = result if isinstance(result, str) else result.get("clarity", "")

        # Determine output path
        if self.output_dir:
            # Calculate relative path and change extension
            output_path = self.output_dir / file_path.with_suffix('.clar').name
            output_path.parent.mkdir(parents=True, exist_ok=True)

            # Write output
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(clarity_code)

            if self.verbose:
                print(f"  → {output_path}")


class DevelopmentServer:
    """Development server with file watching and additional features"""

    def __init__(self,
                 watch_path: Path,
                 output_dir: Optional[Path] = None,
                 ignore_patterns: List[str] = None,
                 verbose: bool = False,
                 auto_format: bool = False,
                 auto_lint: bool = False):
        self.watch_path = watch_path
        self.output_dir = output_dir
        self.ignore_patterns = ignore_patterns or []
        self.verbose = verbose
        self.auto_format = auto_format
        self.auto_lint = auto_lint
        self.observer: Optional[Observer] = None
        self.stats = {
            "builds": 0,
            "successes": 0,
            "errors": 0,
            "start_time": 0
        }

    def start(self) -> None:
        """Start the development server"""
        if not self.watch_path.exists():
            raise ValueError(f"Watch path does not exist: {self.watch_path}")

        self.stats["start_time"] = time.time()

        # Create event handler
        handler = StxScriptWatcher(
            output_dir=self.output_dir,
            ignore_patterns=self.ignore_patterns,
            verbose=self.verbose,
            on_change=self._handle_file_changes
        )

        # Set up observer
        self.observer = Observer()
        self.observer.schedule(handler, str(self.watch_path), recursive=True)

        # Start watching
        self.observer.start()

        if self.verbose:
            print(f"🚀 StxScript development server started")
            print(f"📁 Watching: {self.watch_path}")
            if self.output_dir:
                print(f"📤 Output: {self.output_dir}")
            print("Press Ctrl+C to stop")

        # Initial build
        self._initial_build()

        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            self.stop()

    def stop(self) -> None:
        """Stop the development server"""
        if self.observer:
            self.observer.stop()
            self.observer.join()

        # Print statistics
        uptime = time.time() - self.stats["start_time"]
        print(f"\n📊 Session statistics:")
        print(f"   Uptime: {uptime:.1f}s")
        print(f"   Builds: {self.stats['builds']}")
        print(f"   Successes: {self.stats['successes']}")
        print(f"   Errors: {self.stats['errors']}")

        print("👋 Development server stopped")

    def _initial_build(self) -> None:
        """Perform initial build of all StxScript files"""
        stx_files = list(self.watch_path.rglob("*.stx"))

        if not stx_files:
            if self.verbose:
                print("ℹ️  No .stx files found for initial build")
            return

        print(f"🔄 Initial build: {len(stx_files)} files...")

        success_count = 0
        error_count = 0

        for file_path in stx_files:
            try:
                if self._should_ignore(file_path):
                    continue

                handler = StxScriptWatcher(
                    output_dir=self.output_dir,
                    ignore_patterns=self.ignore_patterns,
                    verbose=False
                )
                handler._build_file(file_path)
                success_count += 1

            except Exception as e:
                error_count += 1
                if self.verbose:
                    error_message = create_helpful_error_message(e, file_path.read_text())
                    print(f"❌ {file_path}:")
                    print(error_message)

        print(f"✅ Initial build complete: {success_count} succeeded, {error_count} failed")
        self.stats["builds"] += 1
        self.stats["successes"] += success_count
        self.stats["errors"] += error_count

    def _handle_file_changes(self, files: List[Path], success_count: int, error_count: int) -> None:
        """Handle file change events"""
        self.stats["builds"] += 1
        self.stats["successes"] += success_count
        self.stats["errors"] += error_count

        # Additional development features
        if self.auto_format and success_count > 0:
            self._auto_format_files(files)

        if self.auto_lint and success_count > 0:
            self._auto_lint_files(files)

    def _auto_format_files(self, files: List[Path]) -> None:
        """Auto-format files after successful build"""
        try:
            from .formatter import StxScriptFormatter, FormatterConfig

            formatter = StxScriptFormatter(FormatterConfig())

            for file_path in files:
                try:
                    original_content = file_path.read_text(encoding='utf-8')
                    formatted_content = formatter.format(original_content)

                    if original_content != formatted_content:
                        file_path.write_text(formatted_content, encoding='utf-8')
                        if self.verbose:
                            print(f"🎨 Auto-formatted: {file_path}")

                except Exception as e:
                    if self.verbose:
                        print(f"⚠️  Format error for {file_path}: {e}")

        except ImportError:
            pass  # Formatter not available

    def _auto_lint_files(self, files: List[Path]) -> None:
        """Auto-lint files after successful build"""
        try:
            from .linter import StxScriptLinter, LintConfig

            linter = StxScriptLinter(LintConfig())

            for file_path in files:
                try:
                    issues = linter.lint_file(str(file_path))

                    if issues and self.verbose:
                        print(f"🔍 Lint issues in {file_path}:")
                        for issue in issues[:3]:  # Show first 3 issues
                            print(f"  {issue}")
                        if len(issues) > 3:
                            print(f"  ... and {len(issues) - 3} more")

                except Exception as e:
                    if self.verbose:
                        print(f"⚠️  Lint error for {file_path}: {e}")

        except ImportError:
            pass  # Linter not available

    def _should_ignore(self, file_path: Path) -> bool:
        """Check if file should be ignored"""
        file_str = str(file_path)

        for pattern in self.ignore_patterns:
            if fnmatch.fnmatch(file_str, pattern) or fnmatch.fnmatch(file_path.name, pattern):
                return True

        return False


def start_watcher(watch_path: Path,
                  output_dir: Optional[Path] = None,
                  ignore_patterns: List[str] = None,
                  verbose: bool = False,
                  auto_format: bool = False,
                  auto_lint: bool = False) -> None:
    """Start file watcher with development server"""

    try:
        server = DevelopmentServer(
            watch_path=watch_path,
            output_dir=output_dir,
            ignore_patterns=ignore_patterns,
            verbose=verbose,
            auto_format=auto_format,
            auto_lint=auto_lint
        )

        server.start()

    except KeyboardInterrupt:
        print("\nStopping watcher...")
    except Exception as e:
        print(f"Error in watcher: {e}", file=sys.stderr)
        raise


def start_simple_watcher(watch_path: Path,
                        output_dir: Optional[Path] = None,
                        ignore_patterns: List[str] = None,
                        verbose: bool = False) -> None:
    """Start simple file watcher (lightweight version)"""

    handler = StxScriptWatcher(
        output_dir=output_dir,
        ignore_patterns=ignore_patterns,
        verbose=verbose
    )

    observer = Observer()
    observer.schedule(handler, str(watch_path), recursive=True)

    try:
        observer.start()

        if verbose:
            print(f"👁️  Watching {watch_path} for changes...")

        while True:
            time.sleep(1)

    except KeyboardInterrupt:
        observer.stop()
        print("\n👋 Watcher stopped")

    observer.join()


if __name__ == "__main__":
    # Example usage
    import sys

    if len(sys.argv) < 2:
        print("Usage: python watcher.py <watch_path> [output_dir]")
        sys.exit(1)

    watch_path = Path(sys.argv[1])
    output_dir = Path(sys.argv[2]) if len(sys.argv) > 2 else None

    start_watcher(
        watch_path=watch_path,
        output_dir=output_dir,
        verbose=True
    )