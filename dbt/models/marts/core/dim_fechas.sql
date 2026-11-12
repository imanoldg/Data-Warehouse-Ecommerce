-- Dimension de calendario: un dia por fila, de 2016 a 2018 (el periodo del dataset).
with dias as (

    select cast(d as date) as fecha
    from range(date '2016-01-01', date '2019-01-01', interval 1 day) as t (d)

)

select
    fecha,
    year(fecha) as anio,
    quarter(fecha) as trimestre,
    month(fecha) as mes,
    ['enero', 'febrero', 'marzo', 'abril', 'mayo', 'junio', 'julio', 'agosto',
     'septiembre', 'octubre', 'noviembre', 'diciembre'][month(fecha)] as nombre_mes,
    strftime(fecha, '%Y-%m') as anio_mes,
    isodow(fecha) as dia_semana,
    ['lunes', 'martes', 'miercoles', 'jueves', 'viernes', 'sabado', 'domingo'][isodow(fecha)]
        as nombre_dia,
    isodow(fecha) in (6, 7) as es_fin_de_semana
from dias
