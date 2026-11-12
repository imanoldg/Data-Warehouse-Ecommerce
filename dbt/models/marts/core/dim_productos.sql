select
    p.producto_id,
    coalesce(p.categoria, 'sin_categoria') as categoria,
    -- Algunas categorias no tienen traduccion: se usa el nombre en portugues
    coalesce(c.categoria_en, p.categoria, 'uncategorized') as categoria_en,
    p.num_fotos,
    p.peso_g,
    p.largo_cm * p.alto_cm * p.ancho_cm as volumen_cm3
from {{ ref('stg_olist__productos') }} as p
left join {{ ref('stg_olist__categorias') }} as c on p.categoria = c.categoria
