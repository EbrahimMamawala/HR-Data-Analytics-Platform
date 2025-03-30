"use client"

import { CartesianGrid, Line, LineChart, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts"
import { ChartContainer, ChartTooltipContent } from "@/components/ui/chart"

const data = [
  {
    name: "Jan",
    total: 1200,
    hired: 45,
    departed: 32,
  },
  {
    name: "Feb",
    total: 1213,
    hired: 35,
    departed: 22,
  },
  {
    name: "Mar",
    total: 1226,
    hired: 25,
    departed: 12,
  },
  {
    name: "Apr",
    total: 1239,
    hired: 30,
    departed: 17,
  },
  {
    name: "May",
    total: 1252,
    hired: 28,
    departed: 15,
  },
  {
    name: "Jun",
    total: 1265,
    hired: 32,
    departed: 19,
  },
  {
    name: "Jul",
    total: 1278,
    hired: 40,
    departed: 27,
  },
  {
    name: "Aug",
    total: 1291,
    hired: 35,
    departed: 22,
  },
  {
    name: "Sep",
    total: 1304,
    hired: 30,
    departed: 17,
  },
  {
    name: "Oct",
    total: 1317,
    hired: 25,
    departed: 12,
  },
  {
    name: "Nov",
    total: 1330,
    hired: 20,
    departed: 7,
  },
  {
    name: "Dec",
    total: 1248,
    hired: 15,
    departed: 97,
  },
]

export function Overview() {
  return (
    <ChartContainer
      config={{
        total: {
          label: "Total Employees",
          color: "hsl(var(--chart-1))",
        },
        hired: {
          label: "New Hires",
          color: "hsl(var(--chart-2))",
        },
        departed: {
          label: "Departures",
          color: "hsl(var(--chart-3))",
        },
      }}
      className="h-[300px]"
    >
      <ResponsiveContainer width="100%" height="100%">
        <LineChart
          data={data}
          margin={{
            top: 5,
            right: 10,
            left: 10,
            bottom: 0,
          }}
        >
          <CartesianGrid strokeDasharray="3 3" className="stroke-muted" />
          <XAxis dataKey="name" className="text-sm text-muted-foreground" tickLine={false} axisLine={false} />
          <YAxis className="text-sm text-muted-foreground" tickLine={false} axisLine={false} />
          <Tooltip content={<ChartTooltipContent />} />
          <Line type="monotone" dataKey="total" strokeWidth={2} activeDot={{ r: 6 }} className="stroke-primary" />
          <Line type="monotone" dataKey="hired" strokeWidth={2} className="stroke-emerald-500" strokeDasharray="5 5" />
          <Line
            type="monotone"
            dataKey="departed"
            strokeWidth={2}
            className="stroke-destructive"
            strokeDasharray="5 5"
          />
        </LineChart>
      </ResponsiveContainer>
    </ChartContainer>
  )
}

