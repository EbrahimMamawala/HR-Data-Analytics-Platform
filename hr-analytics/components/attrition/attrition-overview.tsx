"use client"

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { ArrowDown, ArrowUp, Users, UserMinus, UserPlus, Percent } from "lucide-react"

export function AttritionOverview() {
  return (
    <>
      <Card>
        <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
          <CardTitle className="text-sm font-medium">Total Employees</CardTitle>
          <Users className="h-4 w-4 text-muted-foreground" />
        </CardHeader>
        <CardContent>
          <div className="text-2xl font-bold">1,248</div>
          <p className="text-xs text-muted-foreground flex items-center gap-1 mt-1">
            <span className="text-emerald-500 flex items-center">
              <ArrowUp className="h-3 w-3" />
              2.5%
            </span>
            from last month
          </p>
        </CardContent>
      </Card>

      <Card>
        <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
          <CardTitle className="text-sm font-medium">Voluntary Exits</CardTitle>
          <UserMinus className="h-4 w-4 text-muted-foreground" />
        </CardHeader>
        <CardContent>
          <div className="text-2xl font-bold">42</div>
          <p className="text-xs text-muted-foreground flex items-center gap-1 mt-1">
            <span className="text-emerald-500 flex items-center">
              <ArrowDown className="h-3 w-3" />
              8.7%
            </span>
            from last month
          </p>
        </CardContent>
      </Card>

      <Card>
        <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
          <CardTitle className="text-sm font-medium">New Hires</CardTitle>
          <UserPlus className="h-4 w-4 text-muted-foreground" />
        </CardHeader>
        <CardContent>
          <div className="text-2xl font-bold">58</div>
          <p className="text-xs text-muted-foreground flex items-center gap-1 mt-1">
            <span className="text-emerald-500 flex items-center">
              <ArrowUp className="h-3 w-3" />
              12.3%
            </span>
            from last month
          </p>
        </CardContent>
      </Card>

      <Card>
        <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
          <CardTitle className="text-sm font-medium">Attrition Rate</CardTitle>
          <Percent className="h-4 w-4 text-muted-foreground" />
        </CardHeader>
        <CardContent>
          <div className="text-2xl font-bold">3.4%</div>
          <p className="text-xs text-muted-foreground flex items-center gap-1 mt-1">
            <span className="text-emerald-500 flex items-center">
              <ArrowDown className="h-3 w-3" />
              0.8%
            </span>
            from last month
          </p>
        </CardContent>
      </Card>
    </>
  )
}

