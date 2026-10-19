# syntax=docker/dockerfile:1.27.1@sha256:4edf897a3ffa55b89f906fc8cc78afdb3f1834cc9c7083565e611a8a7d5fe99e
FROM ghcr.io/astral-sh/uv:0.12.15@sha256:62f8c047d0a0e9ece6b53fc63df902585a67a47a7f318ddec4a37db586edc8e3 AS uv
FROM python:3.14.7-slim-bookworm@sha256:82bc3c539b8813ada9d68c63b40158fa002f7f33de9bf3312a3dfdc0620dff56
COPY --from=uv /uv /usr/local/bin/uv
RUN apt-get update && apt-get install -y --no-install-recommends git gh ca-certificates && rm -rf /var/lib/apt/lists/*
WORKDIR /admission
ENV PATH=/admission/.venv/bin:$PATH UV_LINK_MODE=copy UV_PYTHON_DOWNLOADS=never PYTHONDONTWRITEBYTECODE=1
COPY --chmod=u=rwX,go=rX .github/admission/pyproject.toml .github/admission/uv.lock ./
RUN --mount=type=cache,id=sdk-admission-uv-314-linux-amd64,target=/root/.cache/uv,sharing=locked uv sync --locked --no-install-project
COPY --chmod=u=rwX,go=rX .github/scripts/sdk_admission.py .github/scripts/test_sdk_admission.py ./
ENTRYPOINT ["python", "/admission/sdk_admission.py"]
