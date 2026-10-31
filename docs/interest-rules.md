# Interest rules: what ChaseKit calculates, and the law behind it

ChaseKit is not a lawyer. This page states what the code calculates and
the statute each calculation encodes, so a user (or their accountant or
solicitor) can check the figure against their own position. Whether
statutory interest applies to a specific contract depends on that
contract's terms.

Interest is simple interest: principal × annual rate × days overdue /
365, rounded half-up to cents. Days overdue counts from the due date on
the invoice to the run date (or `--as-of` date).

## United Kingdom

**Statute:** Late Payment of Commercial Debts (Interest) Act 1998, as
amended (including the Late Payment of Commercial Debts Regulations
2013).

- **Rate (Act, section 6):** the Bank of England base rate plus 8
  percentage points. The Act fixes the reference rate by half-year: the
  base rate in force at the previous 31 December applies to debts whose
  interest period starts January to June; the rate at the previous
  30 June applies July to December. ChaseKit takes the base rate as
  configuration (`--uk-base-rate`) because the correct value depends on
  when the debt's interest period started. The shipped default is
  4.00%, the base rate set in August 2025. Verify the current rate at
  bankofengland.co.uk.
- **Fixed compensation (Act, section 5A)**, charged once per invoice on
  top of interest, scaled by the size of the debt:
  - under £1,000: **£40**
  - £1,000 to £9,999.99: **£70**
  - £10,000 or more: **£100**
- The Act covers business-to-business debts (and debts where the buyer
  is a public authority). If the contract already provides a substantial
  remedy for late payment, that remedy generally replaces the statutory
  scheme. Applies where the invoice currency is GBP.

Worked example: £1,000 at 30 days overdue with a 4.00% base rate.
Rate = 12%. Interest = 1000 × 0.12 × 30 / 365 = £9.86. Fee = £70.
Total = £1,079.86. (Tested in `tests/test_interest_uk.py`.)

## European Union

**Statute:** Directive 2011/7/EU of 16 February 2011 on combating late
payment in commercial transactions, as implemented in each member
state's national law.

- **Rate (Articles 2 and 3):** the reference rate plus at least 8
  percentage points. For euro-area member states the reference rate is
  the European Central Bank main refinancing operations rate, taken at
  1 January or 1 July for the following six months. Other member states
  use their national central bank rate. ChaseKit takes the reference
  rate as configuration (`--eu-reference-rate`); the shipped default is
  2.15%, the ECB rate set in June 2025.
- **Fixed compensation (Article 6):** the creditor is entitled to a
  minimum fixed sum of **€40** as compensation for recovery costs,
  without needing to send a reminder. Reasonable recovery costs above
  €40 can also be claimable; ChaseKit calculates the €40 statutory
  minimum only.
- The Directive sets a floor: member-state law can be more favourable
  to the creditor, never less. ChaseKit calculates the Directive floor.
  Applies where the invoice currency is EUR.

Worked example: €2,000 at 60 days overdue with a 2.15% reference rate.
Rate = 10.15%. Interest = 2000 × 0.1015 × 60 / 365 = €33.37. Fee = €40.
Total = €2,073.37. (Tested in `tests/test_interest_eu.py`.)

## United States

There is **no** US federal statute setting late-payment interest on
ordinary business-to-business invoices. What can be charged comes from
the parties' contract or from state law, which varies (sector-specific
prompt-payment acts, differing state default rates).

ChaseKit's US pack therefore defaults, honestly, to **0% interest and a
$0 fee**. Set `--us-rate` and `--us-fee` to your contracted terms or
your state's figure and the pack will calculate and state them. Nothing
is invented on your behalf.

## Adding a jurisdiction

A jurisdiction pack is one small module in `src/chasekit/interest/`
implementing `annual_rate_percent()`, `fixed_fee_for(principal)`, and
`basis()`, plus tests with hand-checkable numbers, plus a section on
this page citing the statute. See CONTRIBUTING.md.
