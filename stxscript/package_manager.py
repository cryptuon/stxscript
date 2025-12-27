"""
StxScript Package Manager

Provides dependency management for StxScript projects:
- Package manifest (stxscript.toml)
- Dependency resolution
- Version management
- Package installation
"""

import os
import re
import json
import shutil
import hashlib
from dataclasses import dataclass, field
from typing import List, Dict, Optional, Set, Tuple
from pathlib import Path

try:
    import toml
except ImportError:
    toml = None


# =============================================================================
# DATA TYPES
# =============================================================================

@dataclass
class Version:
    """Semantic version representation."""
    major: int
    minor: int
    patch: int
    prerelease: Optional[str] = None

    @classmethod
    def parse(cls, version_str: str) -> 'Version':
        """Parse a version string."""
        # Remove 'v' prefix if present
        version_str = version_str.lstrip('v')

        # Match semantic version pattern
        pattern = r'^(\d+)\.(\d+)\.(\d+)(?:-(.+))?$'
        match = re.match(pattern, version_str)

        if not match:
            raise ValueError(f"Invalid version string: {version_str}")

        return cls(
            major=int(match.group(1)),
            minor=int(match.group(2)),
            patch=int(match.group(3)),
            prerelease=match.group(4)
        )

    def __str__(self) -> str:
        base = f"{self.major}.{self.minor}.{self.patch}"
        if self.prerelease:
            return f"{base}-{self.prerelease}"
        return base

    def __lt__(self, other: 'Version') -> bool:
        if (self.major, self.minor, self.patch) != (other.major, other.minor, other.patch):
            return (self.major, self.minor, self.patch) < (other.major, other.minor, other.patch)
        # Prerelease versions are less than release versions
        if self.prerelease and not other.prerelease:
            return True
        if not self.prerelease and other.prerelease:
            return False
        return (self.prerelease or "") < (other.prerelease or "")

    def __eq__(self, other) -> bool:
        if not isinstance(other, Version):
            return False
        return (self.major, self.minor, self.patch, self.prerelease) == \
               (other.major, other.minor, other.patch, other.prerelease)

    def __hash__(self) -> int:
        return hash((self.major, self.minor, self.patch, self.prerelease))


@dataclass
class VersionRequirement:
    """Version requirement specification."""
    operator: str  # "^", "~", ">=", "<=", ">", "<", "="
    version: Version

    @classmethod
    def parse(cls, req_str: str) -> 'VersionRequirement':
        """Parse a version requirement string."""
        req_str = req_str.strip()

        # Match operator and version
        pattern = r'^(\^|~|>=|<=|>|<|=)?(.+)$'
        match = re.match(pattern, req_str)

        if not match:
            raise ValueError(f"Invalid version requirement: {req_str}")

        operator = match.group(1) or "^"  # Default to caret
        version = Version.parse(match.group(2))

        return cls(operator=operator, version=version)

    def satisfies(self, version: Version) -> bool:
        """Check if a version satisfies this requirement."""
        if self.operator == "=":
            return version == self.version
        elif self.operator == ">":
            return version > self.version
        elif self.operator == ">=":
            return version >= self.version
        elif self.operator == "<":
            return version < self.version
        elif self.operator == "<=":
            return version <= self.version
        elif self.operator == "^":
            # Caret: compatible with (same major, >= minor.patch)
            if version.major != self.version.major:
                return False
            return version >= self.version
        elif self.operator == "~":
            # Tilde: compatible with (same major.minor, >= patch)
            if version.major != self.version.major:
                return False
            if version.minor != self.version.minor:
                return False
            return version >= self.version

        return False


@dataclass
class Dependency:
    """Package dependency."""
    name: str
    version_req: VersionRequirement
    source: str = "registry"  # "registry", "git", "path"
    git_url: Optional[str] = None
    path: Optional[str] = None

    @classmethod
    def from_dict(cls, name: str, spec: dict) -> 'Dependency':
        """Create dependency from dictionary spec."""
        if isinstance(spec, str):
            return cls(name=name, version_req=VersionRequirement.parse(spec))

        version = spec.get("version", "*")
        source = "registry"
        git_url = None
        path = None

        if "git" in spec:
            source = "git"
            git_url = spec["git"]
        elif "path" in spec:
            source = "path"
            path = spec["path"]

        return cls(
            name=name,
            version_req=VersionRequirement.parse(version),
            source=source,
            git_url=git_url,
            path=path
        )


