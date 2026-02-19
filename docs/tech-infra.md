# Tech & Infrastructure

The architecture behind Blackboard is built for speed, security, and scalability.

## Session Key Architecture
One of the biggest hurdles in on-chain trading is the need to sign every single transaction. Blackboard solves this with **Session Keys**.
*   **One-Time Authorization**: At the start of your session, you sign a temporary key that is valid for a limited period (e.g., 24 hours).
*   **Seamless Execution**: Once authorized, you can place, move, and cancel orders with a single click. No recurring wallet popups.
*   **Restricted Permissions**: Session keys are designed with limited scope—they can only perform trading actions and cannot withdraw funds. Your assets remain secure.

## In-house Infrastructure
To provide a superior experience, we don't rely on generic third-party providers.

### Dedicated RPC & Nodes
Blackboard operates its own dedicated RPC (Remote Procedure Call) nodes for all supported chains.
*   **Ultra-Low Latency**: By eliminating middlemen, we reduce the time between your click and the transaction hitting the chain.
*   **99.9% Uptime**: Redundant node infrastructure ensures that the terminal remains accessible even during periods of heavy network congestion.

### Proprietary Validators
We run our own validators for partner networks (e.g., Hyperliquid L1). This vertical integration allows us to:
*   **Prioritize Performance**: Optimize data synchronization for real-time price updates.
*   **Enhance Security**: Contribute directly to the security of the underlying networks we use.

## The Brokerage Layer
Blackboard is built as a transparent, non-custodial brokerage.
*   **Builder Codes (Dreamcash, Based)**: We use a unique "Builder Identification" system. Users who join through specific ecosystem partners receive specialized UI skins, tiered rewards, and access to exclusive alpha communities.
*   **Developer Friendly**: Our modular GTM approach allows other builders to integrate Blackboard's features into their own communities via our API and builder code system.
