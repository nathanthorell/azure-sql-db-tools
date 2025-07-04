"""
Azure SQL DB Logs Client - Core functionality for querying Log Analytics
"""

from datetime import timedelta
from typing import Any, List, Optional

from azure.core.credentials import TokenCredential
from azure.core.exceptions import HttpResponseError
from azure.identity import DefaultAzureCredential, InteractiveBrowserCredential
from azure.monitor.query import LogsQueryClient, LogsQueryResult, LogsQueryStatus

from .config import get_config


class LogsClient:
    def __init__(self, workspace_id: Optional[str] = None) -> None:
        self.workspace_id = workspace_id or get_config().workspace_id
        self.credential: Optional[TokenCredential] = None
        self.logs_client: Optional[LogsQueryClient] = None

    def _get_credential(self) -> TokenCredential:
        """Get Azure credential with fallback to interactive browser login"""
        if self.credential is not None:
            return self.credential

        # Try DefaultAzureCredential first (works with az login, env vars, etc.)
        default_credential = DefaultAzureCredential()
        try:
            # Test the credential by attempting to get a token
            default_credential.get_token("https://api.loganalytics.io/.default")
            print("Using existing Azure authentication")
            self.credential = default_credential
            self.logs_client = LogsQueryClient(self.credential)
            return default_credential
        except Exception:
            # Fall back to interactive browser login
            print("No existing Azure authentication found. Opening browser for login...")
            print("Please complete the authentication in your browser and wait for it to finish...")
            interactive_credential = InteractiveBrowserCredential()
            self.credential = interactive_credential
            self.logs_client = LogsQueryClient(self.credential)
            return interactive_credential

    def run_query(self, query: str, timespan: Optional[timedelta] = None) -> Optional[List[Any]]:
        """Execute a KQL query against the Log Analytics workspace"""
        try:
            # Validate workspace ID
            if not self.workspace_id or self.workspace_id == "your-log-analytics-workspace-id":
                print("ERROR: Please set a valid workspace_id in your config.toml file")
                print("Add your Log Analytics workspace ID to the [azure] section")
                return None

            # Initialize authentication if not already done
            if self.logs_client is None:
                self._get_credential()

            if not timespan:
                timespan = timedelta(minutes=10)

            # Type assertion since we know logs_client is not None after _get_credential
            assert self.logs_client is not None
            response = self.logs_client.query_workspace(
                workspace_id=self.workspace_id, query=query, timespan=timespan
            )

            if hasattr(response, "status") and response.status == LogsQueryStatus.SUCCESS:
                if isinstance(response, LogsQueryResult) and response.tables:
                    return response.tables[0].rows
                else:
                    return []
            else:
                print(f"Query failed: {response.status}")
                return None

        except HttpResponseError as e:
            print(f"HTTP Error: {e}")
            return None
        except Exception as e:
            print(f"Error executing query: {e}")
            return None

    def recent_errors(self, minutes: int = 10) -> Optional[List[Any]]:
        """Get recent SQL database errors from audit events"""
        query = f"""
        AzureDiagnostics
        | where TimeGenerated > ago({minutes}m)
        | where Category == "SQLSecurityAuditEvents"
        | where database_name_s != "master"
        | where succeeded_s == "false" or succeeded_s == "False"
        | project TimeGenerated, database_name_s, statement_s, server_principal_name_s,
                action_name_s, additional_information_s, AdditionalFields
        | order by TimeGenerated desc
        """
        return self.run_query(query, timedelta(minutes=minutes))

    def slow_queries(self, minutes: int = 10, threshold_ms: int = 5000) -> Optional[List[Any]]:
        """Find slow running queries"""
        query = f"""
        AzureDiagnostics
        | where TimeGenerated > ago({minutes}m)
        | where duration_milliseconds_d > {threshold_ms}
        | where Category == "SQLSecurityAuditEvents"
        | where database_name_s != "master"
        | project TimeGenerated, statement_s, duration_milliseconds_d, database_name_s,
                server_principal_name_s
        | order by duration_milliseconds_d desc
        """
        return self.run_query(query, timedelta(minutes=minutes))
