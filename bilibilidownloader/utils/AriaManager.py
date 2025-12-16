import json
import uuid
from typing import Any, Dict, List, Optional

import httpx


class AriaManager:
    """
    A manager class for communicating with Aria2 RPC server to manage download tasks.
    """

    def __init__(self, host: str = "localhost", port: int = 6800, secret: str = None):
        """
        Initialize the AriaManager.

        Args:
            host: The host address of the Aria2 RPC server
            port: The port number of the Aria2 RPC server
            secret: The secret token for authentication (if required)
        """
        self.host = host
        self.port = port
        self.secret = secret
        self.rpc_url = f"http://{host}:{port}/jsonrpc"
        self.client = httpx.Client()
        assert self.test_conn()

    def test_conn(self):
        """Test the connection to the Aria2 RPC server."""
        try:
            self.client.get(self.rpc_url)
            return True
        except Exception as e:
            raise ConnectionError(f"Failed to connect to Aria2 RPC server: {e}")

    def _generate_request(
        self, method: str, params: List[Any] = None
    ) -> Dict[str, Any]:
        """
        Generate a JSON-RPC request.

        Args:
            method: The RPC method name
            params: The parameters for the method

        Returns:
            A dictionary representing the JSON-RPC request
        """
        request = {"jsonrpc": "2.0", "id": str(uuid.uuid4()), "method": method}

        if params is None:
            params = []

        # Add secret token if provided
        if self.secret:
            params.insert(0, f"token:{self.secret}")

        request["params"] = params
        return request

    def _send_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """
        Send a JSON-RPC request to the Aria2 server.

        Args:
            request: The JSON-RPC request to send

        Returns:
            The response from the server
        """
        headers = {"Content-Type": "application/json"}
        response = self.client.post(
            self.rpc_url, content=json.dumps(request), headers=headers
        )
        response.raise_for_status()
        return response.json()

    def add_uri(self, uris: List[str], options: Dict[str, Any] = None) -> str:
        """
        Add a new download task using URIs.

        Args:
            uris: A list of URIs to download
            options: Additional options for the download

        Returns:
            The GID (Global ID) of the newly created download task
        """
        params = [uris]
        if options:
            params.append(options)

        request = self._generate_request("aria2.addUri", params)
        response = self._send_request(request)
        return response["result"]

    def pause(self, gid: str) -> str:
        """
        Pause a download task.

        Args:
            gid: The GID of the download task to pause

        Returns:
            The GID of the paused task
        """
        request = self._generate_request("aria2.pause", [gid])
        response = self._send_request(request)
        return response["result"]

    def pause_all(self) -> str:
        """
        Pause all active download tasks.

        Returns:
            "OK" if successful
        """
        request = self._generate_request("aria2.pauseAll")
        response = self._send_request(request)
        return response["result"]

    def unpause(self, gid: str) -> str:
        """
        Resume a paused download task.

        Args:
            gid: The GID of the download task to resume

        Returns:
            The GID of the resumed task
        """
        request = self._generate_request("aria2.unpause", [gid])
        response = self._send_request(request)
        return response["result"]

    def unpause_all(self) -> str:
        """
        Resume all paused download tasks.

        Returns:
            "OK" if successful
        """
        request = self._generate_request("aria2.unpauseAll")
        response = self._send_request(request)
        return response["result"]

    def remove(self, gid: str) -> str:
        """
        Remove a download task.

        Args:
            gid: The GID of the download task to remove

        Returns:
            The GID of the removed task
        """
        request = self._generate_request("aria2.remove", [gid])
        response = self._send_request(request)
        return response["result"]

    def get_status(self, gid: str) -> Dict[str, Any]:
        """
        Get the status of a download task.

        Args:
            gid: The GID of the download task

        Returns:
            A dictionary containing the status information
        """
        request = self._generate_request("aria2.tellStatus", [gid])
        response = self._send_request(request)
        return response["result"]

    def get_active_downloads(self) -> List[Dict[str, Any]]:
        """
        Get all active download tasks.

        Returns:
            A list of active download tasks
        """
        request = self._generate_request("aria2.tellActive")
        response = self._send_request(request)
        return response["result"]

    def get_waiting_downloads(self) -> List[Dict[str, Any]]:
        """
        Get all waiting download tasks.

        Returns:
            A list of waiting download tasks
        """
        # Get first 1000 waiting downloads
        request = self._generate_request("aria2.tellWaiting", [0, 1000])
        response = self._send_request(request)
        return response["result"]

    def get_stopped_downloads(self) -> List[Dict[str, Any]]:
        """
        Get all stopped download tasks.

        Returns:
            A list of stopped download tasks
        """
        # Get first 1000 stopped downloads
        request = self._generate_request("aria2.tellStopped", [0, 1000])
        response = self._send_request(request)
        return response["result"]

    def get_global_stat(self) -> Dict[str, Any]:
        """
        Get global statistics.

        Returns:
            A dictionary containing global statistics
        """
        request = self._generate_request("aria2.getGlobalStat")
        response = self._send_request(request)
        return response["result"]

    def purge_download_result(self) -> str:
        """
        Purge completed/error/removed downloads from memory.

        Returns:
            "OK" if successful
        """
        request = self._generate_request("aria2.purgeDownloadResult")
        response = self._send_request(request)
        return response["result"]

    def remove_download_result(self, gid: str) -> str:
        """
        Remove a completed/error/removed download from memory.

        Args:
            gid: The GID of the download result to remove

        Returns:
            "OK" if successful
        """
        request = self._generate_request("aria2.removeDownloadResult", [gid])
        response = self._send_request(request)
        return response["result"]

    def close(self):
        """
        Close the HTTP client connection.
        """
        self.client.close()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()


if __name__ == "__main__":
    from pathlib import Path

    ROOT = Path(__file__).parent.resolve()

    aria = AriaManager(
        host="localhost",
        port=16800,
        secret="",
    )

    pass
