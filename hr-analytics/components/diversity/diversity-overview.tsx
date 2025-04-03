"use client";

import React, { useEffect, useState } from "react";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Pie, PieChart, ResponsiveContainer, Cell, Legend, Tooltip } from "recharts";

interface DiversityData {
  _id: string;
  frequency: string;
  period: string;
  gender_distribution: { [key: string]: number };
  age_distribution: { [key: string]: number };
  tenure_distribution: { [key: string]: number };
  diversity_by_department: any;
}

interface DiversityOverviewProps {
  period: string;
  date: string; // Updated type from Date | null to string
}

export function DiversityOverview({ period, date }: DiversityOverviewProps) {
  const [data, setData] = useState<DiversityData | null>(null);

  useEffect(() => {
    // Build query parameters based on the selected filters.
    const queryParams = new URLSearchParams();
    queryParams.append("period", period);
    if (date) {
      queryParams.append("date", date); // Directly append the string
    }

    fetch(`/api/diversity?${queryParams.toString()}`)
      .then((res) => res.json())
      .then((data) => setData(data));
  }, [period, date]);

  if (!data) {
    return <div>Loading...</div>;
  }
  
  console.log(data);
  
  // Map the MongoDB document into chart data.
  const genderData = [
    { name: "Male", value: data.gender_distribution.Male, color: "#3b82f6" },
    { name: "Female", value: data.gender_distribution.Female, color: "#ec4899" },
    { name: "Other", value: data.gender_distribution.Other, color: "#8b5cf6" },
  ];

  const ageData = [
    { name: "18-25", value: data.age_distribution["18-25"], color: "#22c55e" },
    { name: "26-35", value: data.age_distribution["26-35"], color: "#3b82f6" },
    { name: "36-45", value: data.age_distribution["36-45"], color: "#8b5cf6" },
    { name: "46-55", value: data.age_distribution["46-55"], color: "#f97316" },
    { name: "56+", value: data.age_distribution["56+"], color: "#ef4444" },
  ];

  const tenureData = [
    { name: "<1 year", value: data.tenure_distribution["<1"], color: "#22c55e" },
    { name: "1-3 years", value: data.tenure_distribution["1-3"], color: "#3b82f6" },
    { name: "3-5 years", value: data.tenure_distribution["3-5"], color: "#8b5cf6" },
    { name: "5-10 years", value: data.tenure_distribution["5-10"], color: "#f97316" },
    { name: "10+ years", value: 0, color: "#ef4444" },
  ];

  return (
    <>
      <Card>
        <CardHeader>
          <CardTitle>Gender Distribution</CardTitle>
          <CardDescription>
            Overall gender distribution across the organization
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="h-[300px]">
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Pie
                  data={genderData}
                  cx="50%"
                  cy="50%"
                  innerRadius={60}
                  outerRadius={90}
                  paddingAngle={2}
                  dataKey="value"
                  label={({ name, percent }) =>
                    `${name}: ${(percent * 100).toFixed(0)}%`
                  }
                  labelLine={false}
                >
                  {genderData.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={entry.color} />
                  ))}
                </Pie>
                <Tooltip
                  formatter={(value) => [`${value} employees`, "Count"]}
                  contentStyle={{
                    borderRadius: "8px",
                    border: "1px solid #e2e8f0",
                  }}
                />
                <Legend />
              </PieChart>
            </ResponsiveContainer>
          </div>
        </CardContent>
      </Card>

      <Card className="mt-4">
        <CardHeader>
          <CardTitle>Age Distribution</CardTitle>
          <CardDescription>
            Employee age groups across the organization
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="h-[300px]">
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Pie
                  data={ageData}
                  cx="50%"
                  cy="50%"
                  innerRadius={60}
                  outerRadius={90}
                  paddingAngle={2}
                  dataKey="value"
                  label={({ name, percent }) =>
                    `${name}: ${(percent * 100).toFixed(0)}%`
                  }
                  labelLine={false}
                >
                  {ageData.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={entry.color} />
                  ))}
                </Pie>
                <Tooltip
                  formatter={(value) => [`${value} employees`, "Count"]}
                  contentStyle={{
                    borderRadius: "8px",
                    border: "1px solid #e2e8f0",
                  }}
                />
                <Legend />
              </PieChart>
            </ResponsiveContainer>
          </div>
        </CardContent>
      </Card>

      <Card className="mt-4">
        <CardHeader>
          <CardTitle>Tenure Distribution</CardTitle>
          <CardDescription>
            Employee tenure across the organization
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="h-[300px]">
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Pie
                  data={tenureData}
                  cx="50%"
                  cy="50%"
                  innerRadius={60}
                  outerRadius={90}
                  paddingAngle={2}
                  dataKey="value"
                  label={({ name, percent }) =>
                    `${name}: ${(percent * 100).toFixed(0)}%`
                  }
                  labelLine={false}
                >
                  {tenureData.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={entry.color} />
                  ))}
                </Pie>
                <Tooltip
                  formatter={(value) => [`${value} employees`, "Count"]}
                  contentStyle={{
                    borderRadius: "8px",
                    border: "1px solid #e2e8f0",
                  }}
                />
                <Legend />
              </PieChart>
            </ResponsiveContainer>
          </div>
        </CardContent>
      </Card>
    </>
  );
}
