"use client";
import React, { useState } from "react";
import { DiversityOverview } from "@/components/diversity/diversity-overview";
import { DiversityByDepartment } from "@/components/diversity/diversity-by-department";
import { DiversityTrends } from "@/components/diversity/diversity-trends";
import { DiversityFilters } from "@/components/diversity/diversity-filters";

export default function ClientDiversityPage() {
  const [filters, setFilters] = useState<{ date: string; period: string }>({
    date: "2014-Q4", // Default value if needed
    period: "quarterly", // Default value if needed
  });

  return (
    <div className="flex flex-col gap-4">
      <div className="flex flex-col gap-2">
        <h1 className="text-2xl font-bold tracking-tight">Diversity Analysis</h1>
        <p className="text-muted-foreground">
          Analyze organizational diversity metrics across departments and time periods.
        </p>
      </div>

      <DiversityFilters onFiltersChange={setFilters} />

      <div className="grid gap-4 md:grid-cols-3">
        <DiversityOverview period={filters.period} date={filters.date} />
      </div>

      <div className="grid gap-4 md:grid-cols-1 lg:grid-cols-2">
        <DiversityByDepartment period={filters.period} date={filters.date}/>
        {/* <DiversityTrends /> */}
      </div>
    </div>
  );
}
