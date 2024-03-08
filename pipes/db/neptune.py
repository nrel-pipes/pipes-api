from __future__ import annotations

import logging

from gremlin_python.process.graph_traversal import GraphTraversalSource
from gremlin_python.structure.graph import Graph
from gremlin_python.driver.driver_remote_connection import DriverRemoteConnection
from gremlin_python.driver.aiohttp.transport import AiohttpTransport

from pipes.config.settings import settings
from pipes.db.abstract import AbstractDatabase

logger = logging.getLogger(__name__)


class NeptuneDB(AbstractDatabase):

    def __init__(self):
        self.connection = None

    @property
    def endpoint(self) -> str:
        host = settings.PIPES_NEPTUNE_HOST
        port = settings.PIPES_NEPTUNE_PORT
        secure = settings.PIPES_NEPTUNE_SECURE
        if secure:
            return f"wss://{host}:{port}/gremlin"
        return f"ws://{host}:{port}/gremlin"

    def connect(self) -> GraphTraversalSource:
        event_loop = settings.PIPES_NEPTUNE_EVENT_LOOP
        connection = DriverRemoteConnection(
            self.endpoint,
            "g",
            transport_factory=lambda: AiohttpTransport(call_from_event_loop=event_loop),
        )
        self.connection = connection
        graph = Graph()
        self.g = graph.traversal().with_remote(self.connection)

    def close(self) -> None:
        if self.connection:
            self.connection.close()
        self.connection = None
        self.g = None

    def ping(self) -> list:
        """Query graph and avoid Neptune disconnection due to long idle."""
        return self.g.V().limit(1).toList()
