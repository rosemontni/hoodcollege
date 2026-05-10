from __future__ import annotations

from collections import Counter, defaultdict, deque
from dataclasses import dataclass
from datetime import date, timedelta
from itertools import combinations
from typing import Any, Iterable, Mapping


ROLE_LABELS = {
    "administrator": "Administrators",
    "faculty": "Faculty",
    "staff": "Staff",
    "alumni": "Alumni",
    "student": "Students",
    "student-athlete": "Student-Athletes",
    "coach": "Coaches",
    "guest": "Guests / External Partners",
    "person": "Unclassified People",
}

ROLE_ORDER = [
    "faculty",
    "administrator",
    "student",
    "student-athlete",
    "staff",
    "alumni",
    "coach",
    "guest",
    "person",
]


@dataclass(frozen=True)
class NetworkEvidence:
    article_url: str
    name: str
    role_category: str
    source_id: str
    seen_date: date
    title: str


@dataclass(frozen=True)
class SocialNetworkAnalysisReport:
    run_date: date
    narratives: dict[str, str]
    overview: dict[str, Any]
    strongest_bonds: list[dict[str, Any]]
    role_leaders: dict[str, list[dict[str, Any]]]
    faculty_visibility: list[dict[str, Any]]
    faculty_administration_connectors: list[dict[str, Any]]
    brokers: list[dict[str, Any]]
    articulation_people: list[dict[str, Any]]
    local_bridges: list[dict[str, Any]]
    role_mixing: list[dict[str, Any]]
    emerging_people: list[dict[str, Any]]
    communities: list[dict[str, Any]]

    def to_dict(self) -> dict[str, Any]:
        return {
            "run_date": self.run_date.isoformat(),
            "narratives": self.narratives,
            "overview": self.overview,
            "strongest_bonds": self.strongest_bonds,
            "role_leaders": self.role_leaders,
            "faculty_visibility": self.faculty_visibility,
            "faculty_administration_connectors": self.faculty_administration_connectors,
            "brokers": self.brokers,
            "articulation_people": self.articulation_people,
            "local_bridges": self.local_bridges,
            "role_mixing": self.role_mixing,
            "emerging_people": self.emerging_people,
            "communities": self.communities,
        }


class SocialNetworkAnalyzer:
    def analyze(
        self,
        run_date: date,
        rows: Iterable[object],
    ) -> SocialNetworkAnalysisReport:
        evidence = [self._evidence_from_row(row) for row in rows]
        graph = _EvidenceGraph.from_evidence(evidence, run_date)
        return graph.to_report()

    def _evidence_from_row(self, row: object) -> NetworkEvidence:
        seen_value = _row_value(row, "seen_date", "")
        if isinstance(seen_value, date):
            seen_date = seen_value
        else:
            seen_date = date.fromisoformat(str(seen_value))
        return NetworkEvidence(
            article_url=str(_row_value(row, "article_url", "")),
            name=str(_row_value(row, "name", "")),
            role_category=str(_row_value(row, "role_category", "person") or "person"),
            source_id=str(_row_value(row, "source_id", "unknown") or "unknown"),
            seen_date=seen_date,
            title=str(_row_value(row, "title", "") or ""),
        )


