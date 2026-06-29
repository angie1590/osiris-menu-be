"""§22 — Sin entidades propias.

El módulo consume `ItemComanda` de §21 (filtrado por ruteo) y `Producto`/`Receta` de
§25/§26. El ruteo canónico vive en `modules.comandas.models.Ruteo`. Aquí no se declaran
tablas ni enums nuevos.
"""

from __future__ import annotations

from ..comandas.models import Ruteo

__all__ = ["Ruteo"]
