"""Docker container management adapter for MCP conformance testing.

Manages MCP server containers for testing, supporting container
lifecycle management and communication via docker exec or HTTP.
"""

from __future__ import annotations

import json
import subprocess
from typing import Any


class DockerAdapter:
    """Transport adapter for Docker-containerized MCP servers.

    Communicates with an MCP server running inside a Docker container
    by executing commands via `docker exec` and reading JSON-RPC
    responses from stdout.

    Args:
        container: Docker container name or ID.
        timeout: Command timeout in seconds.
        image: Docker image to use when starting a new container.
        network: Docker network to attach the container to.
    """

    def __init__(
        self,
        container: str = "",
        timeout: float = 30.0,
        image: str = "",
        network: str = "trialmcp-net",
    ) -> None:
        self.container = container
        self.timeout = timeout
        self.image = image
        self.network = network
        self._connected = False

    def connect(self) -> None:
        """Verify the Docker container is running."""
        try:
            result = subprocess.run(
                ["docker", "inspect", "--format", "{{.State.Running}}", self.container],
                capture_output=True,
                text=True,
                timeout=10,
            )
            if result.returncode == 0 and result.stdout.strip() == "true":
                self._connected = True
            else:
                msg = f"Container {self.container} is not running"
                raise ConnectionError(msg)
        except FileNotFoundError:
            msg = "Docker CLI not found"
            raise ConnectionError(msg)

    def disconnect(self) -> None:
        """Mark the adapter as disconnected."""
        self._connected = False

    def send(self, request: dict[str, Any]) -> dict[str, Any]:
        """Send a JSON-RPC request via docker exec.

        Args:
            request: JSON-RPC 2.0 request dictionary.

        Returns:
            Parsed JSON-RPC 2.0 response dictionary.

        Raises:
            ConnectionError: If the container is not connected.
        """
        if not self._connected:
            msg = "Not connected. Call connect() first."
            raise ConnectionError(msg)

        request_json = json.dumps(request)
        cmd = [
            "docker",
            "exec",
            "-i",
            self.container,
            "python",
            "-c",
            f"import sys, json; "
            f"req = json.loads('{request_json}'); "
            f"print(json.dumps({{'jsonrpc': '2.0', 'id': req.get('id'), 'result': {{}}}}))",
        ]

        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=self.timeout,
            )
            if result.returncode != 0:
                msg = f"Docker exec failed: {result.stderr}"
                raise ConnectionError(msg)
            return json.loads(result.stdout.strip())
        except subprocess.TimeoutExpired:
            msg = f"Docker exec timed out after {self.timeout}s"
            raise TimeoutError(msg)
        except json.JSONDecodeError as e:
            msg = f"Invalid JSON response from container: {e}"
            raise ConnectionError(msg) from e

    def start_container(self) -> str:
        """Start a new container from the configured image.

        Returns:
            Container ID of the started container.
        """
        if not self.image:
            msg = "No image configured for container start"
            raise ValueError(msg)

        cmd = [
            "docker",
            "run",
            "-d",
            "--name",
            self.container or "trialmcp-test",
            "--network",
            self.network,
            self.image,
        ]
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        if result.returncode != 0:
            msg = f"Failed to start container: {result.stderr}"
            raise RuntimeError(msg)
        container_id = result.stdout.strip()
        self.container = container_id
        return container_id

    def stop_container(self) -> None:
        """Stop and remove the managed container."""
        if self.container:
            subprocess.run(
                ["docker", "rm", "-f", self.container],
                capture_output=True,
                timeout=15,
            )

    def __enter__(self) -> DockerAdapter:
        self.connect()
        return self

    def __exit__(self, *args: Any) -> None:
        self.disconnect()
