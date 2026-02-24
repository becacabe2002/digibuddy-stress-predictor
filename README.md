# DigiBuddy Stress Predictor

A stateless HTTP API that predicts a user’s stress level for the DigiBuddy mobile app.  
It is implemented with **FastAPI** and a pre-trained **Random Forest** model (`random_forest.joblib`).

## Features

- `/health` endpoint to check service and model health
- `/predict` endpoint that returns a stress level (`low`, `Medium`, `High`)
- Dockerized, ready to run on Kubernetes / OpenShift (Rahti CSC)

---

## Technology Stack

- Python 3.12
- FastAPI
- Uvicorn
- scikit-learn (Random Forest model loaded via `joblib`)
- Docker
- OpenShift (Rahti CSC) for deployment

---

## Getting Started (Local Development)

### 1. Clone the repository

```bash
git clone https://github.com/becacabe2002/digibuddy-stress-predictor.git
cd digibuddy-stress-predictor
```

### 2. Create a virtual environment (optional but recommended)

```bash
python3 -m venv .venv
source .venv/bin/activate  # on Windows: .venv\\Scripts\\activate
```

### 3. Install dependencies

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### 4. Run the API locally

```bash
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

The service will be available at: `http://localhost:8000`

- Interactive API docs (Swagger UI): `http://localhost:8000/docs`
- Alternative docs (ReDoc): `http://localhost:8000/redoc`

---

## API Endpoints

### `GET /health`

Returns basic health information and whether the ML model was loaded successfully.

**Example response (healthy):**

```json
{
  "status": "ok"
}
```

**Example response (model not loaded):**

```json
{
  "status": "unhealthy",
  "detail": "model not loaded"
}
```

---

### `POST /predict`

Predicts the stress level for a user based on their demographic and behavior features.

#### Request body

```json
{
  "age": 25,
  "gender": "female",
  "region": "Europe",
  "income_level": "Upper-Mid",
  "education_level": "Master",
  "daily_role": "Student",
  "device_hours_per_day": 6.5,
  "phone_unlocks": 80,
  "notifications_per_day": 120,
  "social_media_mins": 90,
  "study_mins": 180,
  "physical_activity_days": 3,
  "sleep_hours": 7.5,
  "sleep_quality": 4.0,
  "device_type": "Android"
}
```

#### Field constraints (as enforced by the Pydantic model)

- `age`: integer
- `gender`: `"male" | "female"`
- `region`: `"Asia" | "Africa" | "North America" | "Middle East" | "Europe" | "South America"`
- `income_level`: `"High" | "Lower-Mid" | "Low" | "Upper-Mid"`
- `education_level`: `"High School" | "Master" | "Bachelor" | "PhD"`
- `daily_role`: `"Part-time/Shift" | "Full-time Employee" | "Caregiver/Home" | "Unemployed_Looking" | "Student"`
- `device_hours_per_day`: float
- `phone_unlocks`: integer
- `notifications_per_day`: integer
- `social_media_mins`: integer
- `study_mins`: integer
- `physical_activity_days`: float (e.g. 0–7 days/week, range enforced by caller)
- `sleep_hours`: float
- `sleep_quality`: float (e.g. 1–5 scale, range enforced by caller)
- `device_type`: `"Android" | "Laptop" | "Tablet" | "iPhone"`

#### Example response

```json
{
  "stress_level": "Medium"
}
```

The exact labels depend on the trained model, but are expected to be one of: `low`, `Medium`, `High`.

---

## Docker Usage

### Build the image locally

```bash
docker build -t digibuddy-stress-predictor:latest .
```

### Run the container locally

```bash
docker run --rm -p 8000:8000 digibuddy-stress-predictor:latest
```

The API will now be available at `http://localhost:8000`.

---

## Deployment on Rahti (OpenShift)

This service is designed to run on **Rahti CSC** (OpenShift). A sample `deployment.yml` is provided which defines:

- A `Deployment` named `digibuddy-stress-predictor`
- A `Service` exposing port 80 → container port 8000 (`http`)
- An OpenShift `Route` for external access

### Image registry

The deployment expects the container image to be available at:

```text
image-registry.apps.2.rahti.csc.fi/sdx-assignment-tngo/digibuddy-stress-predictor:latest
```

### Manual deployment steps (reference)

From the project root:

```bash
# Build image
docker build -t image-registry.apps.2.rahti.csc.fi/sdx-assignment-tngo/digibuddy-stress-predictor:latest --no-cache .

# Push image to Rahti image registry
docker push image-registry.apps.2.rahti.csc.fi/sdx-assignment-tngo/digibuddy-stress-predictor:latest

# Apply OpenShift resources
oc apply -f deployment.yml
```

Your cluster/namespace, login method, and image tag may differ depending on your Rahti configuration.

---

## CI/CD (GitHub Actions)

A workflow file under `.github/workflows/build-deploy.yml` can be configured to:

- Build and push the Docker image to Rahti’s image registry on each push to `main`.
- Log in to the OpenShift cluster.
- Run `oc apply -f deployment.yml` to roll out new versions automatically.

This repository is prepared to be used with such a pipeline; adjust the workflow to match your Rahti project, registry credentials, and namespace.

---

## Project Structure

```text
.
├── main.py                 # FastAPI application and endpoints
├── random_forest.joblib    # Pre-trained Random Forest model
├── requirements.txt        # Python dependencies
├── Dockerfile              # Container build instructions
├── deployment.yml          # OpenShift/Rahti deployment, service, and route
└── README.md               # Project documentation
```


