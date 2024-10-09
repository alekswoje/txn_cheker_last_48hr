**Criteria for Identifying Bots**

The script uses the following two primary criteria to flag an address as a likely bot:

Recently Funded by Another Wallet:

Definition: The wallet was funded (received tokens or BNB) from another wallet (doesn't include bridging contracts) within the last 48 hours.
Rationale: Bots often operate with freshly funded accounts to perform specific actions, such as claiming airdrops, without maintaining long-term balances.

Single Outgoing Transaction (Airdrop Claim):

Definition: The wallet has only one outgoing transaction, which is the action of claiming the airdrop.
Rationale: Genuine users typically engage in multiple transactions (e.g., sending ETH, interacting with various contracts). In contrast, bots may only perform the specific action they are programmed for, resulting in a single outgoing transaction.

Both criteria must be met to flag a wallet as a bot address.

Latest output

Analyzing addresses: 100%|██████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████| 191499/191499 [29:24<00:00, 108.51it/s]
2024-10-09 06:29:55,418 [INFO] Analysis Complete.
2024-10-09 06:29:55,418 [INFO] Total claimants: 191499
2024-10-09 06:29:55,419 [INFO] Likely bots: 138207
2024-10-09 06:29:55,419 [INFO] Percentage of bots: 72.17%
2024-10-09 06:29:55,437 [INFO] Bot addresses have been saved to 'bot_addresses.txt'.
