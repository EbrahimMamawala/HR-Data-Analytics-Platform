// app/api/employees/route.ts
import { NextRequest, NextResponse } from "next/server";
import { getEmployees } from "@/lib/data";
import { EmployeeResponse } from "@/lib/data";
import { connectToDatabase } from "@/lib/mongodb";

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

export async function POST(request: NextRequest) {
  try {
    const data = await request.json()

    // Destructure & basic validation
    const {
      firstName,
      lastName,
      email,
      department,
      position,
      status,
      joinDate,
      gender,
      age,
    } = data as {
      firstName: string
      lastName: string
      email: string
      department: string
      position: string
      status: string
      joinDate: string
      gender: string
      age: number
    }

    if (
      !firstName ||
      !lastName ||
      !email ||
      !department ||
      !position ||
      !status ||
      !joinDate ||
      !gender ||
      typeof age !== 'number'
    ) {
      return NextResponse.json(
        { error: 'Missing or invalid fields' },
        { status: 400 }
      )
    }

    // Use your connectToDatabase helper
    const { db } = await connectToDatabase()

    const doc = {
      FirstName: firstName,
      LastName: lastName,
      Email: email,
      Department: department,
      Position: position,
      Status: status,
      JoinDate: joinDate,
      Gender: gender,
      Age: age,
    }

    const result = await db.collection('Employees').insertOne(doc)

    return NextResponse.json(
      { message: 'Employee added', id: result.insertedId },
      { status: 201 }
    )
  } catch (error) {
    console.error('API POST /employees Error:', error)
    return NextResponse.json(
      { message: 'Internal Server Error' },
      { status: 500 }
    )
  }
}