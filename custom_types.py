# fichier: types.py
from typing import Optional, TypedDict

# Définition des types basés sur le fichier TypeScript
class Vo(TypedDict, total=False):
    main: Optional[str]

class Female(TypedDict, total=False):
    text: Optional[str]
    vo: Optional[Vo]

class Dialogue(TypedDict):
    id: str
    female: Optional[Female]
    _path: str
