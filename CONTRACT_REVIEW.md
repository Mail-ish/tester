# Contract review: Logistics x Storefront

Contract: `openapi.yaml`, version **1.1.0** (session 7). The history below is kept as the record of the session 5 review.
Status: **not yet agreed.** Storefront sent the order payload they plan to use, and we changed the draft to follow their address field names and id formats. Storefront has not yet confirmed the result. `info.version` carries the suffix `-draft` until they do; the agreed version will then be numbered 1.0.0.

## First message from Storefront: order payload

```json
{
  "customerId": "C-1",
  "cartItems": [{ "productId": "P-1", "quantity": 2 }],
  "paymentReference": "PAY-1",
  "totalAmount": 35.98,
  "currency": "EUR",
  "shippingMethod": "standard",
  "shippingAddress": {
    "recipientName": "Max Mustermann",
    "street": "Musterstrasse 1",
    "postalCode": "94469",
    "city": "Deggendorf",
    "country": "DE"
  }
}
```

## Comparison with what Logistics needs (`createShipment`)

| Field                           | Storefront sends                           | Logistics needs                | Result                                                                                                                                                               |
| ------------------------------- | ------------------------------------------ | ------------------------------ | -------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `customerId`                    | `C-1`                                      | opaque string                  | OK as is                                                                                                                                                             |
| `shippingAddress.recipientName` | yes                                        | yes                            | **We adopted their name** (was `fullName`)                                                                                                                           |
| `shippingAddress.country`       | `DE`                                       | 2-letter ISO code              | **We adopted their name** (was `countryCode`)                                                                                                                        |
| `street`, `postalCode`, `city`  | yes                                        | yes                            | OK as is                                                                                                                                                             |
| `shippingMethod`                | `"standard"` (lowercase)                   | `STANDARD` / `EXPRESS`         | **Open:** enum is uppercase in this ERP's convention. Ask Storefront to send uppercase, or we accept lowercase and normalise.                                        |
| `orderId`                       | **missing**                                | required (`O-` + digits)       | **Open:** the payload has no order id. Who creates it and when?                                                                                                      |
| `paymentStatus`                 | **missing** (they send `paymentReference`) | must be `PAID` before shipping | **Open:** who confirms payment, Storefront or Accounting? Logistics only ships paid orders.                                                                          |
| `cartItems`                     | yes                                        | not needed for status tracking | Not in the contract. It could become an optional `items` list later (parcel contents, weight).                                                                       |
| `totalAmount`, `currency`       | yes                                        | not needed                     | Not in the Logistics contract. Note for Storefront/Accounting: the repo convention is money in integer minor units with a currency, so `35.98` should become `3598`. |

## Changes made in v0.2.0-draft

1. `shippingAddress.fullName` renamed to `recipientName`.
2. `shippingAddress.countryCode` renamed to `country` (same format: 2 capital letters).

No other field changed. The code and tests were updated together and pass.

## Second message from Storefront: `getOrder` and `listCustomerOrders`

Storefront asked whether Logistics can also return one order or a customer's orders, and sent the doc _Proposed Order Fields for Logistics_ (`GET /orders/{orderId}`, `GET /customers/{customerId}/orders`). Our answer:

| Point in their doc                                      | Finding                                                                                                                        | Action                                                                                                                          |
| ------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------ | ------------------------------------------------------------------------------------------------------------------------------- |
| `orderId` "created by Logistics"                        | **Wrong owner.** Storefront creates orders (their module creates an order from a cart). Logistics only receives the `orderId`. | Tell Storefront; we need the `orderId` in the message we receive.                                                               |
| `getOrder` / `listCustomerOrders`                       | These are order operations, so they belong to Storefront.                                                                      | Logistics does not implement them. It supplies the delivery part.                                                               |
| Ids like `O-1`, `C-1`                                   | Our `orderId` pattern required 4+ digits (`O-1001`), so `O-1` would have been **rejected**.                                    | **Changed in v0.3.0-draft:** `^[OM]-[0-9]+$`. The lecture slides also name `M-` ids from the Marketplace, so both are accepted. |
| `tracking.trackingNumber` (`TRK-1`)                     | We issue `TRK-2001`-style numbers.                                                                                             | Tracking number now has the form `TRK-<digits>`.                                                                                |
| `tracking.shipmentStatus` (`in_transit`)                | Our enum is uppercase (`IN_TRANSIT`).                                                                                          | Ask Storefront to use our 8 values unchanged, or map them on their side.                                                        |
| Order `status` (`shipped`, `delivered`)                 | Derived from our status.                                                                                                       | Proposed mapping below.                                                                                                         |
| `shipping.estimatedDelivery`                            | Logistics has no delivery estimate yet.                                                                                        | Not provided. Ask whether it is needed.                                                                                         |
| `listCustomerOrders` needs delivery status per customer | We could only look up by order.                                                                                                | **Added in v0.3.0-draft:** `customerId` on every shipment and a `customerId` filter on `listShipments`.                         |
| `cursor` paging                                         | We use `page` / `pageSize`.                                                                                                    | Both are fine; they are separate APIs.                                                                                          |

