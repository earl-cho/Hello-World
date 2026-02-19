# Trading Guide

Master the core mechanics of on-chain perpetual trading on Blackboard.

## Price Mechanisms
To ensure fair execution and prevent market manipulation, Blackboard utilizes multiple price feeds.

### Index Price
The **Index Price** represents the average price of an asset across multiple high-volume exchanges (e.g., Binance, OKX, Bybit). This ensures that the terminal's benchmark reflects the true global market value.

### Mark Price
The **Mark Price** is used for calculating unrealized PnL and triggering liquidations. It is a smoothed version of the Index Price combined with funding rate data, designed to protect traders from temporary price spikes within the order book.

## Order Types
Blackboard supports a variety of order types to enable complex trading strategies.
*   **Market Order**: Execute instantly at the best available price in the order book.
*   **Limit Order**: Specify the exact price at which you wish to buy or sell.
*   **Stop-Loss (SL)**: Automatically close a position if the price reaches a certain level to limit losses.
*   **Take-Profit (TP)**: Automatically close a position to lock in gains at a predefined price.
*   **Advanced Orders**: Post-Only, FOK (Fill-or-Kill), and IOC (Immediate-or-Cancel) are available for pro users.

## Margin & Leverage
### Cross Margin
By default, Blackboard uses a **Cross Margin** system. This means your entire account balance is used as collateral for your open positions, allowing for more flexible capital management and reducing the risk of liquidation for individual positions.

### Leverage Tiers
Trade with up to **50x leverage** on major pairs.
*   **Dynamic Limits**: Maximum leverage is determined by your position size. Larger positions require a higher initial margin to ensure system stability.
*   **Margin Maintenance**: If your margin ratio falls below the required maintenance level, the liquidation engine will be triggered.

## Liquidation Engine
Liquidations on Blackboard are transparent and automated.
1.  **Trigger**: If the Mark Price hits your liquidation price, the position is partially or fully closed.
2.  **Safety Buffer**: A liquidation fee is applied to the remaining collateral to stabilize the protocol insurance fund.
3.  **No Negative Balance**: Our L1 liquidity partners (e.g., Hyperliquid) use sophisticated insurance funds to ensure that traders never lose more than their initial collateral.
