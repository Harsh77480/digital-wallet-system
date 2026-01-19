# Digital Wallet – Event-Driven Core 
![Docker](https://img.shields.io/badge/docker-%230db7ed.svg?style=for-the-badge&logo=docker&logoColor=white)
![Apache Kafka](https://img.shields.io/badge/Apache%20Kafka-000?style=for-the-badge&logo=apachekafka)
![Django](https://img.shields.io/badge/django-%23092e20.svg?style=for-the-badge&logo=django&logoColor=white)

## Overview

This project implements the **core transaction flow of a digital wallet system** using an **event-driven, service-oriented architecture**.

There are **no real payments**, authentication, or user management.  
The focus is on **correctness, consistency, idempotency, and failure handling** in distributed systems.

### Key Principles

- **Ledger Service is the source of truth**
- **Wallet Service is a derived snapshot**
- **Transaction Service is the saga coordinator**
- **All cross-service communication is event-driven**
- **Idempotency is enforced at every boundary**
- **No dual writes without guarantees**

---

## Architecture

### Services

| Service | Responsibility |
|-------|---------------|
| Transaction Service | API entry point, transaction lifecycle, coordination |
| Wallet Service | Wallet balances, fund reservation, final credit/debit |
| Ledger Service | Immutable double-entry ledger (source of truth) |

Each service:
- Is a **separate Django project**
- Has its **own PostgreSQL database**
- Communicates via **Kafka events**
- Owns and mutates **only its own data**

---

## High-Level Transfer Flow (Wallet A → Wallet B)

### 1. Transaction Creation (Synchronous)

Client → Nginx → Transaction Service

Transaction Service:
- Accepts sender_wallet_id, receiver_wallet_id, amount, idempotency_key
- Creates a Transaction with status INITIATED
- Enforces API-level idempotency
- Calls Wallet Service synchronously to reserve funds

---

### 2. Wallet Reservation (Atomic)

BEGIN TRANSACTION  
validate wallets and balance  
enforce idempotency  
reserve amount in sender wallet  
write WalletReserved event to outbox  
COMMIT

---

### 3. Wallet Outbox Publishing

A background process reads the outbox table and publishes WalletReserved events to Kafka with retries.

---

### 4. Ledger Processing (Source of Truth)

Ledger Service consumes WalletReserved events:

BEGIN TRANSACTION  
if ledger entry already exists: COMMIT and return  
create debit and credit ledger entries  
write LedgerSuccess event to outbox  
COMMIT

Ledger is append-only and owns financial truth.

---

### 5. Ledger Outbox Publishing

Ledger Service publishes LedgerSuccess or LedgerFailed events via its outbox.

---

### 6. Wallet Finalization

On LedgerSuccess:
- Credit receiver wallet
- Debit sender wallet from reserved balance
- Clear reservation

On LedgerFailed:
- Release sender reservation

All operations are atomic.

---

### 7. Transaction Completion

Transaction Service consumes ledger events:
- LedgerSuccess → SUCCESS
- LedgerFailed → FAILED

Transaction Service is the sole owner of transaction state.

---

## Technologies Used

- Python 3.11
- Django + Django REST Framework
- PostgreSQL (one DB per service)
- Kafka
- Docker & Docker Compose

---

## Reliability Patterns

- Event-driven architecture
- Outbox pattern
- Database-backed idempotency
- At-least-once message delivery
- Idempotent consumers

---

## What Is Intentionally Excluded

- Authentication / Authorization
- User management
- Distributed transactions (2PC)
- Shared databases
- Celery as Kafka consumer

---

## Project Goal

This project demonstrates how to build a **financially correct, event-driven backend system** using real-world patterns, without unnecessary complexity.
