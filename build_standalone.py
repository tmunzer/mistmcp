#!/usr/bin/env python3
"""
Build standalone executable for mistmcp evaluation

This script creates a standalone executable that evaluators can use
without needing to install Python, uv, or any dependencies.

Usage:
    cd /path/to/mistmcp
    uv run python build_standalone.py

Output:
    evaluation-package/
    ├── mistmcp-{platform}-{arch}[.exe]
    ├── README.md
    ├── claude_desktop_config.json
    └── PLATFORM-{PLATFORM}.md
"""

import json
import os
import platform
import shutil
import subprocess  # nosec B404
import sys
from datetime import datetime
from pathlib import Path

# Project paths
PROJECT_ROOT = Path(__file__).parent
BUILD_DIR = Path(__file__).parent
SRC_DIR = PROJECT_ROOT / "src"
TOOLS_JSON_PATH = SRC_DIR / "mistmcp" / "tools.json"

# Add src to Python path for imports
sys.path.insert(0, str(SRC_DIR))


def safe_print(message, file=None):
    """Print message with Windows-compatible encoding handling"""
    try:
        print(message, file=file)
    except UnicodeEncodeError:
        # Fallback to ASCII-safe version
        ascii_message = message.encode("ascii", "replace").decode("ascii")
        print(ascii_message, file=file)


def print_banner() -> None:
    """Print build banner with Windows-compatible characters"""
    safe_print("*** Mist MCP Standalone Builder ***")
    safe_print("=" * 50)
    safe_print(f"Project: {PROJECT_ROOT}")
    safe_print(f"Platform: {platform.system()} {platform.machine()}")
    safe_print(f"Python: {sys.version.split()[0]}")
    safe_print("")


def check_prerequisites() -> bool:
    """Check that required tools are available"""
    safe_print("Checking prerequisites...")

    # Check if we're in a virtual environment with PyInstaller
    try:
        result = subprocess.run(
            [sys.executable, "-m", "PyInstaller", "--version"],
            capture_output=True,
            text=True,
            check=True,
        )  # nosec B603
        safe_print(f"[OK] PyInstaller: {result.stdout.strip()}")
    except (subprocess.CalledProcessError, FileNotFoundError):
        safe_print("[ERROR] PyInstaller not found!")
        safe_print("Install with: uv add --dev pyinstaller")
        return False

    # Check if we can import mistmcp
    import importlib.util

    if importlib.util.find_spec("mistmcp") is not None:
        safe_print("[OK] mistmcp importable")
    else:
        safe_print("[ERROR] Cannot import mistmcp: module not found")
        return False

    return True


def create_tools_json_if_needed() -> bool:
    """Create tools.json only if it doesn't exist"""
    if TOOLS_JSON_PATH.exists():
        safe_print(f"[OK] Found existing {TOOLS_JSON_PATH}")
        return True

    try:
        safe_print("Creating tools.json for PyInstaller...")
        from mistmcp.tool_helper import TOOLS

        with open(TOOLS_JSON_PATH, "w", encoding="utf-8") as f:
            json.dump(TOOLS, f, indent=2)

        safe_print(f"[OK] Created {TOOLS_JSON_PATH}")
        safe_print(f"Contains {len(TOOLS)} tool categories")
        return True

    except ImportError as e:
        safe_print(f"[ERROR] Could not import TOOLS from tool_helper: {e}")
        return False
    except Exception as e:
        safe_print(f"[ERROR] Error creating tools.json: {e}")
        return False


def get_executable_name():
    """Generate platform-specific executable name"""
    system = platform.system().lower()
    machine = platform.machine().lower()

    # Normalize machine names
    if machine in ("x86_64", "amd64"):
        machine = "x64"
    elif machine in ("aarch64", "arm64"):
        machine = "arm64"
    elif machine.startswith("arm"):
        machine = "arm"

    name = f"mistmcp-{system}-{machine}"

    if system == "windows":
        name += ".exe"

    return name


