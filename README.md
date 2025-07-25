# 🌾 Crop Yield Prediction using ML Workflow

[![CI/CD](https://github.com/Sumanthcs4/Crop-Yield-Prediction/actions/workflows/main.yaml/badge.svg)](https://github.com/Sumanthcs4/Crop-Yield-Prediction/actions/workflows/main.yaml)

---

## 📌 Project Overview

This project focuses on predicting agricultural crop yield using a full machine learning lifecycle — from data ingestion and validation to model deployment. It uses a modular pipeline, supports experiment tracking (MLflow), and is deployed with FastAPI on Render using Docker and GitHub Actions for CI/CD.

The deployed model is a **regression-based estimator**, trained on real-world agricultural features like rainfall, temperature, crop type, and pesticide usage.

---

## 📐 Project Architecture

```mermaid
graph TD
    subgraph "Data Ingestion"
        A[MongoDB Atlas] --> B(Data Ingestion)
        B --> C{Split Train/Val/Test}
    end

    subgraph "Data Validation"
        C --> D(Data Validation)
        D --> E{Schema & Drift Check}
        E -- Pass --> F[Valid Data]
        E -- Fail --> G[Error Logged]
    end

    subgraph "Data Transformation"
        F --> H(Data Transformation)
        H --> I[Encoder & Scaler]
        I --> J[Transformed Arrays]
    end

    subgraph "Model Training"
        J --> K(Model Trainer)
        K --> L["Regressor: DecisionTrees, RandomForest, XGBoost"]
        K --> M[Trained Model Artifacts]
    end

    subgraph "Model Evaluation"
        M --> N(Evaluation)
        N --> O{Performance Metrics}
    end

    subgraph "Deployment"
        O --> P[Saved Model]
        P --> Q[FastAPI App]
        Q --> R[Dockerized & Deployed on Render]
    end

    classDef primary fill:#4285f4,stroke:#333,stroke-width:2px,color:white
    classDef success fill:#34a853,stroke:#333,stroke-width:2px,color:white
    classDef warning fill:#fbbc05,stroke:#333,stroke-width:2px,color:black
    classDef error fill:#ea4335,stroke:#333,stroke-width:2px,color:white

    class A,B,C,D,H,K,N,P,Q primary
    class F,J,M,R success
    class E,O warning
    class G error
    class I,L secondary
```

---

## 🚀 Deployment Pipeline (CI/CD)

```mermaid
graph TD
    A[Push to GitHub main] --> B[GitHub Actions Trigger]
    B --> C[Optional: Lint/Test]
    C --> D[Trigger Render Deploy Hook]
    D --> E[Docker Build on Render]
    E --> F[App Deployed Publicly]

    classDef process fill:#fbbc05,stroke:#333,stroke-width:2px,color:black
    classDef success fill:#34a853,stroke:#333,stroke-width:2px,color:white
    classDef trigger fill:#4285f4,stroke:#333,stroke-width:2px,color:white

    class A,B,C trigger
    class D,E success
    class F process
```

---
// Rest of the content remains unchanged
