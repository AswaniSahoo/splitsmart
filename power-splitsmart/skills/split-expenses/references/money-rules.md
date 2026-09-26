# SplitSmart money rules

- Money is always integer minor units (cents / paise). `12.34` is `1234`.
- Equal split: `base, remainder = divmod(amount, n)`; the first `remainder` participants (in listed order) pay 1 extra cent.
  Example: 10000 split 3 ways → `[3334, 3333, 3333]`.
- Balance = total paid − total share owed. The balances of a group always sum to exactly 0.
- Settle-up is greedy (largest debtor pays largest creditor) and needs at most `non-zero members − 1` transfers.
