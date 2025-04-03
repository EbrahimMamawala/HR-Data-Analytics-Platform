// lib/data.ts
import { connectToDatabase } from "./mongodb";
import { ObjectId, Db } from "mongodb";

// Type definition for your employee documents
interface Employee {
  _id: ObjectId;
  EmployeeID: string;
  Age: number;
  Department: string;
  Email: string;
  FirstName: string;
  LastName: string;
  // Add other fields as needed
}

export async function getEmployees(): Promise<EmployeeResponse[]> {
  try {
    const { db } = await connectToDatabase();
    
    // Access the Employees collection
    const employees = await (db as Db).collection<Employee>("Employees")
      .find({})
      .toArray();

    // Convert ObjectId to string for serialization
    return employees.map(employee => ({
      ...employee,
      _id: employee._id.toString(),
      // Convert other MongoDB specific types if needed
    }));
    
  } catch (error) {
    console.error("Error fetching employees:", error);
    throw new Error("Failed to fetch employees");
  }
}

// Optional: Type for API response
export type EmployeeResponse = Omit<Employee, "_id"> & {
  _id: string;
};