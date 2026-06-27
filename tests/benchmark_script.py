"""Benchmark independiente del sistema de caché.
Ejecutar: python tests/benchmark_script.py
"""

import asyncio
import sys
import time
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))
from database import CacheTTL, SupabaseAdaptador


def fmt(n):
    if n >= 1_000_000:
        return f"{n/1_000_000:.2f}M"
    if n >= 1_000:
        return f"{n/1_000:.2f}K"
    return f"{n:.2f}"


class RecordFake(dict):
    pass


# ─── Benchmark 1: CacheTTL puro (microbenchmark) ────────────────────────────

def bench_cache_ttl_speed():
    N = 50_000
    cache = CacheTTL(ttl_segundos=300)

    inicio = time.perf_counter()
    for i in range(N):
        cache.guardar(f"k{i}", i)
    for i in range(N):
        _ = cache.obtener(f"k{i}")
    duracion = time.perf_counter() - inicio

    ops = (N * 2) / duracion
    print(f"  {N} writes + {N} reads en {duracion:.3f}s → {fmt(ops)} ops/s")


# ─── Benchmark 2: Adaptador con/sin caché (100 requests secuenciales) ───────

async def bench_adaptador_secuencial():
    doc = {"id": 1, "titulo": "T", "descripcion": "x", "imagen": None, "content_md": None, "fecha_creacion": None}

    a = SupabaseAdaptador("postgres://fake:5432/db")
    a.pool = MagicMock()
    mock_con = AsyncMock()
    mock_con.fetchrow = AsyncMock(return_value=RecordFake(doc))
    a.pool.acquire.return_value.__aenter__ = AsyncMock(return_value=mock_con)
    a.pool.acquire.return_value.__aexit__ = AsyncMock()

    N = 100

    # ── Sin caché (TTL=0) ──
    a.cache_individual = CacheTTL(ttl_segundos=0)
    inicio = time.perf_counter()
    for _ in range(N):
        await a.obtener_documento_por_id(1)
    t_sin = time.perf_counter() - inicio

    # ── Con caché ──
    a.cache_individual = CacheTTL(ttl_segundos=120)
    mock_con.fetchrow.call_count = 0
    await a.obtener_documento_por_id(1)  # poblar caché
    inicio = time.perf_counter()
    for _ in range(N):
        await a.obtener_documento_por_id(1)
    t_con = time.perf_counter() - inicio

    print(f"  {N} requests SIN caché: {t_sin:.4f}s → {fmt(N/t_sin)} req/s")
    print(f"  {N} requests CON caché: {t_con:.4f}s → {fmt(N/t_con)} req/s")
    print(f"  Mejora: {t_sin/t_con:.1f}x más rápido")


# ─── Benchmark 3: Concurrencia (50 requests en paralelo) ────────────────────

async def bench_concurrencia():
    a_sin = SupabaseAdaptador("postgres://fake:5432/db")
    a_con = SupabaseAdaptador("postgres://fake:5432/db")

    for a in (a_sin, a_con):
        a.pool = MagicMock()
        mock_con = AsyncMock()
        a.pool.acquire.return_value.__aenter__ = AsyncMock(return_value=mock_con)
        a.pool.acquire.return_value.__aexit__ = AsyncMock()

        async def fetch_slow(*args, **kwargs):
            await asyncio.sleep(0.01)
            return []

        mock_con.fetch = AsyncMock(side_effect=fetch_slow)
        a.cache_todos = CacheTTL(ttl_segundos=0)

    # Poblar caché en a_con
    a_con.cache_todos = CacheTTL(ttl_segundos=120)
    await a_con.obtener_todos_documentos()
    a_con.cache_todos._cache["todos"] = (
        time.time() + 120,
        [{"id": 1, "titulo": "A", "descripcion": "x", "imagen": None, "content_md": None, "fecha_creacion": None}],
    )

    N_CONCURRENTES = 50

    # Sin caché
    inicio = time.perf_counter()
    await asyncio.gather(*[a_sin.obtener_todos_documentos() for _ in range(N_CONCURRENTES)])
    t_sin = time.perf_counter() - inicio

    # Con caché
    inicio = time.perf_counter()
    await asyncio.gather(*[a_con.obtener_todos_documentos() for _ in range(N_CONCURRENTES)])
    t_con = time.perf_counter() - inicio

    # Contar cuántas veces se tocó el mock de fetch
    fetch_sin = a_sin.pool.acquire.return_value.__aenter__.return_value.fetch.call_count
    fetch_con = a_con.pool.acquire.return_value.__aenter__.return_value.fetch.call_count

    print(f"  {N_CONCURRENTES} concurrentes SIN caché: {t_sin:.4f}s → {fmt(N_CONCURRENTES/t_sin)} req/s [{fetch_sin} DB calls]")
    print(f"  {N_CONCURRENTES} concurrentes CON caché: {t_con:.4f}s → {fmt(N_CONCURRENTES/t_con)} req/s [{fetch_con} DB calls]")
    print(f"  Mejora: {t_sin/t_con:.1f}x más rápido, DB: {fetch_sin}→{fetch_con} consultas")


# ─── Benchmark 4: Caché cliente htmx (simulado) ────────────────────────────

def bench_cliente_htmx():
    """Simula el Map cache del lado del cliente con 1000 URLs."""
    N = 10_000
    cache = {}
    TTL = 300_000

    inicio = time.perf_counter()
    for i in range(N):
        cache[f"/api/contenido-md/{i}"] = {
            "html": f"<p>contenido {i}</p>",
            "expira": time.time() * 1000 + TTL,
        }
    for i in range(N):
        cached = cache.get(f"/api/contenido-md/{i}")
        if cached and time.time() * 1000 < cached["expira"]:
            _ = cached["html"]
    duracion = time.perf_counter() - inicio
    print(f"  {N} escrituras+lecturas en Map JS simulado: {duracion:.3f}s → {fmt(N*2/duracion)} ops/s")


# ─── Main ───────────────────────────────────────────────────────────────────

print(f"\n{'='*60}")
print(f"  BENCHMARKS - Sistema de Caché Portfolio")
print(f"{'='*60}\n")

print("📦 CacheTTL (dict con TTL):")
bench_cache_ttl_speed()

print(f"\n🔁 SupabaseAdaptador (100 requests secuenciales):")
asyncio.run(bench_adaptador_secuencial())

print(f"\n⚡ Alta concurrencia (50 requests paralelos):")
asyncio.run(bench_concurrencia())

print(f"\n🌐 Caché cliente htmx simulado:")
bench_cliente_htmx()

print(f"\n{'='*60}")
print(f"  FIN")
print(f"{'='*60}\n")
