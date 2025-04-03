import { NextResponse } from "next/server";
import { connectToDatabase } from "@/lib/mongodb";

export async function GET(request: Request) {
  const { searchParams } = new URL(request.url);

  // Get the period type and date from query parameters.
  const periodType = searchParams.get("period") || "quarterly";
  const date = searchParams.get("date") || "2014-Q4";

  // Map the period type to the frequency field in the document.
  let frequency: string;
  if (periodType === "monthly") {
    frequency = "month";
  } else if (periodType === "quarterly") {
    frequency = "quarter";
  } else if (periodType === "yearly") {
    frequency = "year";
  } else {
    frequency = "quarter"; // default fallback
  }

  console.log("API Route: Query Params:", { frequency, period: date });

  const { db } = await connectToDatabase();
  const collection = db.collection("Diversity"); // Use your actual collection name

  // Query using the mapped frequency and the date (which represents the period value)
  const data = await collection.findOne({ frequency, period: date });
  console.log("API Route: Fetched Data:", data);

  if (!data) {
    return NextResponse.json({ error: "Data not found" }, { status: 404 });
  }

  return NextResponse.json(data);
}
