# Build stage
FROM node:18-alpine

WORKDIR /app

# Copy package files
COPY package*.json ./

# Install dependencies
RUN npm install

# Copy app source
COPY . .

# Expose port
EXPOSE 3000

# Start in development mode (for this demo/dev setup)
# For production, we would build and serve with Nginx
CMD ["npm", "start"]
