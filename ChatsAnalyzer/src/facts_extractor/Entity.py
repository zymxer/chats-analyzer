from dataclasses import dataclass


@dataclass
class Entity:
    id: int
    name: str

    def __str__(self):
        return f"{self.name}"
