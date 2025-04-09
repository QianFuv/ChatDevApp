import requests
from typing import Optional, Dict, Any
import logging


class APIClient:
    """
    Client for communicating with the ChatDev API
    
    This client implements all endpoints from the ChatDev API specification
    and handles authentication, error handling, and response parsing.
    """
    def __init__(self, base_url: str = "http://localhost:8000/", api_key: str = "", logger=None):
        """
        Initialize the API client
        
        Args:
            base_url: Base URL for the API (default: http://localhost:8000/)
            api_key: API key for authentication
            logger: Optional logger instance for logging
        """
        # Ensure base_url ends with '/' and contains the API prefix
        self.base_url = self._normalize_base_url(base_url)
        self.api_key = api_key
        self.headers = {"Content-Type": "application/json"}
        self.logger = logger or logging.getLogger(__name__)
        
    def _normalize_base_url(self, base_url: str) -> str:
        """Normalize the base URL to ensure it has the correct format"""
        if not base_url.endswith("/"):
            base_url += "/"
            
        # Ensure the API prefix is included
        if not base_url.endswith("api/v1/") and "api/v1/" not in base_url:
            base_url += "api/v1/"
            
        return base_url
    
    def _log(self, message: str, level: str = "INFO") -> None:
        """Log a message using the provided logger"""
        # Convert string level to int
        level_map = {
            "DEBUG": 10,
            "INFO": 20,
            "WARNING": 30,
            "ERROR": 40,
            "CRITICAL": 50
        }
        level_int = level_map.get(level, 20)  # Default to INFO (20)
        
        if hasattr(self.logger, "log"):
            self.logger.log(level_int, message)
        elif hasattr(self.logger, level.lower()):
            getattr(self.logger, level.lower())(message)
            
    def set_api_key(self, api_key: str) -> None:
        """
        Set the API key for authentication
        
        Args:
            api_key: API key string
        """
        self.api_key = api_key
        self._log("API key updated")
        
    def set_base_url(self, base_url: str) -> None:
        """
        Set the base URL for the API
        
        Args:
            base_url: Base URL for the API
        """
        self.base_url = self._normalize_base_url(base_url)
        self._log(f"API URL set to: {self.base_url}")
    
    def _get_headers_with_api_key(self) -> Dict[str, str]:
        """Get headers with API key for endpoints that require header authentication"""
        headers = self.headers.copy()
        if self.api_key:
            # FastAPI converts parameter name 'api_key' to header name 'api-key'
            headers["api-key"] = self.api_key
        return headers
    
    def generate_project(self, 
                        task: str, 
                        name: str, 
                        config: str = "Default", 
                        org: str = "DefaultOrganization", 
                        model: str = "CLAUDE_3_5_SONNET",
                        path: str = "",
                        build_apk: bool = False,
                        base_url: Optional[str] = None) -> Dict[str, Any]:
        """
        Start a new ChatDev generation task
        
        Args:
            task: Description of the software to build (10-2000 characters)
            name: Name of the software project
            config: Configuration name under CompanyConfig/ (Default, Art, Human, Flet)
            org: Organization name
            model: LLM model to use
            path: Path to existing code for incremental development
            build_apk: Whether to build an APK after generating the software
            base_url: Optional base URL for API calls (useful for proxies)
            
        Returns:
            Dict containing task_id, status, and created_at
        """
        # Validate inputs
        if not task or len(task) < 10 or len(task) > 2000:
            raise ValueError("Task description must be between 10 and 2000 characters")
        
        if not name:
            raise ValueError("Project name is required")
            
        data = {
            "api_key": self.api_key,
            "task": task,
            "name": name,
            "config": config,
            "org": org,
            "model": model,
            "path": path,
            "build_apk": build_apk
        }
        
        # Add optional base_url parameter if provided
        if base_url:
            data["base_url"] = base_url
        
        try:
            self._log(f"Creating new project: {name}")
            response = requests.post(
                f"{self.base_url}generate", 
                headers=self.headers,
                json=data
            )
            
            # Handle common status codes
            if response.status_code == 401:
                self._log("Authentication failed: Invalid API key", "ERROR")
                raise Exception("Authentication failed: Invalid API key")
            elif response.status_code == 422:
                error_data = response.json()
                self._log(f"Validation error: {error_data}", "ERROR")
                raise ValueError(f"Validation error: {str(error_data.get('detail', 'Unknown validation error'))}")
                
            response.raise_for_status()
            result = response.json()
            self._log(f"Project generation task created successfully. ID: {result.get('task_id')}")
            return result
        except requests.RequestException as e:
            self._log(f"Failed to create project generation task: {str(e)}", "ERROR")
            raise Exception(f"Failed to create project generation task: {str(e)}")
    
    def get_task_status(self, task_id: int) -> Dict[str, Any]:
        """
        Get the status of a ChatDev generation task
        
        Args:
            task_id: The unique identifier of the task to check
            
        Returns:
            Dict containing task status information
        """
        if not isinstance(task_id, int) or task_id <= 0:
            raise ValueError("task_id must be a positive integer")
            
        try:
            self._log(f"Checking status of task #{task_id}")
            
            response = requests.get(
                f"{self.base_url}status/{task_id}", 
                headers=self.headers
            )
            
            if response.status_code == 404:
                self._log(f"Task #{task_id} not found", "ERROR")
                raise Exception(f"Task with ID {task_id} not found")
                
            response.raise_for_status()
            result = response.json()
            self._log(f"Task #{task_id} status: {result.get('status', 'Unknown')}")
            return result
        except requests.RequestException as e:
            self._log(f"Failed to get task status: {str(e)}", "ERROR")
            raise Exception(f"Failed to get task status: {str(e)}")
    
    def list_tasks(self, 
                  status: Optional[str] = None, 
                  limit: int = 10, 
                  offset: int = 0) -> Dict[str, Any]:
        """
        List all ChatDev generation tasks
        
        Args:
            status: Filter tasks by status (PENDING, RUNNING, COMPLETED, FAILED, CANCELLED)
            limit: Maximum number of tasks to return (1-100)
            offset: Number of tasks to skip for pagination
            
        Returns:
            Dict containing tasks list and total count
        """
        # Validate inputs
        if limit < 1 or limit > 100:
            raise ValueError("limit must be between 1 and 100")
        
        if offset < 0:
            raise ValueError("offset must be non-negative")
            
        try:
            self._log(f"Fetching tasks from API" + (f" with status: {status}" if status else ""))
            
            params = {}
            if status:
                params["status"] = status
            params["limit"] = limit
            params["offset"] = offset
            
            response = requests.get(
                f"{self.base_url}tasks", 
                headers=self.headers,
                params=params
            )
            
            # Handle validation errors
            if response.status_code == 422:
                error_data = response.json()
                self._log(f"Validation error: {error_data}", "ERROR")
                raise ValueError(f"Validation error: {str(error_data.get('detail', 'Unknown validation error'))}")
                
            response.raise_for_status()
            result = response.json()
            self._log(f"Successfully fetched {len(result.get('tasks', []))} tasks")
            return result
        except requests.RequestException as e:
            self._log(f"Failed to get tasks: {str(e)}", "ERROR")
            raise Exception(f"Failed to get tasks: {str(e)}")
    
    def cancel_task(self, task_id: int) -> Dict[str, Any]:
        """
        Cancel a running ChatDev generation task
        
        Args:
            task_id: The ID of the task to cancel
            
        Returns:
            Dict containing updated task status
        """
        if not isinstance(task_id, int) or task_id <= 0:
            raise ValueError("task_id must be a positive integer")
            
        data = {
            "api_key": self.api_key
        }
        
        try:
            self._log(f"Canceling task #{task_id}")
            response = requests.post(
                f"{self.base_url}cancel/{task_id}", 
                headers=self.headers,
                json=data
            )
            
            if response.status_code == 404:
                self._log(f"Task #{task_id} not found", "ERROR")
                raise Exception(f"Task with ID {task_id} not found")
            elif response.status_code == 400:
                error_data = response.json()
                self._log(f"Cannot cancel task: {error_data.get('detail', 'Unknown error')}", "ERROR")
                raise Exception(f"Cannot cancel task: {error_data.get('detail', 'Unknown error')}")
            elif response.status_code == 401:
                self._log("Authentication failed: Invalid API key", "ERROR")
                raise Exception("Authentication failed: Invalid API key")
                
            response.raise_for_status()
            result = response.json()
            self._log(f"Task #{task_id} cancellation result: {result.get('status', 'Unknown')}")
            return result
        except requests.RequestException as e:
            self._log(f"Failed to cancel task: {str(e)}", "ERROR")
            raise Exception(f"Failed to cancel task: {str(e)}")
    
    def delete_task(self, task_id: int) -> Dict[str, Any]:
        """
        Delete a ChatDev task record
        
        Args:
            task_id: The ID of the task to delete
            
        Returns:
            Dict containing confirmation message
        """
        if not isinstance(task_id, int) or task_id <= 0:
            raise ValueError("task_id must be a positive integer")
            
        try:
            self._log(f"Deleting task #{task_id}")
                
            # Use the correct header name to match FastAPI's expectation
            headers = self._get_headers_with_api_key()
            
            # Log the headers for debugging
            self._log(f"Using headers for delete: {headers}", "DEBUG")
            
            response = requests.delete(
                f"{self.base_url}task/{task_id}", 
                headers=headers
            )
            
            if response.status_code == 404:
                self._log(f"Task #{task_id} not found", "ERROR")
                raise Exception(f"Task with ID {task_id} not found")
            elif response.status_code == 401:
                self._log("Authentication failed: Invalid API key", "ERROR")
                raise Exception("Authentication failed: Invalid API key")
                
            response.raise_for_status()
            result = response.json()
            self._log(f"Task #{task_id} deleted successfully: {result}")
            return result
        except requests.RequestException as e:
            self._log(f"Failed to delete task: {str(e)}", "ERROR")
            raise Exception(f"Failed to delete task: {str(e)}")
    
    def build_apk(self, 
                 project_name: str, 
                 organization: Optional[str] = None, 
                 timestamp: Optional[str] = None) -> Dict[str, Any]:
        """
        Build an APK from an existing project
        
        Args:
            project_name: Name of the project to build
            organization: Organization name in the project path
            timestamp: Timestamp in the project path
            
        Returns:
            Dict containing build status, message, and artifact paths
        """
        if not project_name:
            raise ValueError("project_name is required")
            
        # Include API key in both header and body as recommended in the API documentation
        data = {
            "api_key": self.api_key,
            "project_name": project_name
        }
        
        # Add optional parameters if provided and they're not empty or "string" placeholder
        if organization and organization != "string":
            data["organization"] = organization
        if timestamp:
            data["timestamp"] = timestamp
        
        try:
            self._log(f"Building APK for project: {project_name}")
            
            # Add API key to headers for additional authentication
            headers = self._get_headers_with_api_key()
            
            # Log the request for debugging
            self._log(f"Using headers for build APK: {headers}", "DEBUG")
            self._log(f"Request payload: {data}", "DEBUG")
            
            # Send API request
            response = requests.post(
                f"{self.base_url}build-apk", 
                headers=headers,
                json=data
            )
            
            # Log the response for debugging
            self._log(f"APK build response status: {response.status_code}", "DEBUG")
            
            # Handle common error codes
            if response.status_code == 404:
                self._log(f"Project not found: {project_name}", "ERROR")
                raise Exception(f"Project not found: {project_name}")
            elif response.status_code == 401:
                self._log("Authentication failed: Invalid API key", "ERROR")
                raise Exception("Authentication failed: Invalid API key")
            elif response.status_code == 422:
                error_data = response.json()
                error_detail = error_data.get("detail", "Validation error")
                self._log(f"Validation error details: {error_detail}", "ERROR")
                raise ValueError(f"Validation error: {error_detail}")
            elif response.status_code != 200:
                self._log(f"Error response content: {response.text}", "DEBUG")
                    
            response.raise_for_status()
            result = response.json()
            
            # Log the result
            if result.get("success"):
                self._log(f"APK built successfully: {result.get('apk_path')}")
            else:
                self._log(f"APK build failed: {result.get('message')}", "ERROR")
            
            return result
        except requests.RequestException as e:
            self._log(f"Failed to build APK: {str(e)}", "ERROR")
            raise Exception(f"Failed to build APK: {str(e)}")
            
    def health_check(self) -> Dict[str, Any]:
        """
        Check if the API is healthy
        
        Returns:
            Dict containing API status, version, and timestamp
        """
        try:
            self._log(f"Checking API health")
            
            response = requests.get(f"{self.base_url}health")
            response.raise_for_status()
            result = response.json()
            
            self._log(f"API health status: {result.get('status', 'Unknown')}")
            
            return result
        except requests.RequestException as e:
            self._log(f"Health check failed: {str(e)}", "ERROR")
            raise Exception(f"Health check failed: {str(e)}")
    
    def simple_health_check(self) -> Dict[str, Any]:
        """
        Simple health check (alternative endpoint)
        
        Returns:
            Dict containing health check response
        """
        try:
            self._log(f"Performing simple health check")
            
            # Remove the api/v1 prefix for this endpoint
            base_url = self.base_url.replace("api/v1/", "")
            
            response = requests.get(f"{base_url}health")
            response.raise_for_status()
            result = response.json()
            
            self._log(f"Simple health check completed successfully")
            
            return result
        except requests.RequestException as e:
            self._log(f"Simple health check failed: {str(e)}", "ERROR")
            raise Exception(f"Simple health check failed: {str(e)}")