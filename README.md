# Privacy-Preserving HR Verification

> **Verify sensitive HR information without exposing the underlying data.**

A privacy-preserving HR verification prototype built with **Midnight** and **Compact**.

The system allows a recruiter or hiring manager to answer questions such as:

> **"Is this candidate's salary within the approved budget?"**

without revealing the candidate's actual salary.

The salary remains private to the HR verification service and is supplied to the Midnight circuit as a **private witness**. The circuit evaluates the policy and exposes only the verification result.

**Private data in. → Zero-knowledge verification. → Simple result out.**

---

## The Problem

HR systems handle sensitive information such as salaries, compensation bands, and candidate records.

Often, a verifier doesn't actually need to know the underlying data. They only need to know whether a policy has been satisfied.

For example, a traditional workflow might expose:

```text
Candidate salary: $88,000
Approved budget:  $95,000
Result:           VERIFIED
```

But the verifier only needs:

```text
Candidate: Candidate 1
Budget:    $95,000
Result:    VERIFIED
```

The exact salary is unnecessary exposure.

### The goal

Allow someone to verify a claim **without giving them the underlying sensitive information**.

---

## How It Works

At a high level:

```text
┌──────────────────────┐
│     Streamlit UI     │
│                      │
│  Candidate ID        │
│  Approved Budget     │
└──────────┬───────────┘
           │
           │ POST /verify
           ▼
┌──────────────────────┐
│   HR Node Service    │
│                      │
│  Candidate database  │
│  Private salary      │
│  Midnight wallet     │
└──────────┬───────────┘
           │
           │ Private witness
           ▼
┌──────────────────────┐
│   Midnight Circuit   │
│                      │
│ salary <= budget ?   │
└──────────┬───────────┘
           │
           │ ZK proof / result
           ▼
┌──────────────────────┐
│    Verification      │
│                      │
│  VERIFIED             │
│  or                   │
│  NOT VERIFIED         │
└──────────────────────┘
```

The critical boundary is between **public inputs** and the **private witness**.

### Public

The verifier provides:

- Candidate ID
- Approved salary budget

### Private

The HR service provides:

- Candidate salary

The salary is used during private circuit execution and is **not sent to the Streamlit frontend**.

---

## The Midnight Circuit

The core verification logic is intentionally simple:

```compact
witness candidateSalary(): Uint<0..2^32>

circuit verifySalary(
    budget: Uint<0..2^32>
): Boolean {
    const salary = candidateSalary();
    return disclose(salary <= budget);
}
```

The important operation is:

```text
salary <= budget
```

The circuit does **not** disclose:

```text
salary
```

It discloses only the result:

```text
TRUE
```

or

```text
FALSE
```

For example:

```text
PRIVATE                     PUBLIC

Candidate salary            Approved budget
     $88,000                    $95,000
        │                          │
        └──────────┬───────────────┘
                   │
                   ▼
             salary <= budget
                   │
                   ▼
                 TRUE
                   │
                   ▼
              VERIFIED
```

The verifier can establish that the salary satisfies the policy without being given the salary itself.

---

## Why This Matters

This changes the model from:

> **"Give me the data so I can verify it."**

to:

> **"Prove to me that the condition is true without giving me the data."**

That's the core privacy property this prototype demonstrates.

The same idea can apply anywhere a party needs to verify a condition over sensitive information without needing access to the information itself.

---

## Architecture

### Streamlit Frontend

The Streamlit application provides the verifier-facing interface.

The user can select a candidate and provide an approved salary budget.

The frontend **does not receive the candidate's salary**.

It communicates with the backend through HTTP.

```text
Streamlit
    │
    │ POST /verify
    ▼
HR Node Service
```

### HR Verification Service

`hr-cli/src/server.ts` provides the HTTP interface between the frontend and the Midnight verification system.

It is responsible for:

- receiving verification requests,
- accessing private candidate information,
- providing the salary as a witness,
- interacting with the Midnight wallet and network,
- constructing/executing the verification,
- and returning the result.

