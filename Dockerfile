# Multi-stage build for HLSL TC57 website with Hugo and LaTeX

# Stage 1: Builder
FROM ubuntu:22.04

# Set environment variables
ENV HUGO_VERSION=0.148.1 \
    DEBIAN_FRONTEND=noninteractive \
    HUGO_ENVIRONMENT=production

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    wget \
    git \
    cmake \
    build-essential \
    texlive \
    texlive-latex-extra \
    inkscape \
    unzip \
    npm \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Install Hugo extended and Pandoc for the container architecture
RUN arch=$(dpkg --print-architecture) \
    && case "$arch" in \
      amd64) HUGO_ARCH=amd64 PANDOC_ARCH=amd64 ;; \
      arm64|arm64v8) HUGO_ARCH=arm64 PANDOC_ARCH=arm64 ;; \
      aarch64) HUGO_ARCH=arm64 PANDOC_ARCH=arm64 ;; \
      *) echo "Unsupported architecture: $arch" >&2 ; exit 1 ;; \
    esac \
    && wget -O /tmp/hugo.deb https://github.com/gohugoio/hugo/releases/download/v${HUGO_VERSION}/hugo_extended_${HUGO_VERSION}_linux-${HUGO_ARCH}.deb \
    && dpkg -i /tmp/hugo.deb \
    && rm /tmp/hugo.deb \
    && wget -O /tmp/pandoc.deb https://github.com/jgm/pandoc/releases/download/3.1.9/pandoc-3.1.9-1-${PANDOC_ARCH}.deb \
    && dpkg -i /tmp/pandoc.deb \
    && rm /tmp/pandoc.deb

# Install Dart Sass
RUN npm install -g sass

# Set working directory
WORKDIR /workspace

# Copy the entire repository
COPY . .

# Install Node.js dependencies for the theme
RUN if [ -f package-lock.json ] || [ -f npm-shrinkwrap.json ]; then npm ci; fi || true

# Build LaTeX specification
RUN cmake -B build ./spec \
    && cmake --build build --target html-chunked \
    && cmake --build build --target pdf

# Build Hugo website
RUN cd website \
    && hugo \
    --minify \
    --baseURL "/"

# Copy LaTeX outputs to Hugo public directory
RUN mkdir -p website/public/spec/assets \
    && cp spec/assets/* website/public/spec/assets/ 2>/dev/null || true \
    && cp build/hlsl.pdf website/public/spec/ \
    && unzip build/html/hlsl.zip -d website/public/spec/

# Stage 2: Runtime (optional - for serving the built site)
FROM nginx:alpine

COPY --from=0 /workspace/website/public /usr/share/nginx/html

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
