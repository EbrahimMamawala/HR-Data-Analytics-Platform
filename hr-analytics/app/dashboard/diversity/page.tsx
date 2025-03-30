import type { Metadata } from "next"
import { DiversityOverview } from "@/components/diversity/diversity-overview"
import { DiversityByDepartment } from "@/components/diversity/diversity-by-department"
import { DiversityTrends } from "@/components/diversity/diversity-trends"
import { DiversityFilters } from "@/components/diversity/diversity-filters"

export const metadata: Metadata = {
  title: "Diversity Analysis | HR Analytics Platform",
  description: "Analyze organizational diversity metrics",
}

export default function DiversityPage() {
  return (
    <div className="flex flex-col gap-4">
      <div className="flex flex-col gap-2">
        <h1 className="text-2xl font-bold tracking-tight">Diversity Analysis</h1>
        <p className="text-muted-foreground">
          Analyze organizational diversity metrics across departments and time periods.
        </p>
      </div>

      <DiversityFilters />

      <div className="grid gap-4 md:grid-cols-3">
        <DiversityOverview />
      </div>

      <div className="grid gap-4 md:grid-cols-2">
        <DiversityByDepartment />
        <DiversityTrends />
      </div>
    </div>
  )
}

