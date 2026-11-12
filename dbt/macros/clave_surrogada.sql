{#-
  Clave surrogada: un hash estable de una o varias columnas.
  Uso: {{ clave_surrogada(['vendedor_id', 'valido_desde']) }}
-#}
{% macro clave_surrogada(columnas) -%}
    md5(concat_ws('|'
    {%- for columna in columnas %}, coalesce(cast({{ columna }} as varchar), '')
    {%- endfor %}))
{%- endmacro %}
