"""
Knowledge Graph Engine using NetworkX.
Represents skill prerequisites and enables:
- Prerequisite checking
- Topological ordering of skills
- Prerequisite-aware learning path generation
"""
import os
import csv
import networkx as nx
from typing import List, Set, Dict, Optional

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data")


class LearningKnowledgeGraph:
    """
    Directed graph where edges represent PREREQUISITE relationships.
    Edge: prerequisite → skill  means "learn prerequisite before skill"
    """

    def __init__(self):
        self.graph = nx.DiGraph()
        self._load_from_csv()

    def _load_from_csv(self):
        """Load skill prerequisite relationships from prerequisites.csv."""
        path = os.path.join(DATA_DIR, "prerequisites.csv")
        if not os.path.exists(path):
            print("⚠️  prerequisites.csv not found, building empty graph.")
            return

        with open(path, newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                skill = row["skill"].strip()
                prerequisite = row["prerequisite"].strip()
                # Add directed edge: prerequisite → skill
                self.graph.add_edge(prerequisite, skill,
                                    relation="PREREQUISITE")

        # Ensure all nodes have a label attribute
        for node in self.graph.nodes:
            self.graph.nodes[node].setdefault("label", node)

        print(f"✅ Knowledge graph loaded: {self.graph.number_of_nodes()} nodes, "
              f"{self.graph.number_of_edges()} edges.")

    def add_skill(self, skill: str, prerequisites: List[str] = None):
        """Dynamically add a skill and its prerequisites to the graph."""
        self.graph.add_node(skill)
        for prereq in (prerequisites or []):
            self.graph.add_edge(prereq, skill, relation="PREREQUISITE")

    def get_prerequisites(self, skill: str) -> Set[str]:
        """Return ALL prerequisite skills (transitive ancestors) for a given skill."""
        if skill not in self.graph:
            return set()
        # Predecessors in the transitive closure
        return set(nx.ancestors(self.graph, skill))

    def get_direct_prerequisites(self, skill: str) -> List[str]:
        """Return only direct (immediate) prerequisites for a skill."""
        if skill not in self.graph:
            return []
        return list(self.graph.predecessors(skill))

    def get_dependent_skills(self, skill: str) -> List[str]:
        """Return skills that DEPEND ON (come after) the given skill."""
        if skill not in self.graph:
            return []
        return list(nx.descendants(self.graph, skill))

    def is_prerequisite_satisfied(self, skill: str, user_skills: Dict[str, float],
                                   min_proficiency: float = 40.0) -> bool:
        """
        Check if all prerequisites for a skill are satisfied.
        A prerequisite is satisfied if the user has >= min_proficiency in it.
        """
        direct_prereqs = self.get_direct_prerequisites(skill)
        for prereq in direct_prereqs:
            if user_skills.get(prereq, 0.0) < min_proficiency:
                return False
        return True

    def get_missing_prerequisites(self, skill: str,
                                   user_skills: Dict[str, float],
                                   min_proficiency: float = 40.0) -> List[str]:
        """Return list of prerequisites not yet satisfied for a skill."""
        direct_prereqs = self.get_direct_prerequisites(skill)
        return [p for p in direct_prereqs if user_skills.get(p, 0.0) < min_proficiency]

    def topological_learning_order(self, skills: List[str]) -> List[str]:
        """
        Return skills in topological order (prerequisites before dependents).
        Skills not in the graph are placed at the beginning.
        """
        # Build subgraph of only the requested skills
        subgraph_nodes = set(skills)
        # Add transitive prerequisites of skills that are also in skills list
        for skill in list(skills):
            for anc in nx.ancestors(self.graph, skill) if skill in self.graph else []:
                if anc in subgraph_nodes:
                    subgraph_nodes.add(anc)

        sub = self.graph.subgraph(subgraph_nodes)
        try:
            ordered = list(nx.topological_sort(sub))
        except nx.NetworkXUnfeasible:
            # Cycle detected — fall back to original order
            ordered = skills

        # Include any skills that were in the input but not in graph
        in_graph = set(ordered)
        extra = [s for s in skills if s not in in_graph]
        return extra + ordered

    def generate_learning_phases(
        self,
        target_skills: List[str],
        user_skills: Dict[str, float],
        skill_gaps: List[Dict],
        career_goal: str = "",
    ) -> List[Dict]:
        """
        Generate ordered learning phases accounting for prerequisites.

        Each phase contains:
          - phase number
          - skill to learn
          - prerequisites (satisfied/missing)
          - priority (gap size)
          - is_unlocked (all prereqs satisfied)
        """
        # Only include skills with gaps > 5
        skills_with_gaps = [
            sg for sg in skill_gaps
            if sg.get("gap", 0) > 5 and sg["skill"] in target_skills
        ]

        # Also add prerequisite skills that aren't in target but needed
        needed_prereqs = set()
        for sg in skills_with_gaps:
            for prereq in self.get_direct_prerequisites(sg["skill"]):
                if prereq not in [s["skill"] for s in skills_with_gaps]:
                    if user_skills.get(prereq, 0) < 50:
                        needed_prereqs.add(prereq)

        all_skills = [sg["skill"] for sg in skills_with_gaps] + list(needed_prereqs)
        ordered = self.topological_learning_order(all_skills)

        gap_map = {sg["skill"]: sg for sg in skill_gaps}

        phases = []
        phase_num = 1
        for skill in ordered:
            sg = gap_map.get(skill, {
                "skill": skill, "current": user_skills.get(skill, 0),
                "target": 70, "gap": max(0, 70 - user_skills.get(skill, 0)),
                "gap_category": "Moderate Gap"
            })
            missing_prereqs = self.get_missing_prerequisites(skill, user_skills)
            is_unlocked = len(missing_prereqs) == 0

            phases.append({
                "phase": phase_num,
                "skill": skill,
                "current_proficiency": sg.get("current", 0),
                "target_proficiency": sg.get("target", 80),
                "gap": sg.get("gap", 0),
                "gap_category": sg.get("gap_category", "Moderate Gap"),
                "prerequisites": self.get_direct_prerequisites(skill),
                "missing_prerequisites": missing_prereqs,
                "is_unlocked": is_unlocked,
                "status": "available" if is_unlocked else "locked",
            })
            phase_num += 1

        # First phase is always current
        if phases:
            phases[0]["status"] = "in_progress"

        return phases

    def get_graph_data(self) -> Dict:
        """Return graph data suitable for visualization."""
        nodes = [{"id": n, "label": n, "domain": self.graph.nodes[n].get("domain", "")}
                 for n in self.graph.nodes]
        edges = [{"source": u, "target": v, "relation": d.get("relation", "PREREQUISITE")}
                 for u, v, d in self.graph.edges(data=True)]
        return {"nodes": nodes, "edges": edges}


# Singleton instance
_graph_instance: Optional[LearningKnowledgeGraph] = None


def get_knowledge_graph() -> LearningKnowledgeGraph:
    """Return the singleton knowledge graph instance."""
    global _graph_instance
    if _graph_instance is None:
        _graph_instance = LearningKnowledgeGraph()
    return _graph_instance
