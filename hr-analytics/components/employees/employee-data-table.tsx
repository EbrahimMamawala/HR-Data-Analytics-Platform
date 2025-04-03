"use client";
import * as React from "react";
import useSWR from "swr";
import { ColumnDef, flexRender, useReactTable, getCoreRowModel } from "@tanstack/react-table";
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table";
import { Badge } from "@/components/ui/badge";

const fetcher = (url: string) => fetch(url).then((res) => res.json());

export function EmployeeDataTable() {
  const { data, error } = useSWR("/api/employees", fetcher);

  const columns: ColumnDef<any>[] = [
    {
      accessorKey: "FirstName",
      header: "Name",
      cell: ({ row }) => <div>{row.original.FirstName} {row.original.LastName}</div>,
    },
    { accessorKey: "Email", header: "Email" },
    { accessorKey: "Department", header: "Department" },
    { accessorKey: "Position", header: "Position" },
    { accessorKey: "Status", header: "Status", cell: ({ row }) => <Badge>{row.original.Status}</Badge> },
    { accessorKey: "JoinDate", header: "Join Date" },
    { accessorKey: "Gender", header: "Gender" },
    { accessorKey: "Age", header: "Age" },
  ];

  const table = useReactTable({
    data: data || [],
    columns,
    getCoreRowModel: getCoreRowModel(),
  });

  if (error) return <div>Failed to load</div>;
  if (!data) return <div>Loading...</div>;

  return (
    <div className="w-full border rounded-md">
      <Table>
        <TableHeader>
          {table.getHeaderGroups().map((headerGroup) => (
            <TableRow key={headerGroup.id}>
              {headerGroup.headers.map((header) => (
                <TableHead key={header.id}>{flexRender(header.column.columnDef.header, header.getContext())}</TableHead>
              ))}
            </TableRow>
          ))}
        </TableHeader>
        <TableBody>
          {table.getRowModel().rows.map((row) => (
            <TableRow key={row.id}>
              {row.getVisibleCells().map((cell) => (
                <TableCell key={cell.id}>{flexRender(cell.column.columnDef.cell, cell.getContext())}</TableCell>
              ))}
            </TableRow>
          ))}
        </TableBody>
      </Table>
    </div>
  );
}
