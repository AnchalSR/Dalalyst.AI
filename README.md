# Dalalyst AI

Production-ready AI investor platform built with FastAPI, React, Tailwind, SQLite, yfinance, and Groq.

## Features

- Opportunity Radar: scores each stock using price change, volume ratio, and trend direction to produce Strong Breakout, Moderate Breakout, or Weak Signal with confidence.
- Historical Validation: reviews the last 30-60 sessions for similar setups and reports `historical_accuracy`.
- Portfolio Intelligence: lets each user save stocks, scan portfolio-only signals, and monitor personalized opportunities.
- Risk Alert System: flags downtrends, sudden drops, and heavy selling pressure.
- Chart Intelligence: fetches historical data, classifies trend, and returns chart-ready moving-average series.
- Market Chatbot: multi-turn investor chat with SQLite persistence and optional stock-symbol context in the prompt.
- Video Engine: turns stock analysis into slide-ready JSON storyboards.
- Authentication: register, login, JWT-based protected routes, and frontend logout via local token removal.

## Project Structure

```text
backend/
  agents/
  auth/
  models/
  routes/
  services/
  config.py
  database.py
  main.py

frontend/
  components/
  lib/
  pages/
```

## Environment Variables

Create a root `.env` file:

```env
GROQ_API_KEY=your_key_here
GROQ_MODEL=llama-3.3-70b-versatile
JWT_SECRET_KEY=replace_with_a_long_random_secret
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=240
SQLITE_PATH=backend/dalalyst.db
CORS_ORIGINS=http://localhost:5173,http://127.0.0.1:5173
```

`GROQ_API_KEY` is required for Groq responses. If it is missing, the backend still runs and returns deterministic fallback text for AI-generated sections.

## Run The Backend

```bash
cd backend
pip install -r requirements.txt
uvicorn main:app --reload --port 8000
```

Backend base URL: `http://localhost:8000`

## Run The Frontend

```bash
cd frontend
npm install
npm run dev
```

Frontend URL: `http://localhost:5173`

The Vite dev server proxies `/api/*` requests to `http://localhost:8000`.

## Authentication Flow

1. Register with email and password.
2. Passwords are hashed with `bcrypt` before storage in SQLite.
3. Login returns a JWT bearer token.
4. The frontend stores the token in `localStorage`.
5. Protected routes include:
   - `GET /radar/alerts`
   - `GET /radar/saved`
   - `POST /chat/message`
   - `GET /chat/history`
   - `GET /video/generate`
   - `GET /auth/me`
6. Logout removes the token from `localStorage`.

## Core API Routes

### Auth

- `POST /auth/register`
- `POST /auth/login`
- `GET /auth/me`

### Opportunity Radar

- `GET /radar/watchlist`
- `GET /radar/analyze?symbol=NVDA`
- `GET /radar/alerts?symbols=AAPL,MSFT,NVDA`
- `GET /radar/saved`
- `GET /radar/portfolio`
- `POST /radar/portfolio`
- `DELETE /radar/portfolio/{stock}`

### Chart Intelligence

- `GET /chart/analyze?symbol=NVDA`

### Market Chat

- `POST /chat/message`
- `GET /chat/history`

### Video Engine

- `GET /video/generate?symbol=AAPL`

## Common Errors And Fixes

- `401 Could not authenticate user`
  - Log in again or clear `localStorage` if the token is expired or invalid.
- `GROQ_API_KEY is missing`
  - Add `GROQ_API_KEY` to the root `.env` file and restart the backend.
- `No market data found for SYMBOL`
  - Check the ticker symbol and confirm that yfinance has data for it.
- Frontend shows fetch failures
  - Make sure the FastAPI app is running on port `8000`.
- Groq request fails
  - Check internet access, key validity, and the configured Groq model name.

## Notes

- SQLite tables are created automatically on backend startup.
- Radar scans persist alert snapshots to the `alerts` table for the logged-in user.
- Chat responses are stored in the `chats` table for conversation history.
- The database file defaults to `backend/dalalyst.db`.
- Radar scoring uses a 100-point model:
  - Price change contributes up to 35 points.
  - Volume ratio contributes up to 35 points.
  - Trend direction contributes up to 30 points.
- Historical accuracy:
  - Looks back across roughly the last 30-60 trading sessions.
  - Finds prior setups with the same signal-strength bucket.
  - Marks a bullish setup successful if it reached about +3% within the next 5 sessions.
  - Marks an avoid setup successful if it fell about -3% within the next 5 sessions.
- Portfolio insights:
  - Portfolio symbols are stored per user in SQLite.
  - Each saved stock is re-run through the same radar engine.
  - The app summarizes strongest current opportunities and aggregates risk alerts for the portfolio.
- Signal buckets:
  - `75+`: Strong Breakout -> `BUY`
  - `55-74`: Moderate Breakout -> `WATCH`
  - `<55`: Weak Signal -> `AVOID`
