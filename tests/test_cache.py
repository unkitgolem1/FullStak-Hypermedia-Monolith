import time
import pytest
from database import CacheTTL


def test_guarda_y_obtiene_valor():
    cache = CacheTTL(ttl_segundos=60)
    cache.guardar("foo", {"data": 42})
    assert cache.obtener("foo") == {"data": 42}


def test_obtener_devuelve_none_si_no_existe():
    cache = CacheTTL(ttl_segundos=60)
    assert cache.obtener("no-existe") is None


def test_obtener_devuelve_none_si_expiro():
    cache = CacheTTL(ttl_segundos=1)
    cache.guardar("bar", "valor")
    time.sleep(1.5)
    assert cache.obtener("bar") is None


def test_limpiar_vacia_todo():
    cache = CacheTTL(ttl_segundos=60)
    cache.guardar("a", 1)
    cache.guardar("b", 2)
    cache.limpiar()
    assert cache.obtener("a") is None
    assert cache.obtener("b") is None


def test_ttls_diferentes_por_instancia():
    rapido = CacheTTL(ttl_segundos=30)
    lento = CacheTTL(ttl_segundos=120)
    rapido.guardar("x", "rapido")
    lento.guardar("x", "lento")
    rapido._cache["x"] = (0, "rapido")
    assert rapido.obtener("x") is None
    assert lento.obtener("x") == "lento"


def test_sobrescribe_misma_clave():
    cache = CacheTTL(ttl_segundos=60)
    cache.guardar("key", "v1")
    cache.guardar("key", "v2")
    assert cache.obtener("key") == "v2"


def test_tipos_de_valores():
    cache = CacheTTL()
    cache.guardar("str", "hola")
    cache.guardar("int", 42)
    cache.guardar("list", [1, 2, 3])
    cache.guardar("dict", {"a": 1})
    assert cache.obtener("str") == "hola"
    assert cache.obtener("int") == 42
    assert cache.obtener("list") == [1, 2, 3]
    assert cache.obtener("dict") == {"a": 1}


def test_no_comparten_estado_instancias_distintas():
    a = CacheTTL()
    b = CacheTTL()
    a.guardar("clave", "de-a")
    assert b.obtener("clave") is None
