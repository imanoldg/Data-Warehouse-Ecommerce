-- Una resena por pedido. En el dataset hay pedidos con varias resenas (el cliente la
-- actualiza): nos quedamos con la mas reciente. Y un mismo review_id puede estar en varios
-- pedidos, asi que review_id NO es una clave unica: la clave de este modelo es pedido_id.
with resenas as (

    select
        review_id as resena_id,
        order_id as pedido_id,
        cast(review_score as integer) as nota,
        review_comment_title as titulo,
        review_comment_message as comentario,
        try_cast(review_creation_date as timestamp) as creada_en,
        try_cast(review_answer_timestamp as timestamp) as respondida_en
    from {{ source('olist', 'olist_order_reviews_dataset') }}

)

select *
from resenas
qualify row_number() over (
    partition by pedido_id
    order by creada_en desc, respondida_en desc, resena_id
) = 1
