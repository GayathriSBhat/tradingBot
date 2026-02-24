# Order Placement Limitations — Binance Futures

## Overview

This document describes key limitations and constraints enforced by Binance Futures when placing orders. Understanding these rules is essential for building reliable trading systems and preventing order rejections.

These constraints apply to both Testnet and Production environments.

---

## 1. Minimum Notional Requirement

Orders must meet a minimum value threshold.

**Rule:**

```
price × quantity ≥ minimum notional (typically around 100 USDT)
```

If the order value is too small, it will be rejected.

**Why it exists:**

* Prevents very small “dust” trades
* Reduces unnecessary load on the exchange

---

## 2. Price Band Restrictions

Limit order prices must remain within an acceptable range relative to the current market (mark price).

**Rules:**

* SELL limit orders cannot be far below market price.
* BUY limit orders cannot be far above market price.

**Why it exists:**

* Prevents manipulation
* Avoids accidental executions

---

## 3. Quantity Precision

Each trading pair defines a step size for quantity.

**Example:**

* Valid: `0.001 BTC`
* Invalid: `0.0007 BTC`

**Why it exists:**

* Ensures consistent order increments

---

## 4. Price Tick Size

Prices must follow predefined increments.

**Example:**

* Valid: `62000`
* Invalid: `62000.123`

**Why it exists:**

* Standardizes pricing across the order book

---

## 5. Margin / Balance Requirement

Orders require sufficient available margin.

If funds are insufficient, the order is rejected.

**Why it exists:**

* Protects against excessive risk
* Maintains account solvency

---

## 6. Leverage Constraints

Maximum allowable position size depends on leverage and available margin.

**Why it exists:**

* Limits exposure
* Enforces risk controls

---

## 7. Reduce-Only Rules

Reduce-only orders must only decrease existing positions.

If they increase exposure, the exchange rejects them.

**Why it exists:**

* Prevents unintended position increases

---

## 8. Time-in-Force Requirement

LIMIT orders must specify execution policy.

**Supported values:**

* GTC — Good Till Cancelled
* IOC — Immediate or Cancel
* FOK — Fill or Kill

**Why it exists:**

* Defines how long orders remain active

---

## 9. Timestamp Validation

Requests must be within an acceptable time window.

If the client clock is out of sync, requests may fail.

**Why it exists:**

* Prevents replay attacks
* Ensures request integrity

---

## 10. Symbol Filters

Each trading pair defines filters such as:

* Minimum quantity
* Maximum quantity
* Minimum notional
* Price limits

These can be fetched via:

```
/fapi/v1/exchangeInfo
```

**Why it exists:**

* Enforces exchange trading rules

---

## Best Practices

When building trading applications:

* Validate inputs before sending orders
* Fetch exchange metadata dynamically
* Handle API errors gracefully
* Provide clear feedback to users

---

## Conclusion

Understanding exchange limitations helps prevent failed orders, improves system robustness, and ensures smoother trading operations.

These constraints should ideally be validated client-side to enhance user experience and reliability.

---

End of document.
