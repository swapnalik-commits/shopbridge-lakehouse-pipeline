# ShopBridge model notes

## Source grains

- **Orders:** one row = one `order_id`. Status and delivery timestamps live here.
- **Items:** one row = one `order_id` + `order_item_id`. `price` and `freight_value` live here. This is gold `fct_order_items`.
- **Payments:** one row = one payment for an order (`order_id` + `payment_sequential`). Never join this to items to compute GMV.

## Known order_status values

delivered, shipped, canceled, unavailable, invoiced, processing, created, approved