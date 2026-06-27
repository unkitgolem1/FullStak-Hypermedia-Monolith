import pytest
from unittest.mock import AsyncMock, MagicMock
from database import SupabaseAdaptador


@pytest.fixture
def adaptador():
    a = SupabaseAdaptador("postgres://fake:5432/db")
    a.pool = MagicMock()
    return a


class RecordFake(dict):
    """Simula el comportamiento de un asyncpg.Record (soporta dict() y acceso por clave)."""
    pass


def _make_record(data: dict):
    return RecordFake(data)


@pytest.mark.asyncio
async def test_obtener_todos_usa_cache_en_segunda_llamada(adaptador):
    doc = {"id": 1, "titulo": "A", "descripcion": "x", "imagen": None, "content_md": None, "fecha_creacion": None}

    mock_con = AsyncMock()
    mock_con.fetch = AsyncMock(return_value=[_make_record(doc)])

    adaptador.pool.acquire.return_value.__aenter__ = AsyncMock(return_value=mock_con)
    adaptador.pool.acquire.return_value.__aexit__ = AsyncMock()

    primera = await adaptador.obtener_todos_documentos()
    assert primera is not None
    assert adaptador.cache_todos.obtener("todos") is not None

    segunda = await adaptador.obtener_todos_documentos()
    assert segunda == primera
    assert mock_con.fetch.call_count == 1


@pytest.mark.asyncio
async def test_obtener_por_id_usa_cache_en_segunda_llamada(adaptador):
    doc = {"id": 1, "titulo": "Test", "descripcion": "x", "imagen": None, "content_md": "# Hola", "fecha_creacion": None}

    mock_con = AsyncMock()
    mock_con.fetchrow = AsyncMock(return_value=_make_record(doc))

    adaptador.pool.acquire.return_value.__aenter__ = AsyncMock(return_value=mock_con)
    adaptador.pool.acquire.return_value.__aexit__ = AsyncMock()

    primera = await adaptador.obtener_documento_por_id(1)
    assert primera is not None
    assert adaptador.cache_individual.obtener("doc:1") is not None

    segunda = await adaptador.obtener_documento_por_id(1)
    assert segunda == primera
    assert mock_con.fetchrow.call_count == 1


@pytest.mark.asyncio
async def test_ids_distintos_no_comparten_cache(adaptador):
    doc1 = {"id": 1, "titulo": "Uno", "descripcion": "x", "imagen": None, "content_md": None, "fecha_creacion": None}
    doc2 = {"id": 2, "titulo": "Dos", "descripcion": "y", "imagen": None, "content_md": None, "fecha_creacion": None}

    mock_con = AsyncMock()
    mock_con.fetchrow = AsyncMock(side_effect=lambda q, i: _make_record(doc1 if i == 1 else doc2))

    adaptador.pool.acquire.return_value.__aenter__ = AsyncMock(return_value=mock_con)
    adaptador.pool.acquire.return_value.__aexit__ = AsyncMock()

    r1 = await adaptador.obtener_documento_por_id(1)
    r2 = await adaptador.obtener_documento_por_id(2)
    assert r1["id"] == 1
    assert r2["id"] == 2

    assert adaptador.cache_individual.obtener("doc:1")["id"] == 1
    assert adaptador.cache_individual.obtener("doc:2")["id"] == 2


@pytest.mark.asyncio
async def test_cache_no_anda_si_pool_no_inicializado(adaptador):
    adaptador.pool = None
    with pytest.raises(RuntimeError, match="no ha sido inicializado"):
        await adaptador.obtener_todos_documentos()