class _EvidenceGraph:
    def __init__(self, run_date: date) -> None:
        self.run_date = run_date
        self.article_names: dict[str, set[str]] = defaultdict(set)
        self.article_sources: dict[str, set[str]] = defaultdict(set)
        self.article_titles: dict[str, str] = {}
        self.article_seen_dates: dict[str, date] = {}
        self.role_by_name: dict[str, str] = {}
        self.articles_by_name: dict[str, set[str]] = defaultdict(set)
        self.sources_by_name: dict[str, set[str]] = defaultdict(set)
        self.seen_dates_by_name: dict[str, set[date]] = defaultdict(set)
        self.edge_articles: dict[tuple[str, str], set[str]] = defaultdict(set)
        self.adjacency: dict[str, dict[str, int]] = defaultdict(dict)
        self.recent_articles_by_name: dict[str, set[str]] = defaultdict(set)
        self.recent_adjacency: dict[str, set[str]] = defaultdict(set)

    @classmethod
    def from_evidence(cls, evidence: list[NetworkEvidence], run_date: date) -> "_EvidenceGraph":
        graph = cls(run_date)
        recent_cutoff = run_date - timedelta(days=30)
        for item in evidence:
            if not item.name or not item.article_url:
                continue
            graph.article_names[item.article_url].add(item.name)
            graph.article_sources[item.article_url].add(item.source_id)
            graph.article_titles[item.article_url] = item.title
            graph.article_seen_dates[item.article_url] = min(
                graph.article_seen_dates.get(item.article_url, item.seen_date),
                item.seen_date,
            )
            graph.role_by_name[item.name] = _preferred_role(
                graph.role_by_name.get(item.name, "person"),
                item.role_category,
            )
            graph.articles_by_name[item.name].add(item.article_url)
            graph.sources_by_name[item.name].add(item.source_id)
            graph.seen_dates_by_name[item.name].add(item.seen_date)
            if item.seen_date >= recent_cutoff:
                graph.recent_articles_by_name[item.name].add(item.article_url)

        for article_url, names in graph.article_names.items():
            sorted_names = sorted(names)
            if len(sorted_names) < 2:
                for name in sorted_names:
                    graph.adjacency.setdefault(name, {})
                continue
            for left, right in combinations(sorted_names, 2):
                graph.edge_articles[(left, right)].add(article_url)

        for (left, right), article_urls in graph.edge_articles.items():
            weight = len(article_urls)
            graph.adjacency[left][right] = weight
            graph.adjacency[right][left] = weight
            if any(graph.article_seen_dates.get(url, run_date) >= recent_cutoff for url in article_urls):
                graph.recent_adjacency[left].add(right)
                graph.recent_adjacency[right].add(left)

        for name in graph.articles_by_name:
            graph.adjacency.setdefault(name, {})
            graph.recent_adjacency.setdefault(name, set())
        return graph

    def to_report(self) -> SocialNetworkAnalysisReport:
        node_metrics = self._node_metrics()
        components = self._components()
        narratives = self._narratives()
        return SocialNetworkAnalysisReport(
            run_date=self.run_date,
            narratives=narratives,
            overview=self._overview(components),
            strongest_bonds=self._strongest_bonds(limit=15),
            role_leaders=self._role_leaders(node_metrics, limit=8),
            faculty_visibility=self._faculty_visibility(node_metrics, limit=12),
            faculty_administration_connectors=self._faculty_administration_connectors(node_metrics, limit=12),
            brokers=self._rank_people(node_metrics, "betweenness", limit=12),
            articulation_people=self._articulation_people(node_metrics, limit=12),
            local_bridges=self._local_bridges(limit=12),
            role_mixing=self._role_mixing(limit=16),
            emerging_people=self._emerging_people(node_metrics, limit=12),
            communities=self._community_summaries(components, node_metrics, limit=8),
        )

    def _overview(self, components: list[list[str]]) -> dict[str, Any]:
        node_count = len(self.adjacency)
        edge_count = len(self.edge_articles)
        density = 0.0 if node_count < 2 else (2 * edge_count) / (node_count * (node_count - 1))
        role_counts = Counter(self.role_by_name.values())
        largest_component = max((len(component) for component in components), default=0)
        return {
            "people": node_count,
            "connections": edge_count,
            "articles": len(self.article_names),
            "sources": len({source for sources in self.article_sources.values() for source in sources}),
            "density": round(density, 4),
            "connected_groups": len(components),
            "largest_group_size": largest_component,
            "roles": [
                {"role": role, "label": _role_label(role), "count": role_counts.get(role, 0)}
                for role in _ordered_roles(role_counts)
            ],
        }

    def _node_metrics(self) -> dict[str, dict[str, Any]]:
        betweenness = _betweenness_centrality(self.adjacency)
        pagerank = _pagerank(self.adjacency)
        faculty_admin_scores = self._faculty_admin_bridge_scores()
        metrics: dict[str, dict[str, Any]] = {}
        for name in sorted(self.adjacency):
            neighbors = self.adjacency[name]
            seen_dates = self.seen_dates_by_name.get(name, set())
            metrics[name] = {
                "name": name,
                "role": self.role_by_name.get(name, "person"),
                "role_label": _role_label(self.role_by_name.get(name, "person")),
                "degree": len(neighbors),
                "weighted_degree": sum(neighbors.values()),
                "mention_count": len(self.articles_by_name.get(name, set())),
                "source_count": len(self.sources_by_name.get(name, set())),
                "betweenness": round(betweenness.get(name, 0.0), 5),
                "pagerank": round(pagerank.get(name, 0.0), 6),
                "faculty_admin_bridge_score": faculty_admin_scores.get(name, {}).get("score", 0),
                "faculty_neighbor_count": faculty_admin_scores.get(name, {}).get("faculty_neighbors", 0),
                "administrator_neighbor_count": faculty_admin_scores.get(name, {}).get("administrator_neighbors", 0),
                "recent_mentions": len(self.recent_articles_by_name.get(name, set())),
                "recent_degree": len(self.recent_adjacency.get(name, set())),
                "first_seen": min(seen_dates).isoformat() if seen_dates else "",
                "last_seen": max(seen_dates).isoformat() if seen_dates else "",
            }
        return metrics

    def _strongest_bonds(self, limit: int) -> list[dict[str, Any]]:
        bonds: list[dict[str, Any]] = []
        for (left, right), article_urls in self.edge_articles.items():
            shared_count = len(article_urls)
            union_count = len(self.articles_by_name[left] | self.articles_by_name[right])
            source_ids = sorted({source for url in article_urls for source in self.article_sources.get(url, set())})
            bonds.append(
                {
                    "left": left,
                    "left_role": self.role_by_name.get(left, "person"),
                    "right": right,
                    "right_role": self.role_by_name.get(right, "person"),
                    "shared_article_count": shared_count,
                    "jaccard": round(_safe_divide(shared_count, union_count), 4),
                    "source_count": len(source_ids),
                    "sources": source_ids,
                }
            )
        bonds.sort(
            key=lambda item: (
                -int(item["shared_article_count"]),
                -float(item["jaccard"]),
                str(item["left"]).lower(),
                str(item["right"]).lower(),
            )
        )
        return bonds[:limit]

    def _role_leaders(
        self,
        node_metrics: dict[str, dict[str, Any]],
        limit: int,
    ) -> dict[str, list[dict[str, Any]]]:
        leaders: dict[str, list[dict[str, Any]]] = {}
        roles = _ordered_roles(Counter(metric["role"] for metric in node_metrics.values()))
        for role in roles:
            candidates = [metric for metric in node_metrics.values() if metric["role"] == role]
            ranked = sorted(
                candidates,
                key=lambda item: (
                    -int(item["weighted_degree"]),
                    -int(item["degree"]),
                    -int(item["mention_count"]),
                    str(item["name"]).lower(),
                ),
            )
            leaders[role] = [self._public_person_metric(item) for item in ranked[:limit]]
        return leaders

    def _faculty_visibility(
        self,
        node_metrics: dict[str, dict[str, Any]],
        limit: int,
    ) -> list[dict[str, Any]]:
        faculty = [metric for metric in node_metrics.values() if metric["role"] == "faculty"]
        faculty.sort(
            key=lambda item: (
                -int(item["mention_count"]),
                -int(item["source_count"]),
                -int(item["weighted_degree"]),
                -float(item["pagerank"]),
                str(item["name"]).lower(),
            )
        )
        return [self._public_person_metric(item) for item in faculty[:limit]]

    def _faculty_administration_connectors(
        self,
        node_metrics: dict[str, dict[str, Any]],
        limit: int,
    ) -> list[dict[str, Any]]:
        candidates = [
            metric
            for metric in node_metrics.values()
            if int(metric["faculty_admin_bridge_score"]) > 0
        ]
        candidates.sort(
            key=lambda item: (
                -int(item["faculty_admin_bridge_score"]),
                -float(item["betweenness"]),
                -int(item["weighted_degree"]),
                str(item["name"]).lower(),
            )
        )
        return [self._public_person_metric(item) for item in candidates[:limit]]

    def _rank_people(
        self,
        node_metrics: dict[str, dict[str, Any]],
        metric_name: str,
        limit: int,
    ) -> list[dict[str, Any]]:
        ranked = sorted(
            node_metrics.values(),
            key=lambda item: (
                -float(item[metric_name]),
                -int(item["weighted_degree"]),
                str(item["name"]).lower(),
            ),
        )
        return [self._public_person_metric(item) for item in ranked if float(item[metric_name]) > 0][:limit]

    def _articulation_people(
        self,
        node_metrics: dict[str, dict[str, Any]],
        limit: int,
    ) -> list[dict[str, Any]]:
        articulation_names = _articulation_points(self.adjacency)
        ranked = sorted(
            (node_metrics[name] for name in articulation_names),
            key=lambda item: (
                -float(item["betweenness"]),
                -int(item["degree"]),
                str(item["name"]).lower(),
            ),
        )
        return [self._public_person_metric(item) for item in ranked[:limit]]

    def _local_bridges(self, limit: int) -> list[dict[str, Any]]:
        bridges: list[dict[str, Any]] = []
        for left, right in sorted(self.edge_articles):
            if set(self.adjacency[left]) & set(self.adjacency[right]):
                continue
            weight = len(self.edge_articles[(left, right)])
            bridges.append(
                {
                    "left": left,
                    "left_role": self.role_by_name.get(left, "person"),
                    "right": right,
                    "right_role": self.role_by_name.get(right, "person"),
                    "shared_article_count": weight,
                    "left_degree": len(self.adjacency[left]),
                    "right_degree": len(self.adjacency[right]),
                }
            )
        bridges.sort(
            key=lambda item: (
                -int(item["shared_article_count"]),
                -(int(item["left_degree"]) + int(item["right_degree"])),
                str(item["left"]).lower(),
                str(item["right"]).lower(),
            )
        )
        return bridges[:limit]

    def _role_mixing(self, limit: int) -> list[dict[str, Any]]:
        pairs: dict[tuple[str, str], dict[str, Any]] = {}
        for (left, right), article_urls in self.edge_articles.items():
            left_role = self.role_by_name.get(left, "person")
            right_role = self.role_by_name.get(right, "person")
            role_pair = tuple(sorted((left_role, right_role)))
            item = pairs.setdefault(
                role_pair,
                {
                    "left_role": role_pair[0],
                    "right_role": role_pair[1],
                    "left_role_label": _role_label(role_pair[0]),
                    "right_role_label": _role_label(role_pair[1]),
                    "edge_count": 0,
                    "weighted_count": 0,
                },
            )
            item["edge_count"] += 1
            item["weighted_count"] += len(article_urls)
        ranked = sorted(
            pairs.values(),
            key=lambda item: (
                -int(item["weighted_count"]),
                -int(item["edge_count"]),
                str(item["left_role_label"]),
                str(item["right_role_label"]),
            ),
        )
        return ranked[:limit]

    def _emerging_people(
        self,
        node_metrics: dict[str, dict[str, Any]],
        limit: int,
    ) -> list[dict[str, Any]]:
        candidates = [metric for metric in node_metrics.values() if int(metric["recent_mentions"]) > 0]
        candidates.sort(
            key=lambda item: (
                -int(item["recent_mentions"]),
                -int(item["recent_degree"]),
                -int(item["weighted_degree"]),
                str(item["name"]).lower(),
            )
        )
        return [self._public_person_metric(item) for item in candidates[:limit]]

    def _community_summaries(
        self,
        components: list[list[str]],
        node_metrics: dict[str, dict[str, Any]],
        limit: int,
    ) -> list[dict[str, Any]]:
        summaries: list[dict[str, Any]] = []
        for index, component in enumerate(sorted(components, key=lambda item: (-len(item), item)), start=1):
            roles = Counter(self.role_by_name.get(name, "person") for name in component)
            top_people = sorted(
                component,
                key=lambda name: (
                    -int(node_metrics[name]["weighted_degree"]),
                    -int(node_metrics[name]["mention_count"]),
                    name.lower(),
                ),
            )[:8]
            summaries.append(
                {
                    "group": index,
                    "size": len(component),
                    "role_mix": [
                        {"role": role, "label": _role_label(role), "count": count}
                        for role, count in sorted(roles.items(), key=lambda item: (-item[1], item[0]))
                    ],
                    "top_people": top_people,
                }
            )
        return summaries[:limit]

    def _components(self) -> list[list[str]]:
        remaining = set(self.adjacency)
        components: list[list[str]] = []
        while remaining:
            start = min(remaining)
            stack = [start]
            component: list[str] = []
            remaining.remove(start)
            while stack:
                current = stack.pop()
                component.append(current)
                for neighbor in sorted(self.adjacency[current], reverse=True):
                    if neighbor in remaining:
                        remaining.remove(neighbor)
                        stack.append(neighbor)
            components.append(sorted(component))
        return components

    def _faculty_admin_bridge_scores(self) -> dict[str, dict[str, int]]:
        scores: dict[str, dict[str, int]] = {}
        for name, neighbors in self.adjacency.items():
            faculty_neighbors = [
                neighbor
                for neighbor in neighbors
                if self.role_by_name.get(neighbor) == "faculty"
            ]
            admin_neighbors = [
                neighbor
                for neighbor in neighbors
                if self.role_by_name.get(neighbor) == "administrator"
            ]
            role = self.role_by_name.get(name, "person")
            through_pairs = len(faculty_neighbors) * len(admin_neighbors)
            direct_cross_role = 0
            if role == "faculty":
                direct_cross_role = len(admin_neighbors)
            elif role == "administrator":
                direct_cross_role = len(faculty_neighbors)
            score = through_pairs + direct_cross_role
            scores[name] = {
                "score": score,
                "faculty_neighbors": len(faculty_neighbors),
                "administrator_neighbors": len(admin_neighbors),
            }
        return scores

    def _public_person_metric(self, item: dict[str, Any]) -> dict[str, Any]:
        keys = [
            "name",
            "role",
            "role_label",
            "degree",
            "weighted_degree",
            "mention_count",
            "source_count",
            "betweenness",
            "pagerank",
            "faculty_admin_bridge_score",
            "faculty_neighbor_count",
            "administrator_neighbor_count",
            "recent_mentions",
            "recent_degree",
            "first_seen",
            "last_seen",
        ]
        return {key: item[key] for key in keys}

    def _narratives(self) -> dict[str, str]:
        return {
            "scope": (
                "This report analyzes public co-mentions, not private relationships. "
                "A connection means two people appeared in the same stored Hood College source item. "
                "The measures are useful for discovering public visibility, repeated co-appearance, and possible brokerage patterns, "
                "but they should not be read as friendship, endorsement, authority, or institutional reporting lines."
            ),
            "overview": (
                "The overview gives the size and shape of the evidence graph. Density and connected groups help show whether coverage is still fragmented "
                "or beginning to form a single interpretable campus network."
            ),
            "strongest_bonds": (
                "Strongest bonds are ranked by repeated shared articles. The Jaccard score is included because it balances raw shared coverage against each person's total coverage, "
                "making smaller but consistently paired relationships visible alongside high-volume public figures."
            ),
            "role_leaders": (
                "Most connected people by role are ranked by weighted degree first, then ordinary degree. This answers role-specific questions such as who is the most connected faculty member, "
                "student, administrator, alumnus, or staff member in the public evidence graph."
            ),
            "faculty_visibility": (
                "Faculty public visibility combines mention count, source diversity, connection strength, and PageRank. This is the safest proxy for 'popular faculty' in the current dataset: "
                "it measures public prominence in collected sources, not student opinion or campus popularity."
            ),
            "faculty_administration_connectors": (
                "Faculty-administration connectors are people adjacent to both faculty and administrator neighborhoods, plus faculty or administrators with direct cross-role ties. "
                "This highlights public bridge figures between academic and administrative coverage."
            ),
            "brokers": (
                "Brokerage uses betweenness centrality, which rewards people who lie on many shortest paths between others. In this project, high values suggest public connector roles across otherwise separated coverage areas."
            ),
            "articulation_people": (
                "Articulation people are cut points: removing them would split at least one connected group into more pieces. This is a structural fragility signal, useful for finding people who hold sparse public subnetworks together."
            ),
            "local_bridges": (
                "Local bridges are co-mention edges whose endpoints do not share any other neighbor. These ties are useful weak-link indicators because they connect neighborhoods without being embedded in a dense triangle."
            ),
            "role_mixing": (
                "Role mixing counts which categories connect most often, such as faculty-student or faculty-administrator ties. This makes cross-role patterns visible without overclaiming the nature of the relationship."
            ),
            "emerging_people": (
                "Emerging people are ranked by recent mentions and recent degree over the last 30 days. This helps distinguish newly active public figures from people who are important only because of older accumulated coverage."
            ),
            "communities": (
                "Communities are reported here as connected groups in the current evidence graph. They are a conservative first step: later, this module can be replaced with modularity or label-propagation clustering when the graph grows larger."
            ),
        }


