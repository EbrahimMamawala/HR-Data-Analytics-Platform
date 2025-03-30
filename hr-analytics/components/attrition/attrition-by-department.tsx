"use client"

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Bar, BarChart, CartesianGrid, Legend, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts"
import { ChartContainer, ChartTooltipContent } from "@/components/ui/chart"

const data = [
  {
    department: "Engineering",
    voluntary: 12,
    involuntary: 5,
    rate: 4.2,
  },
  {
    department: "Marketing",
    voluntary: 8,
    involuntary: 2,
    rate: 5.0,
  },
  {
    department: "Finance",
    voluntary: 5,
    involuntary: 1,
    rate: 3.1,
  },
  {
    department: "HR",
    voluntary: 3,
    involuntary: 0,
    rate: 2.8,
  },
  {
    department: "Product",
    voluntary: 6,
    involuntary: 2,
    rate: 4.5,
  },
  {
    department: "Design",
    voluntary: 4,
    involuntary: 1,
    rate: 3.8,
  },
  {
    department: "Sales",
    voluntary: 10,
    involuntary: 3,
    rate: 6.2,
  },
]

export function AttritionByDepartment() {
  return (
    <Card className="col-span-1">
      <CardHeader>
        <CardTitle>Attrition by Department</CardTitle>
        <CardDescription>Voluntary and involuntary exits by department</CardDescription>
      </CardHeader>
      <CardContent>
        <ChartContainer
          config={{
            voluntary: {
              label: "Voluntary Exits",
              color: "hsl(var(--chart-1))",
            },
            involuntary: {
              label: "Involuntary Exits",
              color: "hsl(var(--chart-2))",
            },
            rate: {
              label: "Attrition Rate (%)",
              color: "hsl(var(--chart-3))",
            },
          }}
          className="h-[400px]"
        >
          <ResponsiveContainer width="100%" height="100%">
            <BarChart
              data={data}
              margin={{
                top: 20,
                right: 30,
                left: 20,
                bottom: 5,
              }}
            >
              <CartesianGrid strokeDasharray="3 3" className="stroke-muted" />
              <XAxis dataKey="department" className="text-sm text-muted-foreground" />
              <YAxis yAxisId="left" orientation="left" className="text-sm text-muted-foreground" />
              <YAxis yAxisId="right" orientation="right" className="text-sm text-muted-foreground" />
              <Tooltip content={<ChartTooltipContent />} />
              <Legend />
              <Bar yAxisId="left" dataKey="voluntary" fill="var(--color-voluntary)" />
              <Bar yAxisId="left" dataKey="involuntary" fill="var(--color-involuntary)" />
              <Bar yAxisId="right" dataKey="rate" fill="var(--color-rate)" />
            </BarChart>
          </ResponsiveContainer>
        </ChartContainer>
      </CardContent>
    </Card>
  )
}

