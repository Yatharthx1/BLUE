import type { Metadata } from 'next';
import { Bebas_Neue, JetBrains_Mono, Space_Mono } from 'next/font/google';
import './globals.css';
import { PerformanceProvider } from '@/lib/performanceContext';

const bebas = Bebas_Neue({ weight: '400', subsets: ['latin'], variable: '--font-bebas' });
const jetbrains = JetBrains_Mono({ subsets: ['latin'], variable: '--font-jetbrains' });
const space = Space_Mono({ weight: ['400', '700'], subsets: ['latin'], variable: '--font-space' });

export const metadata: Metadata = {
  title: 'BLUE | Water Quality Intelligence',
  description: 'Water holds truth. We translate it.',
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" className={`${bebas.variable} ${jetbrains.variable} ${space.variable}`}>
      <body className={`font-jetbrains antialiased`}>
        <PerformanceProvider>
          {children}
        </PerformanceProvider>
      </body>
    </html>
  );
}
