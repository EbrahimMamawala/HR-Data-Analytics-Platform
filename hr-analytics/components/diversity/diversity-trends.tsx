"use client"

import { useEffect, useState } from "react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Area, AreaChart, CartesianGrid, Legend, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts"
import { ChartContainer, ChartTooltipContent } from "@/components/ui/chart"

interface TrendData {
  period: string;
  male: number;
  female: number;
  other: number;
}

const monthNames = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", 
  "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"];

export function DiversityTrends() {
  const [data, setData] = useState<TrendData[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetch('/api/diversity/trends')
      .then(res => res.json())
      .then((dbData: TrendData[]) => {
        const transformed = dbData.map(item => {
          const [year, month] = item.period.split('-');
          return {
            ...item,
            month: monthNames[parseInt(month) - 1]
          };
        });
        setData(transformed);
        setLoading(false);
      })
      .catch(() => setLoading(false));
  }, []);

  if (loading) return <div>Loading...</div>;

  return (
    <Card className="col-span-1">
      <CardHeader>
        <CardTitle>Diversity Trends</CardTitle>
        <CardDescription>Gender distribution over time</CardDescription>
      </CardHeader>
      <CardContent>
        <ChartContainer
          config={{
            male: { label: "Male", color: "hsl(var(--chart-1))" },
            female: { label: "Female", color: "hsl(var(--chart-2))" },
            other: { label: "Non-Binary", color: "hsl(var(--chart-3))" },
          }}
          className="h-[400px]"
        >
          <ResponsiveContainer width="100%" height="100%">
            <AreaChart
              data={data}
              margin={{ top: 20, right: 30, left: 20, bottom: 5 }}
            >
              <CartesianGrid strokeDasharray="3 3" className="stroke-muted" />
              <XAxis 
                dataKey="month" 
                className="text-sm text-muted-foreground"
              />
              <YAxis className="text-sm text-muted-foreground" />
              <Tooltip 
                content={<ChartTooltipContent />}
                formatter={(value) => [value, "Employees"]}
              />
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
  );
}