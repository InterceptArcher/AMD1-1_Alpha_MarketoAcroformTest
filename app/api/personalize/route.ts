import { NextRequest, NextResponse } from 'next/server';
import { PersonalizeRequestSchema } from '@/lib/schemas';
import { extractDomain, inferPersona, inferBuyerStage } from '@/lib/utils/email';
import { enrichCompanyData } from '@/lib/utils/enrichment';
import { generatePersonalizedContent } from '@/lib/anthropic/client';
import { generateMockPersonalizedContent } from '@/lib/anthropic/mock-client';
import {
  createPersonalizationJob,
  storePersonalizationOutput,
  updateJobStatus,
} from '@/lib/supabase/queries';

// Check if running in mock mode (for testing without API keys)
const MOCK_MODE = process.env.MOCK_MODE === 'true';

export async function POST(request: NextRequest) {
  try {
    // Parse and validate request body
    const body = await request.json();
    const validationResult = PersonalizeRequestSchema.safeParse(body);

    if (!validationResult.success) {
      return NextResponse.json(
        {
          error: 'Invalid request data',
          details: validationResult.error.flatten().fieldErrors,
        },
        { status: 400 }
      );
    }

    const { email, cta } = validationResult.data;

    // Step 1: Extract domain from email
    const domain = extractDomain(email);

    // Step 2: Infer persona and buyer stage
    const persona = inferPersona(email);
    const buyer_stage = inferBuyerStage(cta);

    // Step 3: Enrich company data (mocked for alpha)
    const companyData = enrichCompanyData(domain);

    // MOCK MODE: Skip database and use mock AI
    if (MOCK_MODE) {
      console.log('🧪 MOCK MODE: Generating mock personalized content...');

      const personalizedContent = await generateMockPersonalizedContent({
        persona,
        buyer_stage,
        industry: companyData.industry,
        company_size: companyData.company_size,
        cta,
      });

      return NextResponse.json({
        success: true,
        jobId: 'mock-' + Date.now(),
        data: personalizedContent,
        metadata: {
          persona,
          buyer_stage,
          company: companyData.company_name,
          industry: companyData.industry,
        },
        mock: true,
      });
    }

    // PRODUCTION MODE: Use real database and Claude API
    // Step 4: Create job record in Supabase
    const jobId = await createPersonalizationJob({
      email,
      domain,
      cta,
      persona,
      buyer_stage,
      company_name: companyData.company_name,
      industry: companyData.industry,
      company_size: companyData.company_size,
    });

    try {
      // Step 5: Call Claude API to generate personalized content
      const personalizedContent = await generatePersonalizedContent({
        persona,
        buyer_stage,
        industry: companyData.industry,
        company_size: companyData.company_size,
        cta,
      });

      // Step 6: Store the output in Supabase
      await storePersonalizationOutput(jobId, personalizedContent);

      // Step 7: Update job status to completed
      await updateJobStatus(jobId, 'completed');

      // Step 8: Return the personalized content to frontend
      return NextResponse.json({
        success: true,
        jobId,
        data: personalizedContent,
        metadata: {
          persona,
          buyer_stage,
          company: companyData.company_name,
          industry: companyData.industry,
        },
      });
    } catch (claudeError) {
      // Update job status to failed
      await updateJobStatus(jobId, 'failed');

      console.error('Personalization error:', claudeError);

      // Check if it's a missing API key error
      if (
        claudeError instanceof Error &&
        claudeError.message.includes('ANTHROPIC_API_KEY')
      ) {
        return NextResponse.json(
          {
            error: 'Service configuration error',
            message:
              'Claude API key is not configured. Please set ANTHROPIC_API_KEY environment variable.',
            jobId,
          },
          { status: 503 }
        );
      }

      throw claudeError;
    }
  } catch (error) {
    console.error('API error:', error);

    // Handle specific error types
    if (error instanceof Error) {
      if (error.message.includes('Invalid email format')) {
        return NextResponse.json(
          { error: 'Invalid email format' },
          { status: 400 }
        );
      }

      if (error.message.includes('Supabase')) {
        return NextResponse.json(
          {
            error: 'Database error',
            message: 'Failed to process request. Please check Supabase configuration.',
          },
          { status: 503 }
        );
      }
    }

    // Generic server error
    return NextResponse.json(
      {
        error: 'Internal server error',
        message: error instanceof Error ? error.message : 'Unknown error',
      },
      { status: 500 }
    );
  }
}

// Reject non-POST requests
export async function GET() {
  return NextResponse.json(
    { error: 'Method not allowed' },
    { status: 405, headers: { Allow: 'POST' } }
  );
}

export async function PUT() {
  return NextResponse.json(
    { error: 'Method not allowed' },
    { status: 405, headers: { Allow: 'POST' } }
  );
}

export async function DELETE() {
  return NextResponse.json(
    { error: 'Method not allowed' },
    { status: 405, headers: { Allow: 'POST' } }
  );
}
