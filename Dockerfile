# Build stage
FROM node:18-alpine AS builder

# Create non-root user
RUN addgroup -S appgroup && adduser -S appuser -G appgroup

# Set working directory
WORKDIR /app

# Copy package files
COPY package*.json ./

# Install dependencies with security audit
RUN npm ci && \
    npm audit fix --force || true

# Copy source code
COPY . .

# Build application
RUN npm run build

# Production stage
FROM node:18-alpine

# Install security updates and required packages
RUN apk update && \
    apk upgrade && \
    apk add --no-cache tini && \
    rm -rf /var/cache/apk/*

# Create non-root user
RUN addgroup -S appgroup && adduser -S appuser -G appgroup

# Set working directory
WORKDIR /app

# Copy package files
COPY package*.json ./

# Install production dependencies only
RUN npm ci --only=production && \
    npm audit fix --force || true

# Copy built application from builder stage
COPY --from=builder /app/dist ./dist

# Set proper permissions
RUN chown -R appuser:appgroup /app

# Set non-root user
USER appuser

# Expose port
EXPOSE 3000

# Use tini as init system
ENTRYPOINT ["/sbin/tini", "--"]

# Start application with proper signal handling
CMD ["node", "dist/index.js"] 