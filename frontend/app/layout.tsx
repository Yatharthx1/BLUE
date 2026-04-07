import type { Metadata } from 'next';
import { Bebas_Neue, Inter } from 'next/font/google';
import './globals.css';

const bebas = Bebas_Neue({ weight: '400', subsets: ['latin'], variable: '--font-bebas' });
const inter = Inter({ subsets: ['latin'], variable: '--font-inter' });

export const metadata: Metadata = {
  title: 'BLUE | Water Intelligence. Redefined.',
  description: 'Know what\'s in your water — before it\'s too late. BLUE is the AI-powered water quality intelligence platform.',
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" className={`${bebas.variable} ${inter.variable}`}>
      <body className="antialiased" style={{ margin: 0, padding: 0, background: '#020617' }}>
        {children}
      </body>
    </html>
  );
}
