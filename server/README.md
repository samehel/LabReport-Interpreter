# LabReport Interpreter — Backend Server

REST API backend for the LabReport Interpreter mobile application. Built with FastAPI, SQLite, and a custom-trained RandomForestClassifier for lab result analysis.

## Quick Start

### 1. Set Up Python Environment

```bash
# Navigate to the server directory
cd server

# Create a virtual environment
python -m venv venv

# Activate it
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Configure Environment

```bash
# Copy the example env file
copy .env.example .env    # Windows
# cp .env.example .env    # macOS/Linux

# Edit .env and set a secure SECRET_KEY for production
```

The default `.env` uses SQLite and a 24-hour token expiry. No external database setup needed.

### 3. Run the Server

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at:
- **API**: http://localhost:8000
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

### 4. (Optional) Train the ML Model

The server works without a trained model — it will still classify values against reference ranges and generate summaries. To enable condition prediction:

1. Download datasets from Kaggle (see `datasets/README.md` for links)
2. Place CSV files in the `datasets/` folder
3. Run the training script:

```bash
python -m app.ml.train_model
```

The trained model will be saved to `app/ml/models/classifier_model.joblib`.

## API Endpoints

### Authentication
| Method | Path | Auth | Description |
|--------|------|------|-------------|
| POST | `/auth/register` | No | Create account |
| POST | `/auth/login` | No | Returns JWT (24h) |
| GET | `/auth/me` | Yes | User profile |
| PUT | `/auth/password` | Yes | Change password |
| DELETE | `/auth/account` | Yes | Delete account |

### Reports
| Method | Path | Auth | Description |
|--------|------|------|-------------|
| GET | `/reports` | Yes | List reports |
| GET | `/reports/dashboard` | Yes | Dashboard stats |
| POST | `/reports/upload` | Yes | Upload PDF/image |
| POST | `/reports/manual` | Yes | Manual entry |
| GET | `/reports/{id}` | Yes | Report detail |
| DELETE | `/reports/{id}` | Yes | Delete report |

### Metrics & Trends
| Method | Path | Auth | Description |
|--------|------|------|-------------|
| GET | `/metrics/available` | Yes | List test names |
| GET | `/metrics/{test_name}/trend` | Yes | Trend data |

### Summary & PDF
| Method | Path | Auth | Description |
|--------|------|------|-------------|
| POST | `/summary/{report_id}` | Yes | Regenerate summary |
| GET | `/summary/{report_id}/pdf` | Yes | Download PDF |

## Authentication

All authenticated endpoints require a Bearer token in the `Authorization` header:

```
Authorization: Bearer <your_token_here>
```

Get a token by calling `POST /auth/login` with email and password. The token is valid for 24 hours.

## Project Structure

```
server/
├── app/
│   ├── main.py              # FastAPI app entry point
│   ├── config.py            # Settings (.env)
│   ├── database.py          # SQLite async engine
│   ├── routers/             # API endpoints
│   ├── models/              # SQLAlchemy models
│   ├── schemas/             # Pydantic schemas
│   ├── services/            # Business logic
│   ├── ml/                  # ML pipeline
│   │   ├── ocr.py           # PDF/image text extraction
│   │   ├── parser.py        # Lab value parsing
│   │   ├── classifier.py    # Reference range classification
│   │   ├── condition_predictor.py  # RF model inference
│   │   ├── summarizer.py    # Summary generation
│   │   ├── correlations.py  # Clinical patterns
│   │   └── train_model.py   # Model training script
│   ├── data/
│   │   └── reference_ranges.py  # 80+ lab test ranges
│   └── utils/
│       ├── security.py      # JWT + bcrypt
│       └── pdf_generator.py # PDF reports
├── datasets/                # Training data (CSV)
├── uploads/                 # Uploaded files
├── requirements.txt
└── .env
```

## Security

- **JWT Authentication**: Single token, 24h expiry, HS256
- **Password Hashing**: bcrypt via passlib
- **Input Validation**: Pydantic schemas on all endpoints
- **File Upload**: MIME type whitelist, 10MB limit
- **User Isolation**: All queries filtered by authenticated user ID
- **Rate Limiting**: 30/min for auth, 60/min for general endpoints
- **CORS**: Configurable origins

## Connecting from Flutter

Set the base URL in your Flutter app to point to the server:

```dart
// lib/config/api_config.dart
const String baseUrl = 'http://<your-ip>:8000';
// For local Android emulator: http://10.0.2.2:8000
// For local iOS simulator: http://localhost:8000
```

Store the JWT token from login in `flutter_secure_storage`:

```dart
final token = loginResponse['access_token'];
await secureStorage.write(key: 'auth_token', value: token);
```
