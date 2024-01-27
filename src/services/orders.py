from src.database.models import Basket


async def calculate_basket_total_cost(basket: Basket):
    """Determination of total order value"""

    total_cost = 0.0

    if basket.basket_items:
        for basket_item in basket.basket_items:
            product = basket_item.product
            price = next(
                (p for p in product.prices if p.id == basket_item.price_id_by_the_user),
                None
            )

            if price:
                total_cost += float(price.price * basket_item.quantity)

    return total_cost
