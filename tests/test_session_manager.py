"""Tests for mistmcp session manager module"""

from datetime import datetime, timedelta
from unittest.mock import Mock, patch

from mistmcp.session_manager import ClientSession, SessionManager, get_current_session


class TestClientSession:
    """Test ClientSession dataclass"""

    def test_session_creation(self):
        """Test creating a new session"""
        session = ClientSession(session_id="test_session")
        assert session.session_id == "test_session"
        assert isinstance(session.enabled_tools, set)
        assert isinstance(session.enabled_categories, set)
        assert isinstance(session.created_at, datetime)
        assert isinstance(session.last_activity, datetime)
        assert isinstance(session.client_info, dict)
        assert isinstance(session.mist_api_config, dict)

    def test_session_touch(self):
        """Test updating session activity"""
        session = ClientSession(session_id="test_session")
        original_time = session.last_activity

        # Mock datetime.now to return a different time
        with patch("mistmcp.session_manager.datetime") as mock_datetime:
            new_time = original_time + timedelta(minutes=5)
            mock_datetime.now.return_value = new_time

            session.touch()
            assert session.last_activity == new_time

    def test_session_expiry(self):
        """Test session expiry logic"""
        session = ClientSession(session_id="test_session")

        # Fresh session should not be expired
        assert not session.is_expired(timeout_minutes=60)

        # Mock old activity time
        old_time = datetime.now() - timedelta(minutes=120)
        session.last_activity = old_time

        assert session.is_expired(timeout_minutes=60)
        assert not session.is_expired(timeout_minutes=180)


class TestSessionManager:
    """Test SessionManager class"""

    def test_session_manager_creation(self):
        """Test creating a new session manager"""
        manager = SessionManager()
        assert manager.session_timeout_minutes == 60
        assert isinstance(manager.sessions, dict)
        assert manager.default_enabled_tools == {"getSelf", "manageMcpTools"}

    def test_session_manager_custom_timeout(self):
        """Test session manager with custom timeout"""
        manager = SessionManager(session_timeout_minutes=30)
        assert manager.session_timeout_minutes == 30

    @patch("mistmcp.session_manager.get_http_request")
    def test_get_session_req_info_with_request(self, mock_get_request):
        """Test getting session info from HTTP request"""
        # Mock HTTP request
        mock_request = Mock()
        mock_request.client = Mock()
        mock_request.client.host = "192.168.1.100"
        mock_request.client.port = 8080
        mock_get_request.return_value = mock_request

        manager = SessionManager()
        ip, port = manager.get_session_req_info()

        assert ip == "192.168.1.100"
        assert port == "8080"

    @patch("mistmcp.session_manager.get_http_request")
    def test_get_session_req_info_no_client(self, mock_get_request):
        """Test getting session info when no client info available"""
        # Mock HTTP request without client
        mock_request = Mock()
        mock_request.client = None
        mock_get_request.return_value = mock_request

        manager = SessionManager()
        ip, port = manager.get_session_req_info()

        assert ip == "unknown"
        assert port == "unknown"

    @patch("mistmcp.session_manager.get_http_request")
    def test_get_or_create_session_new(self, mock_get_request):
        """Test creating a new session"""
        # Mock HTTP request
        mock_request = Mock()
        mock_request.client = Mock()
        mock_request.client.host = "127.0.0.1"
        mock_request.client.port = 8080
        mock_get_request.return_value = mock_request

        manager = SessionManager()
        session = manager.get_or_create_session()

        assert isinstance(session, ClientSession)
        assert session.enabled_tools == {"getSelf", "manageMcpTools"}
        assert len(manager.sessions) == 1

    @patch("mistmcp.session_manager.get_http_request")
    def test_get_or_create_session_existing(self, mock_get_request):
        """Test getting an existing session"""
        # Mock HTTP request
        mock_request = Mock()
        mock_request.client = Mock()
        mock_request.client.host = "127.0.0.1"
        mock_request.client.port = 8080
        mock_get_request.return_value = mock_request

        manager = SessionManager()

        # Create first session
        session1 = manager.get_or_create_session()

        # Get same session
        session2 = manager.get_or_create_session()

        assert session1.session_id == session2.session_id
        assert len(manager.sessions) == 1

    @patch("mistmcp.session_manager.get_http_request")
    def test_update_session_tools(self, mock_get_request):
        """Test updating session tools"""
        # Mock HTTP request
        mock_request = Mock()
        mock_request.client = Mock()
        mock_request.client.host = "127.0.0.1"
        mock_request.client.port = 8080
        mock_get_request.return_value = mock_request

        manager = SessionManager()

        new_tools = {"getSelf", "manageMcpTools", "listOrgSites"}
        new_categories = {"orgs", "sites"}

        session = manager.update_session_tools(new_tools, new_categories)

        assert session.enabled_tools == new_tools
        assert session.enabled_categories == new_categories

    @patch("mistmcp.session_manager.get_http_request")
    def test_is_tool_enabled_for_session(self, mock_get_request):
        """Test checking if tool is enabled for session"""
        # Mock HTTP request
        mock_request = Mock()
        mock_request.client = Mock()
        mock_request.client.host = "127.0.0.1"
        mock_request.client.port = 8080
        mock_get_request.return_value = mock_request

        manager = SessionManager()

        # Tool should be enabled by default
        assert manager.is_tool_enabled_for_session("getSelf")
        assert manager.is_tool_enabled_for_session("manageMcpTools")

        # Tool should not be enabled by default
        assert not manager.is_tool_enabled_for_session("listOrgSites")

        # Enable tool and test again
        manager.update_session_tools(
            {"getSelf", "manageMcpTools", "listOrgSites"}, {"orgs"}
        )
        assert manager.is_tool_enabled_for_session("listOrgSites")

    def test_get_all_sessions(self):
        """Test getting all sessions"""
        manager = SessionManager()

        # Initially empty
        sessions = manager.get_all_sessions()
        assert len(sessions) == 0

        # Add some mock sessions
        session1 = ClientSession(session_id="session1")
        session2 = ClientSession(session_id="session2")
        manager.sessions["session1"] = session1
        manager.sessions["session2"] = session2

        sessions = manager.get_all_sessions()
        assert len(sessions) == 2
        assert "session1" in sessions
        assert "session2" in sessions

    def test_remove_session(self):
        """Test removing a session"""
        manager = SessionManager()

        # Add a session
        session = ClientSession(session_id="test_session")
        manager.sessions["test_session"] = session

        # Remove it
        result = manager.remove_session("test_session")
        assert result is True
        assert "test_session" not in manager.sessions

        # Try to remove non-existent session
        result = manager.remove_session("non_existent")
        assert result is False


@patch("mistmcp.session_manager.session_manager")
def test_get_current_session(mock_session_manager):
    """Test get_current_session function"""
    mock_session = ClientSession(session_id="test_session")
    mock_session_manager.get_or_create_session.return_value = mock_session

    session = get_current_session()

    assert session == mock_session
    mock_session_manager.get_or_create_session.assert_called_once()
