/**
 * Company enrichment data (mocked for alpha)
 * In production, this would call an enrichment API like Clearbit or ZoomInfo
 */

interface CompanyData {
  company_name: string;
  industry: string;
  company_size: string;
}

// Hardcoded lookup table for alpha version
const companyDatabase: Record<string, CompanyData> = {
  'google.com': {
    company_name: 'Google',
    industry: 'Technology',
    company_size: 'Enterprise',
  },
  'microsoft.com': {
    company_name: 'Microsoft',
    industry: 'Technology',
    company_size: 'Enterprise',
  },
  'amazon.com': {
    company_name: 'Amazon',
    industry: 'E-commerce',
    company_size: 'Enterprise',
  },
  'apple.com': {
    company_name: 'Apple',
    industry: 'Technology',
    company_size: 'Enterprise',
  },
  'salesforce.com': {
    company_name: 'Salesforce',
    industry: 'Software',
    company_size: 'Enterprise',
  },
  'example.com': {
    company_name: 'Example Corp',
    industry: 'General',
    company_size: 'Mid-market',
  },
};

/**
 * Enrich company data from domain
 * @param domain - Company domain
 * @returns Company enrichment data
 */
export function enrichCompanyData(domain: string): CompanyData {
  const enriched = companyDatabase[domain.toLowerCase()];

  if (enriched) {
    return enriched;
  }

  // Default values for unknown domains
  return {
    company_name: 'Unknown',
    industry: 'General',
    company_size: 'Mid-market',
  };
}
