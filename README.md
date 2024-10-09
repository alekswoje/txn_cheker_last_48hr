_Criteria for Identifying Bots_

The script uses the following two primary criteria to flag an address as a likely bot:

Recently Funded by Another Wallet:

Definition: The wallet was funded (received tokens or ETH) from another wallet within a recent time frame (e.g., the last 48 hours).
Rationale: Bots often operate with freshly funded accounts to perform specific actions, such as claiming airdrops, without maintaining long-term balances.
Single Outgoing Transaction (Airdrop Claim):

Definition: The wallet has only one outgoing transaction, which is the action of claiming the airdrop.
Rationale: Genuine users typically engage in multiple transactions (e.g., sending ETH, interacting with various contracts). In contrast, bots may only perform the specific action they are programmed for, resulting in a single outgoing transaction.
