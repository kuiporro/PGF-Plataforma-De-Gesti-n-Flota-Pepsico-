from django.utils import timezone
from .models import OrdenTrabajo
# Definición de transiciones válidas
VALID_TRANSITIONS = {
    "ABIERTA": {"EN_EJECUCION", "ANULADA"},
    "EN_EJECUCION": {"EN_QA", "ANULADA"},
    "EN_QA": {"CERRADA", "EN_EJECUCION"},
    "CERRADA": set(),
    "ANULADA": set(),
}

def can_transition(current: str, target: str) -> bool:
    return target in VALID_TRANSITIONS.get(current, set())

def transition(ot, target: str):
    if not can_transition(ot.estado, target):
        return False, f"Transición inválida: {ot.estado} → {target}"
    ot.estado = target
    if target == "CERRADA":
        ot.cierre = timezone.now()
    ot.save(update_fields=["estado","cierre"] if target == "CERRADA" else ["estado"])
    return True, None
def do_transition(ot, target: str):
    ok, err = transition(ot, target)
    if not ok:
        raise ValueError(err)

