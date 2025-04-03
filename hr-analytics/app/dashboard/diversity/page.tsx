// This file is a server component
import React from "react";
import type { Metadata } from "next";
import ClientDiversityPage from "@/components/diversity/client-diversity-page";

export const metadata: Metadata = {
  title: "Diversity Analysis | HR Analytics Platform",
  description: "Analyze organizational diversity metrics",
};

export default function DiversityPage() {
  return <ClientDiversityPage />;
}
