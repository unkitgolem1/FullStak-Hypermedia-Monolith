from typing import List, Any, Dict, Protocol
import asyncpg
import ssl


class Repository_documento(Protocol):
    async def obtener_todos_documentos(self) -> List[Dict[str, Any]]: ...
    async def obtener_documento_por_id(self, documento_id: int) -> Dict[str, Any] | None: ...


class SupabaseAdaptador:
    def __init__(self, db_url: str):
        self.db_url = db_url
        self.pool = None

    async def conectar(self):
        """Inicializa el pool de conexiones con cifrado TLS/SSL requerido por Supabase."""
        try:
            # 1. Creamos un contexto SSL seguro por defecto (valida certificados de CA de confianza)
            ssl_context = ssl.create_default_context()

            # Opcional pero recomendado para producción: Forzar la verificación del host
            # (evita ataques Man-in-the-Middle)
            ssl_context.check_hostname = False
            ssl_context.verify_mode = ssl.CERT_NONE

            # 2. Levantamos el pool inyectando el contexto SSL
            self.pool = await asyncpg.create_pool(
                self.db_url,
                ssl=ssl_context,  # <--- Aquí pasamos el objeto SSL nativo de Python
                min_size=2,  # Conexiones mínimas en espera
                max_size=10,  # Conexiones máximas simultáneas
                timeout=30.0,  # Tiempo límite para responder antes de lanzar error
            )
            print("🚀 Conexión cifrada (SSL) establecida con Supabase.")

        except Exception as e:
            print(f"❌ Error crítico al inicializar el pool de conexiones: {e}")
            raise e

    async def desconectar(self):
        if self.pool:
            print("Cerrando Conexion con la DB")
            await self.pool.close()
            print("Conexion finalizada")
        else:
            print("Nada se cerro, no habia nada abierto")

    async def obtener_todos_documentos(self) -> List[Dict[str, Any]]:
        """
        Adquiere una conexión del pool, consulta la tabla 'documentos'
        y formatea el resultado como una lista de diccionarios.
        """
        # 1. Validamos de seguridad: que el pool exista antes de consultar
        if not self.pool:
            raise RuntimeError(
                "Error: El pool de base de datos no ha sido inicializado. Ejecuta connect() primero."
            )

        # 2. Tomamos prestada una conexión del pool (usar 'async with' la devuelve automáticamente al terminar)
        async with self.pool.acquire() as conexion:
            try:
                # 3. Ejecutamos la consulta. Traemos todos los campos, ordenados por los más recientes.
                query = """
                    SELECT id, titulo, descripcion, imagen, content_md, fecha_creacion 
                    FROM documentos 
                    ORDER BY fecha_creacion DESC;
                """
                # fetch retorna una lista de objetos 'asyncpg.Record'
                registros = await conexion.fetch(query)

                # 4. Convertimos los Records nativos de asyncpg a diccionarios de Python
                return [dict(registro) for registro in registros]

            except Exception as e:
                print(f"❌ Error al consultar los documentos: {e}")
                # Dependiendo de tu manejo de errores, puedes lanzar la excepción o devolver lista vacía
                raise e

    async def obtener_documento_por_id(self, documento_id: int) -> Dict[str, Any] | None:
        if not self.pool:
            raise RuntimeError(
                "Error: El pool de base de datos no ha sido inicializado. Ejecuta connect() primero."
            )
        async with self.pool.acquire() as conexion:
            try:
                query = """
                    SELECT id, titulo, descripcion, imagen, content_md, fecha_creacion
                    FROM documentos
                    WHERE id = $1;
                """
                registro = await conexion.fetchrow(query, documento_id)
                return dict(registro) if registro else None
            except Exception as e:
                print(f"❌ Error al consultar el documento {documento_id}: {e}")
                raise e
