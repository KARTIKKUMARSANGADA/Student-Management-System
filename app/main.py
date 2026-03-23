from fastapi import FastAPI, Request
from starlette.responses import Response

import sentry_sdk
from prometheus_client import Counter, Histogram, generate_latest, CONTENT_TYPE_LATEST

from app.database import engine, Base
from app.routers import auth, student, course, enrollments, grade
import app.models

Base.metadata.create_all(bind=engine)

sentry_sdk.init(
    dsn="https://5ca89e16de715881600f2f4bf3443ebf@o4510991175057408.ingest.us.sentry.io/4510991176761344",
    # Add data like request headers and IP for users,
    # see https://docs.sentry.io/platforms/python/data-management/data-collected/ for more info
    send_default_pii=True,
)


app = FastAPI(title="Student Management System")

# Metrics
REQUEST_COUNT = Counter(
    "http_requests_total",
    "Total HTTP Requests"
)

REQUEST_TIME = Histogram(
    "http_request_duration_seconds",
    "Request duration in seconds"
)

@app.middleware("http")
async def metrics_middleware(request: Request, call_next):
    REQUEST_COUNT.inc()

    with REQUEST_TIME.time():
        response = await call_next(request)

    return response


@app.get("/", tags=["Welcome"])
def welcome():
    return {"message": "Welcome TO Student Management System"}


    
# Routers
app.include_router(auth.router)
app.include_router(student.router)
app.include_router(course.router)
app.include_router(enrollments.router)
app.include_router(grade.router)


# Metrics endpoint
@app.get("/metrics",tags=['Checking'])
def metrics():
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)

@app.get("/sentry-debug",tags=['Checking'])
async def trigger_error():
    division_by_zero = 10 / 5
