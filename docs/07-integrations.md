# Integrations

> **Re-authored 2026-11-03** for Odoo 18 (ADR-0003). The original was lost in transit. Every
> integration below is an outbound data flow and must follow ADR-0005: an allowlisted host, a test,
> and a "what leaves" line. Odoo's own IAP-based services (SMS, snail mail, partner autocomplete,
> media library) are excluded entirely.

| Integration | Phase | How | Licence path | Data that leaves | Allowlist host(s) |
|---|---|---|---|---|---|
| WhatsApp, click-to-chat | P1 | `wa.me/<E.164>?text=...` link opened on the cashier's own phone or WhatsApp Web; the server sends nothing | P (`kitaab_khata`, `kitaab_receipt`) | Nothing from the server. The user's device sends the message. | none |
| WhatsApp Cloud API | P2 | OCA `mail_gateway` + `mail_gateway_whatsapp` (18.0), wired by `kitaab_whatsapp_oca`. Templates for receipts, khata reminders, restock reminders and order updates; opt-in required (FR-CUS-001) | G (AGPL glue) | Recipient phone, template parameters (name, amount, link) | `graph.facebook.com` |
| Email (digest, statements) | P1 | Odoo outgoing mail server (SMTP relay of the deployment) | core | Email address, document PDF | SMTP relay host |
| WooCommerce | P2 | `kitaab_channel_woo` (our own; no maintained free Odoo 18 connector exists): product link by SKU/barcode, stock push of available qty within 60 s, order pull to the Orders inbox | P | SKU, stock qty (out); orders (in) | the shop's own store domain |
| Shopify | P2 | `kitaab_channel_shopify` (our own), same scope via the Admin API | P | Same as WooCommerce | `<shop>.myshopify.com` |
| Couriers (PostEx, Leopards, TCS, Trax) | P3 | Per-courier adapter: booking, tracking, COD settlement import | P | Consignee name, phone, address, COD amount | each courier API host |
| Payments (JazzCash, Easypaisa, Raast) | P1 record-only; P3 API | P1: payment methods recorded at the POS (no API). P3: payment links / QR where APIs are accessible. | P | P3: amount, reference, customer phone | provider API hosts |
| FBR POS fiscalisation | P3, opt-in (`00` P8) | Fork `ol_pos_fbr_connector` (LGPL-3, bought once, $78) or build `kitaab_fbr_pos`; FBR invoice number + QR on the receipt | P (LGPL fork allowed) | Invoice lines, totals, tax, NTN (only when the tenant opts in) | FBR endpoint(s) |
| SMS OTP | OPEN (`00` T5) | A local aggregator through our own adapter, never Odoo SMS (IAP) | P | Phone number, OTP | aggregator host |
| Receipt printing | P1 | Browser print to 80/58 mm thermal printers (OS print dialog); no Odoo IoT box | core | none | none |
| Barcode scanners | P1 | USB/Bluetooth HID keyboard input (POS barcode reader) | core | none | none |
| Label printing | P1 | PDF label sheets (50×25 / 38×25 mm) from `kitaab_catalog` | P | none | none |

**Rules for adding one:**
1. Add the host to the deployment's `kitaab_egress_allowlist`.
2. Add a row here and in `09` §4.
3. Add a test that the integration works through the guard, and that nothing else is reached.
4. Store credentials in system parameters set at deploy time, never in data files.
