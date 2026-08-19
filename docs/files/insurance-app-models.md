# Insurance Agency App — Data Models

_Conceptual model design. No code — this describes what each model represents,
its fields, and how models relate to each other, as a reference for building
the actual Django models._

## Overview Diagram

```
PolicyType          Insurer
     \                /
      \              /
       Customer → Policy
                    ├── Payment
                    ├── Claim → ClaimStatusHistory
                    ├── Beneficiary
                    ├── PremiumSchedule
                    └── Document (also attachable to Customer or Claim directly)
```

Core relationship: one **Customer** can hold many **Policies**. Everything
else (payments, claims, beneficiaries, schedules, documents) hangs off a
Policy, except Documents, which can also attach directly to a Customer or a
Claim.

---

## Customer
One record per person the agency serves.

| Field | Notes |
|---|---|
| Full name | |
| Phone number | |
| Email | |
| Physical/postal address | |
| National ID number | |
| KRA PIN | |
| Date registered/onboarded | |
| Notes | Free text |

**Relationships:** one Customer → many Policies.

---

## PolicyType
Open-ended lookup table — staff can add new types freely (Motor, Life,
Health, Property, etc.) rather than being limited to a fixed list baked
into the code.

| Field | Notes |
|---|---|
| Name | e.g. "Motor" |
| Description | Optional |

**Relationships:** one PolicyType → many Policies.

---

## Insurer
Lookup table for the actual insurance company backing a policy (the agency
brokers for multiple insurers). Avoids inconsistent free-text entry of
insurer names.

| Field | Notes |
|---|---|
| Name | |
| Contact phone/email | Agency's reference contact |
| Notes | |

**Relationships:** one Insurer → many Policies.

---

## Policy
The central record — one per policy issued.

| Field | Notes |
|---|---|
| Customer | Link |
| Policy type | Link |
| Insurer | Link |
| Policy number | Agency/insurer reference number |
| Coverage amount | |
| Premium amount | |
| Premium frequency | Monthly / quarterly / annually |
| Start date | |
| Expiry/renewal date | |
| Status | Active / lapsed / cancelled / expired — **manually set by staff**, not auto-computed |
| Notes | |

**Relationships:** belongs to one Customer, one PolicyType, one Insurer.
Has many Payments, Claims, Beneficiaries, PremiumSchedule entries, and
(optionally) Documents.

---

## Payment
What was actually paid, and when.

| Field | Notes |
|---|---|
| Policy | Link |
| Amount paid | |
| Date paid | |
| Payment method | Cash / M-Pesa / bank transfer / cheque |
| Reference/transaction number | |
| Period covered | e.g. "Jan–Mar premium" |
| Notes | |

**Relationships:** belongs to one Policy.

---

## PremiumSchedule
What's *due* and *when* — distinct from Payment (what was actually
received). Lets you flag overdue premiums rather than only keeping a
historical payment log.

| Field | Notes |
|---|---|
| Policy | Link |
| Amount due | |
| Due date | |
| Status | Pending / paid / overdue |
| Notes | |

**Relationships:** belongs to one Policy.

---

## Claim
One record per claim filed against a policy.

| Field | Notes |
|---|---|
| Policy | Link |
| Date filed | |
| Description | |
| Amount claimed | |
| Amount approved/paid | May differ from amount claimed |
| Current status | Mirrors the latest ClaimStatusHistory entry, for quick display |
| Notes | |

**Relationships:** belongs to one Policy. Has many ClaimStatusHistory
entries, and (optionally) Documents.

---

## ClaimStatusHistory
Full history of status changes on a claim over time — not just a single
current-status field.

| Field | Notes |
|---|---|
| Claim | Link |
| Status | Filed / under review / approved / rejected / paid |
| Date of change | |
| Note | Free text — no per-user attribution, since login is shared |

**Relationships:** belongs to one Claim.

---

## Beneficiary
Who receives payout on a policy — especially relevant for life policies,
where coverage can split across multiple people.

| Field | Notes |
|---|---|
| Policy | Link |
| Full name | |
| Relationship to policyholder | |
| ID number | |
| Percentage share | |
| Contact info | |

**Relationships:** belongs to one Policy. A Policy can have many
Beneficiaries.

---

## Document / Attachment
Generic file storage — scanned ID copies, signed policy documents, claim
evidence, etc.

| Field | Notes |
|---|---|
| Linked to | Customer, Policy, or Claim (one of the three per document) |
| File | |
| Document type | ID copy / policy document / claim evidence / other |
| Description | |
| Date uploaded | |

**Relationships:** attaches to exactly one of Customer, Policy, or Claim.

---

## Open Decisions (not yet finalized)

- Exact wording/list of policy statuses (active/lapsed/cancelled/expired)
- Exact wording/list of claim status stages
- Whether PremiumSchedule "overdue" status is computed or manually updated
