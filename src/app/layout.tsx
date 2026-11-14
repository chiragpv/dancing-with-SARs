import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "Dancing with the SARs | Earth Observation Console",
  description: "Explore SAR observations through an interactive geospatial workspace."
};

export default function RootLayout({ children }: Readonly<{ children: React.ReactNode }>) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}