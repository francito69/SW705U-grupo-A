"""Módulos de dominio del monolito modular (SAD 5.1.2).

Importar este paquete registra todos los modelos en Base.metadata.
"""

from .seguridad import models as _seguridad  # noqa: F401
from .convenios import models as _convenios  # noqa: F401
from .hce import models as _hce  # noqa: F401
from .agenda import models as _agenda  # noqa: F401
from .auditoria import models as _auditoria  # noqa: F401
from .notificaciones import models as _notificaciones  # noqa: F401
from . import ddl as _ddl  # noqa: F401
