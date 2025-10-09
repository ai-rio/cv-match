import './globals.css';

import type { Metadata } from 'next';

export const metadata: Metadata = {
  title: 'CV-Match - AI Resume Optimization',
  description: 'Increase your interview chances with perfectly optimized resumes powered by AI',
};

// This layout is only used for the root URL (/)
// The main layout is in app/[locale]/layout.tsx
export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html>
      <body>{children}</body>
    </html>
  );
}
