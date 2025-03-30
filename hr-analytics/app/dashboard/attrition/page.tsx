import type { Metadata } from "next"
import { AttritionOverview } from "@/components/attrition/attrition-overview"
import { AttritionByDepartment } from "@/components/attrition/attrition-by-department"
import { AttritionPrediction } from "@/components/attrition/attrition-prediction"
import { AttritionFilters } from "@/components/attrition/attrition-filters"
import { AttritionReasons } from "@/components/attrition/attrition-reasons"

export const metadata: Metadata = {
  title: "Attrition Prediction | HR Analytics Platform",
  description: "Analyze and predict employee attrition",
}

export default function AttritionPage() {
  return (
    <div className="flex flex-col gap-4">
      <div className="flex flex-col gap-2">
        <h1 className="text-2xl font-bold tracking-tight">Attrition Prediction</h1>
        <p className="text-muted-foreground">Analyze historical attrition data and predict future trends.</p>
      </div>

      <AttritionFilters />

      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
        <AttritionOverview />
      </div>

      <div className="grid gap-4 md:grid-cols-2">
        <AttritionByDepartment />
        <AttritionReasons />
      </div>

      <div className="grid gap-4">
        <AttritionPrediction />
      </div>
    </div>
  )
}

