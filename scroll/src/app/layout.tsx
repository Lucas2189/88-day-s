import type { Metadata, Viewport } from "next";
import { Inter, Sora } from "next/font/google";
import "./globals.css";
import { AppProviders } from "@/components/providers/AppProviders";
import { TabBar } from "@/components/nav/TabBar";
import { ServiceWorkerRegistrar } from "@/components/providers/ServiceWorkerRegistrar";

const inter = Inter({ variable: "--font-inter", subsets: ["latin"], display: "swap" });
const sora = Sora({ variable: "--font-display", subsets: ["latin"], weight: ["600", "700"], display: "swap" });

export const metadata: Metadata = {
  title: { default: "SCROLL", template: "%s · SCROLL" },
  description: "One app. One feed. Every social network. Discover supported content from YouTube, TikTok, Instagram, X and Reddit in one vertical feed.",
  applicationName: "SCROLL",
  manifest: "/manifest.webmanifest",
  appleWebApp: { capable: true, statusBarStyle: "black-translucent", title: "SCROLL" },
  icons: { icon: "/icons/icon.svg", apple: "/icons/apple-touch-icon.png" },
  formatDetection: { telephone: false },
};

export const viewport: Viewport = {
  themeColor: "#000000",
  width: "device-width",
  initialScale: 1,
  maximumScale: 1,
  viewportFit: "cover",
  colorScheme: "dark",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en" className={`${inter.variable} ${sora.variable} h-full`}>
      <body className="min-h-full bg-bg text-fg">
        <AppProviders>
          <div className="mx-auto min-h-dvh w-full max-w-[560px] md:border-x md:border-line">{children}</div>
          <TabBar />
          <ServiceWorkerRegistrar />
        </AppProviders>
      </body>
    </html>
  );
}
