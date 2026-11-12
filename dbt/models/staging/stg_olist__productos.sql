-- Corrige las erratas de las columnas originales ("lenght").
select
    product_id as producto_id,
    product_category_name as categoria,
    try_cast(product_name_lenght as integer) as longitud_nombre,
    try_cast(product_description_lenght as integer) as longitud_descripcion,
    try_cast(product_photos_qty as integer) as num_fotos,
    try_cast(product_weight_g as integer) as peso_g,
    try_cast(product_length_cm as integer) as largo_cm,
    try_cast(product_height_cm as integer) as alto_cm,
    try_cast(product_width_cm as integer) as ancho_cm
from {{ source('olist', 'olist_products_dataset') }}
