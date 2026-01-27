import { getSupabaseServerClient } from './client';
import type { PersonalizationJob, ClaudeOutput } from '../schemas';

/**
 * Insert a new personalization job into the database
 */
export async function createPersonalizationJob(
  jobData: Omit<PersonalizationJob, 'status'>
): Promise<number> {
  const supabase = getSupabaseServerClient();

  const { data, error } = await supabase
    .from('personalization_jobs')
    .insert({
      ...jobData,
      status: 'pending',
    })
    .select('id')
    .single();

  if (error) {
    console.error('Supabase insert error:', error);
    throw new Error(`Failed to create personalization job: ${error.message}`);
  }

  return data.id;
}

/**
 * Store the Claude API output for a job
 */
export async function storePersonalizationOutput(
  jobId: number,
  output: ClaudeOutput
): Promise<void> {
  const supabase = getSupabaseServerClient();

  const { error } = await supabase
    .from('personalization_outputs')
    .insert({
      job_id: jobId,
      output_json: output,
    });

  if (error) {
    console.error('Supabase insert error:', error);
    throw new Error(`Failed to store personalization output: ${error.message}`);
  }
}

/**
 * Update job status
 */
export async function updateJobStatus(
  jobId: number,
  status: 'completed' | 'failed'
): Promise<void> {
  const supabase = getSupabaseServerClient();

  const { error } = await supabase
    .from('personalization_jobs')
    .update({ status })
    .eq('id', jobId);

  if (error) {
    console.error('Supabase update error:', error);
    throw new Error(`Failed to update job status: ${error.message}`);
  }
}