Proposed mapping, for Storefront to confirm: no shipment or `CREATED` / `LABEL_CREATED` = order `confirmed`; `IN_TRANSIT` / `OUT_FOR_DELIVERY` / `DELIVERY_FAILED` = `shipped`; `DELIVERED` = `delivered`; `RETURNED` / `CANCELLED` = needs a decision (cancelled or a separate state).

## Open questions for Storefront

1. Who emits `OrderReadyForShipping`, Storefront or Accounting, and when (after payment is confirmed)?
2. The order needs an `orderId` like `O-1001`. Which team creates it? Can it be added to your payload?
3. Can you send `shippingMethod` as `STANDARD` / `EXPRESS` (uppercase)?
4. Logistics ships only paid orders, so we need `paymentStatus: "PAID"` in the message. Where does it come from?
5. What do you want back from us? We propose: `GET /shipments?orderId=O-1001` (status and tracking number) and the `ShipmentStatusChanged` event. Do you also want `attemptCount` ("Attempt 2 of 3") in the event? It is optional and marked as a proposal.
6. Can one order produce several shipments (split orders)? We assume **one shipment per order** for now.
7. Should the customer be notified after each failed delivery? That is your decision; Logistics only provides the status.

## Proposed reply to Storefront

> Hi Ismail, thanks for both messages. Orders and customer order lists (`getOrder`, `listCustomerOrders`) belong to Storefront, so we won't build them. We provide the delivery data. To show a customer's orders with their delivery status, call `GET /shipments?customerId=C-1`. For one order, call `GET /shipments?orderId=O-1`. Both return the status and the tracking number. We now accept short ids like `O-1`.
>
> We adopted your address field names (`recipientName`, `country`). We still need three things from you. First, an `orderId` in the message. Storefront creates orders, so the id has to come from you, although your document says Logistics creates it. Second, `paymentStatus` set to `PAID`, because we only ship paid orders. You send `paymentReference`, so who confirms the payment? Third, `shippingMethod` as `STANDARD` or `EXPRESS` in capitals. Our shipment statuses are in capitals too (`IN_TRANSIT`, `DELIVERED` and so on), so please pass them on unchanged or map them on your side.
>
> We don't need `cartItems`, `totalAmount` or `currency`. For amounts, whole cents (3598 instead of 35.98) avoid rounding problems. Do you want an optional `attemptCount` in our status events, so you can show "attempt 2 of 3"? The contract is attached as `openapi.yaml`.

## Change log

| Version     | Change                                                                                                                                                                                                                      | Agreed by                                                                                        |
| ----------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------ |
| 0.1.0-draft | First draft from week-1/week-4 work (MODULE.md, `contracts.ts`)                                                                                                                                                             | nobody yet                                                                                       |
| 0.2.0-draft | Address fields follow Storefront's payload (`recipientName`, `country`)                                                                                                                                                     | **pending Storefront confirmation**                                                              |
| 0.3.0-draft | Order ids may be short (`O-1`); `customerId` added to `Shipment`; `customerId` filter on `listShipments`; tracking number `TRK-<digits>`                                                                                    | **pending Storefront confirmation**                                                              |
| 1.0.0       | Same content as 0.3.0-draft. Open questions answered by the agreed "Order to Shipment" flow: Storefront creates the `orderId`, Accounting confirms payment and calls `createShipment`, `shippingMethod` is sent in capitals | Storefront, Accounting, Logistics (flow diagram); written sign-off in `../docs/session7/flow.md` |
| 1.1.0       | **Addition:** optional `paymentReference` on `OrderReadyForShipping` and `Shipment`. Accounting sends it with the paid order; before 1.1.0 the extra field would have been rejected with 422. No field renamed or removed   | proposed by Logistics, to confirm with Accounting in `flow.md`                                   |

## Assumptions we made without partner input

- One shipment per order.
- The carrier is chosen by Logistics from the shipping method (STANDARD = DHL, EXPRESS = UPS) and the tracking number is assigned at creation (simulated carrier).
- `customerId` is opaque to Logistics.
- `attemptCount` is a proposal.
