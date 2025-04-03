"use client";

import * as React from "react";
import { Button } from "@/components/ui/button";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";

interface DiversityFiltersProps {
  onFiltersChange: (filters: { date: string; period: string }) => void;
}

export function DiversityFilters({ onFiltersChange }: DiversityFiltersProps) {
  const [periodType, setPeriodType] = React.useState("monthly");
  const [selectedYear, setSelectedYear] = React.useState<string>("2023");
  const [selectedMonth, setSelectedMonth] = React.useState<string>("01");
  const [selectedQuarter, setSelectedQuarter] = React.useState<string>("Q1");

  // Define options for years, months, and quarters.
  const years = Array.from({ length: 16 }, (_, i) => String(2010 + i)); // 2010 to 2025
  const months = [
    { value: "01", label: "January" },
    { value: "02", label: "February" },
    { value: "03", label: "March" },
    { value: "04", label: "April" },
    { value: "05", label: "May" },
    { value: "06", label: "June" },
    { value: "07", label: "July" },
    { value: "08", label: "August" },
    { value: "09", label: "September" },
    { value: "10", label: "October" },
    { value: "11", label: "November" },
    { value: "12", label: "December" },
  ];
  const quarters = [
    { value: "Q1", label: "Q1" },
    { value: "Q2", label: "Q2" },
    { value: "Q3", label: "Q3" },
    { value: "Q4", label: "Q4" },
  ];

  // Build the proper date string based on period type.
  const handleSubmit = () => {
    let dateStr = "";
    if (periodType === "monthly") {
      // e.g., "2023-01"
      dateStr = `${selectedYear}-${selectedMonth}`;
    } else if (periodType === "quarterly") {
      // e.g., "2023-Q1"
      dateStr = `${selectedYear}-${selectedQuarter}`;
    } else if (periodType === "yearly") {
      // e.g., "2023"
      dateStr = selectedYear;
    }
    onFiltersChange({ date: dateStr, period: periodType });
  };

  return (
    <div className="flex flex-wrap items-center gap-2">
      {/* Select the period type */}
      <Select value={periodType} onValueChange={setPeriodType}>
        <SelectTrigger className="w-[180px]">
          <SelectValue placeholder="Select period type" />
        </SelectTrigger>
        <SelectContent>
          <SelectItem value="monthly">Monthly</SelectItem>
          <SelectItem value="quarterly">Quarterly</SelectItem>
          <SelectItem value="yearly">Yearly</SelectItem>
        </SelectContent>
      </Select>

      {/* Select the year */}
      <Select value={selectedYear} onValueChange={setSelectedYear}>
        <SelectTrigger className="w-[120px]">
          <SelectValue placeholder="Year" />
        </SelectTrigger>
        <SelectContent>
          {years.map((year) => (
            <SelectItem key={year} value={year}>
              {year}
            </SelectItem>
          ))}
        </SelectContent>
      </Select>

      {/* Conditional dropdown for month or quarter */}
      {periodType === "monthly" && (
        <Select value={selectedMonth} onValueChange={setSelectedMonth}>
          <SelectTrigger className="w-[150px]">
            <SelectValue placeholder="Month" />
          </SelectTrigger>
          <SelectContent>
            {months.map((month) => (
              <SelectItem key={month.value} value={month.value}>
                {month.label}
              </SelectItem>
            ))}
          </SelectContent>
        </Select>
      )}

      {periodType === "quarterly" && (
        <Select value={selectedQuarter} onValueChange={setSelectedQuarter}>
          <SelectTrigger className="w-[120px]">
            <SelectValue placeholder="Quarter" />
          </SelectTrigger>
          <SelectContent>
            {quarters.map((q) => (
              <SelectItem key={q.value} value={q.value}>
                {q.label}
              </SelectItem>
            ))}
          </SelectContent>
        </Select>
      )}

      <Button onClick={handleSubmit}>Submit</Button>
    </div>
  );
}
