# ───── Dockerfile ─────
# 1. start from a tiny Python runtime
FROM python:3.11-slim AS runtime

# 2. copy *only* the frozen deps first – this lets Docker cache them
WORKDIR /app
COPY code/requirements.lock .
COPY code/wheelhouse/ ./wheelhouse/

# 3. install exact wheels with no internet access
RUN pip install --no-index --find-links=wheelhouse -r requirements.lock

# 4. copy the actual source code last
COPY code/ .

# 5. default command when someone runs the container
CMD ["python", "tdc001.py"]
