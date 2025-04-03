"use client";

import * as React from "react";
import useSWR from "swr";
import {
  ColumnDef,
  flexRender,
  useReactTable,
  getCoreRowModel,
  getPaginationRowModel,
} from "@tanstack/react-table";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Label } from "@/components/ui/label";

const fetcher = (url: string) => fetch(url).then((res) => res.json());

// Helper functions to compute period strings
function getMonthKey(dateStr: string): string {
  const d = new Date(dateStr);
  return `${d.getFullYear()}-${(d.getMonth() + 1).toString().padStart(2, "0")}`;
}

function getQuarterKey(dateStr: string): string {
  const d = new Date(dateStr);
  const quarter = Math.floor(d.getMonth() / 3) + 1;
  return `${d.getFullYear()}-Q${quarter}`;
}

function getYearKey(dateStr: string): string {
  const d = new Date(dateStr);
  return `${d.getFullYear()}`;
}

type Employee = {
  _id: string;
  EmployeeID: number;
  Age: number;
  Department: string;
  Email: string;
  FirstName: string;
  LastName: string;
  Gender: string;
  JoinDate: string; // ISO date string (e.g. "2016-08-14")
  Position: string;
  Status: string;
};

export function EmployeeDataTableWithFilters() {
  const { data, error } = useSWR("/api/employees", fetcher);

  // Frequency filter state
  const [frequency, setFrequency] = React.useState<"month" | "quarter" | "year">("month");
  const [selectedPeriod, setSelectedPeriod] = React.useState<string>("all");

  // Additional filter states
  const [departmentFilter, setDepartmentFilter] = React.useState<string>("all");
  const [positionFilter, setPositionFilter] = React.useState<string>("all");
  const [statusFilter, setStatusFilter] = React.useState<string>("all");

  // Unique options for each filter
  const [periodOptions, setPeriodOptions] = React.useState<string[]>([]);
  const [departmentOptions, setDepartmentOptions] = React.useState<string[]>([]);
  const [positionOptions, setPositionOptions] = React.useState<string[]>([]);
  const [statusOptions, setStatusOptions] = React.useState<string[]>([]);

  // Local state for filtered data
  const [filteredData, setFilteredData] = React.useState<Employee[]>([]);

  // Pagination state: show 100 rows per page
  const [pageSize] = React.useState(100);

  // Compute filter options when data loads or frequency changes
  React.useEffect(() => {
    if (data && Array.isArray(data)) {
      const periodSet = new Set<string>();
      const deptSet = new Set<string>();
      const posSet = new Set<string>();
      const statSet = new Set<string>();
      data.forEach((emp: Employee) => {
        if (emp.JoinDate) {
          let key = "";
          if (frequency === "month") key = getMonthKey(emp.JoinDate);
          else if (frequency === "quarter") key = getQuarterKey(emp.JoinDate);
          else if (frequency === "year") key = getYearKey(emp.JoinDate);
          periodSet.add(key);
        }
        if (emp.Department) deptSet.add(emp.Department);
        if (emp.Position) posSet.add(emp.Position);
        if (emp.Status) statSet.add(emp.Status);
      });
      setPeriodOptions(Array.from(periodSet).sort());
      setDepartmentOptions(["all", ...Array.from(deptSet).sort()]);
      setPositionOptions(["all", ...Array.from(posSet).sort()]);
      setStatusOptions(["all", ...Array.from(statSet).sort()]);
      setSelectedPeriod("all");
      setDepartmentFilter("all");
      setPositionFilter("all");
      setStatusFilter("all");
      setFilteredData(data);
    }
  }, [data, frequency]);

  // Function to apply filters
  const applyFilters = () => {
    if (!data) return;
    let filtered = data;
    // Frequency filter on join date
    if (selectedPeriod !== "all") {
      filtered = filtered.filter((emp: Employee) => {
        if (!emp.JoinDate) return false;
        let key = "";
        if (frequency === "month") key = getMonthKey(emp.JoinDate);
        else if (frequency === "quarter") key = getQuarterKey(emp.JoinDate);
        else if (frequency === "year") key = getYearKey(emp.JoinDate);
        return key === selectedPeriod;
      });
    }
    // Department filter
    if (departmentFilter !== "all") {
      filtered = filtered.filter((emp: Employee) => emp.Department === departmentFilter);
    }
    // Position filter
    if (positionFilter !== "all") {
      filtered = filtered.filter((emp: Employee) => emp.Position === positionFilter);
    }
    // Status filter
    if (statusFilter !== "all") {
      filtered = filtered.filter((emp: Employee) => emp.Status === statusFilter);
    }
    setFilteredData(filtered);
  };

  // Define columns for the table
  const columns: ColumnDef<Employee>[] = [
    {
      accessorKey: "FirstName",
      header: "Name",
      cell: ({ row }) => (
        <div>
          {row.original.FirstName} {row.original.LastName}
        </div>
      ),
    },
    { accessorKey: "Email", header: "Email" },
    { accessorKey: "Department", header: "Department" },
    { accessorKey: "Position", header: "Position" },
    {
      accessorKey: "Status",
      header: "Status",
      cell: ({ row }) => <Badge>{row.original.Status}</Badge>,
    },
    { accessorKey: "JoinDate", header: "Join Date" },
    { accessorKey: "Gender", header: "Gender" },
    { accessorKey: "Age", header: "Age" },
  ];

  const table = useReactTable({
    data: filteredData,
    columns,
    getCoreRowModel: getCoreRowModel(),
    getPaginationRowModel: getPaginationRowModel(),
    initialState: { pagination: { pageSize, pageIndex: 0 } },
  });

  if (error) return <div>Failed to load employee data</div>;
  if (!data) return <div>Loading...</div>;

  return (
    <div className="space-y-4">
      {/* Filter Controls */}
      <div className="flex flex-col gap-4">
        <div className="flex gap-4 items-center">
          <Label>Frequency:</Label>
          <Select value={frequency} onValueChange={(value) => setFrequency(value as "month" | "quarter" | "year")}>
            <SelectTrigger className="w-32">
              <SelectValue placeholder="Select frequency" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="month">Month</SelectItem>
              <SelectItem value="quarter">Quarter</SelectItem>
              <SelectItem value="year">Year</SelectItem>
            </SelectContent>
          </Select>
        </div>
        <div className="flex gap-4 items-center">
          <Label>Period:</Label>
          <Select value={selectedPeriod} onValueChange={setSelectedPeriod}>
            <SelectTrigger className="w-40">
              <SelectValue placeholder="Select period" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="all">All</SelectItem>
              {periodOptions.map((option) => (
                <SelectItem key={option} value={option}>
                  {option}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
        </div>
        <div className="flex gap-4 items-center">
          <Label>Department:</Label>
          <Select value={departmentFilter} onValueChange={setDepartmentFilter}>
            <SelectTrigger className="w-40">
              <SelectValue placeholder="Select department" />
            </SelectTrigger>
            <SelectContent>
              {departmentOptions.map((dept) => (
                <SelectItem key={dept} value={dept}>
                  {dept}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
        </div>
        <div className="flex gap-4 items-center">
          <Label>Position:</Label>
          <Select value={positionFilter} onValueChange={setPositionFilter}>
            <SelectTrigger className="w-40">
              <SelectValue placeholder="Select position" />
            </SelectTrigger>
            <SelectContent>
              {positionOptions.map((pos) => (
                <SelectItem key={pos} value={pos}>
                  {pos}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
        </div>
        <div className="flex gap-4 items-center">
          <Label>Status:</Label>
          <Select value={statusFilter} onValueChange={setStatusFilter}>
            <SelectTrigger className="w-40">
              <SelectValue placeholder="Select status" />
            </SelectTrigger>
            <SelectContent>
              {statusOptions.map((stat) => (
                <SelectItem key={stat} value={stat}>
                  {stat}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
        </div>
        <Button onClick={applyFilters}>Apply Filters</Button>
      </div>

      {/* Employee Data Table */}
      <div className="w-full border rounded-md">
        <Table>
          <TableHeader>
            {table.getHeaderGroups().map((headerGroup) => (
              <TableRow key={headerGroup.id}>
                {headerGroup.headers.map((header) =>
                  header.isPlaceholder ? null : (
                    <TableHead key={header.id}>
                      {flexRender(header.column.columnDef.header, header.getContext())}
                    </TableHead>
                  )
                )}
              </TableRow>
            ))}
          </TableHeader>
          <TableBody>
            {table.getRowModel().rows.length ? (
              table.getRowModel().rows.map((row) => (
                <TableRow key={row.id}>
                  {row.getVisibleCells().map((cell) => (
                    <TableCell key={cell.id}>{flexRender(cell.column.columnDef.cell, cell.getContext())}</TableCell>
                  ))}
                </TableRow>
              ))
            ) : (
              <TableRow>
                <TableCell colSpan={columns.length} className="h-24 text-center">
                  No results.
                </TableCell>
              </TableRow>
            )}
          </TableBody>
        </Table>
      </div>

      {/* Pagination Controls */}
      <div className="flex items-center justify-between mt-4">
        <Button onClick={() => table.previousPage()} disabled={!table.getCanPreviousPage()}>
          Previous
        </Button>
        <span>
          Page {table.getState().pagination.pageIndex + 1} of {table.getPageCount()}
        </span>
        <Button onClick={() => table.nextPage()} disabled={!table.getCanNextPage()}>
          Next
        </Button>
      </div>
    </div>
  );
}
