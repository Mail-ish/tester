# Flow: Order to Shipment

Teams: Storefront, Accounting, Logistics. Based on the "Order to Shipment" diagram the three teams agreed in session 6.
Status: **draft for sign-off** (see the table at the end). Proposed by Logistics, revised by Storefront (steps 1, 3–4, contracts, errors, criteria 6–8).

## Trigger

The customer clicks **Buy now** in the **Storefront** checkout. There is no payment processor: the payment is assumed settled. Storefront hands the finalised order to **Accounting** in one call; Accounting confirms the payment and creates the invoice. The payment confirmation in Accounting starts the Logistics part of the flow.

## Steps

| #   | Caller → provider       | Operation                                                                                                                  | Data sent                                                                                                                                                                                                                                                                                         | Data returned                                                                                               |
| --- | ----------------------- | -------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------- |
| 1   | Storefront → Accounting | Accounting's operation for a new order (Accounting contract). Until it exists: MOCK stand-in `POST /mock/paid-orders`. Sent by Storefront's `POST /orders` (`create_order`). | The finalised order in Storefront format (euros, camelCase): `orderId` (`O-` + 6 digits), `customerId` or (guests) `guestEmail`, `shippingAddress` and `billingAddress` (`fullName`, `street`, `houseNumber`, `postcode`, `city`, `country` as ISO code `DE`), `logisticsAddress` (the shipping address already normalised by Storefront into Logistics' `ShippingAddress`), `shippingMethod` (display name), `shippingMethodCode` (`STANDARD` / `EXPRESS`), `shippingCost`, `cartItems`, `subtotal`, `discountAmount`, `totalAmount`, `currency` | `2xx` = accepted (payment confirmed, invoice created). Storefront stores the order only then.                |
| 2   | Accounting → Logistics  | `createShipment` `POST /shipments`                                                                                         | `orderId`, `customerId`, `paymentStatus: "PAID"`, `shippingAddress` = Storefront's `logisticsAddress` unchanged (`recipientName`, `street`, `postalCode`, `city`, `country`), `shippingMethod` = `shippingMethodCode` (`STANDARD` / `EXPRESS`), optional `paymentReference` | `201` with the shipment: `shipmentId` (e.g. `S-2001`), `status: "CREATED"`, `carrierCode`, `trackingNumber` |
| 3   | Storefront → Logistics  | `listShipments` `GET /shipments?orderId=O-…`                                                                               | `orderId`                                                                                                                                                                                                                                                                                         | the shipment of that order: `shipmentId`, `trackingNumber`, `carrierCode`, `status`                         |
| 4   | Storefront → Logistics  | `getShipmentEvents` `GET /shipments/{shipmentId}/events`                                                                   | `shipmentId`                                                                                                                                                                                                                                                                                      | status history, oldest first                                                                                |

**Address normalisation (Storefront):** Storefront and Logistics name the address fields differently, so Storefront's Orders API normalises the shipping address once and sends it as `logisticsAddress`: `fullName` → `recipientName`; `street` + `houseNumber` → `street` (`"Maximilianstraße"` + `"42"` → `"Maximilianstraße 42"`); `postcode` → `postalCode`; `city`; `country` as ISO code. Accounting passes it to Logistics unchanged. Guests have no `customerId`, but Logistics requires one, so Accounting sends `"GUEST"`; the guest's email is never sent to Logistics.

Storefront shows steps 3–4 on its order tracking page, next to the items and prices from its own order: logged-in customers see their orders (`GET /orders?customerId=`), guests enter order number + email (`POST /orders/lookup`). Storefront calls Logistics from its server, not from the browser. Logistics never pushes data: every return arrow is the answer to a request.

**Data is in memory for now** in all three modules: Storefront's orders API, Accounting (MOCK stand-in) and Logistics. A restart loses it, so restart all three together. Storefront creates the order number (`O-` + 6 random digits).

Local ports: Storefront web 3130, orders API 8001, Logistics 8002, Accounting (MOCK stand-in) 8003.

## Contract changes

| Contract                         | Before      | After                  | Change                                                                                                                                                                                                                                                                                                       |
| -------------------------------- | ----------- | ---------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| Logistics `openapi.yaml`         | 0.3.0-draft | **1.1.0**              | 1.0.0 = 0.3.0-draft agreed in this flow. 1.1.0 adds the **optional** `paymentReference` (Accounting sends it). Additions only.                                                                                                                                                                                |
| Storefront `orders_openapi.yaml` | 0.1.0       | **0.2.0**              | Additions: optional `shippingMethodCode`, `shippingCost`, `paymentMethod` (Storefront only, not sent to Accounting); `billingAddress` always stored; `GET /orders?customerId=`, `POST /orders/lookup`; `POST /orders` answers 503/502 when Accounting is down/refuses. Now enforced as 0.1.0 already said: `country` is an ISO code; shipping is Standard or Express only. |
| Accounting `accounting.yaml`     | 0.1.0-draft | (Accounting, pending)  | Must accept step 1 in Storefront format with `O-` order ids (the draft uses `ORD-`, snake_case and cents: Accounting converts on its side) and call Logistics (step 2). Until then Storefront uses the MOCK stand-in in `session7/accountingMock`.                                                              |

## Errors

| Situation                                                                 | Who notices                                             | What happens                                                                                                                             |
| ------------------------------------------------------------------------- | ------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------- |
| Accounting is down when Storefront sends step 1                           | Storefront (connection error or `5xx`)                  | The order is **refused**: `POST /orders` answers `503`, nothing is stored. Checkout stays on step 3 with "Order service is currently unavailable. Please try again later."; address, shipping and cart are kept. |
| Accounting refuses step 1 (`4xx`)                                         | Storefront                                              | `POST /orders` answers `502`, nothing is stored; checkout shows "We could not place your order". A bug to fix, not a temporary failure. |
| Invalid checkout data (country name instead of code, method other than Standard/Express) | Storefront answers `422`                 | Never reaches Accounting.                                                                                                                |
| Logistics is down when Accounting calls step 2                            | Accounting (connection error or `5xx`)                  | The payment stays confirmed. Accounting keeps the order as "paid, shipment pending" and retries later. The flow must not lose the order. |
| Accounting retries an order that already got a shipment                   | Logistics answers `409 ORDER_ALREADY_HAS_SHIPMENT`      | Accounting treats this as success and reads the shipment with `GET /shipments?orderId=…`. No second shipment is created.                 |
| Invalid data in step 2 (wrong id format, lowercase method, missing field) | Logistics answers `422 VALIDATION_ERROR` with a message | Accounting logs it and does not retry; this is a bug to fix, not a temporary failure.                                                    |
| Order not paid (`paymentStatus` not `PAID`)                               | Logistics answers `422`                                 | No shipment is created.                                                                                                                  |
| Wrong order number or email on the tracking page                          | Storefront answers `404`                                | The same "Order not found" for both, so the page does not reveal which order numbers exist.                                              |
| Storefront asks before the shipment exists (step 3 returns an empty list) | Storefront                                              | Tracking page shows "Preparing your shipment".                                                                                           |
| Unknown shipment in step 4                                                | Logistics answers `404 SHIPMENT_NOT_FOUND`              | Storefront shows "Shipment not found" and keeps the rest of the page.                                                                    |
| Logistics is down when Storefront asks (steps 3–4)                        | Storefront                                              | The page still shows the order and "Delivery status is currently unavailable".                                                           |

## Acceptance criteria

1. **Given** a paid order O-100004, **when** Accounting sends it to `POST /shipments`, **then** Logistics answers 201 with a `shipmentId`, status `CREATED`, a carrier and a tracking number.
2. **Given** O-100004 already has a shipment, **when** Accounting sends it again, **then** Logistics answers 409 and there is still exactly one shipment for O-100004.
3. **Given** a shipment exists for O-100004, **when** Storefront calls `GET /shipments?orderId=O-100004`, **then** it gets that shipment's `shipmentId`, `trackingNumber`, `carrierCode` and `status`.
4. **Given** Accounting sends `paymentReference: "PAY-1"`, **when** the shipment is read, **then** it carries `paymentReference: "PAY-1"`; **given** an old client sends no `paymentReference`, **then** the request still succeeds.
5. **Given** the Logistics API is stopped, **when** Accounting confirms a payment, **then** the order stays "paid, shipment pending" and a shipment is created after Logistics is back.
6. **Given** the Logistics API is stopped, **when** the customer opens the tracking page, **then** the page loads with the order and shows "Delivery status is currently unavailable".
7. **Given** Accounting is stopped, **when** the customer clicks Buy now, **then** checkout shows "Order service is currently unavailable" and no order is stored (`GET /orders` is unchanged).
8. **Given** guest order O-100004 placed with `guest@example.com`, **when** the guest enters O-100004 and `guest@example.com` on the tracking page, **then** it shows the items, prices, `shipmentId`, `trackingNumber`, `carrierCode`, `status` and the status history; **with** another email **then** it shows "Order not found".

Logistics' side of criteria 1–4 is covered by `src/features/logistics/api/tests/test_session7.py` and the existing API tests. Criterion 5 is checked on the Accounting side (checked by hand with the MOCK stand-in). Criteria 5 and 7 and the step 1–3 data path are covered end to end by `session7/storefront/for-partners/test_order_to_shipment_e2e.py`; Storefront's contract test against Logistics (steps 3–4) is `session7/storefront/API/tests/test_partner_contract.py`. Criteria 6 and 8 (the pages) are checked in the browser.

## Sign-off

| Team       | Name | Date | Signed |
| ---------- | ---- | ---- | ------ |
| Storefront |      |      |        |
| Accounting |      |      |        |
| Logistics  |      |      |        |
