#!/usr/bin/env python3
"""
Script de depuración para probar el flujo completo de RUC
"""

import json
from services.empresa_service import EmpresaService

if __name__ == "__main__":
    ruc_test = "20601674344"

    print("=== PROBANDO FLUJO COMPLETO DE RUC ===")
    resultado = EmpresaService.buscar_por_ruc(ruc_test)
    print(json.dumps(resultado, indent=2, ensure_ascii=False))
