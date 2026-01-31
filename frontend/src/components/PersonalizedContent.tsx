'use client';

import { useState, useEffect } from 'react';

interface PersonalizationData {
  intro_hook: string;
  cta: string;
  first_name?: string;
  company?: string;
  title?: string;
  email?: string;
}

interface DeliveryStatus {
  email_sent: boolean;
  pdf_url?: string;
  error?: string;
}

interface PersonalizedContentProps {
  data: PersonalizationData | null;
  error?: string | null;
  onReset?: () => void;
}

export default function PersonalizedContent({ data, error, onReset }: PersonalizedContentProps) {
  const [deliveryStatus, setDeliveryStatus] = useState<DeliveryStatus | null>(null);
  const [isDelivering, setIsDelivering] = useState(false);
  const [isDownloading, setIsDownloading] = useState(false);

  // Automatically trigger email delivery when data is available
  useEffect(() => {
    if (data?.email && !deliveryStatus && !isDelivering) {
      deliverEbook();
    }
  }, [data?.email]);

  const deliverEbook = async () => {
    if (!data?.email) return;

    setIsDelivering(true);

    try {
      const response = await fetch(`/api/rad/deliver/${encodeURIComponent(data.email)}`, {
        method: 'POST',
      });

      if (!response.ok) {
        throw new Error('Failed to deliver ebook');
      }

      const result = await response.json();

      setDeliveryStatus({
        email_sent: result.email_sent,
        pdf_url: result.pdf_url,
        error: result.email_error,
      });
    } catch (err) {
      console.error('Delivery error:', err);
      setDeliveryStatus({
        email_sent: false,
        error: 'Failed to deliver your ebook. Please try downloading instead.',
      });
    } finally {
      setIsDelivering(false);
    }
  };

  const handleDownload = async () => {
    if (!data?.email) return;

    setIsDownloading(true);

    try {
      // Use direct download endpoint - returns actual PDF file
      const response = await fetch(`/api/rad/download/${encodeURIComponent(data.email)}`);

      if (!response.ok) {
        throw new Error('Failed to generate PDF');
      }

      // Get the PDF blob
      const blob = await response.blob();

      // Create download link
      const url = window.URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.download = `AMD-AI-Readiness-${data.first_name || 'Guide'}.pdf`;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      window.URL.revokeObjectURL(url);

    } catch (err) {
      console.error('Download error:', err);
    } finally {
      setIsDownloading(false);
    }
  };

  if (error) {
    return (
      <div className="amd-card p-8 border-red-500/30 bg-red-500/5">
        <div className="flex items-center gap-4 mb-4">
          <div className="w-12 h-12 rounded-full bg-red-500/15 flex items-center justify-center">
            <svg className="w-6 h-6 text-red-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
            </svg>
          </div>
          <p className="text-red-400 font-medium text-base">{error}</p>
        </div>
        {onReset && (
          <button onClick={onReset} className="text-sm font-semibold text-[#00c8aa] hover:underline">
            Try again
          </button>
        )}
      </div>
    );
  }

  if (!data) {
    return null;
  }

  const greeting = data.first_name
    ? `Hi ${data.first_name}!`
    : 'Welcome!';

  return (
    <div className="amd-card overflow-hidden amd-glow animate-fade-in-up">
      {/* Header with gradient */}
      <div className="relative px-8 py-12 overflow-hidden">
        {/* Background gradient */}
        <div className="absolute inset-0 bg-gradient-to-br from-[#00c8aa]/20 via-transparent to-[#00c8aa]/5" />
        <div className="absolute top-0 right-0 w-64 h-64 bg-[#00c8aa]/10 rounded-full blur-3xl -translate-y-1/2 translate-x-1/2" />

        {/* Content */}
        <div className="relative">
          <div className="inline-flex items-center gap-2.5 px-4 py-2 rounded-full border border-[#00c8aa]/40 bg-[#00c8aa]/15 mb-5">
            <span className="w-2 h-2 rounded-full bg-[#00c8aa] animate-pulse" />
            <span className="text-sm text-[#00c8aa] font-semibold uppercase tracking-wider">Your Personalized Ebook</span>
          </div>

          <h2 className="text-3xl font-bold text-white mb-3">{greeting}</h2>
          {data.company && (
            <p className="text-white/70 text-lg">
              Tailored insights for {data.title ? <span className="text-white/90 font-medium">{data.title}</span> : null}
              {data.title ? ' at ' : ''}
              <span className="text-[#00c8aa] font-medium">{data.company}</span>
            </p>
          )}
        </div>
      </div>

      {/* Content Section */}
      <div className="px-8 py-8 space-y-6">
        {/* Delivery Status Banners */}
        {isDelivering && (
          <div className="rounded-xl bg-[#00c8aa]/10 border border-[#00c8aa]/30 p-5 flex items-center gap-4">
            <div className="w-12 h-12 rounded-full bg-[#00c8aa]/15 flex items-center justify-center flex-shrink-0">
              <div className="w-5 h-5 border-2 border-[#00c8aa] border-t-transparent rounded-full animate-spin" />
            </div>
            <div>
              <p className="text-[#00c8aa] font-semibold">Sending your personalized ebook...</p>
              <p className="text-sm text-white/60 mt-1">This will just take a moment</p>
            </div>
          </div>
        )}

        {deliveryStatus?.email_sent && (
          <div className="rounded-xl bg-[#00c8aa]/10 border border-[#00c8aa]/40 p-5">
            <div className="flex items-center gap-4">
              <div className="w-12 h-12 rounded-full bg-[#00c8aa]/20 flex items-center justify-center flex-shrink-0">
                <svg className="w-6 h-6 text-[#00c8aa]" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                </svg>
              </div>
              <div>
                <p className="font-semibold text-white text-base">Check your inbox!</p>
                <p className="text-sm text-white/70 mt-1">We&apos;ve sent your personalized ebook to <span className="text-[#00c8aa] font-medium">{data.email}</span></p>
              </div>
            </div>
          </div>
        )}

        {deliveryStatus && !deliveryStatus.email_sent && (
          <div className="rounded-xl bg-amber-500/10 border border-amber-500/30 p-5">
            <div className="flex items-center gap-4">
              <div className="w-12 h-12 rounded-full bg-amber-500/15 flex items-center justify-center flex-shrink-0">
                <svg className="w-6 h-6 text-amber-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
                </svg>
              </div>
              <div>
                <p className="font-semibold text-white text-base">Email delivery unavailable</p>
                <p className="text-sm text-white/70 mt-1">No worries! Download your ebook directly below.</p>
              </div>
            </div>
          </div>
        )}

        {/* Intro Hook */}
        <div className="py-4">
          <p className="text-lg text-white/80 leading-relaxed">{data.intro_hook}</p>
        </div>

        {/* Divider */}
        <div className="flex items-center gap-4">
          <div className="h-px flex-1 bg-gradient-to-r from-transparent via-white/15 to-transparent" />
          <span className="text-sm font-semibold uppercase tracking-widest text-white/50">What&apos;s Inside</span>
          <div className="h-px flex-1 bg-gradient-to-r from-transparent via-white/15 to-transparent" />
        </div>

        {/* Feature List */}
        <ul className="space-y-4">
          <li className="flex items-start gap-4 group">
            <span className="flex-shrink-0 w-7 h-7 rounded-full bg-[#00c8aa]/15 flex items-center justify-center mt-0.5 group-hover:bg-[#00c8aa]/25 transition-colors">
              <svg className="w-4 h-4 text-[#00c8aa]" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2.5} d="M5 13l4 4L19 7" />
              </svg>
            </span>
            <span className="text-white/80 group-hover:text-white transition-colors">Industry-specific strategies and best practices</span>
          </li>
          <li className="flex items-start gap-4 group">
            <span className="flex-shrink-0 w-7 h-7 rounded-full bg-[#00c8aa]/15 flex items-center justify-center mt-0.5 group-hover:bg-[#00c8aa]/25 transition-colors">
              <svg className="w-4 h-4 text-[#00c8aa]" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2.5} d="M5 13l4 4L19 7" />
              </svg>
            </span>
            <span className="text-white/80 group-hover:text-white transition-colors">Real-world case studies from leading companies</span>
          </li>
          <li className="flex items-start gap-4 group">
            <span className="flex-shrink-0 w-7 h-7 rounded-full bg-[#00c8aa]/15 flex items-center justify-center mt-0.5 group-hover:bg-[#00c8aa]/25 transition-colors">
              <svg className="w-4 h-4 text-[#00c8aa]" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2.5} d="M5 13l4 4L19 7" />
              </svg>
            </span>
            <span className="text-white/80 group-hover:text-white transition-colors">Actionable frameworks you can implement today</span>
          </li>
        </ul>

        {/* CTA Box */}
        <div className="rounded-xl bg-gradient-to-r from-[#00c8aa]/15 via-[#00c8aa]/10 to-transparent p-6 border border-[#00c8aa]/25">
          <p className="font-medium text-white text-base">{data.cta}</p>
        </div>

        {/* Download Button */}
        {!isDelivering && (
          <button
            className="amd-button-primary flex items-center justify-center gap-3"
            onClick={handleDownload}
            disabled={isDownloading || !data.email}
          >
            {isDownloading ? (
              <>
                <div className="w-5 h-5 border-2 border-current border-t-transparent rounded-full animate-spin" />
                Generating Your Ebook...
              </>
            ) : (
              <>
                <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4" />
                </svg>
                {deliveryStatus?.email_sent ? 'Download a Copy Now' : 'Download Your Free Ebook'}
              </>
            )}
          </button>
        )}

        <p className="text-center text-sm text-white/50">
          {deliveryStatus?.email_sent
            ? "We've also emailed you a copy. Didn't get it? Check your spam folder."
            : 'Your personalized PDF will download instantly'}
        </p>

        {/* Reset Link */}
        {onReset && (
          <div className="pt-6 border-t border-white/10 text-center">
            <button
              onClick={onReset}
              className="text-sm text-white/50 hover:text-[#00c8aa] transition-colors font-medium"
            >
              Start over with different information
            </button>
          </div>
        )}
      </div>
    </div>
  );
}
