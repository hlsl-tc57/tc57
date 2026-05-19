# Building the HLSL TC57 Website with Docker

This Dockerfile builds the complete HLSL TC57 website, including both the Hugo static site and the LaTeX specification.

## Prerequisites

- Docker and Docker Compose installed
- Approximately 2GB of disk space for the build
- ~5-10 minutes build time (depending on system)

## Quick Start

### Option 1: Using Docker Compose (Recommended)

```bash
docker-compose build
docker-compose up
```

The website will be available at `http://localhost`

### Option 2: Using Docker Directly

```bash
# Build the image
docker build -t hlsl-website .

# Run the container
docker run -p 80:80 hlsl-website
```

## Build Details

The Dockerfile performs the following steps:

1. **System Dependencies**: Installs required packages including CMake, LaTeX, Inkscape, Pandoc, and Node.js
2. **Hugo**: Installs Hugo Extended v0.148.1 and Dart Sass
3. **Node Dependencies**: Installs theme and website dependencies
4. **LaTeX Build**: Builds the specification using CMake, producing:
   - PDF specification (`hlsl.pdf`)
   - HTML specification (`hlsl.zip` with chunked HTML)
5. **Hugo Build**: Generates the static website
6. **Artifact Assembly**: Copies LaTeX outputs to the Hugo public directory
7. **Nginx**: Serves the final website via Nginx

## Output

After a successful build, the website is available at `http://localhost` with:
- Hugo-generated website content
- Embedded LaTeX specification PDF
- Chunked HTML specification

## Building Without Serving

To build only without running the Nginx server, you can modify the `docker-compose.yml` or use:

```bash
docker build -t hlsl-website . --target 0
```

Then copy the output from `/workspace/website/public`:

```bash
docker run --rm -v $(pwd)/website/public:/output hlsl-website:latest cp -r /workspace/website/public /output
```

## Development Notes

- The build is multi-stage; the first stage builds everything, the second stage serves via Nginx
- Build artifacts are cached in the container, so subsequent builds are faster
- The LaTeX build requires a full TeX Live installation (~600MB)
- Node dependencies are optional and only installed if `package-lock.json` or `npm-shrinkwrap.json` exist

## Troubleshooting

### Build fails with "CMake not found"
Ensure the `spec/CMakeLists.txt` file exists and is properly configured.

### LaTeX build fails
Make sure all required LaTeX packages are installed. The Dockerfile includes `texlive-latex-extra` which contains most common packages.

### Large image size
This is expected due to full TeX Live installation (~600MB). For production, consider a separate LaTeX build step or using a more minimal TeX distribution.

### Seeing "Welcome to nginx!"
Ensure you have the most up-to-date version of the hugo-theme-techdoc submodule.
