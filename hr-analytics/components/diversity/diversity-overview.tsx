"use client"

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Pie, PieChart, ResponsiveContainer, Cell, Legend, Tooltip } from "recharts"

const data = [
  { name: "Male", value: 620, color: "#3b82f6" },
  { name: "Female", value: 580, color: "#ec4899" },
  { name: "Non-Binary", value: 48, color: "#8b5cf6" },
]

export function DiversityOverview() {
  return (
    <>
      <Card>
        <CardHeader>
          <CardTitle>Gender Distribution</CardTitle>
          <CardDescription>Overall gender distribution across the organization</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="h-[300px]">
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Pie
                  data={data}
                  cx="50%"
                  cy="50%"
                  innerRadius={60}
                  outerRadius={90}
                  paddingAngle={2}
                  dataKey="value"
                  label={({ name, percent }) => `${name}: ${(percent * 100).toFixed(0)}%`}
                  labelLine={false}
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

      <Card>
        <CardHeader>
          <CardTitle>Age Distribution</CardTitle>
          <CardDescription>Employee age groups across the organization</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="h-[300px]">
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Pie
                  data={[
                    { name: "18-25", value: 180, color: "#22c55e" },
                    { name: "26-35", value: 450, color: "#3b82f6" },
                    { name: "36-45", value: 380, color: "#8b5cf6" },
                    { name: "46-55", value: 180, color: "#f97316" },
                    { name: "56+", value: 58, color: "#ef4444" },
                  ]}
                  cx="50%"
                  cy="50%"
                  innerRadius={60}
                  outerRadius={90}
                  paddingAngle={2}
                  dataKey="value"
                  label={({ name, percent }) => `${name}: ${(percent * 100).toFixed(0)}%`}
                  labelLine={false}
                >
                  {[
                    { name: "18-25", value: 180, color: "#22c55e" },
                    { name: "26-35", value: 450, color: "#3b82f6" },
                    { name: "36-45", value: 380, color: "#8b5cf6" },
                    { name: "46-55", value: 180, color: "#f97316" },
                    { name: "56+", value: 58, color: "#ef4444" },
                  ].map((entry, index) => (
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

      <Card>
        <CardHeader>
          <CardTitle>Tenure Distribution</CardTitle>
          <CardDescription>Employee tenure across the organization</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="h-[300px]">
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Pie
                  data={[
                    { name: "<1 year", value: 210, color: "#22c55e" },
                    { name: "1-3 years", value: 380, color: "#3b82f6" },
                    { name: "3-5 years", value: 320, color: "#8b5cf6" },
                    { name: "5-10 years", value: 240, color: "#f97316" },
                    { name: "10+ years", value: 98, color: "#ef4444" },
                  ]}
                  cx="50%"
                  cy="50%"
                  innerRadius={60}
                  outerRadius={90}
                  paddingAngle={2}
                  dataKey="value"
                  label={({ name, percent }) => `${name}: ${(percent * 100).toFixed(0)}%`}
                  labelLine={false}
                >
                  {[
                    { name: "<1 year", value: 210, color: "#22c55e" },
                    { name: "1-3 years", value: 380, color: "#3b82f6" },
                    { name: "3-5 years", value: 320, color: "#8b5cf6" },
                    { name: "5-10 years", value: 240, color: "#f97316" },
                    { name: "10+ years", value: 98, color: "#ef4444" },
                  ].map((entry, index) => (
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
    </>
  )
}

