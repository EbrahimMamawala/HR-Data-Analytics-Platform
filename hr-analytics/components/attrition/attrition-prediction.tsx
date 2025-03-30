"use client"

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Area, AreaChart, CartesianGrid, Legend, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts"
import { ChartContainer, ChartTooltipContent } from "@/components/ui/chart"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table"

const historicalData = [
  {
    month: "Jan",
    actual: 3.2,
  },
  {
    month: "Feb",
    actual: 3.5,
  },
  {
    month: "Mar",
    actual: 3.8,
  },
  {
    month: "Apr",
    actual: 4.0,
  },
  {
    month: "May",
    actual: 3.7,
  },
  {
    month: "Jun",
    actual: 3.5,
  },
  {
    month: "Jul",
    actual: 3.4,
  },
]

const forecastData = [
  {
    month: "Jul",
    actual: 3.4,
    forecast: 3.4,
  },
  {
    month: "Aug",
    forecast: 3.3,
    lowerBound: 2.9,
    upperBound: 3.7,
  },
  {
    month: "Sep",
    forecast: 3.2,
    lowerBound: 2.7,
    upperBound: 3.7,
  },
  {
    month: "Oct",
    forecast: 3.4,
    lowerBound: 2.8,
    upperBound: 4.0,
  },
  {
    month: "Nov",
    forecast: 3.6,
    lowerBound: 2.9,
    upperBound: 4.3,
  },
  {
    month: "Dec",
    forecast: 3.8,
    lowerBound: 3.0,
    upperBound: 4.6,
  },
]

const tableData = [
  {
    month: "August 2023",
    employees: 1255,
    forecast: 3.3,
    exits: 41,
    voluntary: 32,
    involuntary: 9,
  },
  {
    month: "September 2023",
    employees: 1262,
    forecast: 3.2,
    exits: 40,
    voluntary: 30,
    involuntary: 10,
  },
  {
    month: "October 2023",
    employees: 1270,
    forecast: 3.4,
    exits: 43,
    voluntary: 33,
    involuntary: 10,
  },
  {
    month: "November 2023",
    employees: 1278,
    forecast: 3.6,
    exits: 46,
    voluntary: 35,
    involuntary: 11,
  },
  {
    month: "December 2023",
    employees: 1285,
    forecast: 3.8,
    exits: 49,
    voluntary: 37,
    involuntary: 12,
  },
]

export function AttritionPrediction() {
  return (
    <Card>
      <CardHeader>
        <CardTitle>Attrition Forecast</CardTitle>
        <CardDescription>Historical attrition data and future predictions</CardDescription>
      </CardHeader>
      <CardContent>
        <Tabs defaultValue="chart">
          <TabsList className="mb-4">
            <TabsTrigger value="chart">Chart View</TabsTrigger>
            <TabsTrigger value="table">Table View</TabsTrigger>
          </TabsList>
          <TabsContent value="chart">
            <ChartContainer
              config={{
                actual: {
                  label: "Actual Attrition Rate (%)",
                  color: "hsl(var(--chart-1))",
                },
                forecast: {
                  label: "Forecasted Attrition Rate (%)",
                  color: "hsl(var(--chart-2))",
                },
                lowerBound: {
                  label: "Lower Bound",
                  color: "hsl(var(--chart-3))",
                },
                upperBound: {
                  label: "Upper Bound",
                  color: "hsl(var(--chart-3))",
                },
              }}
              className="h-[400px]"
            >
              <ResponsiveContainer width="100%" height="100%">
                <AreaChart
                  data={[...historicalData, ...forecastData]}
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
                    dataKey="actual"
                    stroke="var(--color-actual)"
                    fill="var(--color-actual)"
                    fillOpacity={0.6}
                    strokeWidth={2}
                  />
                  <Area
                    type="monotone"
                    dataKey="forecast"
                    stroke="var(--color-forecast)"
                    fill="var(--color-forecast)"
                    fillOpacity={0.6}
                    strokeWidth={2}
                    strokeDasharray="5 5"
                  />
                  <Area
                    type="monotone"
                    dataKey="upperBound"
                    stroke="var(--color-upperBound)"
                    fill="var(--color-upperBound)"
                    fillOpacity={0.1}
                    strokeWidth={1}
                    strokeDasharray="3 3"
                  />
                  <Area
                    type="monotone"
                    dataKey="lowerBound"
                    stroke="var(--color-lowerBound)"
                    fill="var(--color-lowerBound)"
                    fillOpacity={0.1}
                    strokeWidth={1}
                    strokeDasharray="3 3"
                  />
                </AreaChart>
              </ResponsiveContainer>
            </ChartContainer>
          </TabsContent>
          <TabsContent value="table">
            <div className="rounded-md border">
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>Month</TableHead>
                    <TableHead className="text-right">Total Employees</TableHead>
                    <TableHead className="text-right">Forecasted Rate (%)</TableHead>
                    <TableHead className="text-right">Total Exits</TableHead>
                    <TableHead className="text-right">Voluntary</TableHead>
                    <TableHead className="text-right">Involuntary</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {tableData.map((row) => (
                    <TableRow key={row.month}>
                      <TableCell className="font-medium">{row.month}</TableCell>
                      <TableCell className="text-right">{row.employees}</TableCell>
                      <TableCell className="text-right">{row.forecast}%</TableCell>
                      <TableCell className="text-right">{row.exits}</TableCell>
                      <TableCell className="text-right">{row.voluntary}</TableCell>
                      <TableCell className="text-right">{row.involuntary}</TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </div>
          </TabsContent>
        </Tabs>
      </CardContent>
    </Card>
  )
}

