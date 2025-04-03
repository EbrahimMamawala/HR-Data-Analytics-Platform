// app/api/employees/route.ts
import { NextResponse } from "next/server";
import { getEmployees } from "@/lib/data";
import { EmployeeResponse } from "@/lib/data";

export async function GET() {
  try {
    const employees = await getEmployees();
    return NextResponse.json(employees satisfies EmployeeResponse[], { 
      status: 200 
    });
  } catch (error) {
    console.error("API Error:", error);
    return NextResponse.json(
      { message: "Internal Server Error" },
      { status: 500 }
    );
  }
}