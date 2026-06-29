"""§21 — Enums de estado (terminología canónica del glosario).

Placeholder: enums de estado de Comanda e Ítem de comanda y el ruteo. Los modelos
SQLAlchemy (Comanda, ItemComanda, DivisionCuenta) y su migración llegan en la
propuesta funcional de §21. Las transiciones (D-01, D-02, D-03...) no se codifican aquí.
"""

from __future__ import annotations

from enum import StrEnum


class EstadoComanda(StrEnum):
    ABIERTA = "Abierta"
    PENDIENTE_DE_COBRO = "Pendiente de cobro"
    CERRADA = "Cerrada"
    ANULADA = "Anulada"


class EstadoItemComanda(StrEnum):
    PENDIENTE = "Pendiente"
    ENVIADO = "Enviado"
    EN_PREPARACION = "En preparación"
    LISTO = "Listo"
    ENTREGADO = "Entregado"
    RECHAZADO = "Rechazado"
    ANULADO = "Anulado"


class Ruteo(StrEnum):
    COCINA = "cocina"
    BARRA = "barra"