@dataclass
class PackageManifest:
    """Package manifest (stxscript.toml)."""
    name: str
    version: Version
    description: str = ""
    authors: List[str] = field(default_factory=list)
    license: str = "MIT"
    repository: Optional[str] = None
    homepage: Optional[str] = None
    keywords: List[str] = field(default_factory=list)
    dependencies: Dict[str, Dependency] = field(default_factory=dict)
    dev_dependencies: Dict[str, Dependency] = field(default_factory=dict)

    @classmethod
    def load(cls, path: str) -> 'PackageManifest':
        """Load manifest from file."""
        if toml is None:
            raise RuntimeError("toml package required for package management")

        with open(path, 'r') as f:
            data = toml.load(f)

        package = data.get("package", {})

        dependencies = {}
        for name, spec in data.get("dependencies", {}).items():
            dependencies[name] = Dependency.from_dict(name, spec)

        dev_dependencies = {}
        for name, spec in data.get("dev-dependencies", {}).items():
            dev_dependencies[name] = Dependency.from_dict(name, spec)

        return cls(
            name=package.get("name", "unnamed"),
            version=Version.parse(package.get("version", "0.1.0")),
            description=package.get("description", ""),
            authors=package.get("authors", []),
            license=package.get("license", "MIT"),
            repository=package.get("repository"),
            homepage=package.get("homepage"),
            keywords=package.get("keywords", []),
            dependencies=dependencies,
            dev_dependencies=dev_dependencies
        )

    def save(self, path: str):
        """Save manifest to file."""
        if toml is None:
            raise RuntimeError("toml package required for package management")

        data = {
            "package": {
                "name": self.name,
                "version": str(self.version),
                "description": self.description,
                "authors": self.authors,
                "license": self.license,
            },
            "dependencies": {},
            "dev-dependencies": {}
        }

        if self.repository:
            data["package"]["repository"] = self.repository
        if self.homepage:
            data["package"]["homepage"] = self.homepage
        if self.keywords:
            data["package"]["keywords"] = self.keywords

        for name, dep in self.dependencies.items():
            if dep.source == "registry":
                data["dependencies"][name] = f"{dep.version_req.operator}{dep.version_req.version}"
            elif dep.source == "git":
                data["dependencies"][name] = {"git": dep.git_url, "version": str(dep.version_req.version)}
            elif dep.source == "path":
                data["dependencies"][name] = {"path": dep.path}

        for name, dep in self.dev_dependencies.items():
            if dep.source == "registry":
                data["dev-dependencies"][name] = f"{dep.version_req.operator}{dep.version_req.version}"

        with open(path, 'w') as f:
            toml.dump(data, f)


@dataclass
class LockEntry:
    """Entry in the lock file."""
    name: str
    version: Version
    source: str
    checksum: Optional[str] = None
    dependencies: List[str] = field(default_factory=list)


@dataclass
class LockFile:
    """Package lock file (stxscript.lock)."""
    packages: Dict[str, LockEntry] = field(default_factory=dict)

    @classmethod
    def load(cls, path: str) -> 'LockFile':
        """Load lock file."""
        if not os.path.exists(path):
            return cls()

        with open(path, 'r') as f:
            data = json.load(f)

        packages = {}
        for name, entry in data.get("packages", {}).items():
            packages[name] = LockEntry(
                name=name,
                version=Version.parse(entry["version"]),
                source=entry.get("source", "registry"),
                checksum=entry.get("checksum"),
                dependencies=entry.get("dependencies", [])
            )

        return cls(packages=packages)

    def save(self, path: str):
        """Save lock file."""
        data = {
            "packages": {
                name: {
                    "version": str(entry.version),
                    "source": entry.source,
                    "checksum": entry.checksum,
                    "dependencies": entry.dependencies
                }
                for name, entry in self.packages.items()
            }
        }

        with open(path, 'w') as f:
            json.dump(data, f, indent=2)


# =============================================================================
# PACKAGE MANAGER
# =============================================================================

