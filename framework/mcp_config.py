import os
import sys
from autogen_ext.tools.mcp import StdioServerParams, McpWorkbench


class McpConfig:
    """MCP Configuration for Windows and cross-platform compatibility"""
    
    # Default configurations (can be overridden via environment variables)
    MYSQL_CONFIG = {
        "host": os.environ.get("MYSQL_HOST", "localhost"),
        "port": os.environ.get("MYSQL_PORT", "3306"),
        "user": os.environ.get("MYSQL_USER", "root"),
        "password": os.environ.get("MYSQL_PASSWORD", "root1234"),
        "database": os.environ.get("MYSQL_DATABASE", "testdb")
    }
    
    REST_API_BASE_URL = os.environ.get("REST_BASE_URL", "https://petstore.swagger.io")
    
    # Windows-compatible working directory
    WORKING_DIR = os.environ.get("MCP_WORKING_DIR", os.path.expanduser("~\\mcp_files"))
    
    @staticmethod
    def _get_npx_command():
        """Get the correct npx command for the current OS"""
        if sys.platform == "win32":
            return "npx.cmd"
        return "npx"
    
    @staticmethod
    def _get_uv_command():
        """Get the correct uv/uvx command for the current OS"""
        if sys.platform == "win32":
            # Try to find uv in PATH or use pip-installed location
            uv_path = os.environ.get("UV_PATH", "uv")
            return uv_path
        return "uv"

    @staticmethod
    def get_mysql_workbench():
        """Get MySQL MCP workbench instance (Windows compatible)"""
        npx_cmd = McpConfig._get_npx_command()
        
        mysql_server_params = StdioServerParams(
            command=npx_cmd,
            args=[
                "-y",
                "@benborber/mcp-server-mysql"
            ],
            env={
                "MYSQL_HOST": McpConfig.MYSQL_CONFIG["host"],
                "MYSQL_PORT": McpConfig.MYSQL_CONFIG["port"],
                "MYSQL_USER": McpConfig.MYSQL_CONFIG["user"],
                "MYSQL_PASSWORD": McpConfig.MYSQL_CONFIG["password"],
                "MYSQL_DATABASE": McpConfig.MYSQL_CONFIG["database"]
            },
            read_timeout_seconds=60
        )
        return McpWorkbench(server_params=mysql_server_params)

    @staticmethod
    def get_rest_api_workbench():
        """Get REST API MCP workbench instance (Windows compatible)"""
        npx_cmd = McpConfig._get_npx_command()
        
        rest_api_server_params = StdioServerParams(
            command=npx_cmd,
            args=[
                "-y",
                "dkmaker-mcp-rest-api"
            ],
            env={
                "REST_BASE_URL": McpConfig.REST_API_BASE_URL,
                "HEADER_Accept": "application/json"
            },
            read_timeout_seconds=60
        )
        return McpWorkbench(server_params=rest_api_server_params)

    @staticmethod
    def get_excel_workbench():
        """Get Excel MCP workbench instance (Windows compatible)"""
        npx_cmd = McpConfig._get_npx_command()
        
        excel_server_params = StdioServerParams(
            command=npx_cmd,
            args=["--yes", "@negokaz/excel-mcp-server"],
            env={
                "EXCEL_MCP_PAGING_CELLS_LIMIT": "4000"
            },
            read_timeout_seconds=60
        )
        return McpWorkbench(server_params=excel_server_params)

    @staticmethod
    def get_filesystem_workbench():
        """Get Filesystem MCP workbench instance (Windows compatible)"""
        npx_cmd = McpConfig._get_npx_command()
        
        # Ensure working directory exists
        working_dir = McpConfig.WORKING_DIR
        os.makedirs(working_dir, exist_ok=True)
        
        filesystem_server_params = StdioServerParams(
            command=npx_cmd,
            args=["-y", "@modelcontextprotocol/server-filesystem", working_dir],
            read_timeout_seconds=60
        )
        return McpWorkbench(server_params=filesystem_server_params)

    @staticmethod
    def get_playwright_workbench():
        """Get Playwright MCP workbench instance for UI testing and visual regression (Windows compatible)"""
        npx_cmd = McpConfig._get_npx_command()
        
        playwright_server_params = StdioServerParams(
            command=npx_cmd,
            args=["--yes", "@playwright/mcp@latest"],
            read_timeout_seconds=60
        )
        return McpWorkbench(server_params=playwright_server_params)
    
    @staticmethod
    def get_fetch_workbench():
        """Get Fetch MCP workbench for HTTP requests (Windows compatible)"""
        npx_cmd = McpConfig._get_npx_command()
        
        fetch_server_params = StdioServerParams(
            command=npx_cmd,
            args=["--yes", "@anthropics/mcp-server-fetch"],
            read_timeout_seconds=60
        )
        return McpWorkbench(server_params=fetch_server_params)
