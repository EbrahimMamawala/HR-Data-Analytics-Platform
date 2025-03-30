"use client"

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Bar, BarChart, CartesianGrid, Legend, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts"
import { ChartContainer, ChartTooltipContent } from "@/components/ui/chart"

const data = [
  {
    department: "Engineering",
    male: 120,
    female: 80,
    other: 10,
  },
  {
    department: "Marketing",
    male: 40,
    female: 60,
    other: 5,
  },
  {
    department: "Finance",
    male: 50,
    female: 45,
    other: 3,
  },
  {
    department: "HR",
    male: 15,
    female: 35,
    other: 2,
  },
  {
    department: "Product",
    male: 35,
    female: 30,
    other: 5,
  },
  {
    department: "Design",
    male: 25,
    female: 35,
    other: 8,
  },
  {
    department: "Sales",
    male: 70,
    female: 50,
    other: 5,
  },
]

export function DiversityByDepartment() {
  return (
    <Card className="col-span-1">
      <CardHeader>
        <CardTitle>Diversity by Department</CardTitle>
        <CardDescription>Gender distribution across departments</CardDescription>
      </CardHeader>
      <CardContent>
        <ChartContainer
          config={{
            male: {
              label: "Male",
              color: "hsl(var(--chart-1))",
            },
            female: {
              label: "Female",
              color: "hsl(var(--chart-2))",
            },
            other: {
              label: "Non-Binary",
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
              <YAxis className="text-sm text-muted-foreground" />
              <Tooltip content={<ChartTooltipContent />} />
              <Legend />
              <Bar dataKey="male" stackId="a" fill="var(--color-male)" />
              <Bar dataKey="female" stackId="a" fill="var(--color-female)" />
              <Bar dataKey="other" stackId="a" fill="var(--color-other)" />
            </BarChart>
          </ResponsiveContainer>
        </ChartContainer>
      </CardContent>
    </Card>
  )
}