class PackageManager:
    """StxScript package manager."""

    PACKAGES_DIR = "stx_packages"
    MANIFEST_FILE = "stxscript.toml"
    LOCK_FILE = "stxscript.lock"

    def __init__(self, project_dir: str = "."):
        self.project_dir = Path(project_dir).absolute()
        self.packages_dir = self.project_dir / self.PACKAGES_DIR
        self.manifest_path = self.project_dir / self.MANIFEST_FILE
        self.lock_path = self.project_dir / self.LOCK_FILE

        self.manifest: Optional[PackageManifest] = None
        self.lock: Optional[LockFile] = None

    def init(self, name: str = None, version: str = "0.1.0"):
        """Initialize a new project."""
        if self.manifest_path.exists():
            raise RuntimeError(f"Project already initialized: {self.manifest_path}")

        project_name = name or self.project_dir.name

        manifest = PackageManifest(
            name=project_name,
            version=Version.parse(version),
            description="A StxScript project"
        )

        manifest.save(str(self.manifest_path))
        self.manifest = manifest

        print(f"Initialized new StxScript project: {project_name}")
        return manifest

    def load(self):
        """Load project manifest and lock file."""
        if not self.manifest_path.exists():
            raise RuntimeError(f"No manifest found: {self.manifest_path}")

        self.manifest = PackageManifest.load(str(self.manifest_path))
        self.lock = LockFile.load(str(self.lock_path))

    def add(self, package: str, version: str = None, dev: bool = False):
        """Add a dependency."""
        if not self.manifest:
            self.load()

        version_req = VersionRequirement.parse(version or "^0.1.0")
        dep = Dependency(name=package, version_req=version_req)

        if dev:
            self.manifest.dev_dependencies[package] = dep
        else:
            self.manifest.dependencies[package] = dep

        self.manifest.save(str(self.manifest_path))
        print(f"Added {package} {version_req.operator}{version_req.version}")

    def remove(self, package: str, dev: bool = False):
        """Remove a dependency."""
        if not self.manifest:
            self.load()

        if dev:
            if package in self.manifest.dev_dependencies:
                del self.manifest.dev_dependencies[package]
        else:
            if package in self.manifest.dependencies:
                del self.manifest.dependencies[package]

        self.manifest.save(str(self.manifest_path))

        # Remove from packages directory
        pkg_dir = self.packages_dir / package
        if pkg_dir.exists():
            shutil.rmtree(pkg_dir)

        print(f"Removed {package}")

    def install(self):
        """Install all dependencies."""
        if not self.manifest:
            self.load()

        # Create packages directory
        self.packages_dir.mkdir(exist_ok=True)

        all_deps = {**self.manifest.dependencies, **self.manifest.dev_dependencies}

        for name, dep in all_deps.items():
            self._install_dependency(dep)

        # Update lock file
        self._update_lock()
        self.lock.save(str(self.lock_path))

        print(f"Installed {len(all_deps)} packages")

    def _install_dependency(self, dep: Dependency):
        """Install a single dependency."""
        pkg_dir = self.packages_dir / dep.name

        if dep.source == "path":
            # Local path dependency
            src_path = Path(dep.path)
            if not src_path.is_absolute():
                src_path = self.project_dir / src_path

            if not src_path.exists():
                raise RuntimeError(f"Path not found: {src_path}")

            # Create symlink
            if pkg_dir.exists():
                shutil.rmtree(pkg_dir)
            pkg_dir.symlink_to(src_path)

        elif dep.source == "git":
            # Git dependency
            if pkg_dir.exists():
                shutil.rmtree(pkg_dir)

            # Clone repository
            import subprocess
            result = subprocess.run(
                ["git", "clone", "--depth", "1", dep.git_url, str(pkg_dir)],
                capture_output=True,
                text=True
            )

            if result.returncode != 0:
                raise RuntimeError(f"Failed to clone {dep.git_url}: {result.stderr}")

        else:
            # Registry dependency (placeholder for future registry)
            print(f"  Note: Registry packages not yet implemented ({dep.name})")

    def _update_lock(self):
        """Update the lock file with installed packages."""
        if not self.lock:
            self.lock = LockFile()

        for name in os.listdir(self.packages_dir):
            pkg_dir = self.packages_dir / name
            if pkg_dir.is_dir():
                # Try to read package manifest
                pkg_manifest_path = pkg_dir / self.MANIFEST_FILE
                if pkg_manifest_path.exists():
                    try:
                        pkg_manifest = PackageManifest.load(str(pkg_manifest_path))
                        self.lock.packages[name] = LockEntry(
                            name=name,
                            version=pkg_manifest.version,
                            source="path" if (pkg_dir.is_symlink()) else "git"
                        )
                    except Exception:
                        pass

    def list(self) -> List[Tuple[str, str, str]]:
        """List installed packages."""
        if not self.manifest:
            self.load()

        packages = []

        all_deps = {**self.manifest.dependencies, **self.manifest.dev_dependencies}
        for name, dep in all_deps.items():
            status = "installed" if (self.packages_dir / name).exists() else "not installed"
            packages.append((name, f"{dep.version_req.operator}{dep.version_req.version}", status))

        return packages

    def outdated(self) -> List[Tuple[str, str, str]]:
        """Check for outdated packages."""
        # Placeholder - would check registry for newer versions
        return []


# =============================================================================
# CLI INTEGRATION
# =============================================================================

def create_manifest_template() -> str:
    """Create a template manifest file content."""
    return '''[package]
name = "my-stxscript-project"
version = "0.1.0"
description = "A StxScript project"
authors = ["Your Name <your.email@example.com>"]
license = "MIT"

[dependencies]
# Add your dependencies here
# example = "^1.0.0"

[dev-dependencies]
# Add development dependencies here
'''


def init_project(project_dir: str = ".", name: str = None):
    """Initialize a new StxScript project."""
    pm = PackageManager(project_dir)
    return pm.init(name)


def install_packages(project_dir: str = "."):
    """Install all dependencies for a project."""
    pm = PackageManager(project_dir)
    pm.install()


def add_package(package: str, version: str = None, dev: bool = False, project_dir: str = "."):
    """Add a package to the project."""
    pm = PackageManager(project_dir)
    pm.add(package, version, dev)


def remove_package(package: str, dev: bool = False, project_dir: str = "."):
    """Remove a package from the project."""
    pm = PackageManager(project_dir)
    pm.remove(package, dev)
