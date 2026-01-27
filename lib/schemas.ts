import { z } from 'zod';

// Input validation schema
export const PersonalizeRequestSchema = z.object({
  email: z.string().email('Invalid email format'),
  cta: z.string().min(1, 'CTA is required'),
});

export type PersonalizeRequest = z.infer<typeof PersonalizeRequestSchema>;

// Claude output schema - must match the expected structure
export const ClaudeOutputSchema = z.object({
  headline: z.string(),
  subheadline: z.string(),
  value_propositions: z.array(z.object({
    title: z.string(),
    description: z.string(),
  })),
  cta_text: z.string(),
  personalization_rationale: z.string().optional(),
});

export type ClaudeOutput = z.infer<typeof ClaudeOutputSchema>;

// Job data schema
export const PersonalizationJobSchema = z.object({
  email: z.string(),
  domain: z.string(),
  cta: z.string(),
  persona: z.string(),
  buyer_stage: z.string(),
  company_name: z.string(),
  industry: z.string(),
  company_size: z.string(),
  status: z.enum(['pending', 'completed', 'failed']),
});

export type PersonalizationJob = z.infer<typeof PersonalizationJobSchema>;