def get_platform_specific_config():
    """Get platform-specific PyInstaller configuration"""
    system = platform.system().lower()

    config = {
        "hidden_imports": [
            "mistapi",
            "fastmcp",
            "fastmcp.server",
            "fastmcp.server.dependencies",
            "fastmcp.exceptions",
            "pydantic",
            "starlette",
            "starlette.requests",
            "uvloop",
            "asyncio",
            "httpx",
            "uuid",
            "enum",
            "typing",
            "dataclasses",
            "datetime",
            "threading",
            "pathlib",
            "argparse",
            "os",
            "sys",
            "json",
            "yaml",
        ],
        "excludes": [
            "tkinter",
            "matplotlib",
            "PIL",
            "numpy",
            "scipy",
            "pandas",
            "jupyter",
            "IPython",
            "notebook",
            "qtconsole",
            "spyder",
            "pyqt5",
            "pyqt6",
            "pyside2",
            "pyside6",
            "wx",
        ],
        "additional_args": [],
    }

    if system == "windows":
        config["additional_args"].extend(
            [
                "--console",  # Keep console window for debugging
                "--icon=NONE",  # Avoid icon issues
            ]
        )

    elif system == "darwin":
        config["additional_args"].extend(
            [
                "--osx-bundle-identifier=com.juniper.mistmcp",
            ]
        )

    elif system == "linux":
        config["additional_args"].extend(
            [
                "--strip",  # Strip debug symbols to reduce size
            ]
        )

    return config


def discover_tool_modules():
    """Discover all tool modules for PyInstaller hidden imports"""
    modules = ["mistmcp.tools"]
    tools_dir = SRC_DIR / "mistmcp" / "tools"

    if not tools_dir.exists():
        safe_print(f"[WARNING] Tools directory not found: {tools_dir}")
        return modules

    for category_dir in tools_dir.iterdir():
        if category_dir.is_dir() and not category_dir.name.startswith("__"):
            # Add category module
            modules.append(f"mistmcp.tools.{category_dir.name}")

            # Add individual tool modules
            for tool_file in category_dir.glob("*.py"):
                if not tool_file.name.startswith("__"):
                    modules.append(
                        f"mistmcp.tools.{category_dir.name}.{tool_file.stem}"
                    )

    safe_print(f"Discovered {len(modules)} tool modules")
    return modules


def test_executable(exe_path) -> bool:
    """Test the built executable"""
    safe_print("Testing executable...")

    try:
        # Test help command
        result = subprocess.run(
            [str(exe_path), "--help"], capture_output=True, text=True, timeout=30
        )  # nosec B603

        if result.returncode == 0:
            safe_print("[OK] Help test passed")
            return True
        else:
            safe_print(f"[WARNING] Help test failed (exit code: {result.returncode})")
            if result.stderr:
                safe_print(f"Error: {result.stderr[:200]}...")
            return False

    except subprocess.TimeoutExpired:
        safe_print("[WARNING] Executable test timed out")
        return False
    except Exception as e:
        safe_print(f"[WARNING] Executable test failed: {e}")
        return False


