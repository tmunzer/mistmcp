"""
--------------------------------------------------------------------------------
-------------------------------- Mist MCP SERVER -------------------------------

    Written by: Thomas Munzer (tmunzer@juniper.net)
    Github    : https://github.com/tmunzer/mistmcp

    This package is licensed under the MIT License.

--------------------------------------------------------------------------------
"""

import asyncio
import hashlib
import threading
from asyncio import Task
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Any, Dict, Set

from fastmcp.exceptions import FastMCPError, NotFoundError
from fastmcp.server.dependencies import get_http_request
from starlette.requests import Request

from mistmcp.config import config


@dataclass
class ClientSession:
    """Represents a single MCP client session"""

    session_id: str
    tools_mode: str
    client_info: Dict[str, Any] = field(default_factory=dict)
    enabled_tools: Set[str] = field(default_factory=set)
    enabled_categories: Set[str] = field(default_factory=set)
    created_at: datetime = field(default_factory=datetime.now)
    last_activity: datetime = field(default_factory=datetime.now)
    mist_api_config: Dict[str, Any] = field(
        default_factory=dict
    )  # Per-client Mist API settings

    def touch(self) -> None:
        """Update last activity timestamp"""
        self.last_activity = datetime.now()

    def is_expired(self, timeout_minutes: int = 60) -> bool:
        """Check if session has expired"""
        return datetime.now() - self.last_activity > timedelta(minutes=timeout_minutes)


class SessionManager:
    """Manages multiple MCP client sessions with per-client tool configurations"""

    def __init__(self, session_timeout_minutes: int = 60) -> None:
        self.sessions: Dict[str, ClientSession] = {}
        self.session_timeout_minutes = session_timeout_minutes
        self._lock = threading.RLock()

        # Default tools that are enabled for all new sessions
        self.default_enabled_tools = {"getSelf", "manageMcpTools"}

        # Cleanup task will be started when needed
        self._cleanup_task: Task[None] | None = None
        self._cleanup_started = False

    def _start_cleanup_task(self) -> None:
        """Start the background cleanup task if not already started"""
        if not self._cleanup_started:
            try:
                self._cleanup_task = asyncio.create_task(
                    self._cleanup_expired_sessions()
                )
                self._cleanup_started = True
            except RuntimeError:
                # No event loop running yet - will start later when needed
                pass

    async def _cleanup_expired_sessions(self) -> None:
        """Background task to clean up expired sessions"""
        while True:
            try:
                await asyncio.sleep(300)  # Run every 5 minutes
                with self._lock:
                    expired_sessions = [
                        session_id
                        for session_id, session in self.sessions.items()
                        if session.is_expired(self.session_timeout_minutes)
                    ]

                    for session_id in expired_sessions:
                        del self.sessions[session_id]
                        print(f"Cleaned up expired session: {session_id}")

            except asyncio.CancelledError:
                break
            except Exception as e:
                print(f"Error in session cleanup: {e}")

    def get_session_req_info(self, default_mode: str) -> tuple[str, str, str]:
        """Get the IP and port of the current HTTP request client"""
        if config.transport_mode == "stdio":
            # In stdio mode, we don't have HTTP request context
            # Use a default session for stdio clients
            return "stdio", "stdio", default_mode

        # Get the current HTTP request context
        # This is only available in HTTP mode, so we can safely call it
        # without checking if req is None or req.client is None
        # This will raise an error if called outside of an HTTP request context
        # which is expected behavior
        try:
            req: Request = get_http_request()
            # In HTTP mode, we can get the request context
            ip = req.client.host if req.client else "unknown"
            port = str(req.client.port) if req.client else "unknown"
            tools_mode = req.query_params.get(
                "mode", default_mode
            )  # Default to HTTP mode
            return ip, port, tools_mode
        except NotFoundError:
            # If we can't get the request context, fallback to default values
            raise FastMCPError(
                "HTTP request context not found. Are you using HTTP transport?"
            ) from None

    def get_or_create_session(self, default_mode: str = "managed") -> ClientSession:
        """Get existing session or create a new one"""
        ip, port, tools_mode = self.get_session_req_info(default_mode)
        session_info = f"session_{ip}:{port}|tools_mode={tools_mode}"
        h = hashlib.new("sha256")
        h.update(session_info.encode("utf-8"))
        session_id = h.hexdigest()

        with self._lock:
            if session_id not in self.sessions:
                # Create new session with default tools enabled
                session = ClientSession(
                    session_id=session_id,
                    tools_mode=tools_mode,
                    enabled_tools=self.default_enabled_tools.copy(),
                )
                self.sessions[session_id] = session
                print(f"Created new session: {session_id}")

                # Try to start cleanup task if not already started
                if not self._cleanup_started:
                    self._start_cleanup_task()
            else:
                session = self.sessions[session_id]
                session.touch()

            return session

    def update_session_tools(
        self,
        enabled_tools: Set[str],
        enabled_categories: Set[str],
    ) -> ClientSession:
        """Update the enabled tools and categories for a session"""
        session = self.get_or_create_session()

        with self._lock:
            session.enabled_tools = enabled_tools.copy()
            session.enabled_categories = enabled_categories.copy()
            session.touch()

        return session

    def is_tool_enabled_for_session(self, tool_name: str) -> bool:
        """Check if a tool is enabled for the current session"""
        session = self.get_or_create_session()
        if not session:
            # If no session exists, check against default tools
            return tool_name in self.default_enabled_tools

        return tool_name in session.enabled_tools

    def get_enabled_tools_for_session(self) -> Set[str]:
        """Get all enabled tools for the current session"""
        session = self.get_or_create_session()
        if not session:
            return self.default_enabled_tools.copy()

        return session.enabled_tools.copy()

    def get_all_sessions(self) -> Dict[str, ClientSession]:
        """Get all active sessions (for debugging/monitoring)"""
        with self._lock:
            return self.sessions.copy()

    def remove_session(self, session_id: str) -> bool:
        """Remove a specific session"""
        with self._lock:
            if session_id in self.sessions:
                del self.sessions[session_id]
                return True
            return False

    def shutdown(self) -> None:
        """Shutdown the session manager"""
        if self._cleanup_task and not self._cleanup_task.done():
            self._cleanup_task.cancel()


# Global session manager instance
session_manager = SessionManager()


def get_current_session(default_mode: str) -> ClientSession:
    """Get the current client session"""
    return session_manager.get_or_create_session(default_mode)


def is_tool_enabled_for_current_session(tool_name: str) -> bool:
    """Check if a tool is enabled for the current session"""
    return session_manager.is_tool_enabled_for_session(tool_name)


def get_enabled_tools_for_current_session() -> Set[str]:
    """Get enabled tools for the current session"""
    return session_manager.get_enabled_tools_for_session()
