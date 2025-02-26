from database.db_connection import get_db_session
from database.models import Enfermedad
from sqlalchemy import func

def obtener_datos(fecha_inicio=None, fecha_fin=None, provincia=None):
    """Obtiene datos según los filtros aplicados."""
    session = get_db_session()
    
    consulta = session.query(
        Enfermedad.codigo_postal, 
        Enfermedad.provincia,
        Enfermedad.latitud,
        Enfermedad.longitud,
        func.sum(Enfermedad.casos).label("total_casos")
    ).group_by(Enfermedad.codigo_postal, Enfermedad.provincia, Enfermedad.latitud, Enfermedad.longitud)

    if fecha_inicio and fecha_fin:
        consulta = consulta.filter(Enfermedad.fecha.between(fecha_inicio, fecha_fin))
    
    if provincia:
        consulta = consulta.filter(Enfermedad.provincia == provincia)

    resultados = consulta.all()
    session.close()
    
    return resultados