def build_executable():
    """Build the standalone executable using PyInstaller with platform-specific optimizations"""
    safe_print("Building standalone executable...")

    exe_name = get_executable_name()
    main_file = SRC_DIR / "mistmcp" / "__main__.py"

    if not main_file.exists():
        safe_print(f"[ERROR] Main file not found: {main_file}")
        return None

    # Clean previous builds
    dist_dir = PROJECT_ROOT / "dist"
    build_dir = PROJECT_ROOT / "build"
    spec_file = PROJECT_ROOT / "mistmcp.spec"

    for path in [dist_dir, build_dir, spec_file]:
        if path.exists():
            if path.is_dir():
                shutil.rmtree(path)
            else:
                path.unlink()

    # Get platform-specific configuration
    platform_config = get_platform_specific_config()

    # Build PyInstaller command
    cmd = [
        sys.executable,
        "-m",
        "PyInstaller",
        "--onefile",
        "--name",
        exe_name.replace(".exe", ""),  # PyInstaller adds .exe automatically on Windows
        "--console",  # Keep console for debugging
        "--noconfirm",  # Overwrite without asking
        "--clean",  # Clean PyInstaller cache
        "--optimize",
        "2",  # Optimize bytecode
    ]

    # Add platform-specific arguments
    cmd.extend(platform_config.get("additional_args", []))

    # Add excludes to reduce size
    for exclude in platform_config.get("excludes", []):
        cmd.extend(["--exclude-module", exclude])

    # Add tools.json if it exists
    if TOOLS_JSON_PATH.exists():
        cmd.extend(["--add-data", f"{TOOLS_JSON_PATH}:mistmcp"])
        safe_print("Including tools.json in build")

    # Add all hidden imports
    for module in platform_config["hidden_imports"]:
        cmd.extend(["--hidden-import", module])

    # Add discovered tool modules
    tool_modules = discover_tool_modules()
    for module in tool_modules:
        cmd.extend(["--hidden-import", module])

    # Add main file
    cmd.append(str(main_file))

    safe_print(f"Running PyInstaller for {platform.system()} {platform.machine()}...")
    safe_print(f"Command: {' '.join(cmd[:8])}... (truncated)")

    try:
        # Change to project root for build
        original_cwd = os.getcwd()
        os.chdir(PROJECT_ROOT)

        subprocess.run(
            cmd,
            check=True,
            capture_output=True,
            text=True,
            timeout=600,  # 10 minute timeout
        )  # nosec B603

        # Find the executable
        exe_path = dist_dir / exe_name

        if exe_path.exists():
            size_mb = exe_path.stat().st_size / (1024 * 1024)
            safe_print("[OK] Build successful!")
            safe_print(f"Executable: {exe_path}")
            safe_print(f"Size: {size_mb:.1f} MB")

            # Test the executable
            safe_print("Testing executable...")
            if test_executable(exe_path):
                safe_print("[OK] Executable test passed")
            else:
                safe_print("[WARNING] Executable test failed but file exists")

            return exe_path
        else:
            safe_print(f"[ERROR] Executable not found at {exe_path}")
            return None

    except subprocess.CalledProcessError as e:
        safe_print("[ERROR] PyInstaller build failed!")
        safe_print(f"Exit code: {e.returncode}")
        if e.stdout:
            safe_print(f"stdout: {e.stdout[-500:]}")  # Last 500 chars
        if e.stderr:
            safe_print(f"stderr: {e.stderr[-500:]}")  # Last 500 chars
        return None
    except subprocess.TimeoutExpired:
        safe_print("[ERROR] Build timed out after 10 minutes")
        return None
    finally:
        os.chdir(original_cwd)


def create_platform_readme(package_dir, exe_name) -> None:
    """Create platform-specific README"""
    system = platform.system().lower()

    platform_notes = {
        "windows": f"""
# Platform-Specific Notes: Windows

## Security Settings
Windows may show security warnings for unsigned executables:
1. Click "More info" then "Run anyway" if Windows Defender blocks execution
2. Consider adding the executable to Windows Defender exclusions
3. Some antivirus software may flag PyInstaller executables as suspicious

## Running the Executable
```cmd
# In Command Prompt or PowerShell
{exe_name} --help
```

## Claude Desktop Configuration
Use backslashes or forward slashes in paths:
```json
{{
    "command": "C:/absolute/path/to/{exe_name}"
}}
```

## Troubleshooting
- Ensure you're using the absolute path in Claude Desktop configuration
- If the executable doesn't run, try running from Command Prompt to see error messages
- Check that all required DLLs are available (the executable should be self-contained)
        """,
        "darwin": f"""
# Platform-Specific Notes: macOS

## Security Settings
macOS may prevent execution of unsigned applications:

```bash
# Make executable
chmod +x {exe_name}

# Remove quarantine attribute if needed
xattr -d com.apple.quarantine {exe_name}
```

## Gatekeeper Issues
If you see "cannot be opened because it is from an unidentified developer":
1. Go to System Preferences → Security & Privacy → General
2. Click "Allow Anyway" next to the blocked app message
3. Or use: `sudo spctl --master-disable` (not recommended for security)

## Running the Executable
```bash
./{exe_name} --help
```

## Claude Desktop Configuration
Use absolute paths:
```json
{{
    "command": "/absolute/path/to/{exe_name}"
}}
```

## Architecture Notes
- ARM64 version: For Apple Silicon Macs (M1, M2, M3)
- x64 version: For Intel Macs
        """,
        "linux": f"""
# Platform-Specific Notes: Linux

## Making Executable
```bash
chmod +x {exe_name}
```

## Dependencies
The executable should be self-contained, but you may need system libraries:

```bash
# Debian/Ubuntu
sudo apt-get install libc6-dev libffi-dev

# RHEL/CentOS/Fedora
sudo dnf install glibc-devel libffi-devel

# Alpine Linux
sudo apk add glibc libffi
```

## Running the Executable
```bash
./{exe_name} --help
```

## Claude Desktop Configuration
```json
{{
    "command": "/absolute/path/to/{exe_name}"
}}
```

## Distribution Compatibility
- Built on Ubuntu 22.04
- Should work on most modern Linux distributions
- May require additional libraries on minimal distributions

## Troubleshooting
- Check executable permissions: `ls -la {exe_name}`
- Verify shared library dependencies: `ldd {exe_name}`
- Run from terminal to see error messages
        """,
    }

    content = platform_notes.get(
        system,
        f"# Platform Notes for {system}\n\nNo specific notes available for this platform.",
    )

    with open(
        package_dir / f"PLATFORM-{system.upper()}.md", "w", encoding="utf-8"
    ) as f:
        f.write(content)

    safe_print(f"Created platform-specific notes: PLATFORM-{system.upper()}.md")


