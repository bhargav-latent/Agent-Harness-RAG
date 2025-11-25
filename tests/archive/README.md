# Archived Tests

This folder contains test scripts used during Deep Agents FilesystemBackend debugging and Windows path bug investigation. These tests are preserved for reference.

## Test Scripts

### test_agent_access.py
**Purpose:** Test Deep Agents filesystem tool access patterns
**Status:** Archived - used during initial FilesystemBackend configuration

### test_read_with_paths.py
**Purpose:** Test read_file tool with various path formats
**Status:** Archived - used to diagnose Windows path bug (GitHub Issue #340)

### test_tool_outputs.py
**Purpose:** Test tool output handling and formatting
**Status:** Archived - validated tool output behavior

### test_virtual_paths.py
**Purpose:** Test FilesystemBackend virtual mode path translation
**Status:** Archived - confirmed virtual_mode=True requirement

## Related Documentation

- [FILESYSTEM_BACKEND_FIX.md](../../FILESYSTEM_BACKEND_FIX.md) - FilesystemBackend configuration guide
- [WINDOWS_PATH_BUG.md](../../WINDOWS_PATH_BUG.md) - Windows path separator bug documentation
- [WSL_DEPLOYMENT.md](../../WSL_DEPLOYMENT.md) - Recommended WSL/Linux deployment guide

## Key Findings

These tests confirmed:
1. FilesystemBackend requires `virtual_mode=True` (not optional)
2. Windows has path separator bug returning malformed paths (`/\file.md`)
3. Agent-level path cleaning workaround implemented
4. WSL/Linux deployment recommended for production
