import type { Metadata } from 'next';

export const metadata: Metadata = {
  title: 'LinkedIn Post-Click Personalization',
  description: 'Personalized landing page based on LinkedIn campaign parameters',
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
