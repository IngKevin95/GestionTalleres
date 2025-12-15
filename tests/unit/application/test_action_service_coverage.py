"""Tests adicionales para aumentar cobertura de action_service.py"""

import pytest
from unittest.mock import Mock, patch
from app.application.action_service import ActionService
from app.application.dtos import OrdenDTO
from app.domain.enums import CodigoError, EstadoOrden




