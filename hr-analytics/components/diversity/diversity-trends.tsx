"use client"

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Area, AreaChart, CartesianGrid, Legend, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts"
import { ChartContainer, ChartTooltipContent } from "@/components/ui/chart"

const data = [
  {
    month: "Jan",
    male: 600,
    female: 550,
    other: 40,
  },
  {
    month: "Feb",
    male: 605,
    female: 555,
    other: 42,
  },
  {
    month: "Mar",
    male: 610,
    female: 560,
    other: 43,
  },
  {
    month: "Apr",
    male: 615,
    female: 565,
    other: 45,
  },
  {
    month: "May",
    male: 615,
    female: 570,
    other: 46,
  },
  {
    month: "Jun",
    male: 620,
    female: 575,
    other: 47,
  },
  {
    month: "Jul",
    male: 620,
    female: 580,
    other: 48,
  },
]

export function DiversityTrends() {
  return (
    <Card className="col-span-1">
      <CardHeader>
        <CardTitle>Diversity Trends</CardTitle>
        <CardDescription>Gender distribution over time</CardDescription>
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
            <AreaChart
              data={data}
              margin={{
                top: 20,
                right: 30,
                left: 20,
                bottom: 5,
              }}
            >
              <CartesianGrid strokeDasharray="3 3" className="stroke-muted" />
              <XAxis dataKey="month" className="text-sm text-muted-foreground" />
              <YAxis className="text-sm text-muted-foreground" />
              <Tooltip content={<ChartTooltipContent />} />
              <Legend />
              <Area
                type="monotone"
                dataKey="male"
                stackId="1"
                stroke="var(--color-male)"
                fill="var(--color-male)"
                fillOpacity={0.6}
              />
              <Area
                type="monotone"
                dataKey="female"
                stackId="1"
                stroke="var(--color-female)"
                fill="var(--color-female)"
                fillOpacity={0.6}
              />
              <Area
                type="monotone"
                dataKey="other"
                stackId="1"
                stroke="var(--color-other)"
                fill="var(--color-other)"
                fillOpacity={0.6}
              />
            </AreaChart>
          </ResponsiveContainer>
        </ChartContainer>
      </CardContent>
    </Card>
  )
}

