import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "Market Brief | Stock news, distilled",
  description:
    "Get a concise stock news summary for the companies on your watchlist.",
};

export default function RootLayout({ children }: LayoutProps<"/">) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