def _betweenness_centrality(adjacency: dict[str, dict[str, int]]) -> dict[str, float]:
    nodes = sorted(adjacency)
    centrality = dict.fromkeys(nodes, 0.0)
    for source in nodes:
        stack: list[str] = []
        predecessors: dict[str, list[str]] = {node: [] for node in nodes}
        shortest_counts = dict.fromkeys(nodes, 0.0)
        distances = dict.fromkeys(nodes, -1)
        shortest_counts[source] = 1.0
        distances[source] = 0
        queue = deque([source])
        while queue:
            current = queue.popleft()
            stack.append(current)
            for neighbor in adjacency[current]:
                if distances[neighbor] < 0:
                    queue.append(neighbor)
                    distances[neighbor] = distances[current] + 1
                if distances[neighbor] == distances[current] + 1:
                    shortest_counts[neighbor] += shortest_counts[current]
                    predecessors[neighbor].append(current)
        dependency = dict.fromkeys(nodes, 0.0)
        while stack:
            node = stack.pop()
            for predecessor in predecessors[node]:
                if shortest_counts[node] == 0:
                    continue
                dependency[predecessor] += (
                    shortest_counts[predecessor] / shortest_counts[node]
                ) * (1.0 + dependency[node])
            if node != source:
                centrality[node] += dependency[node]

    node_count = len(nodes)
    if node_count <= 2:
        return centrality
    scale = 1.0 / ((node_count - 1) * (node_count - 2))
    return {node: value * scale for node, value in centrality.items()}