Keeping this service separate from the frontend prevents the sensitive witness from needing to cross into the UI layer.

### Midnight Contract

The Compact contract contains the privacy-preserving verification logic.

Its core question is:

```text
Is candidateSalary <= budget?
```

The salary remains private while the verification result is disclosed.

---

## Privacy Model

The intended data flow is:

```text
                PRIVATE
                   │
                   ▼
          Candidate salary
                   │
                   ▼
          HR Node Service
                   │
                   │ witness
                   ▼
          Midnight Circuit
                   │
                   │
                   ▼
              TRUE / FALSE
                   │
                   │ public result
                   ▼
             Streamlit UI
```

The frontend should never receive the raw salary.

Likewise, the verification response should contain the policy result rather than the sensitive underlying value.

This means the privacy property is architectural, not simply a UI decision.

---

## Example

Assume the private HR data contains:

```text
Candidate 1 → $88,000
Candidate 7 → $110,000
```

A verifier submits:

```yaml
Candidate: Candidate 1
Budget:    $95,000
```

The system returns:

```text
VERIFIED
```

The verifier does not need to learn that the salary is `$88,000`.

For another candidate:

```yaml
Candidate: Candidate 7
Budget:    $100,000
```

The system returns:

```text
NOT VERIFIED
```

Again, the verifier only learns the result of the policy check.

---

## Running the Project

The MVP consists of two application processes:

1. **Midnight HR verification service**
2. **Streamlit frontend**

### 1. Start the HR service

```bash
cd ~/Projects/midnight-hack/hr-cli
npm run server
```

The service should report that it is listening on its configured HTTP port.

### 2. Start the Streamlit frontend

From the repository root:

```bash
cd ~/Projects/midnight-hack
source .venv/bin/activate
streamlit run app.py
```

The Python virtual environment keeps the frontend dependencies isolated from the system Python installation.

> **Note:** The Midnight development/test infrastructure and required services must also be running according to the project's development environment.

---

## Repository Structure

```text
midnight-hack/
├── app.py                  # Streamlit frontend
├── hr-cli/
│   ├── src/
│   │   └── server.ts       # HR verification API
│   └── ...
├── .venv/                  # Python virtual environment
└── ...
```

---

## What This Prototype Demonstrates

This MVP demonstrates:

- **Private candidate information**
- **Public verification criteria**
- **Private witnesses**
- **Zero-knowledge verification**
- **Selective disclosure of results**
- **Frontend/backend separation**
- **Midnight + Compact integration**

The current policy is intentionally simple:

```text
candidate salary <= approved budget
```

But the architecture can be extended to more complex policies.

For example:

```text
salary within approved range
candidate satisfies a compensation band
candidate meets a minimum experience requirement
candidate satisfies a department-specific policy
```

The underlying principle remains the same:

> **Reveal the result of a computation without revealing all of the data used to perform it.**

---

## Why HR?

HR is a useful demonstration of this technology because many HR decisions are fundamentally **policy checks over sensitive data**.

A verifier might need to establish:

```text
Does the candidate satisfy the policy?
```

without necessarily needing:

```text
What is the candidate's exact salary?
What is their full compensation?
What other private information do they have?
```

Zero-knowledge proofs provide a mechanism for separating those two questions.

---

## Project Status

**Hackathon MVP / prototype**

The current implementation focuses on demonstrating the privacy-preserving verification flow rather than providing a production-ready HR platform.

A production implementation would require additional work around:

- authentication and authorisation,
- secure candidate-data storage,
- key management,
- access control,
- audit logging,
- production deployment,
- error handling,
- privacy threat modelling,
- and integration with existing HR systems.

---

## Tech Stack

- **Midnight**
- **Compact**
- **Zero-knowledge proofs**
- **TypeScript / Node.js**
- **Streamlit**
- **Python**
- **Docker / Midnight development infrastructure**

---

## Core Idea

Traditional verification asks:

> **"Can I see the data so I can verify it?"**

Privacy-preserving verification asks:

> **"Can you prove the claim without showing me the data?"**

That's what this project demonstrates with Midnight.
