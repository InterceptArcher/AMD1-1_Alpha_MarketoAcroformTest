```markdown
# Technical Specification: Backend API Route for Personalization

## 1. Summary
This document outlines the technical specifications for implementing a backend API route in a Next.js application to handle personalization logic. The route will interact with Claude's API to infer user persona and buyer stage based on email and `cta` inputs, validate the response using Zod, and store relevant data in Supabase.

## 2. Implementation Steps

### Step 1: Set Up API Route
- Create a new API route at `/api/personalize` within the Next.js application.
- Ensure the route is configured to handle POST requests only.

### Step 2: Extract Domain from Email
- Parse the incoming request payload to extract the email.
- Use a regular expression or a URL parsing library to extract the domain from the email address.

### Step 3: Infer Persona and Buyer Stage
- Analyze the email and `cta` (call-to-action) to infer the user's persona and buyer stage.
- Implement logic or use a predefined mapping to determine these attributes.

### Step 4: Integrate with Claude's API
- Construct a request payload with the inferred persona, buyer stage, and any additional required information.
- Send this payload to Claude's API using an appropriate HTTP client (e.g., Axios or Fetch API).
- Design the prompt and JSON schema to match Claude's API requirements.

### Step 5: Validate Response with Zod
- Upon receiving a response from Claude's API, validate the JSON structure using Zod to ensure data integrity.
- Define a Zod schema that matches the expected response format.

### Step 6: Handle Valid and Invalid Responses
- If the response is valid:
  - Parse the JSON response.
  - Send the parsed data back to the frontend.
- If the response is invalid:
  - Implement a retry mechanism with a "fix JSON" prompt to correct common errors.
  - Log errors and handle exceptions gracefully.

### Step 7: Store Data in Supabase
- Insert the job details and the output from Claude's API into Supabase tables.
- Ensure data is stored in a secure and efficient manner.

## 3. Tech Stack
- **Next.js**: For server-side rendering and API route management.
- **Claude's API**: For personalization logic and insights.
- **Zod**: For validating the structure of API responses.
- **Supabase**: As a database for storing job details and API outputs.
- **Axios or Fetch API**: For making HTTP requests to Claude's API.

## 4. Edge Cases
- **Invalid Email Format**: Handle cases where the email address is improperly formatted; reject the request with a clear error message.
- **Claude's API Errors**: Implement retry logic for handling timeouts or server errors from Claude's API.
- **Data Validation**: Ensure all incoming and outgoing data is validated to prevent injection attacks or malformed data storage.
- **Network Interruptions**: Plan for network failures and implement retries or fallback mechanisms.
```
