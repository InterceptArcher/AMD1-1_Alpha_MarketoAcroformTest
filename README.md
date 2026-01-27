# LinkedIn Post-Click Personalization

A Next.js web application for LinkedIn campaign personalization that displays dynamic content based on URL query parameters and captures user email with consent.

## Features

### 1. Query String Parsing and Dynamic Content Display
- **Implementation**: Next.js App Router with client-side `useSearchParams` hook
- **Functionality**: Parses the `cta` query parameter from the URL and displays personalized content
- **Default Behavior**: Shows "Default CTA Message" when no `cta` parameter is provided
- **Edge Cases Handled**:
  - Missing query parameters
  - Special characters in URLs
  - Multiple query parameters
  - URL encoding
- **Rationale**: Using Next.js App Router provides optimal performance with React Server Components while maintaining client-side interactivity for dynamic query parameter handling. The `useSearchParams` hook is wrapped in `Suspense` to prevent hydration issues.

### 2. Email Capture Form with Consent Validation
- **Implementation**: Client-side React form component with real-time validation
- **Validation Methodology**:
  - HTML5 email validation attributes (`type="email"`, `pattern`, `required`)
  - Custom JavaScript validation using regex: `/^[^\s@]+@[^\s@]+\.[^\s@]+$/`
  - Real-time form state management with React hooks (`useState`, `useEffect`)
- **Security Features**:
  - XSS protection through React's automatic escaping
  - Email format validation prevents injection attacks
  - No server-side processing (static form submission simulation)
- **UX Features**:
  - Submit button disabled until both email is valid AND consent is checked
  - Visual feedback with button state changes (color, cursor)
  - Success message display after submission
  - Double-submission prevention during form processing
- **Rationale**: Client-side validation provides immediate user feedback while HTML5 attributes ensure baseline browser validation. The disabled button pattern prevents invalid submissions and provides clear visual cues about form state.

## Tech Stack

### Frontend
- **Framework**: Next.js 14.2+ with App Router
- **Language**: TypeScript 5.9+
- **Runtime**: React 18.3+
- **Styling**: Inline styles (as per spec requirements)

### Infrastructure
- **Hosting**: Vercel (serverless deployment)
- **Build Tool**: Next.js built-in bundler
- **Package Manager**: npm

### Testing
- **Framework**: Playwright 1.58+
- **Test Coverage**:
  - Query string parsing (5 tests)
  - Email form validation (11 tests)
  - Chaos/security testing (4 tests)
- **CI/CD**: Tests run against deployed URLs via `BASE_URL` environment variable

## Project Structure

```
.
├── app/
│   ├── layout.tsx           # Root layout with metadata
│   ├── page.tsx             # Landing page with query parsing
│   └── components/
│       └── EmailForm.tsx    # Email and consent form component
├── tests/
│   ├── landing-page.spec.ts # Query string parsing tests
│   ├── email-form.spec.ts   # Form validation tests
│   └── chaos-security.spec.ts # Security and chaos testing
├── docs/
│   ├── 002-create-nextjs-project-structure.md
│   └── 003-develop-email-and-consent-form.md
├── scripts/
│   └── deploy-frontend-vercel.sh  # Vercel deployment script
├── setup/
│   └── stack.json           # Stack configuration
├── next.config.mjs          # Next.js configuration
├── playwright.config.ts     # Playwright test configuration
├── vercel.json             # Vercel deployment settings
└── package.json            # Dependencies and scripts
```

## Installation

```bash
# Install dependencies
npm install

# Install Playwright browsers (for testing)
npx playwright install --with-deps chromium
```

## Development

```bash
# Start development server
npm run dev

# Open browser to http://localhost:3000
```

### Testing Query Parameters

```bash
# Test with specific CTA value
http://localhost:3000/?cta=compare

# Test with different CTA
http://localhost:3000/?cta=signup

# Test default behavior (no parameter)
http://localhost:3000/
```

## Testing

```bash
# Run all tests
npm test

# Run specific test suites
npm test -- tests/landing-page.spec.ts
npm test -- tests/email-form.spec.ts

# Run tests with UI
npm run test:headed
```

## Deployment

### Prerequisites
Environment variables must be set:
- `VERCEL_TOKEN`: Vercel authentication token

### Deploy to Vercel

```bash
# Deploy to preview environment
./scripts/deploy-frontend-vercel.sh

# Deploy to production
./scripts/deploy-frontend-vercel.sh --production
```

The deployment script will:
1. Validate environment variables
2. Run production build
3. Create/link Vercel project
4. Deploy to Vercel
5. Output the deployed URL
6. Save project IDs to `.env` for future deployments

**Security Note**: The deployment script reads credentials from environment variables only. No secrets are hardcoded or committed to the repository.

## Implementation Methodology

### Test-Driven Development (TDD)
All features were implemented following TDD:
1. **Tests written first**: All Playwright tests were created before implementation
2. **Red-Green-Refactor**: Tests initially failed, then implementation made them pass
3. **Comprehensive coverage**: Tests cover happy paths, edge cases, and security scenarios

### Security-First Approach
- **No secrets in code**: All credentials via environment variables
- **XSS protection**: React's automatic escaping + email validation
- **Input validation**: Multiple layers (HTML5, regex, React state)
- **Form security**: Double-submission prevention, invalid format rejection
- **Chaos testing**: Random interaction tests ensure application stability

### Performance Optimizations
- **React Server Components**: Used where possible for reduced JavaScript bundle
- **Code splitting**: Next.js automatic code splitting for optimal loading
- **Static generation**: Landing page pre-rendered at build time
- **Client-side hydration**: Minimal client JS for query parameter handling

## Configuration

### Stack Configuration (`setup/stack.json`)
```json
{
  "project_name": "linkedin-personalization",
  "owner": "InterceptArcher",
  "stack_type": "fullstack",
  "frontend": {
    "provider": "vercel",
    "framework": "nextjs",
    "language": "typescript"
  }
}
```

This configuration ensures:
- Correct infrastructure generation for Vercel
- TypeScript enforcement
- Next.js-specific optimizations

## Browser Support
- Chrome/Edge (latest)
- Firefox (latest)
- Safari (latest)
- All tests run against Chromium via Playwright

## Known Limitations
- Form submission is simulated (no actual backend)
- Email addresses are not persisted (frontend-only demo)
- Single landing page (no routing beyond query parameters)

## Future Enhancements
Based on the current implementation, potential additions could include:
- Backend API for email storage (Supabase, as per stack capabilities)
- Multiple CTA templates with different designs
- A/B testing framework for conversion optimization
- Analytics integration for campaign tracking
- Multi-language support for international campaigns

## License
ISC

## Author
InterceptArcher