def create_evaluation_package(exe_path):
    """Create evaluation package with documentation and examples"""
    safe_print("Creating evaluation package...")

    package_dir = PROJECT_ROOT / "evaluation-package"

    # Clean and create package directory
    if package_dir.exists():
        shutil.rmtree(package_dir)
    package_dir.mkdir()

    # Copy executable
    target_exe = package_dir / exe_path.name
    shutil.copy2(exe_path, target_exe)

    # Make executable on Unix systems
    if platform.system() != "Windows":
        os.chmod(target_exe, 0o755)  # nosec B103

    # Get current platform info
    current_platform = f"{platform.system()} {platform.machine()}"
    build_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Create comprehensive README
    readme_content = f"""# *** Mist MCP Evaluation Package ***

## What This Is
AI-powered assistant for managing Juniper Mist networks through Claude Desktop.
Provides natural language interface to your Mist network infrastructure.

## Quick Start (5 minutes)

### 1. Get Your Mist API Credentials

**API Token:**
1. Log into your Mist Dashboard
2. Go to Organization → Settings → API Tokens
3. Create a new token with appropriate permissions

**API Host:**
- US: `api.mist.com`
- EU: `api.eu.mist.com`
- APAC: `api.ap.mist.com`

### 2. Test the Executable

```bash
# Test basic functionality
export MIST_APITOKEN="your-api-token-here"
export MIST_HOST="api.mist.com"
./{exe_path.name} --mode managed --debug

# You should see "Starting Mist MCP Server"
# Press Ctrl+C to stop
```

### 3. Configure Claude Desktop

**Config File Location:**
- **Mac/Linux**: `~/.claude_desktop/claude_desktop_config.json`
- **Windows**: `%APPDATA%\\Claude\\claude_desktop_config.json`

**Add this configuration:**
```json
{{
    "mcpServers": {{
        "mist-network": {{
            "command": "/absolute/path/to/{exe_path.name}",
            "args": ["--mode", "managed"],
            "env": {{
                "MIST_APITOKEN": "your-api-token-here",
                "MIST_HOST": "api.mist.com"
            }}
        }}
    }}
}}
```

**WARNING:** Use the **absolute path** to the executable!

### 4. Restart Claude Desktop and Test

Ask Claude: **"Show me my Mist organization information"**

## What You Can Ask Claude

### Organization & Sites
- "Show me my organization details"
- "List all my sites"
- "What's the status of my sites?"

### Device Management
- "What access points do I have?"
- "Show me offline devices"
- "List devices with issues"
- "Find access points by site"

### Client Monitoring
- "Show me connected clients"
- "Find clients with connection problems"
- "What devices are having WiFi issues?"

### Network Health
- "What alarms are currently active?"
- "Show me recent network events"
- "Find high-utilization sites"
- "Check network performance"

### Statistics & Reports
- "Show me network usage statistics"
- "What's my license usage?"
- "Give me a network health summary"
- "Show me top applications by usage"

### Troubleshooting
- "Help me troubleshoot connectivity issues"
- "Run network diagnostics"
- "Show me device configuration issues"

## Advanced Features

### Tool Categories
The system organizes tools into categories for better performance:

```
Ask Claude: "What tool categories are available?"
Then: "Enable device management tools"
```

Available categories include:
- **orgs** - Organization information
- **sites** - Site management
- **devices** - Device monitoring
- **clients** - Client tracking
- **sles** - Service Level Expectations
- **stats** - Statistics and analytics

### Loading Modes
```bash
# Managed mode (default) - tools loaded on demand
./{exe_path.name} --mode managed

# All tools mode - everything loaded at startup
./{exe_path.name} --mode all

# Debug mode for troubleshooting
./{exe_path.name} --mode managed --debug
```

## Troubleshooting

### [ERROR] "Command not found"
- Verify the absolute path to the executable is correct
- On Mac/Linux: Make file executable with `chmod +x {exe_path.name}`

### [ERROR] "API connection failed"
- Check your `MIST_APITOKEN` is correct and has proper permissions
- Verify `MIST_HOST` matches your region (api.mist.com, api.eu.mist.com, etc.)
- Test API manually: `curl -H "Authorization: Token YOUR_TOKEN" https://YOUR_HOST/api/v1/self`

### [ERROR] Claude doesn't see the server
- Restart Claude Desktop completely (quit and reopen)
- Validate JSON syntax in `claude_desktop_config.json`
- Check Claude Desktop logs for error messages
- Ensure no trailing commas in JSON config

### [ERROR] "Tool not available" errors
- The system uses dynamic tool loading for performance
- Ask Claude: "Enable the tools I need for device management"
- Or use `--mode all` to load everything at startup

### Debug Mode
```bash
# Run with debug output
export MISTMCP_DEBUG=true
./{exe_path.name} --mode managed --debug
```

## Example Conversation

```
You: "Show me my organization info and list my sites"

Claude: I'll help you get your Mist organization information and list your sites.

[Claude calls getSelf tool]
Your organization "ACME Corp" (ID: abc123...) is located in the US region...

[Claude calls searchOrgSites tool]
You have 5 sites configured:
1. Headquarters (New York) - 45 APs, Status: Healthy
2. Branch Office (Chicago) - 12 APs, Status: 2 offline
3. Warehouse (Dallas) - 8 APs, Status: Healthy
...

You: "What's wrong with the Chicago office?"

Claude: Let me check the Chicago office devices for you.
[Claude investigates the offline APs and provides troubleshooting steps]
```

## Support & Feedback

This is an evaluation package. For questions or feedback:
- Check the troubleshooting section above
- Test with simple queries first ("Show me my organization")
- Use debug mode for detailed error information

---
**Built on:** {current_platform}
**Version:** mistmcp evaluation build
**Date:** {build_time}
"""

    with open(package_dir / "README.md", "w", encoding="utf-8") as f:
        f.write(readme_content)

    # Create example Claude Desktop config
    config_example = {
        "mcpServers": {
            "mist-network": {
                "command": f"/absolute/path/to/{exe_path.name}",
                "args": ["--mode", "managed"],
                "env": {
                    "MIST_APITOKEN": "your-api-token-here",
                    "MIST_HOST": "api.mist.com",
                },
            }
        }
    }

    with open(package_dir / "claude_desktop_config.json", "w", encoding="utf-8") as f:
        json.dump(config_example, f, indent=2)

    # Create a quick test script
    if platform.system() == "Windows":
        test_script_content = f"""@echo off
REM Quick test script for the Mist MCP executable

echo [INFO] Testing Mist MCP Executable
echo ==============================

if "%MIST_APITOKEN%"=="" (
    echo [ERROR] Please set MIST_APITOKEN environment variable
    echo    set MIST_APITOKEN=your-token-here
    exit /b 1
)

if "%MIST_HOST%"=="" (
    echo [ERROR] Please set MIST_HOST environment variable
    echo    set MIST_HOST=api.mist.com
    exit /b 1
)

echo [OK] Environment variables set
echo [INFO] Testing executable...

timeout 10 {exe_path.name} --help
if %errorlevel% equ 0 (
    echo [OK] Executable test passed!
    echo [INFO] Now configure Claude Desktop with the provided config
) else (
    echo [ERROR] Executable test failed
    exit /b 1
)
"""
        test_script_path = package_dir / "test.bat"
    else:
        test_script_content = f"""#!/bin/bash
# Quick test script for the Mist MCP executable

echo "[INFO] Testing Mist MCP Executable"
echo "=============================="

if [ -z "$MIST_APITOKEN" ]; then
    echo "[ERROR] Please set MIST_APITOKEN environment variable"
    echo "   export MIST_APITOKEN='your-token-here'"
    exit 1
fi

if [ -z "$MIST_HOST" ]; then
    echo "[ERROR] Please set MIST_HOST environment variable"
    echo "   export MIST_HOST='api.mist.com'"
    exit 1
fi

echo "[OK] Environment variables set"
echo "[INFO] Testing executable..."

timeout 10 ./{exe_path.name} --help
if [ $? -eq 0 ]; then
    echo "[OK] Executable test passed!"
    echo "[INFO] Now configure Claude Desktop with the provided config"
else
    echo "[ERROR] Executable test failed"
    exit 1
fi
"""
        test_script_path = package_dir / "test.sh"

    with open(test_script_path, "w", encoding="utf-8") as f:
        f.write(test_script_content)

    if platform.system() != "Windows":
        os.chmod(test_script_path, 0o755)  # nosec B103

    # Create platform-specific notes
    create_platform_readme(package_dir, exe_path.name)

    safe_print(f"[OK] Evaluation package created: {package_dir}")
    safe_print("Package contents:")
    safe_print(f"   * {exe_path.name} - Standalone executable")
    safe_print("   * README.md - Complete setup guide")
    safe_print("   * claude_desktop_config.json - Example config")
    safe_print(f"   * {test_script_path.name} - Quick test script")
    safe_print(
        f"   * PLATFORM-{platform.system().upper()}.md - Platform-specific notes"
    )

    return package_dir


