FROM python:3.11-alpine
RUN addgroup -g 65532 verifier && adduser -D -u 65532 -G verifier verifier && pip install --no-cache-dir 'pytest>=8,<10'
USER 65532:65532
WORKDIR /tmp
