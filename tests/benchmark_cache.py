"""Benchmarks del sistema de caché.

Mide:
  - Velocidad de get/set del CacheTTL
  - Throughput del adaptador con caché vs sin caché
  - Latencia simulada en alta concurrencia
"""

import time
import asyncio
import pytest
from unittest.mock import AsyncMock, MagicMock
from database import CacheTTL, SupabaseAdaptador


# ─── Fixtures ────────────────────────────────────────────────────────────────

@pytest.fixture
def adaptador_con_cache():
    """Adaptador con pool mockeado y caché activo."""
    a = SupabaseAdaptador("postgres://fake:5432/db")
    a.pool = MagicMock()
    mock_con = AsyncMock()
    mock_con.fetch = AsyncMock(return_value=[])
    mock_con.fetchrow = AsyncMock(return_value=None)
    a.pool.acquire.return_value.__aenter__ = AsyncMock(return_value=mock_con)
    a.pool.acquire.return_value.__aexit__ = AsyncMock()
    return a


# ─── Benchmarks: CacheTTL puro ──────────────────────────────────────────────

def test_cache_ttl_get_set_rapido(benchmark):
    """Microbenchmark: velocidad de guardar y leer 1000 veces."""
    cache = CacheTTL(ttl_segundos=300)

    def ciclo():
        for i in range(1000):
            cache.guardar(f"k{i}", i)
        for i in range(1000):
            _ = cache.obtener(f"k{i}")

    benchmark(ciclo)


# ─── Benchmarks: SupabaseAdaptador ──────────────────────────────────────────

@pytest.mark.asyncio
async def test_adaptador_cache_vs_no_cache(benchmark, adaptador_con_cache):
    """Compara latencia con caché activo en la segunda llamada."""
    doc = {"id": 1, "titulo": "A", "descripcion": "x",
           "imagen": None, "content_md": None, "fecha_creacion": None}
    adaptador_con_cache.pool.acquire.return_value.__aenter__.return_value.fetchrow \
        = AsyncMock(return_value=type("R", (), {"__getitem__": lambda s, k: doc[k], "__iter__": lambda s: iter(doc.keys())})())

    # Primera llamada: llena el caché
    await adaptador_con_cache.obtener_documento_por_id(1)

    async def llamada_cacheadas():
        for _ in range(100):
            await adaptador_con_cache.obtener_documento_por_id(1)

    benchmark(lambda: asyncio.run(llamada_cacheadas()))


@pytest.mark.asyncio
async def test_concurrencia_alta_sin_cache(benchmark):
    """Simula 50 requests concurrentes SIN cache (cada uno va a DB)."""
    a = SupabaseAdaptador("postgres://fake:5432/db")
    a.cache_todos = CacheTTL(ttl_segundos=0)     # caché desactivado
    a.cache_individual = CacheTTL(ttl_segundos=0)

    a.pool = MagicMock()
    mock_con = AsyncMock()

    async def fetch_slow(*args, **kwargs):
        await asyncio.sleep(0.01)  # simula latencia de red a DB
        return []

    mock_con.fetch = AsyncMock(side_effect=fetch_slow)
    a.pool.acquire.return_value.__aenter__ = AsyncMock(return_value=mock_con)
    a.pool.acquire.return_value.__aexit__ = AsyncMock()

    async def asedio():
        tareas = [a.obtener_todos_documentos() for _ in range(50)]
        await asyncio.gather(*tareas)

    benchmark(lambda: asyncio.run(asedio()))


@pytest.mark.asyncio
async def test_concurrencia_alta_con_cache(benchmark):
    """Simula 50 requests concurrentes CON cache (solo 1 va a DB)."""
    a = SupabaseAdaptador("postgres://fake:5432/db")

    a.pool = MagicMock()
    mock_con = AsyncMock()

    call_count = 0

    async def fetch_once(*args, **kwargs):
        nonlocal call_count
        call_count += 1
        await asyncio.sleep(0.01)
        return []

    mock_con.fetch = AsyncMock(side_effect=fetch_once)
    a.pool.acquire.return_value.__aenter__ = AsyncMock(return_value=mock_con)
    a.pool.acquire.return_value.__aexit__ = AsyncMock()

    # Primera llamada para poblar caché
    await a.obtener_todos_documentos()
    call_count = 0

    async def asedio():
        tareas = [a.obtener_todos_documentos() for _ in range(50)]
        await asyncio.gather(*tareas)

    benchmark(lambda: asyncio.run(asedio()))

    # Verificamos que la DB se tocó 0 veces durante el asedio
    assert call_count == 0, f"Se hicieron {call_count} consultas a DB, se esperaban 0"