def cleanup_build_artifacts() -> None:
    """Clean up temporary build files"""
    safe_print("Cleaning up build artifacts...")

    artifacts = [
        PROJECT_ROOT / "build",
        PROJECT_ROOT / "mistmcp.spec",
        TOOLS_JSON_PATH,  # Remove generated tools.json
    ]

    for artifact in artifacts:
        if artifact.exists():
            if artifact.is_dir():
                shutil.rmtree(artifact)
            else:
                artifact.unlink()
            safe_print(f"Removed {artifact}")


def main() -> int:
    """Main build function"""
    print_banner()

    # Change to project root
    original_cwd = os.getcwd()
    os.chdir(PROJECT_ROOT)

    try:
        # Check prerequisites
        if not check_prerequisites():
            return 1

        # Create tools.json if needed
        if not create_tools_json_if_needed():
            return 1

        # Build executable
        exe_path = build_executable()
        if not exe_path:
            return 1

        # Create evaluation package
        package_dir = create_evaluation_package(exe_path)

        # Clean up temporary files
        cleanup_build_artifacts()

        # Success message
        safe_print("")
        safe_print("*** BUILD SUCCESSFUL! ***")
        safe_print("=" * 50)
        safe_print(f"Evaluation package: {package_dir}")
        safe_print("Share the entire folder with evaluators")
        safe_print("They should start with README.md")
        safe_print("")
        safe_print("Next steps for evaluators:")
        safe_print("1. Extract the package")
        safe_print("2. Follow README.md instructions")
        safe_print("3. Test with: 'Show me my organization info'")

        return 0

    except KeyboardInterrupt:
        safe_print("")
        safe_print("[WARNING] Build interrupted by user")
        return 1
    except Exception as e:
        safe_print("")
        safe_print(f"[ERROR] Unexpected error: {e}")
        import traceback

        traceback.print_exc()
        return 1
    finally:
        os.chdir(original_cwd)


if __name__ == "__main__":
    sys.exit(main())
