"use client"

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Cell, Legend, Pie, PieChart, ResponsiveContainer, Tooltip } from "recharts"

const data = [
  { name: "Better Opportunity", value: 35, color: "#3b82f6" },
  { name: "Work-Life Balance", value: 25, color: "#8b5cf6" },
  { name: "Compensation", value: 20, color: "#ec4899" },
  { name: "Relocation", value: 10, color: "#f97316" },
  { name: "Career Growth", value: 8, color: "#22c55e" },
  { name: "Other", value: 2, color: "#64748b" },
]

export function AttritionReasons() {
  return (
    <Card className="col-span-1">
      <CardHeader>
        <CardTitle>Exit Reasons</CardTitle>
        <CardDescription>Primary reasons for voluntary exits</CardDescription>
      </CardHeader>
      <CardContent>
        <div className="h-[400px]">
          <ResponsiveContainer width="100%" height="100%">
            <PieChart>
              <Pie
                data={data}
                cx="50%"
                cy="50%"
                innerRadius={70}
                outerRadius={120}
                paddingAngle={2}
                dataKey="value"
                label={({ name, percent }) => `${name}: ${(percent * 100).toFixed(0)}%`}
              >
                {data.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={entry.color} />
                ))}
              </Pie>
              <Tooltip
                formatter={(value) => [`${value} employees`, "Count"]}
                contentStyle={{ borderRadius: "8px", border: "1px solid #e2e8f0" }}
              />
              <Legend />
            </PieChart>
          </ResponsiveContainer>
        </div>
      </CardContent>
    </Card>
  )
}

