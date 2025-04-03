"use client"

import { useEffect, useState } from "react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Bar, BarChart, CartesianGrid, Legend, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts"
import { ChartContainer, ChartTooltipContent } from "@/components/ui/chart"

interface DiversityData {
  _id: string;
  diversity_by_department: { 
    [department: string]: {
      Male: number;
      Female: number;
      Other: number;
    }
  };
}

interface DiversityByDepartmentProps {
  period: string;
  date: string;
}

export function DiversityByDepartment({ period, date }: DiversityByDepartmentProps) {
  const [data, setData] = useState<DiversityData | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const queryParams = new URLSearchParams();
    queryParams.append("period", period);
    if (date) queryParams.append("date", date);

    fetch(`/api/diversity?${queryParams.toString()}`)
      .then((res) => res.json())
      .then((data: DiversityData) => {
        setData(data);
        setLoading(false);
      })
      .catch(() => setLoading(false));
  }, [period, date]);

  if (loading) return <div>Loading...</div>;
  if (!data) return <div>No data available</div>;

  // Transform MongoDB data to chart format
  const chartData = Object.entries(data.diversity_by_department).map(([department, stats]) => ({
    department,
    male: stats.Male || 0,
    female: stats.Female || 0,
    other: stats.Other || 0
  }));

  return (
    <Card className="col-span-1 lg:col-span-2">
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
          className="h-[500px] sm:h-[600px]"
        >
          <ResponsiveContainer width="100%" height="100%">
            <BarChart
              data={chartData}
              margin={{
                top: 20,
                right: 30,
                left: 20,
                bottom: 70,
              }}
            >
              <CartesianGrid strokeDasharray="3 3" className="stroke-muted" />
              <XAxis 
                dataKey="department" 
                className="text-sm text-muted-foreground"
              />
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
  );
}