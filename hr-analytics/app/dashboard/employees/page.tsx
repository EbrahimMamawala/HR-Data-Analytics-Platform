import type { Metadata } from "next"
import { EmployeeDataTable } from "@/components/employees/employee-data-table"
import { EmployeeFilters } from "@/components/employees/employee-filters"

export const metadata: Metadata = {
  title: "Employee Data | HR Analytics Platform",
  description: "View and analyze employee data",
}

export default function EmployeesPage() {
  return (
    <div className="flex flex-col gap-4">
      <div className="flex flex-col gap-2">
        <h1 className="text-2xl font-bold tracking-tight">Employee Data</h1>
        <p className="text-muted-foreground">View and analyze employee data across departments and demographics.</p>
      </div>

      <EmployeeFilters />
      <EmployeeDataTable />
    </div>
  )
}

