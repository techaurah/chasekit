# Tone guide: the ladder, and why it is built this way

Most late payment is not malice. It is a lost email, an approver on
holiday, a purchase order nobody raised. The templates are written for
that reality: the relationship is worth more than any single invoice,
right up to the point where silence makes escalation the honest option.

## The four stages

| Stage | Days overdue | Register | Goal |
|---|---|---|---|
| 1. Friendly | 1 to 13 | Warm, assumes an oversight | Get paid or get told why not |
| 2. Firm | 14 to 27 | Direct, states amounts and the legal basis | A payment date, in writing |
| 3. Final notice | 28 to 41 | Formal, states consequences and a deadline | Payment, or an agreed plan, within 7 days |
| 4. Escalation | 42 and over | Plain statement of handover | A last window to settle before recovery |

## Rules every template follows

- **One invoice per message.** Bundled demands get ignored; a single
  clear ask gets answered.
- **Exact amounts, always.** Principal, interest, fee, and total are
  stated as separate lines from stage 2 on. Vague balances invite
  vague replies.
- **The legal basis is named, not waved.** Templates state the Act or
  Directive behind the interest figure. A citation reads as
  professional; a threat reads as noise.
- **An easy exit is always offered.** "If it has already been paid,
  ignore this." "If something looks wrong, reply and it will be sorted
  the same day." Most replies to stage 1 are one of these.
- **No threat the sender cannot carry out.** ChaseKit does not report
  to credit bureaus, does not add fees the law does not allow, and
  neither should your edits to these templates.
- **The door stays open at every stage, including the last.** Stage 4
  still offers settlement or a plan. Money collected on good terms is
  worth more than money collected on burnt ones.

## Writing a template pack

A pack is a folder `src/chasekit/templates/<language>/` containing the
four stage files with the same placeholder names. Keep the stage
registers above, adapt the courtesy forms to the culture (what reads
as firm in one market reads as rude in another), and never translate
the legal basis loosely: cite the statute that actually applies in
that jurisdiction.
