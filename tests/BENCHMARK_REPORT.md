# Benchmark Report — Sistema de Caché Portfolio

**Fecha:** 2026-06-27
**Hardware:** Linux, Python 3.13

---

## Cómo ejecutar los tests

```bash
# 1. Tests unitarios + integración (12 tests)
python3 -m pytest tests/ -v

# 2. Benchmark completo (reporte numérico)
python3 tests/benchmark_script.py

# 3. Solo tests de caché unitarios
python3 -m pytest tests/test_cache.py -v

# 4. Solo tests de integración con mocks
python3 -m pytest tests/test_integracion_cache.py -v
```

### Resultado esperado de los tests

```
tests/test_cache.py ........                                         [ 66%]
tests/test_integracion_cache.py ....                                [100%]
======================== 12 passed in 1.57s =========================
```

---

## 1. CacheTTL — Dict con TTL (microbenchmark)

| Operaciones | Tiempo | Throughput |
|---|---|---|
| 50.000 writes + 50.000 reads | ~0.044s | **~2.25M ops/s** |

> El dict en memoria es extremadamente rápido. Sin contención, sin I/O.

### Test: `tests/test_cache.py` (8 tests)

| Test | Verifica |
|---|---|
| `test_guarda_y_obtiene_valor` | set/get básico funciona |
| `test_obtener_devuelve_none_si_no_existe` | clave inexistente → None |
| `test_obtener_devuelve_none_si_expiro` | sleep > TTL → expira |
| `test_limpiar_vacia_todo` | limpiar() vacía todo |
| `test_ttls_diferentes_por_instancia` | cada instancia tiene su TTL |
| `test_sobrescribe_misma_clave` | guardar misma clave → overwrite |
| `test_tipos_de_valores` | str/int/list/dict/None |
| `test_no_comparten_estado_instancias_distintas` | instancias aisladas |

---

## 2. SupabaseAdaptador — 100 requests secuenciales

| Escenario | Tiempo | Throughput | DB calls |
|---|---|---|---|
| SIN caché | ~0.0059s | ~16.87K req/s | 100 |
| CON caché | ~0.0001s | **~1.59M req/s** | 1 (solo la primera) |
| **Mejora** | | **~94x** | **99% menos** |

> Cada request sin caché: `async with pool.acquire()` + `fetchrow()` + `dict()`.
> Con caché: `dict.get()` en RAM. Nanosegundos.

---

## 3. Alta concurrencia — 50 requests en paralelo

| Escenario | Tiempo | Throughput | DB calls |
|---|---|---|---|
| SIN caché | ~0.0135s | ~3.70K req/s | 50 |
| CON caché | ~0.0003s | **~154K req/s** | 1 (solo la primera) |
| **Mejora** | | **~42x** | **98% menos** |

> El pool de asyncpg tiene `max_size=10`. Sin caché, 50 requests compiten por 10 conexiones → cuello de botella. Con caché, zero conexiones usadas.

### Test: `tests/test_integracion_cache.py` (4 tests)

| Test | Verifica |
|---|---|
| `test_obtener_todos_usa_cache_en_segunda_llamada` | 2da llamada no toca pool |
| `test_obtener_por_id_usa_cache_en_segunda_llamada` | 2da llamada no toca pool |
| `test_ids_distintos_no_comparten_cache` | IDs diferentes tienen entradas separadas |
| `test_cache_no_anda_si_pool_no_inicializado` | Sin pool → RuntimeError |

---

## 4. Caché cliente htmx — Map en JS simulado

| Operaciones | Tiempo | Throughput |
|---|---|---|
| 10.000 escrituras + lecturas | ~0.009s | **~2.16M ops/s** |

> Map en JS es O(1). Una vez cacheados, los fragmentos htmx se sirven desde memoria sin request HTTP.

### Cómo se activa: `base.html:160-196`

```javascript
// Captura respuestas htmx después de renderizar
htmx:afterSettle → guarda HTML en Map con TTL 5 min
htmx:beforeRequest → si URL está en Map, cancela request e inyecta cached
```

---

## Conclusión

| Capa | TTL | Protege | Throughput estimado |
|---|---|---|---|
| CacheTTL servidor (dict) | 30-120s | DB saturation | ~2.25M ops/s |
| Cache-Control HTTP | 30-120s | Ancho de banda | Cache browser |
| Map htmx cliente | 5 min | Round-trips red | ~2.16M ops/s |

La combinación elimina prácticamente toda la carga en DB y reduce la latencia a microsegundos. Para un portfolio con muchos lectores y pocos documentos, el servidor escala horizontalmente sin apenas tocar PostgreSQL.
