# Second stage: create the final image
FROM apify/actor-python-playwright:3.11

# Copy just requirements.txt first to leverage Docker cache
COPY requirements.txt ./

# Install the packages
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application
COPY . ./

# Ensure playwright browsers are installed
RUN playwright install --with-deps chromium

# Run the actor
CMD ["python", "-m", "apify", "run"]
