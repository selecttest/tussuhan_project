from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from api.dependencies import get_config
from api.routes import router


def create_app() -> FastAPI:
    config = get_config()
    app = FastAPI(
        title="收入理財規劃 Dashboard API",
        description="FastAPI backend for LINE Bot accounting and Google Sheets dashboard data.",
        version="1.0.0",
    )

    allow_origins = config.cors_allow_origins
    app.add_middleware(
        CORSMiddleware,
        allow_origins=allow_origins,
        allow_credentials=False,
        allow_methods=["GET", "POST", "PATCH", "DELETE", "OPTIONS"],
        allow_headers=["Content-Type", "Authorization"],
    )

    @app.exception_handler(RuntimeError)
    async def runtime_error_handler(_, exc: RuntimeError):
        return JSONResponse(status_code=500, content={"error": str(exc)})

    app.include_router(router)
    return app


app = create_app()
