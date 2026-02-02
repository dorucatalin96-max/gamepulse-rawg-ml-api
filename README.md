# GamePulse — RAWG ML API

End-to-end Data & ML project using RAWG video game data:
ingestion on AWS (Lambda → S3), ETL into PostgreSQL (RDS), model training, and a FastAPI service for predictions.

---

## 🔥 What this project demonstrates
- AWS-style data ingestion pipeline (Lambda → S3)
- Event-driven ETL design (S3 trigger → Lambda → PostgreSQL upsert)
- Clean relational schema + raw JSON storage
- ML training + evaluation (baseline model)
- FastAPI endpoints for prediction (Swagger UI)

---

## 🧱 Architecture
RAWG API → Ingestion Lambda → S3 (raw JSON) → ETL Lambda → PostgreSQL (RDS) → ML Training → FastAPI

---

## 📦 Repository structure

sql/ # schema, views
ingestion_lambda/ # RAWG → S3 (raw JSON)
etl_lambda/ # S3 trigger → normalize → upsert into Postgres
ml/ # training, evaluation, saved models
api/ # FastAPI app (health + predict)
docs/ # diagrams + notes + screenshots
data/ # sample dataset for local training

## ✅ Milestones
- [x] Create PostgreSQL schema (raw + structured)
- [x] Ingestion Lambda (RAWG → S3)
- [x] ETL Lambda (S3 → Postgres) with idempotent upsert
- [x] ML baseline training + evaluation
- [x] FastAPI `/predict` endpoint
- [ ] Analytics endpoints: `/ask-text` and `/ask-visual`
- [ ] Deployment notes (AWS + Docker)

## 🛡️ Notes
- No secrets are committed. Use AWS SSM / Secrets Manager.
- All SQL queries for analytics are read-only and validated.

## 📍 Status

✅ Completed — end-to-end data pipeline, ML training and FastAPI prediction endpoint working locally.

