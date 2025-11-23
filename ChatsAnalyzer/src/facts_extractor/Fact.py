from dataclasses import dataclass

from src.facts_extractor.Entity import Entity


@dataclass
class Fact:
    subject: Entity
    verb: str
    object: Entity

    def __str__(self):
        return f"({self.subject},{self.verb},{self.object})"
