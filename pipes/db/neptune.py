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
        self._conn = None

    @property
    def endpoint(self) -> str:
        host = settings.PIPES_NEPTUNE_HOST
        port = settings.PIPES_NEPTUNE_PORT
        secure = settings.PIPES_NEPTUNE_SECURE
        if secure:
            return f"wss://{host}:{port}/gremlin"
        return f"ws://{host}:{port}/gremlin"

    def connect(self) -> GraphTraversalSource:
        connection = DriverRemoteConnection(
            self.endpoint,
            "g",
            transport_factory=lambda: AiohttpTransport(call_from_event_loop=True),
        )
        self._conn = connection
        return connection

    @property
    def conn(self):
        return self._conn

    @property
    def g(self):
        if not self._conn:
            return None
        return self._create_graph_traversal_source()

    def _create_graph_traversal_source(self):
        graph = Graph()
        return graph.traversal().with_remote(self._conn)

    def close(self):
        if self._conn:
            self._conn.close()
        self._conn = None

    def ping(self) -> list:
        """Query graph and avoid Neptune disconnection due to long idle."""
        return self.g.V().limit(1).toList()

    def v(self, id):
        """Get graph vertex by id"""
        return self.g.V(id)

    def exists(self, label, **properties):
        """Check if a given label exists in the graph or not"""
        if self.get_v(label, **properties):
            return True
        return False

    def get_v(self, label, **properties):
        """Get graph vertex"""
        traversal = self.g.V().has_label(label)
        for k, v in properties.items():
            traversal = traversal.has(k, v)
        return traversal.to_list()

    def add_v(self, label, **properties):
        """Create graph vertex"""
        traversal = self.g.add_v(label)
        for k, v in properties.items():
            traversal = traversal.property(k, v)
        return traversal.next()

    def get_or_add_v(self, label, **properties):
        """Get or create vertex"""
        vlist = self.get_v(label, **properties)
        if vlist:
            return vlist[0]

        return self.add_v(label, **properties)

    def add_edge(self, id1, id2, label, **properties):
        """Add edge from v1 to v2"""
        traversal = (
            self.g.V(id1).as_("v1").V(id2).as_("v2").add_e(label).from_("v1").to("v2")
        )

        for k, v in properties.items():
            traversal = traversal.property(k, v)

        result = [r for r in traversal.to_list()]
        return result