def _pagerank(
    adjacency: dict[str, dict[str, int]],
    damping: float = 0.85,
    max_iterations: int = 100,
    tolerance: float = 1.0e-8,
) -> dict[str, float]:
    nodes = sorted(adjacency)
    node_count = len(nodes)
    if not nodes:
        return {}
    ranks = dict.fromkeys(nodes, 1.0 / node_count)
    for _ in range(max_iterations):
        dangling_rank = sum(ranks[node] for node in nodes if not adjacency[node])
        base = (1.0 - damping) / node_count
        next_ranks = dict.fromkeys(nodes, base + damping * dangling_rank / node_count)
        for node in nodes:
            total_weight = sum(adjacency[node].values())
            if total_weight == 0:
                continue
            for neighbor, weight in adjacency[node].items():
                next_ranks[neighbor] += damping * ranks[node] * (weight / total_weight)
        difference = sum(abs(next_ranks[node] - ranks[node]) for node in nodes)
        ranks = next_ranks
        if difference < tolerance:
            break
    return ranks


def _articulation_points(adjacency: dict[str, dict[str, int]]) -> set[str]:
    discovery: dict[str, int] = {}
    low: dict[str, int] = {}
    parent: dict[str, str | None] = {}
    points: set[str] = set()
    time = 0

    def visit(node: str) -> None:
        nonlocal time
        children = 0
        discovery[node] = time
        low[node] = time
        time += 1
        for neighbor in adjacency[node]:
            if neighbor not in discovery:
                parent[neighbor] = node
                children += 1
                visit(neighbor)
                low[node] = min(low[node], low[neighbor])
                if parent.get(node) is None and children > 1:
                    points.add(node)
                if parent.get(node) is not None and low[neighbor] >= discovery[node]:
                    points.add(node)
            elif neighbor != parent.get(node):
                low[node] = min(low[node], discovery[neighbor])

    for node in sorted(adjacency):
        if node not in discovery:
            parent[node] = None
            visit(node)
    return points


def _row_value(row: object, key: str, default: Any = None) -> Any:
    if isinstance(row, Mapping):
        return row.get(key, default)
    try:
        return row[key]  # type: ignore[index]
    except (KeyError, IndexError, TypeError):
        return getattr(row, key, default)


def _preferred_role(current_role: str, new_role: str) -> str:
    priority = {
        "person": 0,
        "guest": 1,
        "student": 2,
        "student-athlete": 3,
        "alumni": 3,
        "staff": 4,
        "coach": 4,
        "faculty": 5,
        "administrator": 6,
    }
    if priority.get(new_role, 0) >= priority.get(current_role, 0):
        return new_role
    return current_role


def _ordered_roles(role_counts: Counter[str]) -> list[str]:
    ordered = [role for role in ROLE_ORDER if role in role_counts]
    ordered.extend(sorted(role for role in role_counts if role not in ordered))
    return ordered


def _role_label(role: str) -> str:
    return ROLE_LABELS.get(role, role.replace("-", " ").title())


def _safe_divide(numerator: int | float, denominator: int | float) -> float:
    if denominator == 0:
        return 0.0
    return float(numerator) / float(denominator)
